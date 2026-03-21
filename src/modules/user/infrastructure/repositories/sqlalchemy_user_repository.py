from sqlalchemy.orm import Session

from src.domain.entities.user import User
from src.infrastructure.db.models.user_model import UserModel


class SqlAlchemyUserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, user: User) -> User:
        db_user = UserModel(
            name=user.name,
            email=user.email,
        )
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)

        return User(
            id=db_user.id,
            name=db_user.name,
            email=db_user.email,
            created_at=db_user.created_at,
        )

    def find_by_id(self, user_id: int) -> User | None:
        db_user = self.session.get(UserModel, user_id)
        if db_user is None:
            return None

        return User(
            id=db_user.id,
            name=db_user.name,
            email=db_user.email,
            created_at=db_user.created_at,
        )
