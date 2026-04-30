from pathlib import Path

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AstraLearn API"
    app_version: str = "0.26.0"
    database_url: str = Field(
        default="postgresql+psycopg://astralearn:astralearn@postgres:5432/astralearn",
        validation_alias=AliasChoices("database_url", "DATABASE_URL"),
    )
    storage_dir: str = Field(
        default="data/storage",
        validation_alias=AliasChoices("storage_dir", "STORAGE_DIR"),
    )
    # Comma-separated list, e.g. "http://localhost:3000,http://127.0.0.1:3000"
    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        validation_alias=AliasChoices("cors_origins", "CORS_ORIGINS"),
    )
    embedding_dimensions: int = 1536

    openai_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("openai_api_key", "OPENAI_API_KEY"),
    )
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        validation_alias=AliasChoices("openai_embedding_model", "OPENAI_EMBEDDING_MODEL"),
    )
    openai_chat_model: str = Field(
        default="gpt-4o-mini",
        validation_alias=AliasChoices("openai_chat_model", "OPENAI_CHAT_MODEL"),
    )
    graph_max_chunks: int = Field(
        default=48,
        ge=1,
        le=200,
        validation_alias=AliasChoices("graph_max_chunks", "GRAPH_MAX_CHUNKS"),
    )
    internal_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("internal_api_key", "INTERNAL_API_KEY"),
    )
    jwt_secret: str = Field(
        default="dev-only-change-in-production-min-32-chars!!",
        min_length=32,
        validation_alias=AliasChoices("jwt_secret", "JWT_SECRET"),
    )
    jwt_algorithm: str = Field(default="HS256", validation_alias=AliasChoices("jwt_algorithm", "JWT_ALGORITHM"))
    jwt_access_token_expire_minutes: int = Field(
        default=30,
        ge=5,
        le=60 * 24 * 7,
        validation_alias=AliasChoices("jwt_access_token_expire_minutes", "JWT_ACCESS_TOKEN_EXPIRE_MINUTES"),
    )
    refresh_token_expire_days: int = Field(
        default=14,
        ge=1,
        le=90,
        validation_alias=AliasChoices("refresh_token_expire_days", "REFRESH_TOKEN_EXPIRE_DAYS"),
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def _normalize_storage_dir(self) -> "Settings":
        p = Path(self.storage_dir)
        if p.is_absolute():
            object.__setattr__(self, "storage_dir", str(p))
            return self

        api_root = Path(__file__).resolve().parents[2]  # apps/api
        object.__setattr__(self, "storage_dir", str((api_root / p).resolve()))
        return self


settings = Settings()
