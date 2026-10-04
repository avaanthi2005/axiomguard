import re
import math
from urllib.parse import urlparse
from collections import Counter
from engines.phish.entropy_calculator import calculate_entropy

SUSPICIOUS_KEYWORDS = [
    "login", "signin", "verify", "secure", "account", "update",
    "confirm", "banking", "password", "credential", "suspend",
    "alert", "urgent", "click", "free", "winner", "prize",
    "otp", "kyc", "aadhar", "pan", "upi", "refund"
]

def extract_features(url: str) -> dict:
    """
    Extracts 12 features from a URL for phishing detection.
    These are the features YOUR model will use.
    """
    try:
        parsed = urlparse(url if url.startswith('http') else 'http://' + url)
        domain = parsed.netloc or parsed.path.split('/')[0]
        path = parsed.path
        query = parsed.query
        full_url = url
    except:
        domain = url
        path = ""
        query = ""
        full_url = url

    # Remove www
    domain_clean = domain.replace("www.", "")

    # Feature 1: URL length
    url_length = len(full_url)

    # Feature 2: Dot count
    dot_count = full_url.count('.')

    # Feature 3: Hyphen count
    hyphen_count = full_url.count('-')

    # Feature 4: Digit count
    digit_count = sum(c.isdigit() for c in full_url)

    # Feature 5: Has IP address instead of domain
    has_ip = bool(re.match(
        r'^(\d{1,3}\.){3}\d{1,3}$', domain_clean
    ))

    # Feature 6: Has @ symbol (used to trick browsers)
    has_at_symbol = '@' in full_url

    # Feature 7: Subdomain depth
    subdomain_count = len(domain_clean.split('.')) - 1

    # Feature 8: HTTPS in path (fake HTTPS in URL path)
    https_in_path = 'https' in path.lower()

    # Feature 9: URL entropy
    url_entropy = calculate_entropy(full_url)

    # Feature 10: Suspicious keyword count
    url_lower = full_url.lower()
    suspicious_count = sum(
        1 for kw in SUSPICIOUS_KEYWORDS if kw in url_lower
    )

    # Feature 11: Path depth
    path_depth = len([p for p in path.split('/') if p])

    # Feature 12: Query parameter count
    query_param_count = len(query.split('&')) if query else 0

    features = {
        "url_length": url_length,
        "dot_count": dot_count,
        "hyphen_count": hyphen_count,
        "digit_count": digit_count,
        "has_ip_address": int(has_ip),
        "has_at_symbol": int(has_at_symbol),
        "subdomain_count": subdomain_count,
        "https_in_path": int(https_in_path),
        "url_entropy": url_entropy,
        "suspicious_keyword_count": suspicious_count,
        "path_depth": path_depth,
        "query_param_count": query_param_count
    }

    # Risk indicators for explanation
    risk_flags = []
    risk_score = 0

    if url_length > 100:
        risk_flags.append("Unusually long URL")
        risk_score += 10
    if has_ip:
        risk_flags.append("IP address used instead of domain name")
        risk_score += 30
    if has_at_symbol:
        risk_flags.append("@ symbol in URL — used to trick browsers")
        risk_score += 25
    if hyphen_count > 4:
        risk_flags.append("Excessive hyphens in URL")
        risk_score += 15
    if subdomain_count > 3:
        risk_flags.append("Too many subdomains")
        risk_score += 15
    if https_in_path:
        risk_flags.append("'https' keyword appears in URL path — deceptive")
        risk_score += 20
    if suspicious_count > 0:
        risk_flags.append(f"{suspicious_count} suspicious keyword(s) found in URL")
        risk_score += suspicious_count * 10
    if url_entropy > 3.8:
        risk_flags.append("High URL entropy — looks randomly generated")
        risk_score += 15

    return {
        "features": features,
        "risk_flags": risk_flags,
        "feature_risk_score": min(risk_score, 100)
    }