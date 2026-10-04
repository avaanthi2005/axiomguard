from fastapi import APIRouter, Depends
from fastapi.responses import Response
from engines.phish.feature_extractor import extract_features
from engines.phish.entropy_calculator import calculate_entropy, get_entropy_risk
from engines.phish.homoglyph_detector import detect_homoglyph
from engines.phish.email_parser import parse_email_headers
from urllib.parse import urlparse
from reports.pdf_generator import generate_phish_report
from database.db import save_scan
from auth.deps import get_current_user_optional
import pickle
import numpy as np
import os

router = APIRouter()

MODEL_PATH = "ml/phish_model.pkl"
ml_model = None
if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, 'rb') as f:
        ml_model = pickle.load(f)
    print("✅ Phishing ML model loaded successfully")

try:
    from ai.gemini import get_gemini_explanation
except Exception:
    get_gemini_explanation = None


def run_full_phish_analysis(url: str, email_text: str, user_id: int = None) -> dict:
    result = {}

    if url:
        try:
            parsed = urlparse(url if url.startswith('http') else 'http://' + url)
            domain = parsed.netloc.replace("www.", "") or url
        except:
            domain = url

        features     = extract_features(url)
        entropy      = calculate_entropy(url)
        entropy_risk = get_entropy_risk(entropy)
        homoglyph    = detect_homoglyph(domain)

        ml_prediction = None
        ml_confidence = None
        if ml_model is not None:
            try:
                feature_values = list(features['features'].values())
                X = np.array([feature_values])
                ml_prediction = int(ml_model.predict(X)[0])
                ml_confidence = round(float(ml_model.predict_proba(X)[0][ml_prediction]) * 100, 1)
            except Exception as e:
                print(f"ML prediction failed: {e}")

        total_risk = (
            features["feature_risk_score"] * 0.5 +
            entropy_risk["score"] * 0.2 +
            homoglyph["risk_score"] * 0.3
        )
        total_risk = round(min(total_risk, 100), 1)

        if total_risk >= 60:
            verdict = "DANGEROUS"
            verdict_color = "red"
        elif total_risk >= 30:
            verdict = "SUSPICIOUS"
            verdict_color = "orange"
        else:
            verdict = "SAFE"
            verdict_color = "green"

        result["url_analysis"] = {
            "url": url,
            "domain": domain,
            "verdict": verdict,
            "verdict_color": verdict_color,
            "risk_score": total_risk,
            "feature_analysis": features,
            "entropy": {
                "value": entropy,
                "risk": entropy_risk
            },
            "homoglyph_check": homoglyph,
            "ml_model_prediction": "PHISHING" if ml_prediction == 1 else "LEGITIMATE" if ml_prediction == 0 else "Model not loaded",
            "ml_confidence": ml_confidence,
        }

        # Save this analysis to history (non-blocking)
        try:
            save_scan(
                module="AXIOM//PHISH",
                target=domain,
                verdict=verdict,
                score=total_risk,
                result=result,
                user_id=user_id
            )
        except Exception as e:
            print(f"Failed to save scan history: {e}")

    if email_text:
        result["email_analysis"] = parse_email_headers(email_text)

    if get_gemini_explanation is not None:
        try:
            result["ai_explanation"] = get_gemini_explanation("phish", result)
        except Exception as e:
            print(f"Gemini explanation failed: {e}")
            result["ai_explanation"] = "AI explanation unavailable"

    return result


@router.post("/")
async def analyze_phish(data: dict, current_user: dict = Depends(get_current_user_optional)):
    url = data.get("url", "").strip()
    email_text = data.get("email_text", "").strip()

    if not url and not email_text:
        return {"error": "Provide a URL or email text"}

    user_id = current_user["id"] if current_user else None
    return run_full_phish_analysis(url, email_text, user_id=user_id)


@router.post("/report")
async def phish_report(data: dict, current_user: dict = Depends(get_current_user_optional)):
    url = data.get("url", "").strip()
    email_text = data.get("email_text", "").strip()

    if not url and not email_text:
        return {"error": "Provide a URL or email text"}

    user_id = current_user["id"] if current_user else None
    result = run_full_phish_analysis(url, email_text, user_id=user_id)
    pdf_bytes = generate_phish_report(result)

    filename_base = (result.get("url_analysis") or {}).get("domain", "email_analysis")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=axiomguard_phish_{filename_base}.pdf"}
    )