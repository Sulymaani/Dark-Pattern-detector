import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Keywords associated with different dark pattern types
URGENCY_KEYWORDS = [
    "now", "today", "limited", "hurry", "don't miss", "expires", 
    "last chance", "only", "left", "ending soon", "act fast"
]

PRESSURE_KEYWORDS = [
    "must", "need", "required", "have to", "should", "important",
    "urgent", "critical", "essential", "necessary"
]

EMOTIONAL_KEYWORDS = [
    "miss out", "regret", "worried", "anxious", "afraid", "scared",
    "guilt", "shame", "disappointed", "sad", "alone", "lonely"
]

SUBSCRIPTION_KEYWORDS = [
    "trial", "subscription", "auto-renew", "recurring", "monthly",
    "annual", "cancel", "billing", "payment", "charge", "free trial"
]

PRIVACY_KEYWORDS = [
    "data", "information", "privacy", "share", "collect", "track",
    "permission", "access", "consent", "agree", "terms", "policy"
]


def compute_text_features(text: str) -> Dict[str, Any]:
    """
    Compute features from OCR-extracted text to aid in dark pattern detection.
    
    Args:
        text: Extracted text from screenshot
        
    Returns:
        Dictionary containing various text features:
        - character_count: Total number of characters
        - word_count: Total number of words
        - urgency_count: Number of urgency-related keywords
        - pressure_count: Number of pressure-related keywords
        - emotional_count: Number of emotional manipulation keywords
        - subscription_count: Number of subscription-related keywords
        - privacy_count: Number of privacy-related keywords
        - all_caps_words: Number of words in ALL CAPS (typically attention-grabbing)
        - exclamation_count: Number of exclamation marks
        - question_count: Number of question marks
    """
    try:
        text_lower = text.lower()
        
        # Basic counts
        character_count = len(text)
        words = text.split()
        word_count = len(words)
        
        # Keyword frequency counts
        urgency_count = sum(1 for keyword in URGENCY_KEYWORDS if keyword in text_lower)
        pressure_count = sum(1 for keyword in PRESSURE_KEYWORDS if keyword in text_lower)
        emotional_count = sum(1 for keyword in EMOTIONAL_KEYWORDS if keyword in text_lower)
        subscription_count = sum(1 for keyword in SUBSCRIPTION_KEYWORDS if keyword in text_lower)
        privacy_count = sum(1 for keyword in PRIVACY_KEYWORDS if keyword in text_lower)
        
        # Stylistic features that often indicate dark patterns
        all_caps_words = sum(1 for word in words if word.isupper() and len(word) > 1)
        exclamation_count = text.count('!')
        question_count = text.count('?')
        
        features = {
            "character_count": character_count,
            "word_count": word_count,
            "urgency_count": urgency_count,
            "pressure_count": pressure_count,
            "emotional_count": emotional_count,
            "subscription_count": subscription_count,
            "privacy_count": privacy_count,
            "all_caps_words": all_caps_words,
            "exclamation_count": exclamation_count,
            "question_count": question_count,
        }
        
        logger.info(f"Computed features: {features}")
        return features
        
    except Exception as e:
        logger.error(f"Feature computation failed: {str(e)}")
        # Return empty features on error
        return {
            "character_count": 0,
            "word_count": 0,
            "urgency_count": 0,
            "pressure_count": 0,
            "emotional_count": 0,
            "subscription_count": 0,
            "privacy_count": 0,
            "all_caps_words": 0,
            "exclamation_count": 0,
            "question_count": 0,
        }
