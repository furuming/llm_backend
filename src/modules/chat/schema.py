from datetime import datetime

from pydantic import BaseModel, Field


class CreateProjectRequest(BaseModel):
    user_id: str
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class ProjectResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: str | None = None
    created_at: datetime


class CreateRoomRequest(BaseModel):
    user_id: str
    project_id: str
    name: str = Field(min_length=1, max_length=255)


class RoomResponse(BaseModel):
    id: str
    project_id: str
    user_id: str
    name: str
    created_at: datetime


class ChatRequest(BaseModel):
    user_id: str
    room_id: str | None = None
    message: str
    model: str = Field(description='LLM family name such as gemma, llama, or gpt-4o-mini')
    use_rag: bool | None = None
    rag_top_k: int | None = Field(default=None, ge=1, le=20)


class ChatResponse(BaseModel):
    response: str
    used_rag: bool
    retrieved_chunk_count: int
    room_id: str | None = None


class MessageResponse(BaseModel):
    id: str
    user_id: str
    room_id: str | None = None
    role: str
    content: str
    model: str
    used_rag: bool
    retrieved_chunk_count: int
    created_at: datetime
