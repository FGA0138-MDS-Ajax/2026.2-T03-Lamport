import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    MetaData,
    SmallInteger,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.domain.avaliacao import Faixa
from app.domain.checkin import Nivel
from app.domain.users import Role

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(
        Enum(
            Role,
            name="role",
            native_enum=False,
            create_constraint=True,
            length=20,
            values_callable=lambda roles: [role.value for role in roles],
        ),
        server_default=Role.USER.value,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ConsentModel(Base):
    __tablename__ = "consents"
    __table_args__ = (UniqueConstraint("user_id", "purpose", "version"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    purpose: Mapped[str] = mapped_column(String(50))
    version: Mapped[str] = mapped_column(String(20))
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RevokedTokenModel(Base):
    __tablename__ = "revoked_tokens"

    jti: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class LoginAttemptModel(Base):
    __tablename__ = "login_attempts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(64), index=True)
    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )


class CheckinModel(Base):
    __tablename__ = "checkins"
    __table_args__ = (
        UniqueConstraint("user_id", "data"),
        CheckConstraint(
            "humor IS NULL OR (humor >= 1 AND humor <= 5)",
            name="humor_range",
        ),
        CheckConstraint(
            "ansiedade IS NULL OR (ansiedade >= 0 AND ansiedade <= 3)",
            name="ansiedade_range",
        ),
        CheckConstraint(
            "sono IS NULL OR (sono >= 1 AND sono <= 5)",
            name="sono_range",
        ),
        CheckConstraint(
            "sobrecarga IS NULL OR (sobrecarga >= 0 AND sobrecarga <= 3)",
            name="sobrecarga_range",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    data: Mapped[date] = mapped_column(Date, index=True)
    pensamento_risco: Mapped[bool] = mapped_column(Boolean)
    humor: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    ansiedade: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    sono: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    sobrecarga: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    nivel: Mapped[Nivel] = mapped_column(
        Enum(
            Nivel,
            name="nivel",
            native_enum=False,
            create_constraint=True,
            length=20,
            values_callable=lambda niveis: [n.value for n in niveis],
        ),
    )
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(30)), server_default="{}")
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# Alias CheckinDiarioModel conforme Arquitetura (Figura 6) e Issue #4
CheckinDiarioModel = CheckinModel


class MaterialModel(Base):
    __tablename__ = "materiais"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    titulo: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(500))
    fonte: Mapped[str] = mapped_column(String(100))
    resumo: Mapped[str] = mapped_column(String(500))
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(30)))
    ativo: Mapped[bool] = mapped_column(Boolean, server_default="true")
    revisado_em: Mapped[date] = mapped_column(Date)


class AvaliacaoModel(Base):
    __tablename__ = "avaliacoes"
    __table_args__ = (
        CheckConstraint(
            "escore_phq9 >= 0 AND escore_phq9 <= 27",
            name="escore_phq9_range",
        ),
        CheckConstraint(
            "escore_gad7 >= 0 AND escore_gad7 <= 21",
            name="escore_gad7_range",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    respostas_phq9: Mapped[list[int]] = mapped_column(ARRAY(SmallInteger))
    respostas_gad7: Mapped[list[int]] = mapped_column(ARRAY(SmallInteger))
    escore_phq9: Mapped[int] = mapped_column(SmallInteger)
    escore_gad7: Mapped[int] = mapped_column(SmallInteger)
    faixa_phq9: Mapped[Faixa] = mapped_column(
        Enum(
            Faixa,
            name="faixa_phq9",
            native_enum=False,
            create_constraint=True,
            length=30,
            values_callable=lambda faixas: [f.value for f in faixas],
        ),
    )
    faixa_gad7: Mapped[Faixa] = mapped_column(
        Enum(
            Faixa,
            name="faixa_gad7",
            native_enum=False,
            create_constraint=True,
            length=30,
            values_callable=lambda faixas: [f.value for f in faixas],
        ),
    )
    nivel: Mapped[Nivel] = mapped_column(
        Enum(
            Nivel,
            name="nivel",
            native_enum=False,
            create_constraint=True,
            length=20,
            values_callable=lambda niveis: [n.value for n in niveis],
        ),
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    @property
    def usuario_id(self) -> uuid.UUID:
        return self.user_id


class RecomendacaoModel(Base):
    __tablename__ = "recomendacoes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    material_id: Mapped[int] = mapped_column(ForeignKey("materiais.id"), index=True)
    checkin_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("checkins.id", ondelete="CASCADE"), nullable=True, index=True
    )
    avaliacao_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("avaliacoes.id", ondelete="CASCADE"), nullable=True, index=True
    )
    regra: Mapped[str] = mapped_column(String(20))
    motivo: Mapped[str] = mapped_column(String(500))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    @property
    def usuario_id(self) -> uuid.UUID:
        return self.user_id
