from dataclasses import dataclass
from datetime import datetime


@dataclass
class RawText:
    """パース後の生テキストと分割設定を表す。"""

    id: int | None
    upload_file_id: int | None
    parse_type: str
    chunk_size: int
    chunk_overlap: int
    text: str
    created_at: datetime | None = None
