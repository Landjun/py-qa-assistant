"""Application configuration."""
import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Teaching Operations CRM API"
    app_version: str = "0.1.0"
    sqlite_url: str = "sqlite:///./crm.db"
    cors_origins: list[str] = ["*"]
    ai_mode: str = os.getenv("AI_MODE", "mock")


settings = Settings()
