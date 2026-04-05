from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.core.config import get_settings
from src.core.db import get_db
from src.modules.chat.domain.entities import ChatProject, ChatRoom
from src.modules.chat.infrastructure.rag_context_provider import RagContextProvider
from src.modules.chat.infrastructure.repository import ChatRepository
from src.modules.chat.schema import (
    ChatRequest,
    ChatResponse,
    CreateProjectRequest,
    CreateRoomRequest,
    MessageResponse,
    ProjectResponse,
    RoomResponse,
)
from src.modules.chat.usecase.send_message import SendMessageUseCase
from src.shared.kernel.id import ulid_generator
from src.shared.llm.factory import get_llm_client

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/projects", response_model=ProjectResponse)
def create_project(req: CreateProjectRequest, db: Session = Depends(get_db)):
    repository = ChatRepository(db)
    id_generator = ulid_generator.ULIDGenerator()
    project = repository.create_project(
        ChatProject(
            id=id_generator.generate(),
            user_id=req.user_id,
            name=req.name,
            description=req.description,
        )
    )
    return ProjectResponse(
        id=project.id,
        user_id=project.user_id,
        name=project.name,
        description=project.description,
        created_at=project.created_at,
    )


@router.get("/projects", response_model=list[ProjectResponse])
def list_projects(user_id: str = Query(...), db: Session = Depends(get_db)):
    repository = ChatRepository(db)
    projects = repository.list_projects_by_user_id(user_id)
    return [
        ProjectResponse(
            id=project.id,
            user_id=project.user_id,
            name=project.name,
            description=project.description,
            created_at=project.created_at,
        )
        for project in projects
    ]


@router.post("/rooms", response_model=RoomResponse)
def create_room(req: CreateRoomRequest, db: Session = Depends(get_db)):
    repository = ChatRepository(db)
    project = repository.get_project(req.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != req.user_id:
        raise HTTPException(status_code=400, detail="Project does not belong to the user")

    id_generator = ulid_generator.ULIDGenerator()
    room = repository.create_room(
        ChatRoom(
            id=id_generator.generate(),
            project_id=req.project_id,
            user_id=req.user_id,
            name=req.name,
        )
    )
    return RoomResponse(
        id=room.id,
        project_id=room.project_id,
        user_id=room.user_id,
        name=room.name,
        created_at=room.created_at,
    )


@router.get("/rooms", response_model=list[RoomResponse])
def list_rooms(project_id: str = Query(...), db: Session = Depends(get_db)):
    repository = ChatRepository(db)
    rooms = repository.list_rooms_by_project_id(project_id)
    return [
        RoomResponse(
            id=room.id,
            project_id=room.project_id,
            user_id=room.user_id,
            name=room.name,
            created_at=room.created_at,
        )
        for room in rooms
    ]


@router.get("/rooms/{room_id}/messages", response_model=list[MessageResponse])
def list_room_messages(
    room_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    repository = ChatRepository(db)
    room = repository.get_room(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    messages = repository.list_by_room_id(room_id=room_id, limit=limit)
    return [
        MessageResponse(
            id=message.id,
            user_id=message.user_id,
            room_id=message.room_id,
            role=message.role,
            content=message.content,
            model=message.model,
            used_rag=message.used_rag,
            retrieved_chunk_count=message.retrieved_chunk_count,
            created_at=message.created_at,
        )
        for message in messages
    ]


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    """チャット要求を受け取り、生成された応答を返す。"""
    settings = get_settings()
    repository = ChatRepository(db)
    if req.room_id is not None:
        room = repository.get_room(req.room_id)
        if room is None:
            raise HTTPException(status_code=404, detail="Room not found")
        if room.user_id != req.user_id:
            raise HTTPException(status_code=400, detail="Room does not belong to the user")

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
        room_id=req.room_id,
        message=req.message,
        model=req.model,
        use_rag=resolved_use_rag,
        rag_top_k=resolved_rag_top_k,
    )
    return ChatResponse(
        response=result.reply,
        used_rag=result.used_rag,
        retrieved_chunk_count=result.retrieved_chunk_count,
        room_id=result.room_id,
    )
