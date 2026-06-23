from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from .env or environment variables."""

    # Application
    app_name: str = "SupplyChainIQ"
    api_env: str = "development"
    log_level: str = "INFO"

    # OpenAI (for future Copilot integration)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"

    # PostgreSQL
    postgres_user: str = "supplyiq"
    postgres_password: str = "supplyiqpass"
    postgres_db: str = "supplyiq"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def DATABASE_URL(self) -> str:
        """Construct DATABASE_URL from components."""
        return (
            f"postgresql+psycopg://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
