import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)


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
