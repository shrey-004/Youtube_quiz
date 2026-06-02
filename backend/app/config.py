"""
config.py — Application configuration using environment variables.

Pydantic Settings reads values from the .env file automatically.
If a required variable is missing, the app raises an error at startup
instead of silently failing later — this is called "fail fast".
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    All configuration comes from environment variables.
    The types (str, int) are enforced by Pydantic automatically.
    """

    # Application
    APP_NAME: str = "YouTube Quiz Generator"
    DEBUG: bool = False

    # Database — we'll get this URL from Supabase
    DATABASE_URL: str

    # JWT Authentication
    # This secret key signs your JWT tokens. Keep it secret!
    # Generate one with: python -c "import secrets; print(secrets.token_hex(32))"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Google Gemini API (free tier)
    GEMINI_API_KEY: str

    class Config:
        # Tells Pydantic to read from the .env file
        env_file = ".env"
        case_sensitive = True


# lru_cache means this function only runs once — the Settings object
# is created once and reused everywhere. This is the Singleton pattern.
@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Create a single instance to import across the app
settings = get_settings()