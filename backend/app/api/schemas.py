import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domain.checkins import (
    INTENSITY_MAX,
    INTENSITY_MIN,
    QUALITY_MAX,
    QUALITY_MIN,
    Nivel,
    Tag,
)
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
    model_config = ConfigDict(extra="forbid")

    humor: int | None = Field(default=None, strict=True, ge=QUALITY_MIN, le=QUALITY_MAX)
    ansiedade: int | None = Field(default=None, strict=True, ge=INTENSITY_MIN, le=INTENSITY_MAX)
    sono: int | None = Field(default=None, strict=True, ge=QUALITY_MIN, le=QUALITY_MAX)
    sobrecarga: int | None = Field(default=None, strict=True, ge=INTENSITY_MIN, le=INTENSITY_MAX)
    pensamento_risco: bool = Field(strict=True)


class CheckinResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    data: date
    humor: int | None
    ansiedade: int | None
    sono: int | None
    sobrecarga: int | None
    pensamento_risco: bool
    nivel: Nivel
    tags: list[Tag]
