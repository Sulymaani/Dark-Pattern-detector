import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import io
import logging

logger = logging.getLogger(__name__)


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Preprocess image for better OCR accuracy.

    Applies grayscale conversion, contrast enhancement, sharpening,
    and resizing for small images.

    Args:
        image: PIL Image object

    Returns:
        Preprocessed PIL Image
    """
    # Convert to RGB if necessary (handles PNG with alpha)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    # Convert to grayscale for better OCR
    image = image.convert("L")

    # Increase contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.5)

    # Slight sharpening to improve text edges
    image = image.filter(ImageFilter.SHARPEN)

    # Resize if too small (improves Tesseract accuracy)
    min_width = 1000
    if image.width < min_width:
        ratio = min_width / image.width
        new_size = (int(image.width * ratio), int(image.height * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)

    return image


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

        # Preprocess for better OCR accuracy
        image = preprocess_image(image)

        # Use PSM 6 for uniform text blocks (common in app UIs)
        # OEM 3 uses default OCR engine mode
        custom_config = r"--oem 3 --psm 6"
        text = pytesseract.image_to_string(image, lang="eng", config=custom_config)

        logger.info(f"Extracted {len(text)} characters from image")
        return text.strip()

    except Exception as e:
        logger.error(f"OCR extraction failed: {str(e)}")
        raise RuntimeError(f"OCR extraction failed: {str(e)}")
