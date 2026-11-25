import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Protocol

from app.domain.checkin import Nivel, Tag
from app.domain.recomendacao import Recomendacao


def _now() -> datetime:
    return datetime.now(UTC)


class Faixa(StrEnum):
    MINIMA = "minima"
    LEVE = "leve"
    MODERADA = "moderada"
    MODERADAMENTE_GRAVE = "moderadamente_grave"
    GRAVE = "grave"


# Textos da coluna "O que o usuário vê" do Quadro 18 (Visão v2.7, seção 4.5.2).
ORIENTACAO_POR_NIVEL: dict[Nivel, str] = {
    Nivel.CRISE: "Tela de Ajuda Imediata. Nenhum material é exibido.",
    Nivel.PRIORITARIO: (
        "Suas respostas indicam sintomas intensos. Recomendamos procurar atendimento "
        "em saúde nos próximos dias, na sua UBS de referência ou em um CAPS. "
        "Se piorar, use a Ajuda Imediata."
    ),
    Nivel.ATENCAO: (
        "Recomendamos conversar com um profissional de saúde. "
        "No SUS, a porta de entrada é a Unidade Básica de Saúde (UBS)."
    ),
    Nivel.AUTOCUIDADO: ("Continue acompanhando como você está. Seguem materiais de autocuidado."),
}


@dataclass
class Avaliacao:
    """Avaliação quinzenal PHQ-9 e GAD-7 (Arquitetura, Figura 6)."""

    user_id: uuid.UUID
    respostas_phq9: list[int]
    respostas_gad7: list[int]
    escore_phq9: int
    escore_gad7: int
    faixa_phq9: Faixa
    faixa_gad7: Faixa
    nivel: Nivel
    recomendacoes: list[Recomendacao] = field(default_factory=list)
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    criado_em: datetime = field(default_factory=_now)

    @property
    def usuario_id(self) -> uuid.UUID:
        return self.user_id

    @property
    def orientacao(self) -> str:
        return ORIENTACAO_POR_NIVEL[self.nivel]


@dataclass(frozen=True)
class ResultadoAvaliacao:
    """Saída de decidir_avaliacao (Arquitetura, Quadro 5)."""

    escore_phq9: int
    escore_gad7: int
    faixa_phq9: Faixa
    faixa_gad7: Faixa
    nivel: Nivel
    tags: tuple[Tag, ...]
    regras: tuple[str, ...]


class AvaliacaoRepository(Protocol):
    def add(self, avaliacao: Avaliacao) -> None: ...

    def get_by_id_for_user(
        self, avaliacao_id: uuid.UUID, user_id: uuid.UUID
    ) -> Avaliacao | None: ...

    def list_by_user(self, user_id: uuid.UUID, limit: int | None = None) -> list[Avaliacao]: ...
