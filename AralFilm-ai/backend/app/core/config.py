"""
Центральная конфигурация платформы AralFilm AI.

Согласно главе 10 (Backend Architecture) и главе 22 (Master Software
Architecture Blueprint) спецификации: все настройки берутся из
переменных окружения / Secrets Manager, ничего не хардкодится в коде.
"""
from functools import lru_cache
from typing import List

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Общие ---
    PROJECT_NAME: str = "AralFilm AI Platform"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development")  # development | staging | production
    DEBUG: bool = Field(default=False)

    # --- Безопасность (глава 13: Security Architecture) ---
    SECRET_KEY: str = Field(..., description="Секрет для подписи JWT, обязателен")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 часа
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 дней
    JWT_ALGORITHM: str = "HS256"

    # --- База данных (глава 11: Database Architecture) ---
    DATABASE_URL: PostgresDsn

    # --- Redis (кеш, очереди, сессии) ---
    REDIS_URL: RedisDsn

    # --- Object Storage (S3-совместимое, глава 11.22) ---
    STORAGE_ENDPOINT_URL: str = Field(default="")
    STORAGE_BUCKET: str = Field(default="aralfilm-assets")
    STORAGE_ACCESS_KEY: str = Field(default="")
    STORAGE_SECRET_KEY: str = Field(default="")
    STORAGE_REGION: str = Field(default="us-east-1")

    # --- CORS ---
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    # --- Rate limiting (глава 13.11) ---
    RATE_LIMIT_FREE_PER_DAY: int = 100
    RATE_LIMIT_PROFESSIONAL_PER_DAY: int = 10_000


@lru_cache
def get_settings() -> Settings:
    """Настройки кешируются на процесс — читаются один раз."""
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
