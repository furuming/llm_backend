from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ChatProject:
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class ChatRoom:
    id: str
    project_id: str
    user_id: str
    name: str
    created_at: Optional[datetime] = None


@dataclass
class ChatMessage:
    id: Optional[str]
    user_id: str
    room_id: Optional[str]
    role: str
    content: str
    model: str
    created_at: Optional[datetime] = None
