from dataclasses import dataclass

from src.modules.rag.models.raw_text import RawText
from src.modules.rag.models.upload_file import UploadFile
from src.modules.rag.repositories.chunk_repository import ChunkRepository
from src.modules.rag.repositories.raw_text_repository import RawTextRepository
from src.modules.rag.repositories.vector_store_repository import VectorStoreRepository
from src.modules.rag.services.chunker import Chunker
from src.modules.rag.services.embedder import Embedder
from src.modules.rag.services.parser import Parser


@dataclass
class IndexDocumentResult:
    """索引化結果の要約を表す。"""

    upload_file_id: int
    raw_text_id: int
    chunk_count: int


class IndexDocumentUseCase:
    """入力テキストをパース、分割、埋め込み、索引化する。"""

    def __init__(
        self,
        raw_text_repository: RawTextRepository,
        chunk_repository: ChunkRepository,
        vector_store_repository: VectorStoreRepository,
        parser: Parser,
        chunker: Chunker,
        embedder: Embedder,
    ) -> None:
        """索引化に必要な依存を受け取る。"""
        self.raw_text_repository = raw_text_repository
        self.chunk_repository = chunk_repository
        self.vector_store_repository = vector_store_repository
        self.parser = parser
        self.chunker = chunker
        self.embedder = embedder

    def execute(
        self,
        *,
        filename: str,
        text: str | None = None,
        content: bytes | None = None,
        content_type: str = 'text/plain',
        parse_type: str = 'plain_text',
        chunk_size: int = 800,
        chunk_overlap: int = 100,
    ) -> IndexDocumentResult:
        """テキストを取り込み、検索用に索引化する。"""
        if text is None and content is None:
            raise ValueError('Either text or content must be provided.')

        if chunk_size <= 0:
            raise ValueError('chunk_size must be greater than zero.')

        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError('chunk_overlap must be between 0 and chunk_size - 1.')

        if text is None:
            assert content is not None
            text = self.parser.parse(
                filename=filename,
                content=content,
                content_type=content_type,
            )

        text = text.strip()
        if not text:
            raise ValueError('No readable text could be extracted from the document.')

        upload_file = self.raw_text_repository.create_upload_file(
            UploadFile(
                id=None,
                filename=filename,
                content_type=content_type,
                size=len(content) if content is not None else len(text.encode('utf-8')),
            )
        )

        raw_text = self.raw_text_repository.save_raw_text(
            RawText(
                id=None,
                upload_file_id=upload_file.id,
                parse_type=parse_type,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                text=text,
            )
        )

        chunks = self.chunker.split(raw_text)
        saved_chunks = self.chunk_repository.save_chunks(chunks)

        if saved_chunks:
            embeddings = self.embedder.embed([chunk.text for chunk in saved_chunks])
            point_ids = self.vector_store_repository.upsert_chunks(saved_chunks, embeddings)
            self.chunk_repository.attach_point_ids(
                [
                    (chunk.id, point_id)
                    for chunk, point_id in zip(saved_chunks, point_ids, strict=False)
                    if chunk.id is not None
                ]
            )

        assert upload_file.id is not None
        assert raw_text.id is not None
        return IndexDocumentResult(
            upload_file_id=upload_file.id,
            raw_text_id=raw_text.id,
            chunk_count=len(saved_chunks),
        )
