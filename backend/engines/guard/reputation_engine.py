import whois
import math
from datetime import datetime
from collections import Counter
from engines.phish.entropy_calculator import calculate_entropy

# TLD risk scores — 1 (safe) to 10 (risky)
TLD_RISK = {
    'com': 1, 'org': 1, 'net': 2, 'edu': 1, 'gov': 1,
    'co': 2, 'io': 3, 'in': 2, 'uk': 2, 'au': 2,
    'de': 2, 'fr': 2, 'jp': 2, 'ca': 2, 'sg': 3,
    'xyz': 8, 'top': 9, 'click': 9, 'loan': 9, 'win': 9,
    'gq': 10, 'ml': 9, 'tk': 10, 'cf': 10, 'ga': 10,
    'info': 5, 'biz': 6, 'online': 6, 'site': 6, 'tech': 4,
    'live': 5, 'store': 4, 'shop': 4, 'club': 6, 'vip': 7
}

# Known safe domains (no need to penalize these)
ALWAYS_TRUSTED = [
    'google.com', 'youtube.com', 'facebook.com', 'amazon.com',
    'microsoft.com', 'apple.com', 'twitter.com', 'instagram.com',
    'linkedin.com', 'github.com', 'wikipedia.org', 'reddit.com',
    'netflix.com', 'zoom.us', 'slack.com', 'dropbox.com'
]

def get_domain_age_days(domain: str) -> int:
    try:
        w = whois.whois(domain)
        creation = w.creation_date
        if isinstance(creation, list):
            creation = creation[0]
        if creation:
            return (datetime.utcnow() - creation).days
    except:
        pass
    return -1  # Unknown

def calculate_reputation(domain: str) -> dict:
    """
    Multi-factor domain reputation engine.
    Uses local logic only — no external reputation API.
    """
    risk_score = 0
    trust_score = 0
    signals = []

    # Clean domain
    domain = domain.lower().replace("www.", "")

    # Always trusted domains
    if domain in ALWAYS_TRUSTED:
        return {
            "reputation_score": 95,
            "risk_score": 0,
            "domain_age_days": -1,
            "trust_level": "HIGHLY_TRUSTED",
            "signals": ["Domain is a globally recognized trusted website"],
            "tld_risk": 1
        }

    # Factor 1: Domain age
    age_days = get_domain_age_days(domain)
    if age_days == -1:
        signals.append("Domain age could not be determined")
        risk_score += 10
    elif age_days < 30:
        signals.append(f"Very new domain ({age_days} days old) — high phishing risk")
        risk_score += 35
    elif age_days < 180:
        signals.append(f"Relatively new domain ({age_days} days old)")
        risk_score += 15
    elif age_days < 365:
        signals.append(f"Domain is {age_days} days old")
        risk_score += 5
    else:
        signals.append(f"Established domain ({age_days} days old)")
        trust_score += 20

    # Factor 2: Domain entropy
    entropy = calculate_entropy(domain)
    if entropy > 4.0:
        signals.append(f"Very high domain entropy ({entropy}) — likely randomly generated")
        risk_score += 25
    elif entropy > 3.5:
        signals.append(f"Elevated domain entropy ({entropy})")
        risk_score += 10
    else:
        trust_score += 10

    # Factor 3: TLD risk
    tld = domain.split('.')[-1]
    tld_risk = TLD_RISK.get(tld, 5)
    if tld_risk >= 8:
        signals.append(f"High-risk TLD (.{tld}) — commonly used in malicious domains")
        risk_score += tld_risk * 3
    elif tld_risk >= 5:
        signals.append(f"Medium-risk TLD (.{tld})")
        risk_score += tld_risk
    else:
        trust_score += 10

    # Factor 4: Domain length
    domain_name = domain.split('.')[0]
    if len(domain_name) > 30:
        signals.append("Unusually long domain name")
        risk_score += 15
    elif len(domain_name) > 20:
        signals.append("Long domain name")
        risk_score += 5

    # Factor 5: Digit ratio in domain
    digit_ratio = sum(c.isdigit() for c in domain_name) / max(len(domain_name), 1)
    if digit_ratio > 0.4:
        signals.append("High ratio of digits in domain name — suspicious")
        risk_score += 15

    # Final reputation score (inverse of risk)
    final_risk = min(risk_score, 100)
    reputation_score = max(0, 100 - final_risk + trust_score)
    reputation_score = min(reputation_score, 100)

    if reputation_score >= 70:
        trust_level = "TRUSTED"
    elif reputation_score >= 50:
        trust_level = "NEUTRAL"
    elif reputation_score >= 30:
        trust_level = "SUSPICIOUS"
    else:
        trust_level = "UNTRUSTED"

    return {
        "reputation_score": round(reputation_score, 1),
        "risk_score": final_risk,
        "domain_age_days": age_days,
        "trust_level": trust_level,
        "signals": signals,
        "tld_risk": tld_risk,
        "domain_entropy": entropy
    }