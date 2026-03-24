from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository


class GetUserUseCase:
    def __init__(self, user_repository: UserRepository) -> None:
        """ユーザー取得に利用するリポジトリを受け取る。"""
        self.user_repository = user_repository

    def execute(self, user_id: int) -> User | None:
        """ユーザー ID に対応するユーザーを取得する。"""
        return self.user_repository.find_by_id(user_id)
