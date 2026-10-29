import uuid
from datetime import date, datetime

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.checkins import Checkin
from app.domain.errors import CheckinAlreadyDoneError, EmailAlreadyRegisteredError
from app.domain.users import Consent, User
from app.infrastructure.models import (
    CheckinModel,
    ConsentModel,
    LoginAttemptModel,
    RevokedTokenModel,
    UserModel,
)


def _to_user(model: UserModel) -> User:
    return User(
        id=model.id,
        email=model.email,
        password_hash=model.password_hash,
        role=model.role,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlUserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        model = self.session.get(UserModel, user_id)
        return _to_user(model) if model else None

    def get_by_email(self, email: str) -> User | None:
        model = self.session.scalar(select(UserModel).where(UserModel.email == email))
        return _to_user(model) if model else None

    def add(self, user: User, consent: Consent) -> None:
        self.session.add(
            UserModel(
                id=user.id,
                email=user.email,
                password_hash=user.password_hash,
                role=user.role,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
        )
        try:
            self.session.flush()
        except IntegrityError as exc:
            self.session.rollback()
            # Two concurrent sign-ups with the same e-mail can both pass the service check.
            if "uq_users_email" in str(exc.orig):
                raise EmailAlreadyRegisteredError from exc
            raise

        self.session.add(
            ConsentModel(
                id=consent.id,
                user_id=consent.user_id,
                purpose=consent.purpose,
                version=consent.version,
                granted_at=consent.granted_at,
            )
        )
        self.session.commit()


class SqlRevokedTokenRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def revoke(self, jti: str, expires_at: datetime) -> None:
        self.session.execute(
            delete(RevokedTokenModel).where(RevokedTokenModel.expires_at < func.now())
        )
        self.session.execute(
            insert(RevokedTokenModel)
            .values(jti=jti, expires_at=expires_at)
            .on_conflict_do_nothing(index_elements=["jti"])
        )
        self.session.commit()

    def is_revoked(self, jti: str) -> bool:
        return self.session.get(RevokedTokenModel, jti) is not None


class SqlLoginAttemptRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def count_failures(self, key: str, since: datetime) -> int:
        return self.session.scalar(
            select(func.count())
            .select_from(LoginAttemptModel)
            .where(LoginAttemptModel.key == key, LoginAttemptModel.attempted_at >= since)
        )

    def record_failure(self, key: str, older_than: datetime) -> None:
        self.session.execute(
            delete(LoginAttemptModel).where(LoginAttemptModel.attempted_at < older_than)
        )
        self.session.add(LoginAttemptModel(key=key))
        self.session.commit()

    def clear(self, key: str) -> None:
        self.session.execute(delete(LoginAttemptModel).where(LoginAttemptModel.key == key))
        self.session.commit()

class SqlCheckinRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def exists_for_date(self, user_id: uuid.UUID, data: date) -> bool:
        return (
            self.session.scalar(
                select(CheckinModel.id).where(
                    CheckinModel.user_id == user_id, CheckinModel.data == data
                )
            )
            is not None
        )

    def add(self, checkin: Checkin) -> None:
        self.session.add(
            CheckinModel(
                id=checkin.id,
                user_id=checkin.user_id,
                data=checkin.data,
                humor=checkin.humor,
                ansiedade=checkin.ansiedade,
                sono=checkin.sono,
                sobrecarga=checkin.sobrecarga,
                pensamento_risco=checkin.pensamento_risco,
                nivel=checkin.nivel.value,
                tags=[tag.value for tag in checkin.tags],
                created_at=checkin.created_at,
            )
        )
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            if "uq_checkins_user_id_data" in str(exc.orig):
                raise CheckinAlreadyDoneError from exc
            raise
