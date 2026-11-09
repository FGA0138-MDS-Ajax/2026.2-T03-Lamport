from typing import NamedTuple

from app.domain.checkin import Tag
from app.rules.checkin import ORDEM_TAGS

DIAS_BLOQUEIO_ULTIMAS_EXIBICOES = 7


class MaterialCatalogo(NamedTuple):
    material_id: str
    tags: set[str]  # Armazenado em string para casar com a formatação yaml da Issue #19
    motivo: str


class Sugestao(NamedTuple):
    material_id: str
    regra: str
    motivo: str


def selecionar_materiais(
    tags_usuario: tuple[Tag, ...],
    catalogo: list[MaterialCatalogo],
    ids_exibidos_recentemente: set[str],
    limite: int = 3,
) -> list[Sugestao]:
    """
    Seleciona sugestões aplicando regras R-S1 a R-S6, com deduplicação e limite.
    Nota (R-S2): `ids_exibidos_recentemente` deve ser filtrado externamente
    pela janela de DIAS_BLOQUEIO_ULTIMAS_EXIBICOES antes de ser injetado.
    """
    if limite <= 0 or not catalogo:
        return []

    sugestoes: list[Sugestao] = []
    adicionados: set[str] = set()

    def registrar_sugestao(material_id: str, regra: str, motivo: str):
        if material_id not in adicionados:
            sugestoes.append(Sugestao(material_id, regra, motivo))
            adicionados.add(material_id)

    # Filtra R-S2 na base
    candidatos_validos = [m for m in catalogo if m.material_id not in ids_exibidos_recentemente]

    # R-S1 (Prioridade) dita a ordem das buscas
    tags_ordenadas = [t for t in ORDEM_TAGS if t in tags_usuario]
    if Tag.BEM_ESTAR in tags_usuario:
        tags_ordenadas.append(Tag.BEM_ESTAR)

    # R-S3: Match exato de tags
    for tag in tags_ordenadas:
        for item in candidatos_validos:
            if tag.value in item.tags:
                registrar_sugestao(item.material_id, "R-S3", item.motivo)
                if len(sugestoes) >= limite:
                    return sugestoes

    # R-S6: Fallback (Bem Estar / Geral) para complementar se faltar limite
    if len(sugestoes) < limite:
        fallback_tag = Tag.BEM_ESTAR.value
        for item in candidatos_validos:
            # Pega itens de bem_estar ou itens gerais (sem tags)
            if fallback_tag in item.tags or not item.tags:
                registrar_sugestao(item.material_id, "R-S6", item.motivo)
                if len(sugestoes) >= limite:
                    return sugestoes

    return sugestoes
