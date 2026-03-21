from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository


class CreateUserUseCase:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def execute(self, name: str, email: str) -> User:
        user = User(
            id=None,
            name=name,
            email=email,
        )
        return self.user_repository.create(user)