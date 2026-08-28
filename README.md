# Dark Pattern Detection API

Detects dark patterns in mental health app screenshots using OCR and Claude AI.

## Patterns Detected

| Pattern               | Description                                         | Weight |
| --------------------- | --------------------------------------------------- | ------ |
| **Forced Continuity** | Hidden auto-renewal, unclear subscription terms     | 3.0    |
| **Privacy Zuckering** | Confusing privacy settings, hidden data collection  | 3.0    |
| **Obstruction**       | Difficult cancellation, hidden settings             | 2.5    |
| **Confirmshaming**    | Guilt-tripping decline options                      | 2.0    |
| **Nagging**           | Persistent upgrade prompts, guilt-inducing messages | 1.0    |

## Features

- **OCR Preprocessing** - Grayscale conversion, contrast enhancement, sharpening for better text extraction
- **Feature Engineering** - Extracts keyword hits, urgency indicators, caps ratio, loss aversion patterns
- **AI Classification** - Uses Claude API with both raw text and computed features
- **Coercion Scoring** - Weighted 0-100 score based on pattern severity and confidence
- **Rate Limiting** - 10 requests/minute per IP (configurable)
- **File Size Limits** - Maximum 10MB images (configurable)

## Setup

### Prerequisites

1. **Python 3.9+**
2. **Tesseract OCR** - [Installation guide](https://github.com/tesseract-ocr/tesseract#installing-tesseract)
   - Windows: Download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - Mac: `brew install tesseract`
   - Linux: `sudo apt install tesseract-ocr`
3. **Anthropic API Key** - Get from [console.anthropic.com](https://console.anthropic.com)

### Installation

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your ANTHROPIC_API_KEY
```

### Run

```bash
uvicorn app.main:app --reload
```

API available at `http://localhost:8000`

## API Usage

### POST /detect

Upload a screenshot for analysis.

```bash
curl -X POST "http://localhost:8000/detect" \
  -F "file=@screenshot.png"
```

**Response:**

```json
{
  "success": true,
  "extracted_text": "Cancel anytime... (subscription auto-renews)",
  "patterns": [
    {
      "pattern_type": "forced_continuity",
      "confidence": 0.85,
      "evidence": "subscription auto-renews",
      "explanation": "Auto-renewal mentioned in small text, may not be clearly visible to users"
    }
  ],
  "message": "Analysis complete",
  "coercion_score": 85.0,
  "features": {
    "length_chars": 156,
    "word_count": 28,
    "sentence_count": 3,
    "urgency_hits": 0,
    "loss_aversion_hits": 0,
    "caps_ratio": 0.05,
    "exclamation_count": 0,
    "question_count": 0,
    "forced_continuity_keyword_hits": 2,
    "nagging_keyword_hits": 0,
    "obstruction_keyword_hits": 0,
    "confirmshaming_keyword_hits": 0,
    "privacy_zuckering_keyword_hits": 0
  }
}
```

### Response Fields

| Field            | Type    | Description                                         |
| ---------------- | ------- | --------------------------------------------------- |
| `success`        | boolean | Whether the analysis completed successfully         |
| `extracted_text` | string  | Raw text extracted from image via OCR               |
| `patterns`       | array   | Detected dark patterns with confidence scores       |
| `message`        | string  | Status message                                      |
| `coercion_score` | float   | 0-100 weighted risk score based on pattern severity |
| `features`       | object  | Pre-computed text features used for classification  |

### GET /health

Health check endpoint.

## Configuration

Environment variables (set in `.env`):

| Variable                   | Default     | Description                           |
| -------------------------- | ----------- | ------------------------------------- |
| `ANTHROPIC_API_KEY`        | _required_  | Claude API key                        |
| `TESSERACT_PATH`           | auto-detect | Path to Tesseract executable          |
| `MIN_CONFIDENCE_THRESHOLD` | 0.3         | Filter patterns below this confidence |
| `MAX_IMAGE_SIZE_MB`        | 10          | Maximum upload size in MB             |
| `RATE_LIMIT_PER_MINUTE`    | 10          | Requests per minute per IP            |

## Project Structure

```
Dark Pattern detector/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py             # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ocr_service.py         # Tesseract OCR with preprocessing
│   │   ├── feature_engineering.py # Text feature extraction
│   │   ├── classifier.py          # Claude API integration
│   │   └── scoring.py             # Coercion score calculation
│   └── utils/
│       ├── __init__.py
│       └── config.py              # Settings management
├── static/
│   ├── index.html                 # Frontend UI
│   ├── styles.css                 # Styling
│   └── app.js                     # Frontend logic
├── tests/
│   ├── __init__.py
│   └── test_api.py                # API and service tests
├── requirements.txt
├── .env.example
└── README.md
```

## Coercion Score Calculation

The coercion score (0-100) is calculated by:

1. Each detected pattern has a weight (see table above)
2. Weight × Confidence is summed for all patterns
3. Normalized to 0-100 scale

**Example:**

- Detected: `forced_continuity` (conf: 0.8) + `nagging` (conf: 0.6)
- Raw: (3.0 × 0.8) + (1.0 × 0.6) = 3.0
- Max possible: 3.0 + 1.0 = 4.0
- Score: (3.0 / 4.0) × 100 = **75.0**

## Testing

```bash
pytest tests/ -v
```

## License

MIT
