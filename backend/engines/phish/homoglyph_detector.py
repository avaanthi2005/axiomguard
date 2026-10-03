from Levenshtein import distance

# Top trusted brand domains to check against
TRUSTED_DOMAINS = [
    "google.com", "gmail.com", "youtube.com", "facebook.com",
    "instagram.com", "twitter.com", "amazon.com", "apple.com",
    "microsoft.com", "linkedin.com", "netflix.com", "paypal.com",
    "sbi.co.in", "hdfcbank.com", "icicibank.com", "axisbank.com",
    "irctc.co.in", "flipkart.com", "myntra.com", "paytm.com",
    "phonepe.com", "gpay.com", "upi.com", "npci.org.in",
    "yahoo.com", "outlook.com", "hotmail.com", "dropbox.com",
    "github.com", "stackoverflow.com", "wikipedia.org",
    "ebay.com", "walmart.com", "target.com", "bestbuy.com",
    "chase.com", "bankofamerica.com", "wellsfargo.com",
    "whatsapp.com", "telegram.org", "zoom.us", "slack.com"
]

def detect_homoglyph(domain: str) -> dict:
    """
    Checks if submitted domain looks like a trusted brand
    using Levenshtein edit distance.
    Distance of 1 or 2 = typosquatting attempt.
    """
    # Clean domain — remove www and get base domain
    domain = domain.lower().replace("www.", "")

    closest_match = None
    closest_distance = 999
    is_typosquat = False

    for trusted in TRUSTED_DOMAINS:
        dist = distance(domain, trusted)

        if dist < closest_distance:
            closest_distance = dist
            closest_match = trusted

        # Exact match = legitimate
        if dist == 0:
            return {
                "is_typosquat": False,
                "domain_checked": domain,
                "closest_trusted": trusted,
                "distance": 0,
                "risk_score": 0,
                "note": "Domain matches a trusted brand exactly"
            }

        # Distance 1 or 2 = typosquatting
        if dist <= 2:
            is_typosquat = True
            closest_match = trusted
            closest_distance = dist
            break

    if is_typosquat:
        return {
            "is_typosquat": True,
            "domain_checked": domain,
            "closest_trusted": closest_match,
            "distance": closest_distance,
            "risk_score": 40,
            "note": f"TYPOSQUATTING DETECTED — '{domain}' closely resembles '{closest_match}' (edit distance: {closest_distance})"
        }

    return {
        "is_typosquat": False,
        "domain_checked": domain,
        "closest_trusted": closest_match,
        "distance": closest_distance,
        "risk_score": 0,
        "note": "No typosquatting detected"
    }