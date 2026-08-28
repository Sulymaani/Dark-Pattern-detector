from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.services.ocr_service import extract_text
from app.services.feature_engineering import compute_text_features
from app.services.classifier import classify_patterns
from app.services.scoring import compute_coercion_score
from app.models.schemas import DetectionResponse, PatternResult
from app.utils.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Dark Pattern Detection API",
    description="Detects dark patterns in mental health app screenshots",
    version="1.0.0",
)

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Serve the frontend"""
    return FileResponse("static/index.html")


@app.post("/detect", response_model=DetectionResponse)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def detect_dark_patterns(request: Request, file: UploadFile = File(...)):
    """
    Analyze screenshot for dark patterns.
    Accepts: PNG, JPG, JPEG images (max 10MB)
    Returns: JSON with detected patterns, confidence scores, and coercion score
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        image_bytes = await file.read()

        # Check file size
        max_size = settings.max_image_size_mb * 1024 * 1024
        if len(image_bytes) > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"Image too large. Maximum size is {settings.max_image_size_mb}MB",
            )

        # Step 1: Extract text from image
        extracted_text = extract_text(image_bytes)

        if not extracted_text.strip():
            return DetectionResponse(
                success=True,
                extracted_text="",
                patterns=[],
                message="No text detected in image",
                coercion_score=0.0,
                features=None,
            )

        # Step 2: Compute text features (keyword hits, metrics)
        features = compute_text_features(extracted_text)

        # Step 3: Classify patterns using Claude API with text + features
        patterns = await classify_patterns(extracted_text, features)

        # Step 4: Compute weighted coercion score
        patterns_dict = [p.model_dump() for p in patterns]
        coercion_score = compute_coercion_score(patterns_dict)

        return DetectionResponse(
            success=True,
            extracted_text=extracted_text,
            patterns=patterns,
            message="Analysis complete",
            coercion_score=coercion_score,
            features=features,
        )

    except Exception as e:
        logger.error(f"Detection failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
