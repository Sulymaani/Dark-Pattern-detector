from typing import List, Dict, Any

PATTERN_WEIGHTS = {
    "forced_continuity": 3.0,
    "privacy_zuckering": 3.0,
    "obstruction": 2.5,
    "confirmshaming": 2.0,
    "nagging": 1.0,
}


def compute_coercion_score(patterns: List[Dict[str, Any]]) -> float:
    """
    Calculate a coercion score based on detected patterns and their confidence.

    The score is weighted by pattern severity:
    - forced_continuity and privacy_zuckering: 3.0 (most harmful)
    - obstruction: 2.5
    - confirmshaming: 2.0
    - nagging: 1.0 (least harmful)

    Args:
        patterns: List of pattern dicts from classifier with pattern_type and confidence

    Returns:
        Coercion score normalized to 0-100 scale
    """
    if not patterns:
        return 0.0

    raw_score = 0.0
    max_possible = 0.0

    for p in patterns:
        pattern_type = p.get("pattern_type")
        if hasattr(pattern_type, "value"):
            pattern_type = pattern_type.value

        w = PATTERN_WEIGHTS.get(pattern_type, 1.0)
        c = float(p.get("confidence", 0))
        raw_score += w * c
        max_possible += w

    if max_possible == 0:
        return 0.0

    normalized = (raw_score / max_possible) * 100.0
    return round(normalized, 1)
