from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Identity & Version
    PROJECT_NAME: str = "PRAGYA API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Database (Native PostgreSQL on Windows)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pragya"
    VECTOR_DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pragya"

    # Security & JWT
    JWT_SECRET: str = "super_secret_pragya_jwt_key_change_in_production_32_chars_min"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # CORS Configuration
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # AI Provider Modes
    LLM_PROVIDER: str = "mock"
    LLM_MODEL: str = "llama-3-8b-instruct"
    LLM_BASE_URL: str = "http://127.0.0.1:11434/v1"
    LLM_API_KEY: str | None = None
    EMBEDDING_PROVIDER: str = "local"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # AI Learning Assistant Configuration
    ASSISTANT_HISTORY_MESSAGES: int = 8
    MAX_MESSAGES_PER_MINUTE: int = 20
    MAX_TOKENS_PER_REQUEST: int = 1024
    MAX_CONTEXT_CHUNKS: int = 5

    # Ecosystem Integration Modes (mock / live)
    IGOT_PROVIDER_MODE: str = "mock"
    NSSTA_PROVIDER_MODE: str = "mock"
    MOCK_IGOT_BASE_URL: str = ""
    MOCK_NSSTA_BASE_URL: str = ""
    IGOT_API_BASE_URL: str | None = None
    IGOT_CLIENT_ID: str | None = None
    IGOT_CLIENT_SECRET: str | None = None

    # Document Intelligence & File Storage
    MAX_UPLOAD_SIZE_MB: int = 25
    STORAGE_UPLOAD_DIR: str = "storage/uploads"
    EMBEDDING_DIMENSION: int = 384
    VECTOR_BACKEND: str = "pgvector"
    MIN_RETRIEVAL_SCORE: float = 0.50

    model_config = SettingsConfigDict(
        env_file=(
            str(Path(__file__).resolve().parents[3] / ".env"),
            str(Path(__file__).resolve().parents[2] / ".env"),
            ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
