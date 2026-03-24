from abc import ABC, abstractmethod

from src.modules.rag.models.chunk import Chunk


class ChunkRepository(ABC):
    """チャンク永続化の境界を表す。"""

    @abstractmethod
    def save_chunks(self, chunks: list[Chunk]) -> list[Chunk]:
        """チャンク群を保存して保存後の値を返す。"""
        raise NotImplementedError

    @abstractmethod
    def attach_point_ids(self, chunk_point_pairs: list[tuple[int, str]]) -> None:
        """保存済みチャンクにベクトルストア上の ID を紐付ける。"""
        raise NotImplementedError
