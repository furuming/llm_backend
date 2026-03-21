from sqlalchemy.orm import Session

from src.modules.chat.domain.entities import ChatMessage
from src.modules.chat.infrastructure.models import ChatMessageModel


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, message: ChatMessage) -> ChatMessage:
        row = ChatMessageModel(
            id=message.id,
            user_id=message.user_id,
            role=message.role,
            content=message.content,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)

        return ChatMessage(
            id=row.id,
            user_id=row.user_id,
            role=row.role,
            content=row.content,
            model=message.model,
            created_at=row.created_at,
        )

    def list_by_user_id(self, user_id: str, limit: int = 50) -> list[ChatMessage]:
        rows = (
            self.db.query(ChatMessageModel)
            .filter(ChatMessageModel.user_id == user_id)
            .order_by(ChatMessageModel.id.desc())
            .limit(limit)
            .all()
        )

        return [
            ChatMessage(
                id=row.id,
                user_id=row.user_id,
                role=row.role,
                content=row.content,
                model="hoge",
                created_at=row.created_at,
            )
            for row in reversed(rows)
        ]