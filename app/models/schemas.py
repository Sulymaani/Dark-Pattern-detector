from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class PatternType(str, Enum):
    FORCED_CONTINUITY = "forced_continuity"
    NAGGING = "nagging"
    OBSTRUCTION = "obstruction"
    CONFIRMSHAMING = "confirmshaming"
    PRIVACY_ZUCKERING = "privacy_zuckering"


class PatternResult(BaseModel):
    pattern_type: PatternType
    confidence: float  # 0.0 to 1.0
    evidence: str  # Text snippet that triggered detection
    explanation: str  # Why this is considered a dark pattern


class DetectionResponse(BaseModel):
    success: bool
    extracted_text: str
    patterns: List[PatternResult]
    message: str
