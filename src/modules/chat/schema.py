# modules/chat/schema.py
from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_id: str
    message: str
    model: str

class ChatResponse(BaseModel):
    response: str
