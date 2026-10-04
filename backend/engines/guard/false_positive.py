def handle_false_positive(
    verdict: str,
    guard_score: float,
    reputation: dict,
    static_signals: list,
    behavior_signals: list
) -> dict:
    """
    Prevents legitimate high-traffic websites from being
    wrongly flagged as dangerous.
    Applies trust overrides when enough trust signals exist.
    """

    if verdict not in ["WARNING", "DANGER"]:
        return {"adjusted": False, "verdict": verdict, "guard_score": guard_score, "note": ""}

    # Trust signal checks
    rep_score = reputation.get("reputation_score", 0)
    age_days = reputation.get("domain_age_days", 0)
    trust_level = reputation.get("trust_level", "")

    trust_signals = {
        "high_reputation": rep_score >= 70,
        "old_domain": age_days > 730,  # 2+ years
        "trusted_level": trust_level == "TRUSTED",
        "no_critical_signal": not any(
            s.get("severity") == "CRITICAL"
            for s in (static_signals + behavior_signals)
        ),
        "no_crypto_mining": not any(
            s.get("signal") == "crypto_mining"
            for s in static_signals
        ),
        "no_keylogger": not any(
            s.get("signal") == "potential_keylogger"
            for s in behavior_signals
        )
    }

    trust_count = sum(trust_signals.values())

    # If 4+ trust signals fire and verdict is WARNING → downgrade to CAUTION
    if trust_count >= 4 and verdict == "WARNING":
        return {
            "adjusted": True,
            "verdict": "CAUTION",
            "guard_score": max(guard_score - 15, 20),
            "note": "Verdict adjusted — site shows trust signals suggesting legitimate high-traffic website. Some behaviors flagged may be normal for this site type.",
            "trust_signals_fired": trust_count
        }

    # If 5+ trust signals and DANGER → downgrade to WARNING
    if trust_count >= 5 and verdict == "DANGER":
        return {
            "adjusted": True,
            "verdict": "WARNING",
            "guard_score": max(guard_score - 20, 45),
            "note": "Verdict adjusted — strong trust indicators present despite high score. Proceed with caution.",
            "trust_signals_fired": trust_count
        }

    return {
        "adjusted": False,
        "verdict": verdict,
        "guard_score": guard_score,
        "note": "",
        "trust_signals_fired": trust_count
    }