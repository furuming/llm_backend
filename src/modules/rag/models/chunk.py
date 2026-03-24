from dataclasses import dataclass
from datetime import datetime


@dataclass
class Chunk:
    """検索対象となるテキストチャンクを表す。"""

    id: int | None
    upload_file_id: int | None
    raw_text_id: int | None
    chunk_index: int
    start_offset: int
    end_offset: int
    text: str
    qdrant_point_id: str | None = None
    created_at: datetime | None = None
