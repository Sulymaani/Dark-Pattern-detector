import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.services.feature_engineering import compute_text_features
from app.services.scoring import compute_coercion_score

client = TestClient(app)


# =============================================================================
# API Tests
# =============================================================================


def test_health_check():
    """Test health endpoint returns healthy status"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_detect_invalid_file_type():
    """Test that non-image files are rejected"""
    response = client.post(
        "/detect", files={"file": ("test.txt", b"not an image", "text/plain")}
    )
    assert response.status_code == 400


@patch("app.main.extract_text")
@patch("app.main.classify_patterns")
def test_detect_no_text(mock_classify, mock_extract):
    """Test handling of image with no extractable text"""
    mock_extract.return_value = ""

    # Create minimal valid PNG
    png_bytes = create_minimal_png()

    response = client.post(
        "/detect", files={"file": ("test.png", png_bytes, "image/png")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["patterns"] == []


def create_minimal_png():
    """Create minimal valid PNG for testing"""
    from PIL import Image
    import io

    img = Image.new("RGB", (10, 10), color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# =============================================================================
# Feature Engineering Tests
# =============================================================================


class TestFeatureEngineering:
    """Tests for feature extraction from text"""

    def test_empty_text(self):
        """Empty text should return zero counts"""
        features = compute_text_features("")
        assert features["word_count"] == 0
        assert features["length_chars"] == 0
        assert features["urgency_hits"] == 0

    def test_basic_text_metrics(self):
        """Test basic text metrics calculation"""
        text = "Hello world. This is a test!"
        features = compute_text_features(text)
        assert features["word_count"] == 6
        assert features["length_chars"] == len(text.lower())
        assert features["exclamation_count"] == 1
        assert features["sentence_count"] == 2

    def test_forced_continuity_keywords(self):
        """Test detection of forced continuity keywords"""
        text = "Start your free trial today! Auto-renews at $9.99/month."
        features = compute_text_features(text)
        assert (
            features["forced_continuity_keyword_hits"] >= 2
        )  # "free trial", "auto-renew", "per month"

    def test_nagging_keywords(self):
        """Test detection of nagging keywords"""
        text = "Upgrade now! Limited time offer. Don't miss out!"
        features = compute_text_features(text)
        assert features["nagging_keyword_hits"] >= 2  # "upgrade now", "limited time"

    def test_confirmshaming_detection(self):
        """Test detection of confirmshaming language"""
        text = "No thanks, I don't want to improve my mental health"
        features = compute_text_features(text)
        assert features["confirmshaming_keyword_hits"] >= 1

    def test_privacy_zuckering_keywords(self):
        """Test detection of privacy-related dark patterns"""
        text = "Accept all cookies to continue. We share data with our partners."
        features = compute_text_features(text)
        assert (
            features["privacy_zuckering_keyword_hits"] >= 2
        )  # "accept all", "share.*data", "partners"

    def test_obstruction_keywords(self):
        """Test detection of obstruction patterns"""
        text = "To cancel, please contact support or call us."
        features = compute_text_features(text)
        assert features["obstruction_keyword_hits"] >= 2  # "contact support", "call us"

    def test_urgency_patterns(self):
        """Test detection of urgency/scarcity indicators"""
        text = "Last chance! Offer expires soon. Only 3 left!"
        features = compute_text_features(text)
        assert features["urgency_hits"] >= 2  # "last chance", "expires soon"

    def test_loss_aversion_patterns(self):
        """Test detection of loss aversion language"""
        text = "Don't lose your progress! You'll miss out on exclusive features."
        features = compute_text_features(text)
        assert features["loss_aversion_hits"] >= 2  # "don't lose", "miss out"

    def test_caps_ratio(self):
        """Test calculation of uppercase ratio"""
        text = "URGENT: Act Now!"
        features = compute_text_features(text)
        assert features["caps_ratio"] > 0.3  # Significant uppercase

    def test_caps_ratio_lowercase(self):
        """Test caps ratio with all lowercase"""
        text = "this is all lowercase text"
        features = compute_text_features(text)
        assert features["caps_ratio"] == 0.0

    def test_question_count(self):
        """Test question mark counting (often used in confirmshaming)"""
        text = "Are you sure? Do you really want to leave? You'll miss out!"
        features = compute_text_features(text)
        assert features["question_count"] == 2


# =============================================================================
# Scoring Tests
# =============================================================================


class TestScoring:
    """Tests for coercion score calculation"""

    def test_empty_patterns(self):
        """Empty patterns list should return zero score"""
        score = compute_coercion_score([])
        assert score == 0.0

    def test_single_high_severity_pattern(self):
        """Test scoring with single high-severity pattern"""
        patterns = [{"pattern_type": "forced_continuity", "confidence": 0.9}]
        score = compute_coercion_score(patterns)
        assert score == 90.0  # 0.9 * 100 = 90

    def test_single_low_severity_pattern(self):
        """Test scoring with single low-severity pattern"""
        patterns = [{"pattern_type": "nagging", "confidence": 0.9}]
        score = compute_coercion_score(patterns)
        assert score == 90.0  # Single pattern always normalizes to confidence * 100

    def test_multiple_patterns_weighted(self):
        """Test that multiple patterns are weighted correctly"""
        patterns = [
            {"pattern_type": "forced_continuity", "confidence": 1.0},  # weight 3.0
            {"pattern_type": "nagging", "confidence": 1.0},  # weight 1.0
        ]
        score = compute_coercion_score(patterns)
        # (3.0 * 1.0 + 1.0 * 1.0) / (3.0 + 1.0) * 100 = 100.0
        assert score == 100.0

    def test_low_confidence_patterns(self):
        """Test that low confidence reduces score"""
        patterns = [{"pattern_type": "forced_continuity", "confidence": 0.5}]
        score = compute_coercion_score(patterns)
        assert score == 50.0

    def test_mixed_confidence_patterns(self):
        """Test scoring with mixed confidence levels"""
        patterns = [
            {"pattern_type": "forced_continuity", "confidence": 0.8},  # weight 3.0
            {"pattern_type": "privacy_zuckering", "confidence": 0.6},  # weight 3.0
        ]
        score = compute_coercion_score(patterns)
        # (3.0 * 0.8 + 3.0 * 0.6) / (3.0 + 3.0) * 100 = (2.4 + 1.8) / 6 * 100 = 70.0
        assert score == 70.0

    def test_all_patterns_detected(self):
        """Test scoring with all pattern types detected"""
        patterns = [
            {"pattern_type": "forced_continuity", "confidence": 1.0},  # 3.0
            {"pattern_type": "privacy_zuckering", "confidence": 1.0},  # 3.0
            {"pattern_type": "obstruction", "confidence": 1.0},  # 2.5
            {"pattern_type": "confirmshaming", "confidence": 1.0},  # 2.0
            {"pattern_type": "nagging", "confidence": 1.0},  # 1.0
        ]
        score = compute_coercion_score(patterns)
        # All at 1.0 confidence = 100.0
        assert score == 100.0

    def test_enum_pattern_type(self):
        """Test scoring works with PatternType enum values"""
        from app.models.schemas import PatternType

        patterns = [{"pattern_type": PatternType.FORCED_CONTINUITY, "confidence": 0.8}]
        score = compute_coercion_score(patterns)
        assert score == 80.0

    def test_unknown_pattern_type(self):
        """Test handling of unknown pattern types"""
        patterns = [{"pattern_type": "unknown_pattern", "confidence": 0.8}]
        score = compute_coercion_score(patterns)
        # Unknown patterns use default weight of 1.0
        assert score == 80.0

    def test_zero_confidence(self):
        """Test handling of zero confidence patterns"""
        patterns = [{"pattern_type": "forced_continuity", "confidence": 0.0}]
        score = compute_coercion_score(patterns)
        assert score == 0.0
