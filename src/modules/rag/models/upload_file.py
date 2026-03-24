from dataclasses import dataclass
from datetime import datetime


@dataclass
class UploadFile:
    """RAG に取り込むファイルのメタデータを表す。"""

    id: int | None
    filename: str
    content_type: str
    size: int = 0
    status: int = 1
    created_at: datetime | None = None
