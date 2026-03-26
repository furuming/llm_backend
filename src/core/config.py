from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "llm-compare-app"
    database_url: str = "sqlite:///./app.db"

    # ローカルLLM
    local_llm_base_url: str = "http://host.docker.internal:9000"
    local_llm_timeout_sec: float = 120.0
    local_llm_model_name: str = "gemma"

    rag_embedding_provider: str = "sentence_transformer"
    rag_embedding_model_name: str = "BAAI/bge-m3"
    rag_embedding_device: str | None = None
    rag_embedding_normalize: bool = True
    rag_embedding_dimensions: int = 32
    rag_embedding_query_instruction: str | None = None
    rag_embedding_document_instruction: str | None = None

    rag_qdrant_host: str = "localhost"
    rag_qdrant_http_port: int = 6333
    rag_qdrant_grpc_port: int = 6334
    rag_qdrant_collection_name: str = "rag_chunks"
    rag_qdrant_prefer_grpc: bool = False
    rag_qdrant_https: bool = False
    rag_qdrant_api_key: str | None = None
    rag_qdrant_timeout_sec: float = 10.0

    chat_use_rag_default: bool = False
    chat_rag_top_k_default: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    """環境変数を反映した設定オブジェクトを生成する。"""
    return Settings()
