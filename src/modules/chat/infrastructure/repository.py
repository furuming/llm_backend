from sqlalchemy.orm import Session

from src.modules.chat.domain.entities import ChatMessage, ChatProject, ChatRoom
from src.modules.chat.infrastructure.models import ChatMessageModel, ChatProjectModel, ChatRoomModel


class ChatRepository:
    def __init__(self, db: Session):
        """初期化時に使用する DB セッションを保持する。"""
        self.db = db

    def create_project(self, project: ChatProject) -> ChatProject:
        row = ChatProjectModel(
            id=project.id,
            user_id=project.user_id,
            name=project.name,
            description=project.description,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return ChatProject(
            id=row.id,
            user_id=row.user_id,
            name=row.name,
            description=row.description,
            created_at=row.created_at,
        )

    def list_projects_by_user_id(self, user_id: str) -> list[ChatProject]:
        rows = (
            self.db.query(ChatProjectModel)
            .filter(ChatProjectModel.user_id == user_id)
            .order_by(ChatProjectModel.created_at.desc())
            .all()
        )
        return [
            ChatProject(
                id=row.id,
                user_id=row.user_id,
                name=row.name,
                description=row.description,
                created_at=row.created_at,
            )
            for row in rows
        ]

    def get_project(self, project_id: str) -> ChatProject | None:
        row = self.db.query(ChatProjectModel).filter(ChatProjectModel.id == project_id).first()
        if row is None:
            return None
        return ChatProject(
            id=row.id,
            user_id=row.user_id,
            name=row.name,
            description=row.description,
            created_at=row.created_at,
        )

    def create_room(self, room: ChatRoom) -> ChatRoom:
        row = ChatRoomModel(
            id=room.id,
            project_id=room.project_id,
            user_id=room.user_id,
            name=room.name,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return ChatRoom(
            id=row.id,
            project_id=row.project_id,
            user_id=row.user_id,
            name=row.name,
            created_at=row.created_at,
        )

    def list_rooms_by_project_id(self, project_id: str) -> list[ChatRoom]:
        rows = (
            self.db.query(ChatRoomModel)
            .filter(ChatRoomModel.project_id == project_id)
            .order_by(ChatRoomModel.created_at.desc())
            .all()
        )
        return [
            ChatRoom(
                id=row.id,
                project_id=row.project_id,
                user_id=row.user_id,
                name=row.name,
                created_at=row.created_at,
            )
            for row in rows
        ]

    def get_room(self, room_id: str) -> ChatRoom | None:
        row = self.db.query(ChatRoomModel).filter(ChatRoomModel.id == room_id).first()
        if row is None:
            return None
        return ChatRoom(
            id=row.id,
            project_id=row.project_id,
            user_id=row.user_id,
            name=row.name,
            created_at=row.created_at,
        )

    def save(self, message: ChatMessage) -> ChatMessage:
        """チャットメッセージを永続化し、保存結果をドメインモデルで返す。"""
        row = ChatMessageModel(
            id=message.id,
            user_id=message.user_id,
            room_id=message.room_id,
            role=message.role,
            content=message.content,
            model=message.model,
            used_rag=message.used_rag,
            retrieved_chunk_count=message.retrieved_chunk_count,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)

        return ChatMessage(
            id=row.id,
            user_id=row.user_id,
            room_id=row.room_id,
            role=row.role,
            content=row.content,
            model=row.model,
            used_rag=row.used_rag,
            retrieved_chunk_count=row.retrieved_chunk_count,
            created_at=row.created_at,
        )

    def list_by_user_id(self, user_id: str, limit: int = 50) -> list[ChatMessage]:
        """指定ユーザーのメッセージ履歴を古い順で取得する。"""
        rows = (
            self.db.query(ChatMessageModel)
            .filter(ChatMessageModel.user_id == user_id)
            .order_by(ChatMessageModel.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
            ChatMessage(
                id=row.id,
                user_id=row.user_id,
                room_id=row.room_id,
                role=row.role,
                content=row.content,
                model=row.model,
                used_rag=row.used_rag,
                retrieved_chunk_count=row.retrieved_chunk_count,
                created_at=row.created_at,
            )
            for row in reversed(rows)
        ]

    def list_by_room_id(self, room_id: str, limit: int = 50) -> list[ChatMessage]:
        rows = (
            self.db.query(ChatMessageModel)
            .filter(ChatMessageModel.room_id == room_id)
            .order_by(ChatMessageModel.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            ChatMessage(
                id=row.id,
                user_id=row.user_id,
                room_id=row.room_id,
                role=row.role,
                content=row.content,
                model=row.model,
                used_rag=row.used_rag,
                retrieved_chunk_count=row.retrieved_chunk_count,
                created_at=row.created_at,
            )
            for row in reversed(rows)
        ]
