from fastapi import APIRouter, Depends
from fastapi.responses import Response
from engines.scan.port_scanner import scan_ports
from engines.scan.ssl_inspector import inspect_ssl
from engines.scan.dns_auditor import audit_dns
from engines.scan.axiom_score import calculate_axiom_score
from reports.pdf_generator import generate_scan_report
from database.db import save_scan
from auth.deps import get_current_user_optional

# Load Gemini explanation helper
try:
    from ai.gemini import get_gemini_explanation
except Exception:
    get_gemini_explanation = None

router = APIRouter()


def run_full_scan(domain: str, user_id: int = None) -> dict:
    domain = domain.replace("https://", "").replace("http://", "").split("/")[0]

    port_results = scan_ports(domain)
    ssl_results  = inspect_ssl(domain)
    dns_results  = audit_dns(domain)

    port_risk = port_results.get("port_risk_score", 0)
    ssl_risk  = ssl_results.get("ssl_risk_score", 0)
    dns_risk  = dns_results.get("dns_risk_score", 0)

    axiom = calculate_axiom_score(port_risk, ssl_risk, dns_risk)

    result = {
        "domain": domain,
        "ip": port_results.get("ip"),
        "axiom_score": axiom,
        "port_scan": port_results,
        "ssl_inspection": ssl_results,
        "dns_audit": dns_results,
    }

    if get_gemini_explanation is not None:
        try:
            result["ai_explanation"] = get_gemini_explanation("scan", result)
        except Exception as e:
            print(f"Gemini explanation failed: {e}")
            result["ai_explanation"] = "AI explanation unavailable"

    # Save this scan to history (non-blocking — don't let a DB error break the scan)
    try:
        save_scan(
            module="AXIOM//SCAN",
            target=domain,
            verdict=axiom.get("level"),
            score=axiom.get("axiom_score"),
            result=result,
            user_id=user_id
        )
    except Exception as e:
        print(f"Failed to save scan history: {e}")

    return result


@router.post("/")
async def scan_domain(data: dict, current_user: dict = Depends(get_current_user_optional)):
    domain = data.get("domain", "").strip()
    if not domain:
        return {"error": "No domain provided"}
    user_id = current_user["id"] if current_user else None
    return run_full_scan(domain, user_id=user_id)


@router.post("/report")
async def scan_report(data: dict, current_user: dict = Depends(get_current_user_optional)):
    domain = data.get("domain", "").strip()
    if not domain:
        return {"error": "No domain provided"}

    user_id = current_user["id"] if current_user else None
    result = run_full_scan(domain, user_id=user_id)
    pdf_bytes = generate_scan_report(result)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=axiomguard_scan_{result['domain']}.pdf"}
    )