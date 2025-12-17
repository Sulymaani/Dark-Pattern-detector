# Dark Pattern Detection API

Detects dark patterns in mental health app screenshots using OCR and Claude AI.

## Patterns Detected

- **Forced Continuity** - Hidden auto-renewal, unclear subscription terms
- **Nagging** - Persistent upgrade prompts, guilt-inducing messages
- **Obstruction** - Difficult cancellation, hidden settings
- **Confirmshaming** - Guilt-tripping decline options
- **Privacy Zuckering** - Confusing privacy settings, hidden data collection

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
  "message": "Analysis complete"
}
```

### GET /health

Health check endpoint.

## Project Structure

```
Dark Pattern detector/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ocr_service.py   # Tesseract OCR
│   │   └── classifier.py    # Claude API integration
│   └── utils/
│       ├── __init__.py
│       └── config.py        # Settings management
├── tests/
│   ├── __init__.py
│   └── test_api.py
├── requirements.txt
├── .env.example
└── README.md
```

## Testing

```bash
pytest tests/
```
