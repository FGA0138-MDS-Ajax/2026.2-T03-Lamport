import uuid
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from app.domain.material import Material


def _now() -> datetime:
    return datetime.now(UTC)


@dataclass
class Recomendacao:
    """Recomendação de um material oficial (Arquitetura, Figura 6)."""

    user_id: uuid.UUID
    material_id: int
    regra: str
    motivo: str
    checkin_id: uuid.UUID | None = None
    titulo: str = ""
    fonte: str = ""
    resumo: str = ""
    url: str = ""
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    criado_em: datetime = field(default_factory=_now)

    @property
    def usuario_id(self) -> uuid.UUID:
        return self.user_id


class RecomendacaoRepository(Protocol):
    def add(self, recomendacao: Recomendacao) -> None: ...

    def add_all(self, recomendacoes: Sequence[Recomendacao]) -> None: ...

    def list_by_checkin(self, checkin_id: uuid.UUID) -> list[Recomendacao]: ...

    def get_last_displayed_by_user(self, user_id: uuid.UUID) -> dict[int, datetime]: ...

    def list_active_materials(self) -> list["Material"]: ...
