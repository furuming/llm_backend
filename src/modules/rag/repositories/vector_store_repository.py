from abc import ABC, abstractmethod

from src.modules.rag.models.chunk import Chunk
from src.modules.rag.models.retrieved_chunk import RetrievedChunk


class VectorStoreRepository(ABC):
    """ベクトルストア操作の境界を表す。"""

    @abstractmethod
    def upsert_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]) -> list[str]:
        """チャンクと埋め込みをベクトルストアへ保存する。"""
        raise NotImplementedError

    @abstractmethod
    def search(self, query_embedding: list[float], top_k: int = 5) -> list[RetrievedChunk]:
        """クエリ埋め込みに類似するチャンクを検索する。"""
        raise NotImplementedError
