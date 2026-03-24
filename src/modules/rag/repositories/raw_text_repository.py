from abc import ABC, abstractmethod

from src.modules.rag.models.raw_text import RawText
from src.modules.rag.models.upload_file import UploadFile


class RawTextRepository(ABC):
    """アップロード情報と生テキストの永続化境界を表す。"""

    @abstractmethod
    def create_upload_file(self, upload_file: UploadFile) -> UploadFile:
        """アップロードファイルのメタデータを保存する。"""
        raise NotImplementedError

    @abstractmethod
    def save_raw_text(self, raw_text: RawText) -> RawText:
        """パース済みテキストを保存する。"""
        raise NotImplementedError

    @abstractmethod
    def get_raw_text(self, raw_text_id: int) -> RawText | None:
        """ID に一致する生テキストを取得する。"""
        raise NotImplementedError
