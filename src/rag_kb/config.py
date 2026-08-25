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
    llm_model: str = 'gemma4:e4b'  # Changed from qwen3.5:4b due to response issues
    llm_temperature: float = 0.3
    llm_top_p: float = 0.9
    llm_max_tokens: int = 4096  # Increased from 2048 to avoid truncation

    # LightRAG settings
    lightrag_chunk_token_size: int = 1200
    lightrag_max_token: int = 4096
    lightrag_query_mode: str = 'hybrid'
    lightrag_enable_llm_cache: bool = True
    
    # LightRAG worker timeout settings (critical for entity extraction)
    lightrag_llm_worker_timeout: int = 600  # 10 minutes for LLM workers (increased from 480s)
    lightrag_embedding_worker_timeout: int = 300  # 5 minutes for embedding workers
    lightrag_max_concurrent_workers: int = 4  # Control concurrent worker count
    lightrag_worker_queue_size: int = 100  # Worker queue size
    
    # Timeout settings (increased for local model performance)
    request_timeout: int = 600  # 10 minutes for LLM requests
    embedding_timeout: int = 180  # 3 minutes for embedding
    query_timeout: int = 600  # 10 minutes for queries
    ingestion_timeout: int = 900  # 15 minutes for document ingestion

    # OpenAI-compatible remote LLM (optional)
    openai_api_key: str | None = Field(default=None)
    openai_base_url: str | None = Field(default=None)


# Global settings instance
settings = Settings()