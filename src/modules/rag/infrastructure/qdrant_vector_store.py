from datetime import datetime

from qdrant_client import QdrantClient
from qdrant_client.http import models

from src.core.config import Settings
from src.modules.rag.models.chunk import Chunk
from src.modules.rag.models.retrieved_chunk import RetrievedChunk
from src.modules.rag.repositories.vector_store_repository import VectorStoreRepository


class QdrantVectorStore(VectorStoreRepository):
    """Qdrant を使ったベクトルストア実装。"""

    def __init__(self, settings: Settings, vector_size: int) -> None:
        """接続設定とベクトル次元数を受け取って初期化する。"""
        self._collection_name = settings.rag_qdrant_collection_name
        self._client = QdrantClient(
            host=settings.rag_qdrant_host,
            port=settings.rag_qdrant_http_port,
            grpc_port=settings.rag_qdrant_grpc_port,
            prefer_grpc=settings.rag_qdrant_prefer_grpc,
            api_key=settings.rag_qdrant_api_key,
            https=settings.rag_qdrant_https,
            timeout=settings.rag_qdrant_timeout_sec,
        )
        self._vector_size = vector_size
        self._ensure_collection()

    def upsert_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]) -> list[str]:
        """チャンク埋め込みを Qdrant に保存する。"""
        points: list[models.PointStruct] = []
        point_ids: list[str] = []

        for chunk, embedding in zip(chunks, embeddings, strict=False):
            point_id = self._resolve_point_id(chunk)
            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=self._chunk_to_payload(chunk),
                )
            )
            point_ids.append(str(point_id))

        if points:
            self._client.upsert(collection_name=self._collection_name, points=points)
        return point_ids

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[RetrievedChunk]:
        """クエリ埋め込みに類似するチャンクを Qdrant から検索する。"""
        results = self._client.search(
            collection_name=self._collection_name,
            query_vector=query_embedding,
            limit=top_k,
            with_payload=True,
        )
        return [self._to_retrieved_chunk(result) for result in results]

    def _ensure_collection(self) -> None:
        if self._client.collection_exists(self._collection_name):
            return

        self._client.create_collection(
            collection_name=self._collection_name,
            vectors_config=models.VectorParams(
                size=self._vector_size,
                distance=models.Distance.COSINE,
            ),
        )

    @staticmethod
    def _build_point_id(chunk: Chunk) -> int:
        if chunk.id is None:
            raise ValueError('Chunk ID is required before upserting to Qdrant.')
        return int(chunk.id)

    @staticmethod
    def _resolve_point_id(chunk: Chunk) -> int:
        if chunk.qdrant_point_id:
            return int(chunk.qdrant_point_id)
        return QdrantVectorStore._build_point_id(chunk)

    @staticmethod
    def _chunk_to_payload(chunk: Chunk) -> dict[str, str | int | None]:
        return {
            'chunk_id': chunk.id,
            'upload_file_id': chunk.upload_file_id,
            'raw_text_id': chunk.raw_text_id,
            'chunk_index': chunk.chunk_index,
            'start_offset': chunk.start_offset,
            'end_offset': chunk.end_offset,
            'text': chunk.text,
            'created_at': chunk.created_at.isoformat() if chunk.created_at is not None else None,
        }

    @staticmethod
    def _to_retrieved_chunk(result: models.ScoredPoint) -> RetrievedChunk:
        payload = result.payload or {}
        created_at = QdrantVectorStore._parse_datetime(payload.get('created_at'))
        return RetrievedChunk(
            chunk_id=QdrantVectorStore._as_int(payload.get('chunk_id')),
            upload_file_id=QdrantVectorStore._as_int(payload.get('upload_file_id')),
            raw_text_id=QdrantVectorStore._as_int(payload.get('raw_text_id')),
            chunk_index=QdrantVectorStore._required_int(payload.get('chunk_index')),
            start_offset=QdrantVectorStore._required_int(payload.get('start_offset')),
            end_offset=QdrantVectorStore._required_int(payload.get('end_offset')),
            text=str(payload.get('text') or ''),
            score=float(result.score),
            qdrant_point_id=str(result.id),
            created_at=created_at,
        )

    @staticmethod
    def _parse_datetime(value: object) -> datetime | None:
        if value is None or not isinstance(value, str) or not value:
            return None
        return datetime.fromisoformat(value)

    @staticmethod
    def _as_int(value: object) -> int | None:
        if value is None:
            return None
        return int(value)

    @staticmethod
    def _required_int(value: object) -> int:
        if value is None:
            raise ValueError('Expected integer payload value from Qdrant.')
        return int(value)
