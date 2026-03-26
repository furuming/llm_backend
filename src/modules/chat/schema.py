from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    user_id: str
    message: str
    model: str
    use_rag: bool | None = None
    rag_top_k: int | None = Field(default=None, ge=1, le=20)


class ChatResponse(BaseModel):
    response: str
    used_rag: bool
    retrieved_chunk_count: int
