def calculate_guard_score(
    static_risk: int,
    behavior_risk: int,
    reputation_risk: int,
    static_signals: list,
    behavior_signals: list
) -> dict:
    """
    YOUR weighted behavioral risk formula.
    Combines all GUARD analysis layers into final verdict.
    """

    # YOUR defined weights
    WEIGHTS = {
        "static":     0.35,
        "behavior":   0.35,
        "reputation": 0.30
    }

    # Weighted sum
    raw_score = (
        WEIGHTS["static"]     * static_risk +
        WEIGHTS["behavior"]   * behavior_risk +
        WEIGHTS["reputation"] * reputation_risk
    )

    final_score = round(min(raw_score, 100), 1)

    # Check for any critical signals
    critical_signals = [
        s for s in (static_signals + behavior_signals)
        if s.get("severity") == "CRITICAL"
    ]

    # Critical signals boost the score
    if critical_signals:
        final_score = min(final_score + 20, 100)

    # Verdict
    if final_score == 0:
        verdict = "TRUSTED"
        color = "green"
        action = "This website appears safe. No suspicious behavior detected."
        extension_ui = "green_shield"
    elif final_score < 25:
        verdict = "CAUTION"
        color = "yellow"
        action = "Minor concerns detected. Proceed carefully and avoid sharing sensitive data."
        extension_ui = "yellow_banner"
    elif final_score < 55:
        verdict = "WARNING"
        color = "orange"
        action = "Suspicious behavior detected. Do not enter passwords or personal information."
        extension_ui = "orange_popup"
    else:
        verdict = "DANGER"
        color = "red"
        action = "High risk website. Do not proceed. Close this page immediately."
        extension_ui = "red_overlay"

    return {
        "guard_score": final_score,
        "verdict": verdict,
        "color": color,
        "action": action,
        "extension_ui": extension_ui,
        "critical_signals_found": len(critical_signals),
        "score_breakdown": {
            "static_contribution":     round(WEIGHTS["static"] * static_risk, 1),
            "behavior_contribution":   round(WEIGHTS["behavior"] * behavior_risk, 1),
            "reputation_contribution": round(WEIGHTS["reputation"] * reputation_risk, 1)
        }
    }