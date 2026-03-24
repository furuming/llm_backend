from fastapi import File, Form, UploadFile
from pydantic import BaseModel, Field


class IndexDocumentRequest:
    """RAG 文書索引化で受け付ける multipart リクエスト。"""

    def __init__(
        self,
        file: UploadFile = File(...),
        parse_type: str = Form(default="plain_text"),
        chunk_size: int = Form(default=800),
        chunk_overlap: int = Form(default=100),
    ) -> None:
        """アップロードファイルと分割パラメータを保持する。"""
        self.file = file
        self.parse_type = parse_type
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap


class IndexDocumentResponse(BaseModel):
    """索引化結果レスポンス。"""

    upload_file_id: int
    raw_text_id: int
    chunk_count: int


class RetrieveChunksRequest(BaseModel):
    """RAG 検索リクエスト。"""

    query: str
    top_k: int = Field(default=5, ge=1, le=20)


class RetrievedChunkResponse(BaseModel):
    """検索結果チャンクのレスポンス。"""

    chunk_id: int | None
    upload_file_id: int | None
    raw_text_id: int | None
    chunk_index: int
    start_offset: int
    end_offset: int
    text: str
    score: float
    qdrant_point_id: str | None


class RetrieveChunksResponse(BaseModel):
    """検索結果レスポンス。"""

    context: str
    chunks: list[RetrievedChunkResponse]
