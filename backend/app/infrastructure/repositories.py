import uuid
from datetime import date, datetime

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.checkin import Checkin, Nivel, Tag
from app.domain.errors import CheckinAlreadyExistsError, EmailAlreadyRegisteredError
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


def _to_checkin(model: CheckinModel) -> Checkin:
    return Checkin(
        id=model.id,
        user_id=model.user_id,
        data=model.data,
        pensamento_risco=model.pensamento_risco,
        humor=model.humor,
        ansiedade=model.ansiedade,
        sono=model.sono,
        sobrecarga=model.sobrecarga,
        nivel=Nivel(model.nivel) if isinstance(model.nivel, str) else model.nivel,
        tags=[Tag(t) for t in model.tags] if model.tags else [],
        criado_em=model.criado_em,
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

    def add(self, checkin: Checkin) -> None:
        model = CheckinModel(
            id=checkin.id,
            user_id=checkin.user_id,
            data=checkin.data,
            pensamento_risco=checkin.pensamento_risco,
            humor=checkin.humor,
            ansiedade=checkin.ansiedade,
            sono=checkin.sono,
            sobrecarga=checkin.sobrecarga,
            nivel=checkin.nivel,
            tags=[t.value if isinstance(t, Tag) else t for t in checkin.tags],
            criado_em=checkin.criado_em,
        )
        self.session.add(model)
        try:
            self.session.flush()
        except IntegrityError as exc:
            self.session.rollback()
            orig_msg = str(exc.orig).lower()
            if (
                "uq_checkins_user_id_data" in orig_msg
                or "checkins.user_id, checkins.data" in orig_msg
            ):
                raise CheckinAlreadyExistsError from exc
            raise
        self.session.commit()

    def get_by_id_for_user(self, checkin_id: uuid.UUID, user_id: uuid.UUID) -> Checkin | None:
        model = self.session.scalar(
            select(CheckinModel).where(
                CheckinModel.id == checkin_id,
                CheckinModel.user_id == user_id,
            )
        )
        return _to_checkin(model) if model else None

    def get_by_user_and_date(self, user_id: uuid.UUID, data: date) -> Checkin | None:
        model = self.session.scalar(
            select(CheckinModel).where(
                CheckinModel.user_id == user_id,
                CheckinModel.data == data,
            )
        )
        return _to_checkin(model) if model else None

    def list_by_user(
        self,
        user_id: uuid.UUID,
        limit: int = 20,
        offset: int = 0,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> tuple[list[Checkin], int]:
        filters = [CheckinModel.user_id == user_id]
        if from_date is not None:
            filters.append(CheckinModel.data >= from_date)
        if to_date is not None:
            filters.append(CheckinModel.data <= to_date)

        count_query = select(func.count()).select_from(CheckinModel).where(*filters)
        total = self.session.scalar(count_query) or 0

        items_query = (
            select(CheckinModel)
            .where(*filters)
            .order_by(CheckinModel.data.desc(), CheckinModel.criado_em.desc())
            .offset(offset)
            .limit(limit)
        )
        models = self.session.scalars(items_query).all()
        return [_to_checkin(m) for m in models], total
