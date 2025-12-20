# Dark Pattern Detection API - Copilot Instructions

## Architecture Overview

This is a FastAPI service that detects dark patterns in mental health app screenshots. The pipeline flows:
**Image Upload → OCR (Tesseract) → Feature Engineering → Text Classification (Claude API) → Scoring → JSON Response**

### Key Components

- [app/main.py](../app/main.py) - FastAPI app with `/detect` and `/health` endpoints
- [app/services/ocr_service.py](../app/services/ocr_service.py) - Tesseract OCR wrapper
- [app/services/feature_engineering.py](../app/services/feature_engineering.py) - Text feature extraction (keyword counts, stylistic features)
- [app/services/classifier.py](../app/services/classifier.py) - Claude API integration with structured prompt
- [app/services/scoring.py](../app/services/scoring.py) - Coercion score calculation based on detected patterns
- [app/models/schemas.py](../app/models/schemas.py) - Pydantic models and `PatternType` enum
- [app/utils/config.py](../app/utils/config.py) - Settings via `pydantic-settings` (loads `.env`)

## Dark Pattern Types

The system detects exactly 5 patterns defined in `PatternType` enum:

- `forced_continuity` - Hidden auto-renewal, unclear subscription terms
- `nagging` - Persistent upgrade prompts, guilt-inducing messages
- `obstruction` - Difficult cancellation, hidden settings
- `confirmshaming` - Guilt-tripping decline options
- `privacy_zuckering` - Confusing privacy settings, hidden data collection

**When modifying detection logic**, update both `CLASSIFICATION_PROMPT` in `classifier.py` and `PatternType` enum in `schemas.py`.

## Development Commands

```bash
# Setup (requires Tesseract OCR installed on system)
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt

# Run server (auto-reload for development)
uvicorn app.main:app --reload

# Run tests
pytest tests/ -v
```

## Environment Configuration

Required in `.env`:

```
ANTHROPIC_API_KEY=sk-ant-...
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe  # Optional on Windows
```

## Code Patterns

### Adding New Endpoints

Follow the pattern in `main.py`: use Pydantic response models, async handlers, and structured error handling with `HTTPException`.

### Adding New Pattern Types

1. Add to `PatternType` enum in `schemas.py`
2. Update `CLASSIFICATION_PROMPT` in `classifier.py` with detection criteria
3. Add test case in `tests/test_api.py`

### Service Layer Pattern

Services in `app/services/` are stateless functions:
- **ocr_service.py**: Sync function - extracts text from images using Tesseract
- **feature_engineering.py**: Sync function - computes text features (keyword counts, stylistic metrics)
- **classifier.py**: Async function - classifies patterns using Claude API (creates new client per request)
- **scoring.py**: Sync function - computes coercion score from detected patterns using severity weights

### Detection Pipeline

The `/detect` endpoint orchestrates four steps:
1. **OCR Extraction**: `extract_text()` - converts image to text
2. **Feature Engineering**: `compute_text_features()` - analyzes text for pattern indicators
3. **Classification**: `classify_patterns()` - uses Claude API to identify specific dark patterns
4. **Scoring**: `compute_coercion_score()` - calculates overall severity score (0.0-1.0)

### Testing Pattern

Tests use `fastapi.testclient.TestClient` with mocked services. Create test images using PIL's `Image.new()` pattern (see `create_minimal_png()` in test file).

## External Dependencies

- **Tesseract OCR**: Must be installed system-wide. Path auto-detected on most systems; set `TESSERACT_PATH` env var if needed.
- **Anthropic API**: Uses `claude-3-haiku-20240307` model. Response must be valid JSON array.

## Common Issues

- **"TesseractNotFoundError"**: Install Tesseract or set `TESSERACT_PATH` in `.env`
- **Empty OCR results**: Check image quality; service returns success with empty patterns list
- **Claude JSON parse errors**: Check `CLASSIFICATION_PROMPT` ends with instruction to return only JSON
