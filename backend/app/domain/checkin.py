import uuid
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Protocol


class Nivel(StrEnum):
    AUTOCUIDADO = "autocuidado"
    ATENCAO = "atencao"
    PRIORITARIO = "prioritario"
    CRISE = "crise"


class Tag(StrEnum):
    HUMOR = "humor"
    ANSIEDADE = "ansiedade"
    SONO = "sono"
    ESTRESSE = "estresse"
    BEM_ESTAR = "bem_estar"
    AJUDA_PROFISSIONAL = "ajuda_profissional"


def _now() -> datetime:
    return datetime.now(UTC)


@dataclass
class Checkin:
    user_id: uuid.UUID
    data: date
    pensamento_risco: bool
    humor: int | None = None
    ansiedade: int | None = None
    sono: int | None = None
    sobrecarga: int | None = None
    nivel: Nivel = Nivel.AUTOCUIDADO
    tags: list[Tag] = field(default_factory=list)
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    criado_em: datetime = field(default_factory=_now)


class CheckinRepository(Protocol):
    def get_by_id_for_user(self, checkin_id: uuid.UUID, user_id: uuid.UUID) -> Checkin | None: ...

    def list_by_user(
        self,
        user_id: uuid.UUID,
        limit: int = 20,
        offset: int = 0,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> tuple[list[Checkin], int]:
        """Returns a page of check-ins (ordered DESC) and the total count."""
        ...
