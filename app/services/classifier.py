import anthropic
import json
import logging
from typing import List
from app.models.schemas import PatternResult, PatternType
from app.utils.config import settings

logger = logging.getLogger(__name__)

CLASSIFICATION_PROMPT = """You are an expert at detecting dark patterns in mental health applications.

Analyze the following text extracted from a mental health app screenshot and identify any dark patterns present.

Dark patterns to detect:
1. FORCED_CONTINUITY - Auto-renewal without clear notice, hidden subscription terms
2. NAGGING - Repeated prompts to upgrade, persistent notifications, guilt-inducing messages
3. OBSTRUCTION - Making it hard to cancel, hidden settings, complex procedures
4. CONFIRMSHAMING - Guilt-tripping language for declining, emotional manipulation
5. PRIVACY_ZUCKERING - Confusing privacy settings, hidden data collection, unclear consent

Text to analyze:
{text}

Respond with a JSON array of detected patterns. For each pattern found, include:
- pattern_type: one of [forced_continuity, nagging, obstruction, confirmshaming, privacy_zuckering]
- confidence: float between 0.0 and 1.0
- evidence: the specific text that indicates this pattern
- explanation: brief explanation of why this is a dark pattern

If no dark patterns are detected, return an empty array: []

Respond ONLY with valid JSON, no additional text."""


async def classify_patterns(text: str) -> List[PatternResult]:
    """
    Classify text for dark patterns using Claude API.

    Args:
        text: Extracted text from screenshot

    Returns:
        List of detected patterns with confidence scores
    """
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": CLASSIFICATION_PROMPT.format(text=text)}
            ],
        )

        response_text = message.content[0].text

        # Parse JSON response
        patterns_data = json.loads(response_text)

        # Convert to PatternResult objects
        patterns = []
        for p in patterns_data:
            try:
                pattern = PatternResult(
                    pattern_type=PatternType(p["pattern_type"]),
                    confidence=float(p["confidence"]),
                    evidence=p["evidence"],
                    explanation=p["explanation"],
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
