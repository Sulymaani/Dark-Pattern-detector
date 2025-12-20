import re
from typing import Dict, Any

PATTERN_KEYWORDS = {
    "forced_continuity": [
        r"free trial",
        r"trial ends",
        r"auto[- ]?renew",
        r"billed",
        r"per month",
        r"per year",
        r"subscription",
        r"cancel anytime",
        r"charged",
    ],
    "nagging": [
        r"upgrade now",
        r"limited time",
        r"don.t miss",
        r"are you sure",
        r"stay (with us|subscribed)",
        r"unlock premium",
        r"go pro",
        r"special offer",
        r"act now",
        r"hurry",
    ],
    "obstruction": [
        r"contact support",
        r"call us",
        r"email us",
        r"cannot cancel",
        r"no refund",
        r"account settings",
        r"manage subscription",
        r"verify identity",
    ],
    "confirmshaming": [
        r"i don.t want",
        r"i.ll stay (anxious|sad|alone)",
        r"don.t care about my health",
        r"no thanks.*(miss|lose|give up)",
        r"i.ll risk it",
        r"i prefer to stay",
        r"not interested in",
    ],
    "privacy_zuckering": [
        r"accept all",
        r"share.*data",
        r"partners",
        r"third part(y|ies)",
        r"personalized ads",
        r"improve.*experience",
        r"analytics",
        r"cookies",
        r"tracking",
    ],
}


def compute_text_features(text: str) -> Dict[str, Any]:
    """
    Extract features from OCR text for dark pattern classification.

    Args:
        text: Extracted text from screenshot

    Returns:
        Dictionary containing text metrics and keyword hit counts per pattern type
    """
    lower = text.lower()
    length = len(lower)
    word_count = len(lower.split())

    keyword_counts: Dict[str, int] = {}
    for pattern, regexes in PATTERN_KEYWORDS.items():
        count = 0
        for rx in regexes:
            count += len(re.findall(rx, lower))
        keyword_counts[f"{pattern}_keyword_hits"] = count

    features: Dict[str, Any] = {
        "length_chars": length,
        "word_count": word_count,
        **keyword_counts,
    }
    return features
