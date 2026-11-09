from dataclasses import dataclass
from datetime import date
from typing import List
from app.domain.checkin import Tag

@dataclass
class Material:
    slug: str
    titulo: str
    url: str
    fonte: str
    resumo: str
    tags: List[Tag]
    ativo: bool
    revisado_em: date