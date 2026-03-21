from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.modules.chat.schema import ChatRequest, ChatResponse
from src.modules.chat.infrastructure.repository import ChatRepository
from src.modules.chat.usecase.send_message import SendMessageUseCase
from src.shared.kernel.id import ulid_generator

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):

    print(req)

    repository = ChatRepository(db)
    id_generator = ulid_generator.ULIDGenerator()
    usecase = SendMessageUseCase(repository, id_generator)

    result = usecase.execute(
        user_id=req.user_id,
        message=req.message,
        model=req.model,
    )
    return ChatResponse(response=result)
