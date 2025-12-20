from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.services.ocr_service import extract_text
from app.services.classifier import classify_patterns
from app.models.schemas import DetectionResponse, PatternResult
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Dark Pattern Detection API",
    description="Detects dark patterns in mental health app screenshots",
    version="1.0.0",
)

# Get the project root directory (parent of app/)
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def root():
    """Serve the frontend"""
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.post("/detect", response_model=DetectionResponse)
async def detect_dark_patterns(file: UploadFile = File(...)):
    """
    Analyze screenshot for dark patterns.
    Accepts: PNG, JPG, JPEG images
    Returns: JSON with detected patterns and confidence scores
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        image_bytes = await file.read()

        # Extract text from image
        extracted_text = extract_text(image_bytes)

        if not extracted_text.strip():
            return DetectionResponse(
                success=True,
                extracted_text="",
                patterns=[],
                message="No text detected in image",
            )

        # Classify patterns using Claude API
        patterns = await classify_patterns(extracted_text)

        return DetectionResponse(
            success=True,
            extracted_text=extracted_text,
            patterns=patterns,
            message="Analysis complete",
        )

    except Exception as e:
        logger.error(f"Detection failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
