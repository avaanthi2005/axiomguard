import re
import requests
from bs4 import BeautifulSoup

REQUIRED_HEADERS = [
    'Content-Security-Policy',
    'Strict-Transport-Security',
    'X-Frame-Options',
    'X-Content-Type-Options',
    'Referrer-Policy'
]

def analyze_behavior(url: str) -> dict:
    """
    Analyzes HTTP response headers and JavaScript
    behavioral patterns for suspicious activity.
    """
    signals = []
    risk_score = 0

    try:
        headers_req = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
        response = requests.get(url, headers=headers_req, timeout=8, allow_redirects=True)
        resp_headers = response.headers
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        redirect_count = len(response.history)
        all_js = ' '.join([s.string or '' for s in soup.find_all('script')])

    except Exception as e:
        return {"error": str(e), "signals": [], "behavior_risk_score": 0}

    # CHECK 1: Missing security headers
    missing_headers = []
    for header in REQUIRED_HEADERS:
        if header not in resp_headers:
            missing_headers.append(header)

    if missing_headers:
        weight = len(missing_headers) * 5
        signals.append({
            "signal": "missing_security_headers",
            "weight": weight,
            "description": f"Missing security headers: {', '.join(missing_headers)}",
            "severity": "MEDIUM" if len(missing_headers) > 2 else "LOW"
        })
        risk_score += weight

    # CHECK 2: Excessive redirects
    if redirect_count > 3:
        signals.append({
            "signal": "excessive_redirects",
            "weight": 20,
            "description": f"Page redirected {redirect_count} times — suspicious redirect chain",
            "severity": "MEDIUM"
        })
        risk_score += 20

    # CHECK 3: Server version exposed
    server = resp_headers.get('Server', '')
    if re.search(r'\d+\.\d+', server):
        signals.append({
            "signal": "server_version_exposed",
            "weight": 10,
            "description": f"Server version exposed in headers: {server}",
            "severity": "LOW"
        })
        risk_score += 10

    # CHECK 4: DevTools detection
    devtools_patterns = [
        r'devtools', r'firebug', r'__debugger',
        r'console\.clear\(\)', r'debugger'
    ]
    for pattern in devtools_patterns:
        if re.search(pattern, all_js, re.IGNORECASE):
            signals.append({
                "signal": "devtools_detection",
                "weight": 25,
                "description": "JavaScript attempts to detect browser DevTools — hiding malicious behavior",
                "severity": "HIGH"
            })
            risk_score += 25
            break

    # CHECK 5: Right-click disabled
    if re.search(r'oncontextmenu|contextmenu.*return.*false', all_js, re.IGNORECASE):
        signals.append({
            "signal": "rightclick_disabled",
            "weight": 15,
            "description": "Right-click disabled via JavaScript — content protection or data theft prevention",
            "severity": "MEDIUM"
        })
        risk_score += 15

    # CHECK 6: History manipulation
    if re.search(r'history\.(push|replace)State', all_js):
        signals.append({
            "signal": "history_manipulation",
            "weight": 10,
            "description": "Browser history manipulation detected via JavaScript",
            "severity": "LOW"
        })
        risk_score += 10

    # CHECK 7: Clipboard access
    if re.search(r'clipboard|navigator\.clipboard|execCommand.*copy', all_js, re.IGNORECASE):
        signals.append({
            "signal": "clipboard_access",
            "weight": 20,
            "description": "JavaScript accesses clipboard — potential data theft",
            "severity": "MEDIUM"
        })
        risk_score += 20

    # CHECK 8: Keylogger patterns
    if re.search(r'keypress|keydown|keyup', all_js) and re.search(r'XMLHttpRequest|fetch', all_js):
        signals.append({
            "signal": "potential_keylogger",
            "weight": 45,
            "description": "Keyboard event listeners combined with network requests — potential keylogger",
            "severity": "CRITICAL"
        })
        risk_score += 45

    return {
        "signals": signals,
        "behavior_risk_score": min(risk_score, 100),
        "redirect_count": redirect_count,
        "security_headers_present": [h for h in REQUIRED_HEADERS if h in resp_headers],
        "security_headers_missing": missing_headers,
        "final_url": response.url
    }