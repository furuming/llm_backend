from collections.abc import Generator

from sqlalchemy.orm import Session

from src.application.usecases.create_user import CreateUserUseCase
from src.application.usecases.get_user import GetUserUseCase
from src.core.db import SessionLocal
from src.infrastructure.repositories.sqlalchemy_user_repository import (
    SqlAlchemyUserRepository,
)


def get_db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_create_user_usecase(session: Session) -> CreateUserUseCase:
    repo = SqlAlchemyUserRepository(session)
    return CreateUserUseCase(repo)


def get_get_user_usecase(session: Session) -> GetUserUseCase:
    repo = SqlAlchemyUserRepository(session)
    return GetUserUseCase(repo)