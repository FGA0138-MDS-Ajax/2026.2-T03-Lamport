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

from app.domain.checkin import Nivel
from app.domain.users import Role

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# 1. A Base DEVE vir primeiro que todos os models
class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# 2. Só depois vêm os models herdando de Base
class MaterialModel(Base):
    __tablename__ = "materiais"

    slug: Mapped[str] = mapped_column(String(100), primary_key=True)
    titulo: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(500))
    fonte: Mapped[str] = mapped_column(String(100))
    resumo: Mapped[str] = mapped_column(String(500))
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(30)))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    revisado_em: Mapped[date] = mapped_column(Date)