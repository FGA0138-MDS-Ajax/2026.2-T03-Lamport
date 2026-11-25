from fastapi import APIRouter, status

from app.api.deps import AuthServiceDep, CurrentSession
from app.api.schemas import UserResponse
from app.domain.users import User

router = APIRouter(prefix="/me", tags=["users"])


@router.get("", response_model=UserResponse)
def read_current_user(session: CurrentSession) -> User:
    return session.user


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user(session: CurrentSession, service: AuthServiceDep) -> None:
    service.delete_account(session.user)
