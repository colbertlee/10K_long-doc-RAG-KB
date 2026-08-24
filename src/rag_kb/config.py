"""Configuration management for RAG KB."""

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
        env_prefix='RAGKB_',
    )

    # Application settings
    app_name: str = 'rag-kb'
    data_dir: Path = Path('./data')
    lightrag_working_dir: Path = Path('./lightrag_db')
    log_level: str = 'INFO'

    # Embedding settings
    embedding_provider: str = 'ollama'
    embedding_base_url: str = 'http://localhost:11434'
    embedding_model: str = 'nomic-embed-text'

    # LLM settings
    llm_provider: str = 'ollama'
    llm_base_url: str = 'http://localhost:11434'
    llm_model: str = 'qwen3.5:4b'
    llm_temperature: float = 0.3
    llm_top_p: float = 0.9
    llm_max_tokens: int = 2048

    # LightRAG settings
    lightrag_chunk_token_size: int = 1200
    lightrag_max_token: int = 4096
    lightrag_query_mode: str = 'hybrid'
    lightrag_enable_llm_cache: bool = True

    # OpenAI-compatible remote LLM (optional)
    openai_api_key: str | None = Field(default=None)
    openai_base_url: str | None = Field(default=None)


# Global settings instance
settings = Settings()