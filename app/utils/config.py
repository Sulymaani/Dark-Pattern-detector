from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    anthropic_api_key: str
    tesseract_path: str = ""  # Optional: path to tesseract executable

    # Detection settings
    min_confidence_threshold: float = 0.3  # Filter patterns below this confidence
    max_image_size_mb: int = 10  # Maximum upload size in MB

    # Rate limiting
    rate_limit_per_minute: int = 10  # Requests per minute per IP

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
