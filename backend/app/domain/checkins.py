import uuid
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Protocol
from zoneinfo import ZoneInfo

CHECKIN_TIMEZONE = ZoneInfo("America/Sao_Paulo")

QUALITY_MIN, QUALITY_MAX = 1, 5
INTENSITY_MIN, INTENSITY_MAX = 0, 3


class Tag(StrEnum):
    HUMOR = "humor"
    ANSIEDADE = "ansiedade"
    SONO = "sono"
    ESTRESSE = "estresse"
    BEM_ESTAR = "bem_estar"
    AJUDA_PROFISSIONAL = "ajuda_profissional"


class Nivel(StrEnum):
    AUTOCUIDADO = "autocuidado"
    ATENCAO = "atencao"
    PRIORITARIO = "prioritario"
    CRISE = "crise"


TAG_PRIORITY = (
    Tag.AJUDA_PROFISSIONAL,
    Tag.ANSIEDADE,
    Tag.HUMOR,
    Tag.ESTRESSE,
    Tag.SONO,
    Tag.BEM_ESTAR,
)


def avaliar_checkin(
    humor: int | None,
    ansiedade: int | None,
    sono: int | None,
    sobrecarga: int | None,
    pensamento_risco: bool,
) -> tuple[Nivel, list[Tag]]:
    """Aplica as regras R-D1 a R-D6. Respostas ausentes (None) não acionam suas regras."""
    if pensamento_risco:  # R-D1: tem precedência e não gera tags
        return Nivel.CRISE, []

    triggered: set[Tag] = set()
    if humor is not None and humor <= 2:  # R-D2
        triggered.add(Tag.HUMOR)
    if ansiedade is not None and ansiedade >= 2:  # R-D3
        triggered.add(Tag.ANSIEDADE)
    if sono is not None and sono <= 2:  # R-D4
        triggered.add(Tag.SONO)
    if sobrecarga is not None and sobrecarga >= 2:  # R-D5
        triggered.add(Tag.ESTRESSE)
    if not triggered:  # R-D6
        triggered.add(Tag.BEM_ESTAR)

    return Nivel.AUTOCUIDADO, [tag for tag in TAG_PRIORITY if tag in triggered]


def today_in_checkin_timezone() -> date:
    return datetime.now(CHECKIN_TIMEZONE).date()


def _now() -> datetime:
    return datetime.now(UTC)


@dataclass
class Checkin:
    user_id: uuid.UUID
    data: date
    humor: int | None
    ansiedade: int | None
    sono: int | None
    sobrecarga: int | None
    pensamento_risco: bool
    nivel: Nivel
    tags: list[Tag]
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=_now)


class CheckinRepository(Protocol):
    def exists_for_date(self, user_id: uuid.UUID, data: date) -> bool: ...

    def add(self, checkin: Checkin) -> None:
        """Persists the check-in; raises CheckinAlreadyDoneError if one exists for that day."""
        ...
