from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.application.usecases.create_user import CreateUserUseCase
from src.application.usecases.get_user import GetUserUseCase
from src.presentation.api.schemas.user_request import CreateUserRequest
from src.presentation.api.schemas.user_response import UserResponse
from src.presentation.dependencies import (
    get_create_user_usecase,
    get_db_session,
    get_get_user_usecase,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse)
def create_user(
    request: CreateUserRequest,
    session: Session = Depends(get_db_session),
) -> UserResponse:
    usecase = get_create_user_usecase(session)
    user = usecase.execute(
        name=request.name,
        email=request.email,
    )
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        created_at=user.created_at,
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    session: Session = Depends(get_db_session),
) -> UserResponse:
    usecase = get_get_user_usecase(session)
    user = usecase.execute(user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        created_at=user.created_at,
    )
