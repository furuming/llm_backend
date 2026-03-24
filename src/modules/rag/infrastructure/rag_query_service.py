from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.core.models import ChunkModel, RawTextModel, UploadFileModel
from src.modules.rag.infrastructure.embedding_gateway import EmbeddingGateway
from src.modules.rag.infrastructure.liteparse_parser import LiteParseParser
from src.modules.rag.infrastructure.qdrant_vector_store import QdrantVectorStore
from src.modules.rag.models.chunk import Chunk
from src.modules.rag.models.raw_text import RawText
from src.modules.rag.models.retrieved_chunk import RetrievedChunk
from src.modules.rag.models.upload_file import UploadFile
from src.modules.rag.repositories.chunk_repository import ChunkRepository
from src.modules.rag.repositories.raw_text_repository import RawTextRepository
from src.modules.rag.repositories.vector_store_repository import VectorStoreRepository
from src.modules.rag.services.chunker import Chunker
from src.modules.rag.services.embedder import Embedder
from src.modules.rag.services.prompt_context_builder import PromptContextBuilder
from src.modules.rag.services.retriver import Retriever
from src.modules.rag.usecases.idex_document import IndexDocumentUseCase
from src.modules.rag.usecases.parse_attached_file import ParseAttachedFileUseCase
from src.modules.rag.usecases.retrieve_chunks import RetrieveChunksUseCase


class SqlAlchemyRawTextRepository(RawTextRepository):
    """RAG のテキスト関連データを SQLAlchemy で永続化する。"""

    def __init__(self, session: Session) -> None:
        """利用する DB セッションを保持する。"""
        self.session = session

    def create_upload_file(self, upload_file: UploadFile) -> UploadFile:
        """アップロードメタデータを保存する。"""
        row = UploadFileModel(
            filename=upload_file.filename,
            content_type=upload_file.content_type,
            size=upload_file.size,
            status=upload_file.status,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return UploadFile(
            id=row.id,
            filename=row.filename,
            content_type=row.content_type,
            size=row.size,
            status=row.status,
            created_at=row.created_at,
        )

    def save_raw_text(self, raw_text: RawText) -> RawText:
        """生テキストを保存する。"""
        row = RawTextModel(
            upload_file_id=raw_text.upload_file_id,
            parse_type=raw_text.parse_type,
            chunk_size=raw_text.chunk_size,
            chunk_overlap=raw_text.chunk_overlap,
            text=raw_text.text,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return RawText(
            id=row.id,
            upload_file_id=row.upload_file_id,
            parse_type=row.parse_type,
            chunk_size=row.chunk_size,
            chunk_overlap=row.chunk_overlap,
            text=row.text,
            created_at=row.created_at,
        )

    def get_raw_text(self, raw_text_id: int) -> RawText | None:
        """ID に対応する生テキストを取得する。"""
        row = self.session.get(RawTextModel, raw_text_id)
        if row is None:
            return None
        return RawText(
            id=row.id,
            upload_file_id=row.upload_file_id,
            parse_type=row.parse_type,
            chunk_size=row.chunk_size,
            chunk_overlap=row.chunk_overlap,
            text=row.text,
            created_at=row.created_at,
        )


class SqlAlchemyChunkRepository(ChunkRepository):
    """チャンクを SQLAlchemy で永続化する。"""

    def __init__(self, session: Session) -> None:
        """利用する DB セッションを保持する。"""
        self.session = session

    def save_chunks(self, chunks: list[Chunk]) -> list[Chunk]:
        """チャンク群を保存し、採番後の値を返す。"""
        if not chunks:
            return []

        rows = [
            ChunkModel(
                upload_file_id=chunk.upload_file_id,
                raw_text_id=chunk.raw_text_id,
                chunk_index=chunk.chunk_index,
                start_offset=chunk.start_offset,
                end_offset=chunk.end_offset,
                chunk_text=chunk.text,
                qdrant_point_id=chunk.qdrant_point_id,
            )
            for chunk in chunks
        ]
        self.session.add_all(rows)
        self.session.commit()
        for row in rows:
            self.session.refresh(row)

        return [
            Chunk(
                id=row.id,
                upload_file_id=row.upload_file_id,
                raw_text_id=row.raw_text_id,
                chunk_index=row.chunk_index,
                start_offset=row.start_offset,
                end_offset=row.end_offset,
                text=row.chunk_text,
                qdrant_point_id=row.qdrant_point_id,
                created_at=row.created_at,
            )
            for row, chunk in zip(rows, chunks, strict=False)
        ]

    def attach_point_ids(self, chunk_point_pairs: list[tuple[int, str]]) -> None:
        """チャンクへベクトルストア上の ID を反映する。"""
        if not chunk_point_pairs:
            return

        for chunk_id, point_id in chunk_point_pairs:
            row = self.session.get(ChunkModel, chunk_id)
            if row is not None:
                row.qdrant_point_id = point_id
        self.session.commit()


class SimpleChunker(Chunker):
    """固定長オーバーラップで文字列を分割する。"""

    def split(self, raw_text: RawText) -> list[Chunk]:
        """生テキストを指定サイズごとのチャンクへ分割する。"""
        text = raw_text.text.strip()
        if not text:
            return []

        chunks: list[Chunk] = []
        start = 0
        step = max(raw_text.chunk_size - raw_text.chunk_overlap, 1)
        index = 0

        while start < len(text):
            end = min(start + raw_text.chunk_size, len(text))
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    Chunk(
                        id=None,
                        upload_file_id=raw_text.upload_file_id,
                        raw_text_id=raw_text.id,
                        chunk_index=index,
                        start_offset=start,
                        end_offset=end,
                        text=chunk_text,
                    )
                )
                index += 1

            if end >= len(text):
                break
            start += step

        return chunks


class RagRetriever(Retriever):
    """Embedder と VectorStore を組み合わせた検索実装。"""

    def __init__(self, embedder: Embedder, vector_store_repository: VectorStoreRepository) -> None:
        """検索に必要な依存を受け取る。"""
        self.embedder = embedder
        self.vector_store_repository = vector_store_repository

    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        """クエリ埋め込みを使って関連チャンクを検索する。"""
        embedding = self.embedder.embed([query])[0]
        return self.vector_store_repository.search(embedding, top_k=top_k)


class SimplePromptContextBuilder(PromptContextBuilder):
    """取得チャンクを単純なコンテキスト文字列へ整形する。"""

    def build(self, chunks: list[RetrievedChunk]) -> str:
        """取得結果を番号付きの文脈文字列へ変換する。"""
        if not chunks:
            return ''

        lines = []
        for index, chunk in enumerate(chunks, start=1):
            lines.append(
                f'[{index}] score={chunk.score:.4f} chunk_index={chunk.chunk_index}\n{chunk.text}'
            )
        return '\n\n'.join(lines)


@dataclass
class RagUseCases:
    """API 層で利用する RAG ユースケース群をまとめる。"""

    parse_attached_file: ParseAttachedFileUseCase
    index_document: IndexDocumentUseCase
    retrieve_chunks: RetrieveChunksUseCase


def build_rag_usecases(session: Session) -> RagUseCases:
    """RAG ユースケース群を依存込みで組み立てる。"""
    parser = LiteParseParser()
    chunker = SimpleChunker()
    embedder = EmbeddingGateway()
    vector_store = QdrantVectorStore()
    raw_text_repository = SqlAlchemyRawTextRepository(session)
    chunk_repository = SqlAlchemyChunkRepository(session)
    retriever = RagRetriever(embedder, vector_store)
    prompt_context_builder = SimplePromptContextBuilder()

    return RagUseCases(
        parse_attached_file=ParseAttachedFileUseCase(parser),
        index_document=IndexDocumentUseCase(
            raw_text_repository=raw_text_repository,
            chunk_repository=chunk_repository,
            vector_store_repository=vector_store,
            parser=parser,
            chunker=chunker,
            embedder=embedder,
        ),
        retrieve_chunks=RetrieveChunksUseCase(
            retriever=retriever,
            prompt_context_builder=prompt_context_builder,
        ),
    )
