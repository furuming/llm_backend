from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base
from src.modules.chat.infrastructure.models import ChatMessageModel

LONG_TEXT = Text().with_variant(mysql.LONGTEXT(), 'mysql')


class UploadFileModel(Base):
    """RAG 取り込み対象ファイルのメタデータを保持する。"""

    __tablename__ = 'upload_files'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(255), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class RawTextModel(Base):
    """パース後の生テキストを保持する。"""

    __tablename__ = 'raw_texts'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    upload_file_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    parse_type: Mapped[str] = mapped_column(String(255), nullable=False)
    chunk_size: Mapped[int] = mapped_column(Integer, nullable=False, default=800)
    chunk_overlap: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    text: Mapped[str] = mapped_column(LONG_TEXT, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class ChunkModel(Base):
    """検索用に分割したチャンクのメタデータを保持する。"""

    __tablename__ = 'chunks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    upload_file_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    raw_text_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    start_offset: Mapped[int] = mapped_column(Integer, nullable=False)
    end_offset: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(LONG_TEXT, nullable=False)
    qdrant_point_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


__all__ = ['ChatMessageModel', 'UploadFileModel', 'RawTextModel', 'ChunkModel']
