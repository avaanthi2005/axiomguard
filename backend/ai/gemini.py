import os
import time
import hashlib
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# Models are tried in order. Each model has its own free-tier quota, so when one is
# rate limited (429) or retired (404) the next one is used. Set GEMINI_MODEL on Render
# to put a different model first without changing any code.
MODELS = [m for m in [os.getenv("GEMINI_MODEL"), "gemini-2.5-flash-lite", "gemini-2.5-flash"] if m]

# Same analysis asked again within 10 minutes = reuse the answer (saves free quota).
_CACHE = {}
CACHE_TTL = 600


def _fallback(module: str, data: dict) -> str:
    """Friendly text shown when every Gemini attempt failed."""
    verdict = score = None
    try:
        if module == "scan":
            a = data.get("axiom_score", {})
            verdict, score = a.get("level"), a.get("axiom_score")
        elif module == "phish":
            u = data.get("url_analysis", {})
            verdict, score = u.get("verdict"), u.get("risk_score")
        elif module == "guard":
            verdict, score = data.get("verdict"), data.get("guard_score")
    except Exception:
        pass
    text = "The AI summary is temporarily unavailable (the Gemini free limit was probably reached)."
    if verdict is not None:
        text += f" The analysis itself is complete: result {verdict}, score {score}."
    return text + " Check the detailed panels above, or run the check again in a minute."


def get_gemini_explanation(module: str, data: dict) -> str:
    """
    Sends scan/phish/guard results to Gemini and returns a plain-English
    security explanation. Falls back gracefully if the key is missing
    or the API call fails.
    """
    if not GEMINI_API_KEY or _client is None:
        return "AI explanation unavailable (no Gemini API key configured)."

    prompts = {
        "scan": f"""You are a cybersecurity assistant. Explain this domain security scan result
in simple, plain English for a non-technical reader. Be concise (4-6 sentences).
Highlight the biggest risk if any, and give one practical recommendation.

Scan data: {data}""",

        "phish": f"""You are a cybersecurity assistant. Explain this phishing/URL analysis result
in simple, plain English for a non-technical reader. Be concise (4-6 sentences).
Explain why the URL was flagged as safe/suspicious/dangerous, and give one practical tip.

Analysis data: {data}""",

        "guard": f"""You are a cybersecurity assistant. Explain this website behavioral security
analysis in simple, plain English for a non-technical reader. Be concise (4-6 sentences).
Explain what was found and whether the site seems safe to visit.

Guard data: {data}"""
    }

    prompt = prompts.get(module, f"Explain this security data in plain English: {data}")

    key = module + hashlib.md5(str(data).encode("utf-8", "ignore")).hexdigest()
    hit = _CACHE.get(key)
    if hit and time.time() - hit[0] < CACHE_TTL:
        return hit[1]

    for model in MODELS:
        for attempt in range(2):
            try:
                response = _client.models.generate_content(model=model, contents=prompt)
                text = (response.text or "").strip()
                if text:
                    if len(_CACHE) > 200:
                        _CACHE.clear()
                    _CACHE[key] = (time.time(), text)
                    return text
                break
            except Exception as e:
                msg = str(e)
                print(f"Gemini call failed on {model} (try {attempt + 1}): {msg}")
                if "503" in msg or "UNAVAILABLE" in msg:
                    time.sleep(1.5)
                    continue
                break

    return _fallback(module, data)
