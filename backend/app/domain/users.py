import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Protocol


class Role(StrEnum):
    USER = "user"
    CURATOR = "curator"
    ADMIN = "admin"


def _now() -> datetime:
    return datetime.now(UTC)


@dataclass
class User:
    email: str
    password_hash: str
    role: Role = Role.USER
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)


@dataclass
class Consent:
    user_id: uuid.UUID
    purpose: str
    version: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    granted_at: datetime = field(default_factory=_now)


class UserRepository(Protocol):
    def get_by_id(self, user_id: uuid.UUID) -> User | None: ...

    def get_by_email(self, email: str) -> User | None: ...

    def add(self, user: User, consent: Consent) -> None:
        """Persists the user and the consent given at sign-up in a single transaction."""
        ...


class RevokedTokenRepository(Protocol):
    def revoke(self, jti: str, expires_at: datetime) -> None: ...

    def is_revoked(self, jti: str) -> bool: ...


class LoginAttemptRepository(Protocol):
    def count_failures(self, key: str, since: datetime) -> int: ...

    def record_failure(self, key: str, older_than: datetime) -> None:
        """Records a failed attempt and drops the ones recorded before ``older_than``."""
        ...

    def clear(self, key: str) -> None: ...
