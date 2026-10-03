import math
from collections import Counter

def calculate_entropy(text: str) -> float:
    """
    Shannon entropy — measures randomness of a string.
    High entropy = random looking = suspicious URL/domain.
    """
    if not text:
        return 0.0

    freq = Counter(text)
    length = len(text)

    entropy = -sum(
        (count / length) * math.log2(count / length)
        for count in freq.values()
    )

    return round(entropy, 4)


def get_entropy_risk(entropy: float) -> dict:
    """
    Converts entropy score to risk level.
    Normal domains have entropy around 2.5-3.5
    Random/suspicious domains have entropy above 3.8
    """
    if entropy > 4.0:
        return {"risk": "HIGH", "score": 25, "note": "Very high entropy — likely randomly generated domain"}
    elif entropy > 3.5:
        return {"risk": "MEDIUM", "score": 15, "note": "Above average entropy — possibly suspicious"}
    elif entropy > 3.0:
        return {"risk": "LOW", "score": 5, "note": "Slightly elevated entropy"}
    else:
        return {"risk": "SAFE", "score": 0, "note": "Normal entropy for a legitimate domain"}