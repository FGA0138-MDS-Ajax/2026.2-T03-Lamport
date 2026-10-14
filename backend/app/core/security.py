import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings

ALGORITHM = "HS256"

password_hash = PasswordHash.recommended()


class InvalidTokenError(Exception):
    pass


@dataclass(frozen=True)
class TokenClaims:
    subject: uuid.UUID
    jti: str
    expires_at: datetime


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_access_token(subject: uuid.UUID) -> tuple[str, int]:
    settings = get_settings()
    expires_in = settings.access_token_expire_minutes * 60
    now = datetime.now(UTC)
    payload = {
        "sub": str(subject),
        "jti": uuid.uuid4().hex,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM), expires_in


def decode_access_token(token: str) -> TokenClaims:
    try:
        payload = jwt.decode(
            token,
            get_settings().secret_key,
            algorithms=[ALGORITHM],
            options={"require": ["sub", "jti", "exp"]},
        )
        return TokenClaims(
            subject=uuid.UUID(payload["sub"]),
            jti=payload["jti"],
            expires_at=datetime.fromtimestamp(payload["exp"], UTC),
        )
    except (jwt.PyJWTError, ValueError) as exc:
        raise InvalidTokenError from exc
