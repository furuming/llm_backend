from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class RetrievedContext:
    """チャット応答生成に使う補助文脈。"""

    context: str
    chunk_count: int


class ContextProvider(ABC):
    """チャット向けの補助文脈取得を抽象化する。"""

    @abstractmethod
    def get_context(self, query: str, top_k: int) -> RetrievedContext:
        """問い合わせに関連する補助文脈を返す。"""
        raise NotImplementedError
