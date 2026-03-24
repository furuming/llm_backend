from dataclasses import dataclass
from datetime import datetime


@dataclass
class RetrievedChunk:
    """検索結果として返されるチャンク情報を表す。"""

    chunk_id: int | None
    upload_file_id: int | None
    raw_text_id: int | None
    chunk_index: int
    start_offset: int
    end_offset: int
    text: str
    score: float
    qdrant_point_id: str | None = None
    created_at: datetime | None = None
