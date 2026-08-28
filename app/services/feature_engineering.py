import re
from typing import Dict, Any, List

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

# Urgency/scarcity indicators (cross-pattern signal)
URGENCY_PATTERNS: List[str] = [
    r"only \d+ left",
    r"expires? (soon|today|in \d+)",
    r"last chance",
    r"ending soon",
    r"while supplies last",
    r"act fast",
    r"don.t wait",
    r"now or never",
    r"today only",
    r"hours left",
    r"minutes left",
]

# Loss aversion language
LOSS_AVERSION_PATTERNS: List[str] = [
    r"you.ll (miss|lose)",
    r"don.t lose",
    r"before it.s (too late|gone)",
    r"missing out",
    r"fomo",
    r"regret",
]


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
    words = lower.split()
    word_count = len(words)

    # Keyword hits per pattern type
    keyword_counts: Dict[str, int] = {}
    for pattern, regexes in PATTERN_KEYWORDS.items():
        count = 0
        for rx in regexes:
            count += len(re.findall(rx, lower))
        keyword_counts[f"{pattern}_keyword_hits"] = count

    # Urgency indicators
    urgency_hits = sum(len(re.findall(rx, lower)) for rx in URGENCY_PATTERNS)

    # Loss aversion language
    loss_aversion_hits = sum(
        len(re.findall(rx, lower)) for rx in LOSS_AVERSION_PATTERNS
    )

    # Caps ratio (aggressive messaging indicator)
    caps_count = sum(1 for c in text if c.isupper())
    caps_ratio = caps_count / max(len(text), 1)

    # Punctuation analysis
    exclamation_count = text.count("!")
    question_count = text.count("?")

    # Sentence count (for context density)
    sentence_count = len(re.findall(r"[.!?]+", text))

    features: Dict[str, Any] = {
        "length_chars": length,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "urgency_hits": urgency_hits,
        "loss_aversion_hits": loss_aversion_hits,
        "caps_ratio": round(caps_ratio, 3),
        "exclamation_count": exclamation_count,
        "question_count": question_count,
        **keyword_counts,
    }
    return features
