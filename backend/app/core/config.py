"""Application configuration settings."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_NAME: str = "CivilEng"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://civileng:civileng@localhost:5432/civileng"

    # Security
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:19006",
        "https://civileng.app",
    ]

    # Engineering defaults
    DEFAULT_PARTIAL_FACTOR_SET: str = "BS_SET_A"  # or "EC7_DA1_C1", "EC7_DA1_C2"
    DEFAULT_CONCRETE_GRADE: str = "C30"
    DEFAULT_REBAR_GRADE: str = "B500"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
