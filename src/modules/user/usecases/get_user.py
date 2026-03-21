from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository


class GetUserUseCase:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def execute(self, user_id: int) -> User | None:
        return self.user_repository.find_by_id(user_id)
