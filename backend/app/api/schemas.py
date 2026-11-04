import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domain.checkin import Nivel, Tag
from app.domain.users import Role


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    accept_terms: bool


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    role: Role
    created_at: datetime


class TermsResponse(BaseModel):
    version: str


class CheckinCreate(BaseModel):
    """Respostas do check-in com os identificadores da API (Arquitetura, Quadro 6)."""

    model_config = ConfigDict(extra="forbid")

    p1: int | None = Field(default=None, strict=True, ge=1, le=5)
    p2: int | None = Field(default=None, strict=True, ge=0, le=3)
    p3: int | None = Field(default=None, strict=True, ge=1, le=5)
    p4: int | None = Field(default=None, strict=True, ge=0, le=3)
    p5: bool = Field(strict=True)


class CheckinCreatedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nivel: Nivel
    tags: list[Tag]


class CheckinTodayResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    p1: int | None = Field(validation_alias="humor")
    p2: int | None = Field(validation_alias="ansiedade")
    p3: int | None = Field(validation_alias="sono")
    p4: int | None = Field(validation_alias="sobrecarga")
    p5: bool = Field(validation_alias="pensamento_risco")
    nivel: Nivel
    tags: list[Tag]
