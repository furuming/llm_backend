from abc import ABC, abstractmethod

from src.modules.rag.models.retrieved_chunk import RetrievedChunk


class Retriever(ABC):
    """問い合わせに対する関連チャンク取得の抽象。"""

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        """クエリに関連するチャンクを取得する。"""
        raise NotImplementedError
