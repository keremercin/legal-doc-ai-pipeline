from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "dev"
    app_name: str = "Legal Doc AI Pipeline"
    log_level: str = "INFO"

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4.1-mini"

    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "legal_doc_ai"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    retriever_backend: str = "memory"  # memory | pgvector

    vector_dim: int = 1536
    top_k: int = 5
    hybrid_keyword_boost: float = 0.15

    chunk_size: int = 700
    chunk_overlap: int = 100

    classifier_mode: str = "auto"  # auto | rule | llm
    ocr_engine: str = "tesseract"
    api_key: str = ""

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
