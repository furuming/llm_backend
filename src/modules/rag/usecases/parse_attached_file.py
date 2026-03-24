from src.modules.rag.models.upload_file import UploadFile
from src.modules.rag.services.parser import Parser


class ParseAttachedFileUseCase:
    """アップロードファイルをテキストへ変換する。"""

    def __init__(self, parser: Parser) -> None:
        """利用するパーサーを受け取る。"""
        self.parser = parser

    def execute(self, upload_file: UploadFile, content: bytes) -> str:
        """ファイル内容を解析してテキストを返す。"""
        return self.parser.parse(
            filename=upload_file.filename,
            content=content,
            content_type=upload_file.content_type,
        )
