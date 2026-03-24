from abc import ABC, abstractmethod

from src.modules.rag.models.retrieved_chunk import RetrievedChunk


class PromptContextBuilder(ABC):
    """検索結果を LLM 用コンテキストへ整形する抽象。"""

    @abstractmethod
    def build(self, chunks: list[RetrievedChunk]) -> str:
        """検索チャンク群からプロンプト用文脈を組み立てる。"""
        raise NotImplementedError
