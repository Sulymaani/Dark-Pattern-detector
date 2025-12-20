import logging
from typing import List, Dict
from app.models.schemas import PatternResult

logger = logging.getLogger(__name__)

# Severity weights for different dark pattern types
# Higher weight means more coercive/harmful
PATTERN_WEIGHTS = {
    "forced_continuity": 0.9,      # Very harmful - charges without clear consent
    "obstruction": 0.85,            # Very harmful - prevents user agency
    "privacy_zuckering": 0.8,       # Highly concerning - privacy violations
    "confirmshaming": 0.7,          # Emotionally manipulative
    "nagging": 0.6,                 # Annoying but less directly harmful
}


def compute_coercion_score(patterns: List[PatternResult]) -> float:
    """
    Compute an overall coercion score based on detected dark patterns.
    
    The score represents the overall severity and manipulative nature of the interface,
    combining both the types of patterns detected and their confidence levels.
    
    Args:
        patterns: List of detected dark patterns with confidence scores
        
    Returns:
        Float score between 0.0 (no coercion) and 1.0 (maximum coercion)
        
    Algorithm:
        1. For each pattern, multiply its confidence by its severity weight
        2. Aggregate scores using a formula that penalizes multiple patterns
        3. Normalize to 0.0-1.0 range
        
    Examples:
        - No patterns: 0.0
        - One low-confidence pattern: ~0.3-0.4
        - One high-confidence severe pattern: ~0.7-0.9
        - Multiple high-confidence patterns: ~0.9-1.0
    """
    try:
        if not patterns:
            logger.info("No patterns detected, coercion score: 0.0")
            return 0.0
        
        # Calculate weighted scores for each pattern
        weighted_scores = []
        for pattern in patterns:
            pattern_type = pattern.pattern_type.value
            confidence = pattern.confidence
            weight = PATTERN_WEIGHTS.get(pattern_type, 0.5)  # Default weight if type unknown
            
            weighted_score = confidence * weight
            weighted_scores.append(weighted_score)
            
            logger.debug(
                f"Pattern {pattern_type}: confidence={confidence:.2f}, "
                f"weight={weight:.2f}, weighted_score={weighted_score:.2f}"
            )
        
        # Aggregate scores with diminishing returns for multiple patterns
        # This prevents the score from being artificially inflated by many low-confidence detections
        if len(weighted_scores) == 1:
            # Single pattern: use the weighted score directly
            final_score = weighted_scores[0]
        else:
            # Multiple patterns: use max score + diminished contribution from others
            sorted_scores = sorted(weighted_scores, reverse=True)
            primary_score = sorted_scores[0]
            
            # Additional patterns contribute with diminishing factor (50% of their value)
            secondary_contribution = sum(score * 0.5 for score in sorted_scores[1:])
            
            # Combine but cap at 1.0
            final_score = min(primary_score + secondary_contribution * 0.5, 1.0)
        
        # Ensure score is in valid range
        final_score = max(0.0, min(1.0, final_score))
        
        logger.info(
            f"Computed coercion score: {final_score:.2f} "
            f"from {len(patterns)} pattern(s)"
        )
        
        return final_score
        
    except Exception as e:
        logger.error(f"Score computation failed: {str(e)}")
        # Return 0.0 on error to fail safe
        return 0.0
