from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://activitylog:changeme@localhost:5432/activitylog"
    REDIS_URL: str = "redis://localhost:6379/0"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5500", "http://127.0.0.1:5500"]
    LOG_LEVEL: str = "INFO"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
