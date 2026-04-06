"""Application configuration using pydantic-settings."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_env: Literal["development", "staging", "production"] = "development"
    log_level: str = "DEBUG"
    api_base_url: str = "http://localhost:8000"
    dashboard_url: str = "http://localhost:3000"

    # Database
    database_url: str = (
        "postgresql+asyncpg://neuraprop:neuraprop@localhost:5432/neuraprop"
    )
    database_url_sync: str = (
        "postgresql://neuraprop:neuraprop@localhost:5432/neuraprop"
    )
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # AWS
    aws_region: str = "us-east-1"
    aws_access_key_id: str = "test"
    aws_secret_access_key: str = "test"
    aws_endpoint_url: str | None = "http://localhost:4566"
    sqs_inbound_queue_url: str = (
        "http://localhost:4566/000000000000/neuraprop-inbound"
    )
    sqs_outbound_queue_url: str = (
        "http://localhost:4566/000000000000/neuraprop-outbound"
    )
    s3_bucket_name: str = "neuraprop-storage"

    # LLM
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Auth
    clerk_secret_key: str = ""

    # Email
    sendgrid_api_key: str = ""

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
