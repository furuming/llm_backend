from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.config import get_settings
from src.core.db import get_db
from src.modules.chat.infrastructure.rag_context_provider import RagContextProvider
from src.modules.chat.infrastructure.repository import ChatRepository
from src.modules.chat.schema import ChatRequest, ChatResponse
from src.modules.chat.usecase.send_message import SendMessageUseCase
from src.shared.kernel.id import ulid_generator
from src.shared.llm.factory import get_llm_client

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    """チャット要求を受け取り、生成された応答を返す。"""
    settings = get_settings()
    repository = ChatRepository(db)
    id_generator = ulid_generator.ULIDGenerator()
    llm_client = get_llm_client(req.model)
    context_provider = RagContextProvider(db)
    usecase = SendMessageUseCase(
        repository=repository,
        id_generator=id_generator,
        llm_client=llm_client,
        context_provider=context_provider,
    )

    resolved_use_rag = req.use_rag if req.use_rag is not None else settings.chat_use_rag_default
    resolved_rag_top_k = req.rag_top_k or settings.chat_rag_top_k_default
    result = usecase.execute(
        user_id=req.user_id,
        message=req.message,
        model=req.model,
        use_rag=resolved_use_rag,
        rag_top_k=resolved_rag_top_k,
    )
    return ChatResponse(
        response=result.reply,
        used_rag=result.used_rag,
        retrieved_chunk_count=result.retrieved_chunk_count,
    )
