from typing import Protocol

from src.domain.entities.user import User


class UserRepository(Protocol):
    def create(self, user: User) -> User:
        """ユーザーを永続化して保存後の値を返す。"""
        ...

    def find_by_id(self, user_id: int) -> User | None:
        """ユーザー ID に一致するユーザーを返す。"""
        ...