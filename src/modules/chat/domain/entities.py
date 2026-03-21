from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ChatMessage:
    id: Optional[str]
    user_id: str
    role: str
    content: str
    model: str
    created_at: Optional[datetime] = None