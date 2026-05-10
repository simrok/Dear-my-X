"""앱 설정 — 환경 변수 -> 타입드 설정 객체.

`pydantic-settings` 를 사용해서 .env 파일과 OS 환경 변수를 자동 로드한다.
프로파일 분리는 `APP_ENV` 로 하고, 필요시 `Settings(...).Config.env_file` 을
오버라이드해서 staging/production 분기를 한다.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- 앱 ---
    APP_ENV: Literal["development", "staging", "production"] = "development"
    APP_NAME: str = "dear-my-x-server"
    APP_DEBUG: bool = True
    APP_LOG_LEVEL: str = "INFO"

    # --- API ---
    API_V1_PREFIX: str = "/api/v1"
    CORS_ALLOW_ORIGINS: list[str] = Field(default_factory=lambda: ["*"])

    # --- DB ---
    DATABASE_URL: str = "postgresql+asyncpg://dear_my_x:dear_my_x_pw@localhost:5432/dear_my_x"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False

    # --- Supabase ---
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""
    SUPABASE_STORAGE_BUCKET: str = "dear-my-x-uploads"

    # --- AI: Anthropic Claude ---
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"

    # --- AI: OpenAI Embedding ---
    OPENAI_API_KEY: str = ""
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536

    # --- 보안 ---
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    @field_validator("CORS_ALLOW_ORIGINS", mode="before")
    @classmethod
    def _split_csv(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
