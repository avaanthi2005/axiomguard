import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def analyze_static(url: str) -> dict:
    """
    Fetches a webpage and analyzes its HTML content
    for suspicious static indicators.
    All logic is yours — no external API.
    """
    signals = []
    risk_score = 0

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=8, allow_redirects=True)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

    except requests.exceptions.Timeout:
        return {"error": "Page took too long to load", "signals": [], "static_risk_score": 0}
    except Exception as e:
        return {"error": str(e), "signals": [], "static_risk_score": 0}

    # CHECK 1: Hidden iframes
    iframes = soup.find_all('iframe')
    hidden_iframes = []
    for iframe in iframes:
        style = iframe.get('style', '')
        width = iframe.get('width', '')
        height = iframe.get('height', '')
        if ('display:none' in style.replace(' ', '') or
            'visibility:hidden' in style.replace(' ', '') or
            width == '0' or height == '0'):
            hidden_iframes.append(str(iframe)[:100])

    if hidden_iframes:
        signals.append({
            "signal": "hidden_iframe",
            "weight": 35,
            "description": f"Hidden iframe detected — classic malware delivery technique",
            "severity": "HIGH"
        })
        risk_score += 35

    # CHECK 2: Obfuscated JavaScript
    scripts = soup.find_all('script')
    all_js = ' '.join([s.string or '' for s in scripts])

    obfuscation_patterns = [
        (r'eval\s*\(', "eval() detected — common obfuscation technique"),
        (r'unescape\s*\(', "unescape() detected — obfuscation indicator"),
        (r'fromCharCode', "String.fromCharCode detected — character encoding obfuscation"),
        (r'atob\s*\(', "atob() detected — base64 decoding in JS"),
        (r'\\x[0-9a-fA-F]{2}', "Hex encoding detected in JavaScript"),
    ]

    for pattern, description in obfuscation_patterns:
        if re.search(pattern, all_js):
            signals.append({
                "signal": "obfuscated_js",
                "weight": 30,
                "description": description,
                "severity": "HIGH"
            })
            risk_score += 30
            break  # Count once even if multiple patterns found

    # CHECK 3: Cross-domain form submissions
    page_domain = urlparse(url).netloc
    forms = soup.find_all('form')
    for form in forms:
        action = form.get('action', '')
        if action and action.startswith('http'):
            form_domain = urlparse(action).netloc
            if form_domain and form_domain != page_domain:
                signals.append({
                    "signal": "cross_domain_form",
                    "weight": 35,
                    "description": f"Form submits data to external domain: {form_domain}",
                    "severity": "HIGH"
                })
                risk_score += 35
                break

    # CHECK 4: Password field on HTTP
    if not url.startswith('https'):
        pwd_fields = soup.find_all('input', {'type': 'password'})
        if pwd_fields:
            signals.append({
                "signal": "password_on_http",
                "weight": 40,
                "description": "Password input field found on non-HTTPS page — credentials sent unencrypted",
                "severity": "CRITICAL"
            })
            risk_score += 40

    # CHECK 5: Invisible text elements
    invisible = soup.find_all(style=re.compile(
        r'(visibility\s*:\s*hidden|display\s*:\s*none|opacity\s*:\s*0)',
        re.IGNORECASE
    ))
    if len(invisible) > 5:
        signals.append({
            "signal": "excessive_invisible_elements",
            "weight": 15,
            "description": f"{len(invisible)} invisible elements found — may be hiding content",
            "severity": "MEDIUM"
        })
        risk_score += 15

    # CHECK 6: Too many external scripts
    ext_scripts = [s for s in scripts if s.get('src', '').startswith('http')]
    if len(ext_scripts) > 15:
        signals.append({
            "signal": "excessive_external_scripts",
            "weight": 10,
            "description": f"{len(ext_scripts)} external scripts loaded — unusual for most websites",
            "severity": "LOW"
        })
        risk_score += 10

    # CHECK 7: Crypto mining patterns
    mining_patterns = ['coinhive', 'cryptonight', 'minero', 'coin-hive', 'cryptoloot']
    for pattern in mining_patterns:
        if pattern in all_js.lower():
            signals.append({
                "signal": "crypto_mining",
                "weight": 50,
                "description": f"Cryptocurrency mining script detected: {pattern}",
                "severity": "CRITICAL"
            })
            risk_score += 50
            break

    # CHECK 8: Fake login page detection
    has_password = bool(soup.find('input', {'type': 'password'}))
    has_username = bool(soup.find('input', {'type': re.compile(r'text|email', re.I)}))
    page_title = soup.title.string.lower() if soup.title else ""
    login_keywords = ['login', 'sign in', 'signin', 'log in', 'verify', 'authenticate']
    is_login_page = any(kw in page_title for kw in login_keywords)

    if has_password and has_username:
        signals.append({
            "signal": "login_form_detected",
            "weight": 5,
            "description": "Login form detected — verify this is the legitimate site",
            "severity": "INFO"
        })
        risk_score += 5

    return {
        "signals": signals,
        "static_risk_score": min(risk_score, 100),
        "page_title": soup.title.string if soup.title else "No title",
        "total_scripts": len(scripts),
        "external_scripts": len(ext_scripts),
        "total_forms": len(forms),
        "total_iframes": len(iframes)
    }