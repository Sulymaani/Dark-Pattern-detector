import pytesseract
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)


def extract_text(image_bytes: bytes) -> str:
    """
    Extract text from image using Tesseract OCR.

    Args:
        image_bytes: Raw image bytes

    Returns:
        Extracted text string
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB if necessary (handles PNG with alpha)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        # Extract text with Tesseract
        text = pytesseract.image_to_string(image, lang="eng")

        logger.info(f"Extracted {len(text)} characters from image")
        return text.strip()

    except Exception as e:
        logger.error(f"OCR extraction failed: {str(e)}")
        raise RuntimeError(f"OCR extraction failed: {str(e)}")
