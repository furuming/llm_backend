from typing import Protocol

from src.domain.entities.user import User


class UserRepository(Protocol):
    def create(self, user: User) -> User:
        ...

    def find_by_id(self, user_id: int) -> User | None:
        ...