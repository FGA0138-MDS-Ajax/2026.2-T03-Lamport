"""Regras puras de seleção de conteúdos do catálogo (R-S1 a R-S6).

Sem acesso a banco de dados, rede, relógio ou aleatoriedade
(Visão v2.7, seção 4.5.3 e Quadro 20; Arquitetura v2.5, Quadro 5).
"""

from collections.abc import Collection, Mapping, Sequence
from datetime import UTC, datetime
from typing import NamedTuple

from app.domain.checkin import Tag
from app.rules.avaliacao import ORDEM_TAGS

_EPOCH_MIN = datetime.min.replace(tzinfo=UTC)


class TagSelecao(NamedTuple):
    tag: Tag
    regra: str
    motivo: str


class MaterialCatalogo(NamedTuple):
    material_id: int
    tags: Collection[Tag | str]
    ativo: bool = True


class Sugestao(NamedTuple):
    material_id: int
    regra: str
    motivo: str


def _normalizar_utc(instante: datetime) -> datetime:
    if instante.tzinfo is None:
        return instante.replace(tzinfo=UTC)
    return instante.astimezone(UTC)


def selecionar_materiais(
    tags: Sequence[TagSelecao],
    catalogo: Sequence[MaterialCatalogo],
    ultimas_exibicoes: Mapping[int, datetime],
    limite: int = 3,
) -> list[Sugestao]:
    """Seleciona até ``limite`` materiais aplicando as regras R-S1 a R-S6."""
    if limite <= 0 or not tags or not catalogo:
        return []

    # R-S1: considera apenas materiais ativos do catálogo.
    materiais_ativos = [material for material in catalogo if material.ativo]
    if not materiais_ativos:
        return []

    tags_por_codigo: dict[Tag, TagSelecao] = {}
    for tag_selecao in tags:
        tags_por_codigo.setdefault(tag_selecao.tag, tag_selecao)

    def chave_ordenacao(item: MaterialCatalogo) -> tuple[int, datetime, int]:
        ultima = ultimas_exibicoes.get(item.material_id)
        if ultima is None:
            return (0, _EPOCH_MIN, item.material_id)
        return (1, _normalizar_utc(ultima), item.material_id)

    sugestoes: list[Sugestao] = []
    adicionados: set[int] = set()

    # R-S1: percorre as tags presentes na ordem fixa de prioridade.
    for tag in ORDEM_TAGS:
        tag_selecao = tags_por_codigo.get(tag)
        if tag_selecao is None:
            continue

        # R-S2: nunca recomendado primeiro, depois o mais antigo; empate pelo menor id.
        candidatos = sorted(
            (item for item in materiais_ativos if tag in item.tags),
            key=chave_ordenacao,
        )
        for item in candidatos:
            # R-S3: um mesmo material não aparece duas vezes na mesma resposta.
            if item.material_id in adicionados:
                continue

            # R-S5: preserva a regra de origem e o motivo da tag selecionada.
            sugestoes.append(Sugestao(item.material_id, tag_selecao.regra, tag_selecao.motivo))
            adicionados.add(item.material_id)

            # R-S4: interrompe ao atingir o limite (3 padrão, 2 para N2).
            if len(sugestoes) >= limite:
                return sugestoes

    # R-S6: sem fallback para BEM_ESTAR ou materiais sem tag.
    return sugestoes
