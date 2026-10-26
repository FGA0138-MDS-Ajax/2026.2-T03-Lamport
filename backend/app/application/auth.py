import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.core.security import (
    InvalidTokenError,
    TokenClaims,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.domain.errors import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    NotAuthenticatedError,
    TermsNotAcceptedError,
    TooManyLoginAttemptsError,
)
from app.domain.users import (
    Consent,
    LoginAttemptRepository,
    RevokedTokenRepository,
    User,
    UserRepository,
)

TERMS_PURPOSE = "terms_of_use"

# Verified against when the e-mail is unknown, so the response time does not reveal
# whether an account exists.
_DUMMY_HASH = hash_password("dummy-password")


@dataclass(frozen=True)
class AccessToken:
    value: str
    expires_in: int


@dataclass(frozen=True)
class AuthenticatedSession:
    user: User
    claims: TokenClaims


def normalize_email(email: str) -> str:
    return email.strip().lower()


def _attempt_key(email: str) -> str:
    # Failed attempts are tracked by a digest so typed e-mails of non-users are not stored.
    return hashlib.sha256(email.encode()).hexdigest()


@dataclass(frozen=True)
class LoginThrottle:
    max_attempts: int
    window: timedelta


class AuthService:
    def __init__(
        self,
        users: UserRepository,
        revoked_tokens: RevokedTokenRepository,
        login_attempts: LoginAttemptRepository,
        terms_version: str,
        throttle: LoginThrottle,
    ) -> None:
        self.users = users
        self.revoked_tokens = revoked_tokens
        self.login_attempts = login_attempts
        self.terms_version = terms_version
        self.throttle = throttle

    def register(self, email: str, password: str, accepted_terms: bool) -> User:
        if not accepted_terms:
            raise TermsNotAcceptedError
        email = normalize_email(email)
        if self.users.get_by_email(email) is not None:
            raise EmailAlreadyRegisteredError

        user = User(email=email, password_hash=hash_password(password))
        consent = Consent(user_id=user.id, purpose=TERMS_PURPOSE, version=self.terms_version)
        self.users.add(user, consent)
        return user

    def login(self, email: str, password: str) -> AccessToken:
        email = normalize_email(email)
        key = _attempt_key(email)
        window_start = datetime.now(UTC) - self.throttle.window
        # Unknown e-mails are throttled too, so a lockout does not reveal whether an account exists.
        if self.login_attempts.count_failures(key, window_start) >= self.throttle.max_attempts:
            raise TooManyLoginAttemptsError

        user = self.users.get_by_email(email)
        if user is None:
            verify_password(password, _DUMMY_HASH)
            valid = False
        else:
            valid = verify_password(password, user.password_hash)
        if not valid:
            self.login_attempts.record_failure(key, older_than=window_start)
            raise InvalidCredentialsError

        self.login_attempts.clear(key)
        value, expires_in = create_access_token(user.id)
        return AccessToken(value=value, expires_in=expires_in)

    def authenticate(self, token: str) -> AuthenticatedSession:
        try:
            claims = decode_access_token(token)
        except InvalidTokenError:
            raise NotAuthenticatedError from None
        if self.revoked_tokens.is_revoked(claims.jti):
            raise NotAuthenticatedError

        user = self.users.get_by_id(claims.subject)
        if user is None:
            raise NotAuthenticatedError
        return AuthenticatedSession(user=user, claims=claims)

    def logout(self, session: AuthenticatedSession) -> None:
        self.revoked_tokens.revoke(session.claims.jti, session.claims.expires_at)
