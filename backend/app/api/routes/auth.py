from fastapi import APIRouter, status

from app.api.deps import AuthServiceDep, CurrentSession
from app.api.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.domain.users import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def register(payload: RegisterRequest, service: AuthServiceDep) -> User:
    return service.register(payload.email, payload.password, payload.accept_terms)


@router.post("/login")
def login(payload: LoginRequest, service: AuthServiceDep) -> TokenResponse:
    token = service.login(payload.email, payload.password)
    return TokenResponse(access_token=token.value, expires_in=token.expires_in)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(session: CurrentSession, service: AuthServiceDep) -> None:
    service.logout(session)
