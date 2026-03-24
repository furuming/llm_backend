from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository


class CreateUserUseCase:
    def __init__(self, user_repository: UserRepository) -> None:
        """ユーザー永続化を担うリポジトリを受け取る。"""
        self.user_repository = user_repository

    def execute(self, name: str, email: str) -> User:
        """受け取った情報からユーザーを作成して保存する。"""
        user = User(
            id=None,
            name=name,
            email=email,
        )
        return self.user_repository.create(user)