from abc import ABC, abstractmethod


class Parser(ABC):
    """入力ファイルをテキストへ変換する抽象。"""

    @abstractmethod
    def parse(self, *, filename: str, content: bytes, content_type: str | None = None) -> str:
        """ファイル内容をテキストへ変換する。"""
        raise NotImplementedError
