from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.modules.rag.api.rag_schema import (
    IndexDocumentRequest,
    IndexDocumentResponse,
    RetrieveChunksRequest,
    RetrieveChunksResponse,
    RetrievedChunkResponse,
)
from src.modules.rag.infrastructure.rag_query_service import build_rag_usecases

router = APIRouter(prefix='/rag', tags=['rag'])


@router.post('/index', response_model=IndexDocumentResponse)
async def index_document(
    req: IndexDocumentRequest = Depends(),
    db: Session = Depends(get_db),
) -> IndexDocumentResponse:
    """アップロードされたファイルを索引化して検索可能にする。"""
    usecases = build_rag_usecases(db)
    content = await req.file.read()
    result = usecases.index_document.execute(
        filename=req.file.filename or 'uploaded_file',
        content=content,
        content_type=req.file.content_type or 'application/octet-stream',
        parse_type=req.parse_type,
        chunk_size=req.chunk_size,
        chunk_overlap=req.chunk_overlap,
    )
    return IndexDocumentResponse(
        upload_file_id=result.upload_file_id,
        raw_text_id=result.raw_text_id,
        chunk_count=result.chunk_count,
    )


@router.post('/retrieve', response_model=RetrieveChunksResponse)
def retrieve_chunks(req: RetrieveChunksRequest, db: Session = Depends(get_db)) -> RetrieveChunksResponse:
    """クエリに関連するチャンクと文脈を取得する。"""
    usecases = build_rag_usecases(db)
    result = usecases.retrieve_chunks.execute(
        query=req.query,
        top_k=req.top_k,
    )
    return RetrieveChunksResponse(
        context=result.context,
        chunks=[
            RetrievedChunkResponse(
                chunk_id=chunk.chunk_id,
                upload_file_id=chunk.upload_file_id,
                raw_text_id=chunk.raw_text_id,
                chunk_index=chunk.chunk_index,
                start_offset=chunk.start_offset,
                end_offset=chunk.end_offset,
                text=chunk.text,
                score=chunk.score,
                qdrant_point_id=chunk.qdrant_point_id,
            )
            for chunk in result.chunks
        ],
    )
