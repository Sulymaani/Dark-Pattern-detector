"""Tests for feature engineering and scoring services"""
import pytest
from app.services.feature_engineering import compute_text_features
from app.services.scoring import compute_coercion_score
from app.models.schemas import PatternResult, PatternType


class TestFeatureEngineering:
    """Test suite for feature_engineering.py"""
    
    def test_empty_text(self):
        """Test handling of empty text"""
        features = compute_text_features("")
        assert features["character_count"] == 0
        assert features["word_count"] == 0
        assert features["urgency_count"] == 0
    
    def test_basic_counts(self):
        """Test basic character and word counting"""
        text = "Hello world this is a test"
        features = compute_text_features(text)
        assert features["character_count"] == len(text)
        assert features["word_count"] == 6
    
    def test_urgency_keywords(self):
        """Test detection of urgency keywords"""
        text = "Act now! Limited time offer expires today!"
        features = compute_text_features(text)
        assert features["urgency_count"] >= 3  # now, limited, expires, today
        assert features["exclamation_count"] == 2
    
    def test_pressure_keywords(self):
        """Test detection of pressure keywords"""
        text = "You must complete this now. It is required and urgent."
        features = compute_text_features(text)
        assert features["pressure_count"] >= 3  # must, required, urgent
    
    def test_emotional_keywords(self):
        """Test detection of emotional manipulation keywords"""
        text = "Don't miss out! You'll regret it if you don't join."
        features = compute_text_features(text)
        assert features["emotional_count"] >= 2  # miss out, regret
    
    def test_subscription_keywords(self):
        """Test detection of subscription-related keywords"""
        text = "Start your free trial today. Auto-renew monthly subscription."
        features = compute_text_features(text)
        assert features["subscription_count"] >= 3  # trial, auto-renew, monthly, subscription
    
    def test_privacy_keywords(self):
        """Test detection of privacy-related keywords"""
        text = "We collect your data and share information with partners."
        features = compute_text_features(text)
        assert features["privacy_count"] >= 3  # collect, data, share, information
    
    def test_all_caps_detection(self):
        """Test detection of ALL CAPS words"""
        text = "BUY NOW or MISS OUT on this DEAL"
        features = compute_text_features(text)
        assert features["all_caps_words"] >= 3  # BUY, NOW, MISS, OUT, DEAL
    
    def test_punctuation_counts(self):
        """Test counting of exclamation marks and questions"""
        text = "Why wait? Act now! Don't miss this! Really?"
        features = compute_text_features(text)
        assert features["exclamation_count"] == 2
        assert features["question_count"] == 2
    
    def test_complex_text(self):
        """Test with complex realistic text"""
        text = """
        LIMITED TIME OFFER!
        Start your FREE TRIAL today - auto-renews at $9.99/month
        Don't miss out on premium features!
        Cancel anytime (terms apply)
        """
        features = compute_text_features(text)
        assert features["urgency_count"] > 0
        assert features["subscription_count"] > 0
        assert features["emotional_count"] > 0
        assert features["all_caps_words"] > 0
        assert features["exclamation_count"] > 0


class TestScoring:
    """Test suite for scoring.py"""
    
    def test_no_patterns(self):
        """Test score with no patterns detected"""
        score = compute_coercion_score([])
        assert score == 0.0
    
    def test_single_low_confidence_pattern(self):
        """Test score with single low-confidence pattern"""
        patterns = [
            PatternResult(
                pattern_type=PatternType.NAGGING,
                confidence=0.3,
                evidence="Some text",
                explanation="Low confidence detection"
            )
        ]
        score = compute_coercion_score(patterns)
        assert 0.1 <= score <= 0.3
    
    def test_single_high_confidence_severe_pattern(self):
        """Test score with high-confidence severe pattern"""
        patterns = [
            PatternResult(
                pattern_type=PatternType.FORCED_CONTINUITY,
                confidence=0.95,
                evidence="Hidden auto-renewal",
                explanation="Clear forced continuity"
            )
        ]
        score = compute_coercion_score(patterns)
        assert 0.7 <= score <= 1.0
    
    def test_multiple_patterns(self):
        """Test score with multiple patterns"""
        patterns = [
            PatternResult(
                pattern_type=PatternType.FORCED_CONTINUITY,
                confidence=0.9,
                evidence="Auto-renewal",
                explanation="Forced continuity"
            ),
            PatternResult(
                pattern_type=PatternType.OBSTRUCTION,
                confidence=0.8,
                evidence="Hard to cancel",
                explanation="Obstruction"
            )
        ]
        score = compute_coercion_score(patterns)
        assert 0.8 <= score <= 1.0
    
    def test_score_bounded(self):
        """Test that score stays within 0.0-1.0 range"""
        patterns = [
            PatternResult(
                pattern_type=PatternType.FORCED_CONTINUITY,
                confidence=1.0,
                evidence="Pattern 1",
                explanation="Explanation 1"
            ),
            PatternResult(
                pattern_type=PatternType.OBSTRUCTION,
                confidence=1.0,
                evidence="Pattern 2",
                explanation="Explanation 2"
            ),
            PatternResult(
                pattern_type=PatternType.PRIVACY_ZUCKERING,
                confidence=1.0,
                evidence="Pattern 3",
                explanation="Explanation 3"
            )
        ]
        score = compute_coercion_score(patterns)
        assert 0.0 <= score <= 1.0
    
    def test_pattern_severity_weights(self):
        """Test that different pattern types have different severity"""
        # Forced continuity should score higher than nagging at same confidence
        forced_patterns = [
            PatternResult(
                pattern_type=PatternType.FORCED_CONTINUITY,
                confidence=0.8,
                evidence="Auto-renewal",
                explanation="Forced continuity"
            )
        ]
        nagging_patterns = [
            PatternResult(
                pattern_type=PatternType.NAGGING,
                confidence=0.8,
                evidence="Popup",
                explanation="Nagging"
            )
        ]
        
        forced_score = compute_coercion_score(forced_patterns)
        nagging_score = compute_coercion_score(nagging_patterns)
        
        assert forced_score > nagging_score
    
    def test_all_pattern_types(self):
        """Test scoring with all pattern types"""
        patterns = [
            PatternResult(
                pattern_type=PatternType.FORCED_CONTINUITY,
                confidence=0.7,
                evidence="Auto-renewal",
                explanation="Forced continuity"
            ),
            PatternResult(
                pattern_type=PatternType.NAGGING,
                confidence=0.6,
                evidence="Repeated prompts",
                explanation="Nagging"
            ),
            PatternResult(
                pattern_type=PatternType.OBSTRUCTION,
                confidence=0.8,
                evidence="Hidden cancel",
                explanation="Obstruction"
            ),
            PatternResult(
                pattern_type=PatternType.CONFIRMSHAMING,
                confidence=0.7,
                evidence="Guilt trip",
                explanation="Confirmshaming"
            ),
            PatternResult(
                pattern_type=PatternType.PRIVACY_ZUCKERING,
                confidence=0.75,
                evidence="Confusing privacy",
                explanation="Privacy zuckering"
            )
        ]
        score = compute_coercion_score(patterns)
        assert 0.8 <= score <= 1.0  # Multiple severe patterns should score high
