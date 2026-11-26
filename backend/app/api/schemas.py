import uuid
from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domain.avaliacao import Faixa
from app.domain.checkin import Nivel, Tag


class RegisterRequest(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)
    aceite_termos: bool
    maior_de_idade: bool


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    criado_em: datetime = Field(validation_alias="created_at")


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


class RecomendacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    titulo: str
    fonte: str
    resumo: str
    url: str
    regra: str
    motivo: str


class CheckinCreatedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nivel: Nivel
    tags: list[Tag]
    recomendacoes: list[RecomendacaoResponse] = Field(default_factory=list)


class CheckinTodayResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    p1: int | None = Field(validation_alias="humor")
    p2: int | None = Field(validation_alias="ansiedade")
    p3: int | None = Field(validation_alias="sono")
    p4: int | None = Field(validation_alias="sobrecarga")
    p5: bool = Field(validation_alias="pensamento_risco")
    nivel: Nivel
    tags: list[Tag]
    recomendacoes: list[RecomendacaoResponse] = Field(default_factory=list)


class CheckinItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    data: date
    p1: int | None = Field(default=None, validation_alias="humor")
    p2: int | None = Field(default=None, validation_alias="ansiedade")
    p3: int | None = Field(default=None, validation_alias="sono")
    p4: int | None = Field(default=None, validation_alias="sobrecarga")
    p5: bool = Field(validation_alias="pensamento_risco")
    nivel: Nivel
    tags: list[Tag]


CheckinResponse = CheckinItemResponse

RespostaItemAvaliacao = Annotated[int, Field(strict=True, ge=0, le=3)]


class AvaliacaoCreate(BaseModel):
    """Respostas da avaliação quinzenal PHQ-9 e GAD-7 (Arquitetura, Quadro 6)."""

    model_config = ConfigDict(extra="forbid")

    phq9: list[RespostaItemAvaliacao] = Field(min_length=9, max_length=9)
    gad7: list[RespostaItemAvaliacao] = Field(min_length=7, max_length=7)


class AvaliacaoCreatedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    escore_phq9: int
    escore_gad7: int
    faixa_phq9: Faixa
    faixa_gad7: Faixa
    nivel: Nivel
    orientacao: str
    recomendacoes: list[RecomendacaoResponse] = Field(default_factory=list)


class AvaliacaoItemResponse(BaseModel):
    """Item do histórico de avaliações (Arquitetura, Quadro 6: GET /api/avaliacoes)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    data: date
    escore_phq9: int
    escore_gad7: int
    faixa_phq9: Faixa
    faixa_gad7: Faixa
    nivel: Nivel


# DP-3: GET /api/avaliacoes/{id} devolve os mesmos campos de POST /api/avaliacoes.
AvaliacaoDetailResponse = AvaliacaoCreatedResponse
