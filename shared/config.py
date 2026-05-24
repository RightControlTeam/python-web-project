from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file= BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    DJANGO_DATABASE_URL: str
    FASTAPI_DATABASE_URL: str
    FLASK_DATABASE_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXP_MINS: int = 30

    DJANGO_BACKEND_URL: str
    TRANSACTION_SERVICE_URL: str
    REVIEW_SERVICE_URL: str
    DJANGO_SECRET_KEY: str

    NOTIFICATION_KEY: str
    DEBUG: bool = True

settings = Settings()
