import os
import time
import json
import hashlib
import requests
import re
from dotenv import load_dotenv
try:
    from google import genai
except Exception:
    genai = None

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

_gemini = genai.Client(api_key=GEMINI_API_KEY) if (GEMINI_API_KEY and genai is not None) else None

# Prefer a current stable Gemini model, while retaining 2.5 fallbacks for existing keys.
GEMINI_MODELS = []
for model in [
    os.getenv("GEMINI_MODEL", "").strip(),
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
]:
    if model and model not in GEMINI_MODELS:
        GEMINI_MODELS.append(model)

GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b").strip()
CACHE_TTL = int(os.getenv("AI_CACHE_TTL", "600"))
_CACHE = {}


def _prompt(module: str, data: dict) -> str:
    instructions = {
        "scan": "Explain this domain security scan. Highlight the biggest risk and give one practical recommendation.",
        "phish": "Explain this phishing/URL analysis. Explain why it was classified this way and give one practical safety tip.",
        "guard": "Explain this website security analysis. Explain the important findings and whether the site appears safe to visit.",
    }
    task = instructions.get(module, "Explain this cybersecurity analysis.")
    return (
        "You are AXIOMGUARD's cybersecurity explanation assistant. "
        "The supplied score and verdict were already calculated by AXIOMGUARD; do not change them. "
        "Explain the result in simple plain English for a non-technical reader in 4-6 concise sentences. "
        "Use plain text only: no Markdown, no asterisks, no headings, and no bullet formatting. "
        f"{task}\n\nAnalysis data:\n{json.dumps(data, default=str, ensure_ascii=False)}"
    )


def _clean_explanation(text: str) -> str:
    """Normalize provider output so the React UI never shows raw Markdown markers."""
    text = str(text or "").strip()
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*•]\s+", "", text, flags=re.MULTILINE)
    return text.strip()


def _extract_summary(module: str, data: dict):
    if module == "scan":
        a = data.get("axiom_score", {}) or {}
        return a.get("level") or a.get("verdict"), a.get("axiom_score") or a.get("score")
    if module == "phish":
        u = data.get("url_analysis", {}) or {}
        return u.get("verdict") or data.get("verdict"), u.get("risk_score") or data.get("risk_score")
    if module == "guard":
        return data.get("verdict"), data.get("guard_score")
    return data.get("verdict"), data.get("score")


def _local_explanation(module: str, data: dict) -> str:
    """Zero-credit fallback so the explanation panel always remains useful."""
    verdict, score = _extract_summary(module, data)
    verdict_text = str(verdict or "completed").replace("_", " ").title()
    score_text = f" with a score of {score}" if score is not None else ""

    if module == "scan":
        return (
            f"AXIOMGUARD completed the domain security analysis and classified the result as {verdict_text}{score_text}. "
            "This result is based on the technical checks shown in the port, SSL/TLS, DNS and related security panels. "
            "Review any warnings or failed checks first, because they contribute to the overall risk level. "
            "The security result remains valid even though an external AI explanation service is temporarily unavailable. "
            "Address the highest-risk finding shown above and run the scan again after making security changes."
        )
    if module == "phish":
        return (
            f"AXIOMGUARD completed the phishing analysis and classified the result as {verdict_text}{score_text}. "
            "The verdict comes from AXIOMGUARD's URL features, entropy/look-alike checks and machine-learning analysis shown above. "
            "A higher risk score means more phishing indicators were detected. "
            "The classification itself does not depend on the external AI explanation service. "
            "Avoid entering credentials or sensitive information when the detailed findings show suspicious indicators."
        )
    if module == "guard":
        return (
            f"AXIOMGUARD completed the website protection analysis and classified the site as {verdict_text}{score_text}. "
            "The result is based on the static, behavioural and domain-reputation checks displayed above. "
            "Warnings in those panels indicate the signals that influenced the final Guard score. "
            "The security verdict remains available even if external AI services are temporarily unavailable. "
            "Use extra caution with sensitive information whenever the site receives a warning or danger verdict."
        )
    return f"AXIOMGUARD completed the analysis with result {verdict_text}{score_text}. Review the detailed findings for the factors that produced this result."


def _call_gemini(prompt: str):
    if not _gemini:
        return None
    for model in GEMINI_MODELS:
        for attempt in range(2):
            try:
                response = _gemini.models.generate_content(model=model, contents=prompt)
                text = (getattr(response, "text", None) or "").strip()
                if text:
                    print(f"AI explanation provider: Gemini ({model})")
                    return text
                break
            except Exception as exc:
                msg = str(exc)
                print(f"Gemini call failed on {model} (try {attempt + 1}): {msg}")
                if attempt == 0 and any(code in msg for code in ("429", "503", "RESOURCE_EXHAUSTED", "UNAVAILABLE")):
                    time.sleep(1.5)
                    continue
                break
    return None


def _call_groq(prompt: str):
    if not GROQ_API_KEY:
        return None
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "max_tokens": 450,
            },
            timeout=20,
        )
        if response.ok:
            payload = response.json()
            text = payload.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            if text:
                print(f"AI explanation provider: Groq ({GROQ_MODEL})")
                return text
        print(f"Groq call failed ({response.status_code}): {response.text[:300]}")
    except Exception as exc:
        print(f"Groq call failed: {exc}")
    return None


def get_gemini_explanation(module: str, data: dict) -> str:
    """Compatibility name used by existing routers; internally uses resilient provider fallback."""
    try:
        serialized = json.dumps(data, sort_keys=True, default=str, ensure_ascii=False)
    except Exception:
        serialized = str(data)
    key = module + hashlib.sha256(serialized.encode("utf-8", "ignore")).hexdigest()
    hit = _CACHE.get(key)
    if hit and time.time() - hit[0] < CACHE_TTL:
        return hit[1]

    prompt = _prompt(module, data)
    text = _call_gemini(prompt)
    if not text:
        text = _call_groq(prompt)
    if not text:
        print("AI explanation provider: AXIOMGUARD local fallback")
        text = _local_explanation(module, data)
    text = _clean_explanation(text)

    if len(_CACHE) > 300:
        _CACHE.clear()
    _CACHE[key] = (time.time(), text)
    return text
