from __future__ import annotations

from functools import lru_cache
from typing import Literal, Optional

from pydantic import AnyHttpUrl, Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Jarvis Brain"
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    environment: str = Field(default="local", alias="ENVIRONMENT")
    log_level: str = Field(default="info", alias="LOG_LEVEL")

    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(alias="REDIS_URL")

    timezone_default: str = Field(default="UTC", alias="TIMEZONE_DEFAULT")

    llm_provider: Literal["ollama", "openai"] = Field(default="ollama", alias="LLM_PROVIDER")

    openai_base_url: str = Field(default="https://api.groq.com/openai/v1", alias="OPENAI_BASE_URL")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="llama-3.3-70b-versatile", alias="OPENAI_MODEL")
    openai_embedding_model: str = Field(default="text-embedding-3-small", alias="OPENAI_EMBEDDING_MODEL")

    ollama_base_url: AnyHttpUrl = Field(default="http://ollama:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3.1", alias="OLLAMA_MODEL")

    vector_backend: Literal["pgvector", "qdrant"] = Field(default="pgvector", alias="VECTOR_BACKEND")
    qdrant_url: Optional[HttpUrl] = Field(default=None, alias="QDRANT_URL")

    google_service_account_json: Optional[str] = Field(default=None, alias="GOOGLE_SERVICE_ACCOUNT_JSON")
    google_oauth_client_id: Optional[str] = Field(default=None, alias="GOOGLE_OAUTH_CLIENT_ID")
    google_oauth_client_secret: Optional[str] = Field(default=None, alias="GOOGLE_OAUTH_CLIENT_SECRET")
    google_calendar_id: Optional[str] = Field(default=None, alias="GOOGLE_CALENDAR_ID")

    notion_api_key: Optional[str] = Field(default=None, alias="NOTION_API_KEY")
    notion_database_id: Optional[str] = Field(default=None, alias="NOTION_DATABASE_ID")

    telegram_bot_token: Optional[str] = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    telegram_webhook_secret: Optional[str] = Field(default=None, alias="TELEGRAM_WEBHOOK_SECRET")

    enable_email_stub: bool = Field(default=True, alias="ENABLE_EMAIL_STUB")

    celery_broker_url: Optional[str] = Field(default=None, alias="CELERY_BROKER_URL")
    celery_result_backend: Optional[str] = Field(default=None, alias="CELERY_RESULT_BACKEND")

    class Config:
        env_prefix = ""


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
