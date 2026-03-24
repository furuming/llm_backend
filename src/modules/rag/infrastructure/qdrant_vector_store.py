from dataclasses import dataclass

from src.modules.rag.models.chunk import Chunk
from src.modules.rag.models.retrieved_chunk import RetrievedChunk
from src.modules.rag.repositories.vector_store_repository import VectorStoreRepository
from src.shared.kernel.id.ulid import new_ulid


@dataclass
class _StoredVector:
    point_id: str
    embedding: list[float]
    chunk: Chunk


class QdrantVectorStore(VectorStoreRepository):
    """Qdrant 風のインターフェースを持つインメモリ実装。"""

    _store: dict[str, _StoredVector] = {}

    def upsert_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]) -> list[str]:
        """チャンク埋め込みをインメモリで保存する。"""
        point_ids: list[str] = []
        for chunk, embedding in zip(chunks, embeddings, strict=False):
            point_id = chunk.qdrant_point_id or new_ulid()
            self._store[point_id] = _StoredVector(
                point_id=point_id,
                embedding=embedding,
                chunk=chunk,
            )
            point_ids.append(point_id)
        return point_ids

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[RetrievedChunk]:
        """コサイン類似度に近い計算で上位チャンクを返す。"""
        scored: list[tuple[float, _StoredVector]] = []
        for stored in self._store.values():
            score = sum(a * b for a, b in zip(query_embedding, stored.embedding, strict=False))
            scored.append((score, stored))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            RetrievedChunk(
                chunk_id=item.chunk.id,
                upload_file_id=item.chunk.upload_file_id,
                raw_text_id=item.chunk.raw_text_id,
                chunk_index=item.chunk.chunk_index,
                start_offset=item.chunk.start_offset,
                end_offset=item.chunk.end_offset,
                text=item.chunk.text,
                score=score,
                qdrant_point_id=item.point_id,
                created_at=item.chunk.created_at,
            )
            for score, item in scored[:top_k]
        ]
