from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
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
    FASTAPI_AUTH_URL: str
    REVIEW_SERVICE_URL: str

settings = Settings()
