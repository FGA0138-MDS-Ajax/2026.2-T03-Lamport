from dataclasses import dataclass
from enum import StrEnum

from app.domain.checkin import Nivel, Tag


class Faixa(StrEnum):
    MINIMA = "minima"
    LEVE = "leve"
    MODERADA = "moderada"
    MODERADAMENTE_GRAVE = "moderadamente_grave"
    GRAVE = "grave"


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
