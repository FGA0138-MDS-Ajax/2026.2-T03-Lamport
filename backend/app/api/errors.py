import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.domain.errors import (
    DomainError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    NotAuthenticatedError,
    TermsNotAcceptedError,
)

logger = logging.getLogger(__name__)

_DOMAIN_ERRORS: dict[type[DomainError], tuple[int, str]] = {
    EmailAlreadyRegisteredError: (status.HTTP_409_CONFLICT, "E-mail already registered"),
    TermsNotAcceptedError: (
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "Terms of use must be accepted",
    ),
    InvalidCredentialsError: (status.HTTP_401_UNAUTHORIZED, "Invalid e-mail or password"),
    NotAuthenticatedError: (status.HTTP_401_UNAUTHORIZED, "Not authenticated"),
}


async def _handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
    status_code, detail = _DOMAIN_ERRORS.get(
        type(exc), (status.HTTP_400_BAD_REQUEST, "Invalid request")
    )
    headers = {"WWW-Authenticate": "Bearer"} if isinstance(exc, NotAuthenticatedError) else None
    return JSONResponse({"detail": detail}, status_code=status_code, headers=headers)


async def _handle_database_error(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.exception("Database error on %s %s", request.method, request.url.path)
    return JSONResponse(
        {"detail": "Service temporarily unavailable"},
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, _handle_domain_error)
    app.add_exception_handler(SQLAlchemyError, _handle_database_error)
