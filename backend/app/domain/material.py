from dataclasses import dataclass
from datetime import date
from typing import Protocol

from app.domain.checkin import Tag


@dataclass
class Material:
    slug: str
    titulo: str
    url: str
    fonte: str
    resumo: str
    tags: list[Tag]
    ativo: bool
    revisado_em: date
    id: int | None = None


class MaterialRepository(Protocol):
    def list_active(self) -> list[Material]: ...
