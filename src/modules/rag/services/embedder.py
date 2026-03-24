from abc import ABC, abstractmethod


class Embedder(ABC):
    """テキスト埋め込み生成の抽象。"""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """複数テキストを埋め込みベクトルへ変換する。"""
        raise NotImplementedError
