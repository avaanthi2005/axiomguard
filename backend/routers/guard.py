from fastapi import APIRouter, Depends
from fastapi.responses import Response
from urllib.parse import urlparse
from engines.guard.static_analyzer import analyze_static
from engines.guard.behavior_analyzer import analyze_behavior
from engines.guard.reputation_engine import calculate_reputation
from engines.guard.risk_scorer import calculate_guard_score
from engines.guard.false_positive import handle_false_positive
from reports.pdf_generator import generate_guard_report
from database.db import save_scan
from auth.deps import get_current_user_optional

try:
    from ai.gemini import get_gemini_explanation
except Exception:
    get_gemini_explanation = None

router = APIRouter()


def run_full_guard_analysis(url: str, user_id: int = None) -> dict:
    if not url.startswith('http'):
        url = 'https://' + url

    try:
        domain = urlparse(url).netloc.replace("www.", "")
    except:
        domain = url

    static_result   = analyze_static(url)
    behavior_result = analyze_behavior(url)
    reputation      = calculate_reputation(domain)

    static_risk     = static_result.get("static_risk_score", 0)
    behavior_risk   = behavior_result.get("behavior_risk_score", 0)
    reputation_risk = reputation.get("risk_score", 0)

    static_signals   = static_result.get("signals", [])
    behavior_signals = behavior_result.get("signals", [])

    guard_result = calculate_guard_score(
        static_risk, behavior_risk, reputation_risk,
        static_signals, behavior_signals
    )

    fp_result = handle_false_positive(
        guard_result["verdict"],
        guard_result["guard_score"],
        reputation,
        static_signals,
        behavior_signals
    )

    final_verdict = fp_result["verdict"]
    final_score   = fp_result["guard_score"]

    result = {
        "url": url,
        "domain": domain,
        "verdict": final_verdict,
        "guard_score": final_score,
        "color": guard_result["color"],
        "action": guard_result["action"],
        "extension_ui": guard_result["extension_ui"],
        "false_positive_adjusted": fp_result["adjusted"],
        "adjustment_note": fp_result.get("note", ""),
        "score_breakdown": guard_result["score_breakdown"],
        "static_analysis": static_result,
        "behavior_analysis": behavior_result,
        "reputation": reputation
    }

    if get_gemini_explanation is not None:
        try:
            result["ai_explanation"] = get_gemini_explanation("guard", result)
        except Exception as e:
            print(f"Gemini explanation failed: {e}")
            result["ai_explanation"] = "AI explanation unavailable"

    # Save this analysis to history (non-blocking)
    try:
        save_scan(
            module="AXIOM//GUARD",
            target=domain,
            verdict=final_verdict,
            score=final_score,
            result=result,
            user_id=user_id
        )
    except Exception as e:
        print(f"Failed to save scan history: {e}")

    return result


@router.post("/analyze")
async def guard_analyze(data: dict, current_user: dict = Depends(get_current_user_optional)):
    url = data.get("url", "").strip()
    if not url:
        return {"error": "No URL provided"}
    user_id = current_user["id"] if current_user else None
    return run_full_guard_analysis(url, user_id=user_id)


@router.post("/report")
async def guard_report(data: dict, current_user: dict = Depends(get_current_user_optional)):
    url = data.get("url", "").strip()
    if not url:
        return {"error": "No URL provided"}

    user_id = current_user["id"] if current_user else None
    result = run_full_guard_analysis(url, user_id=user_id)
    pdf_bytes = generate_guard_report(result)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=axiomguard_guard_{result['domain']}.pdf"}
    )