from pydantic import BaseSettings, Field
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    API_HOST: str = Field("0.0.0.0", env="API_HOST")
    API_PORT: int = Field(8000, env="API_PORT")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    ENV: str = Field("development", env="ENV")

    class Config:
        env_file = ".env"


settings = Settings()
from __future__ import annotations

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = Field("SupplyChainIQ", env="APP_NAME")
    api_env: str = Field("development", env="API_ENV")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini", env="OPENAI_MODEL")

    postgres_user: str = Field("supplyiq", env="POSTGRES_USER")
    postgres_password: str = Field("supplyiqpass", env="POSTGRES_PASSWORD")
    postgres_db: str = Field("supplyiq", env="POSTGRES_DB")
    postgres_host: str = Field("db", env="POSTGRES_HOST")
    postgres_port: int = Field(5432, env="POSTGRES_PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
