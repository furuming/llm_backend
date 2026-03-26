from src.core.config import Settings
from src.modules.rag.infrastructure.hash_embedder import HashEmbedder
from src.modules.rag.services.embedder import Embedder


def build_embedder(settings: Settings) -> Embedder:
    """設定に応じて埋め込み実装を返す。"""
    provider = settings.rag_embedding_provider.lower()

    if provider == 'sentence_transformer':
        from src.modules.rag.infrastructure.sentence_transformer_embedder import (
            SentenceTransformerEmbedder,
        )

        return SentenceTransformerEmbedder(
            model_name=settings.rag_embedding_model_name,
            device=settings.rag_embedding_device,
            normalize_embeddings=settings.rag_embedding_normalize,
            query_instruction=settings.rag_embedding_query_instruction,
            document_instruction=settings.rag_embedding_document_instruction,
        )

    if provider == 'hash':
        return HashEmbedder(dimensions=settings.rag_embedding_dimensions)

    raise ValueError(f'Unsupported embedding provider: {settings.rag_embedding_provider}')
