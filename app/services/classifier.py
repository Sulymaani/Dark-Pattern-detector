import anthropic
import json
import logging
from typing import List, Dict, Any
from app.models.schemas import PatternResult, PatternType
from app.utils.config import settings

logger = logging.getLogger(__name__)

PATTERN_TYPES = [
    "forced_continuity",
    "nagging",
    "obstruction",
    "confirmshaming",
    "privacy_zuckering",
]

CLASSIFICATION_PROMPT = """You are an expert at detecting dark patterns in mental health applications.

Analyze the following text extracted from a mental health app screenshot and identify any dark patterns present.
Use BOTH the raw OCR text AND the pre-computed keyword features to inform your analysis.

Dark patterns to detect:
1. FORCED_CONTINUITY - Auto-renewal without clear notice, hidden subscription terms
2. NAGGING - Repeated prompts to upgrade, persistent notifications, guilt-inducing messages
3. OBSTRUCTION - Making it hard to cancel, hidden settings, complex procedures
4. CONFIRMSHAMING - Guilt-tripping language for declining, emotional manipulation
5. PRIVACY_ZUCKERING - Confusing privacy settings, hidden data collection, unclear consent

OCR_TEXT:
{text}

FEATURES:
{features}

Respond with a JSON array of detected patterns. For each pattern found, include:
- pattern_type: one of [forced_continuity, nagging, obstruction, confirmshaming, privacy_zuckering]
- confidence: float between 0.0 and 1.0
- evidence: the specific text that indicates this pattern
- explanation: brief explanation of why this is a dark pattern

If no dark patterns are detected, return an empty array: []

Respond ONLY with valid JSON, no additional text."""


async def classify_patterns(
    text: str, features: Dict[str, Any] | None = None
) -> List[PatternResult]:
    """
    Classify text for dark patterns using Claude API.

    Args:
        text: Extracted text from screenshot
        features: Pre-computed text features (keyword hits, text metrics)

    Returns:
        List of detected patterns with confidence scores
    """
    if not text.strip():
        return []

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    # Format features for prompt
    features_str = json.dumps(features, indent=2) if features else "{}"

    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": CLASSIFICATION_PROMPT.format(
                        text=text, features=features_str
                    ),
                }
            ],
        )

        response_text = message.content[0].text

        # Parse JSON response
        patterns_data = json.loads(response_text)

        # Convert to PatternResult objects with validation
        patterns = []
        for p in patterns_data:
            try:
                pattern_type = p.get("pattern_type")
                if pattern_type not in PATTERN_TYPES:
                    logger.warning(f"Unknown pattern type: {pattern_type}")
                    continue

                conf = float(p.get("confidence", 0))
                conf = max(0.0, min(1.0, conf))  # Clamp to [0, 1]

                pattern = PatternResult(
                    pattern_type=PatternType(pattern_type),
                    confidence=conf,
                    evidence=p.get("evidence", ""),
                    explanation=p.get("explanation", ""),
                )
                patterns.append(pattern)
            except (KeyError, ValueError) as e:
                logger.warning(f"Skipping invalid pattern data: {e}")
                continue

        logger.info(f"Detected {len(patterns)} dark patterns")
        return patterns

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Claude response: {e}")
        return []
    except anthropic.APIError as e:
        logger.error(f"Claude API error: {e}")
        raise RuntimeError(f"Classification API error: {str(e)}")
