def calculate_axiom_score(
    port_risk: int,
    ssl_risk: int,
    dns_risk: int,
    cve_risk: int = 0
) -> dict:
    """
    YOUR custom weighted risk formula.
    Combines all scan results into one standardized score.
    """

    # YOUR defined weights — must sum to 1.0
    WEIGHTS = {
        "port": 0.30,
        "ssl":  0.25,
        "dns":  0.20,
        "cve":  0.25
    }

    # Weighted sum
    raw_score = (
        WEIGHTS["port"] * port_risk +
        WEIGHTS["ssl"]  * ssl_risk  +
        WEIGHTS["dns"]  * dns_risk  +
        WEIGHTS["cve"]  * cve_risk
    )

    # Normalize to 0-100
    axiom_score = round(min(raw_score, 100), 1)

    # Classify
    if axiom_score == 0:
        level = "SECURE"
        color = "green"
        message = "No significant vulnerabilities detected."
    elif axiom_score <= 25:
        level = "LOW"
        color = "green"
        message = "Minor issues found. Low risk overall."
    elif axiom_score <= 50:
        level = "MEDIUM"
        color = "yellow"
        message = "Moderate vulnerabilities detected. Review recommended."
    elif axiom_score <= 75:
        level = "HIGH"
        color = "orange"
        message = "Significant vulnerabilities found. Action required."
    else:
        level = "CRITICAL"
        color = "red"
        message = "Critical security issues detected. Immediate action required."

    return {
        "axiom_score": axiom_score,
        "level": level,
        "color": color,
        "message": message,
        "breakdown": {
            "port_contribution": round(WEIGHTS["port"] * port_risk, 1),
            "ssl_contribution":  round(WEIGHTS["ssl"]  * ssl_risk,  1),
            "dns_contribution":  round(WEIGHTS["dns"]  * dns_risk,  1),
            "cve_contribution":  round(WEIGHTS["cve"]  * cve_risk,  1)
        }
    }