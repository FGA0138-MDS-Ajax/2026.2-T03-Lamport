from fastapi import APIRouter

from app.api.deps import CurrentSession
from app.api.schemas import UserResponse
from app.domain.users import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def read_current_user(session: CurrentSession) -> User:
    return session.user
