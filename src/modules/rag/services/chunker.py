from abc import ABC, abstractmethod

from src.modules.rag.models.chunk import Chunk
from src.modules.rag.models.raw_text import RawText


class Chunker(ABC):
    """生テキストを検索用チャンクへ分割する抽象。"""

    @abstractmethod
    def split(self, raw_text: RawText) -> list[Chunk]:
        """生テキストをチャンク一覧へ変換する。"""
        raise NotImplementedError
