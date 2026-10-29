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


class CheckinResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    data: date
    pensamento_risco: bool
    humor: int | None = None
    ansiedade: int | None = None
    sono: int | None = None
    sobrecarga: int | None = None
    nivel: Nivel = Nivel.AUTOCUIDADO
    tags: list[Tag] = Field(default_factory=list)
    criado_em: datetime


class CheckinPaginationResponse(BaseModel):
    items: list[CheckinResponse]
    total: int
    limit: int
    offset: int
