from datetime import timedelta
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.application.auth import AuthenticatedSession, AuthService, LoginThrottle
from app.application.checkins import CheckinService
from app.core.config import get_settings
from app.domain.errors import NotAuthenticatedError
from app.infrastructure.database import get_session
from app.infrastructure.repositories import (
    SqlCheckinRepository,
    SqlLoginAttemptRepository,
    SqlRevokedTokenRepository,
    SqlUserRepository,
)

DbSession = Annotated[Session, Depends(get_session)]

bearer_scheme = HTTPBearer(auto_error=False)


def get_auth_service(session: DbSession) -> AuthService:
    settings = get_settings()
    return AuthService(
        users=SqlUserRepository(session),
        revoked_tokens=SqlRevokedTokenRepository(session),
        login_attempts=SqlLoginAttemptRepository(session),
        terms_version=settings.terms_version,
        throttle=LoginThrottle(
            max_attempts=settings.login_max_attempts,
            window=timedelta(minutes=settings.login_lockout_minutes),
        ),
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_checkin_service(session: DbSession) -> CheckinService:
    return CheckinService(checkins=SqlCheckinRepository(session))


CheckinServiceDep = Annotated[CheckinService, Depends(get_checkin_service)]


def get_current_session(
    service: AuthServiceDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> AuthenticatedSession:
    if credentials is None:
        raise NotAuthenticatedError
    return service.authenticate(credentials.credentials)


CurrentSession = Annotated[AuthenticatedSession, Depends(get_current_session)]
