from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.application.auth import AuthenticatedSession, AuthService
from app.core.config import get_settings
from app.domain.errors import NotAuthenticatedError
from app.infrastructure.database import get_session
from app.infrastructure.repositories import SqlRevokedTokenRepository, SqlUserRepository

DbSession = Annotated[Session, Depends(get_session)]

bearer_scheme = HTTPBearer(auto_error=False)


def get_auth_service(session: DbSession) -> AuthService:
    return AuthService(
        users=SqlUserRepository(session),
        revoked_tokens=SqlRevokedTokenRepository(session),
        terms_version=get_settings().terms_version,
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_current_session(
    service: AuthServiceDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> AuthenticatedSession:
    if credentials is None:
        raise NotAuthenticatedError
    return service.authenticate(credentials.credentials)


CurrentSession = Annotated[AuthenticatedSession, Depends(get_current_session)]
