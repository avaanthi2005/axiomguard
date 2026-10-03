import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


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

    try:
        response = _client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip()

    except Exception as e:
        print(f"Gemini call failed: {e}")
        return "AI explanation unavailable (request failed)."