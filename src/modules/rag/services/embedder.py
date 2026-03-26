from abc import ABC, abstractmethod


class Embedder(ABC):
    """テキスト埋め込み生成の抽象。"""

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """複数文書を埋め込みベクトルへ変換する。"""
        raise NotImplementedError

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """検索クエリを埋め込みベクトルへ変換する。"""
        raise NotImplementedError

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """埋め込みベクトルの次元数を返す。"""
        raise NotImplementedError
