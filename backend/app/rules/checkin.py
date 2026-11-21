from app.domain.checkin import Nivel, ResultadoCheckin, Tag
from app.rules.selecao import TagSelecao

# Constantes Originais (Aviso: Alterar exige aprovação do PO)
LIMITE_HUMOR = 2
LIMITE_ANSIEDADE = 2
LIMITE_SONO = 2
LIMITE_ESTRESSE = 2

# R-S1 (Prioridade de tags para exibição e materiais)
ORDEM_TAGS = (Tag.ANSIEDADE, Tag.HUMOR, Tag.ESTRESSE, Tag.SONO)

# Quadro 16 (Visão v2.7, seção 4.5.1): regras e motivos exibidos ao usuário por tag do check-in.
REGRA_POR_TAG_CHECKIN: dict[Tag, str] = {
    Tag.HUMOR: "R-D2",
    Tag.ANSIEDADE: "R-D3",
    Tag.SONO: "R-D4",
    Tag.ESTRESSE: "R-D5",
    Tag.BEM_ESTAR: "R-D6",
}

MOTIVO_POR_REGRA_CHECKIN: dict[str, str] = {
    "R-D2": "Você indicou humor ruim ou muito ruim hoje.",
    "R-D3": "Você indicou ter se sentido bastante ou extremamente ansioso(a) hoje.",
    "R-D4": "Você indicou que dormiu mal na última noite.",
    "R-D5": "Você indicou ter se sentido bastante ou extremamente sobrecarregado(a).",
    "R-D6": "Você não indicou dificuldades marcantes hoje.",
}

MOTIVO_POR_TAG_CHECKIN: dict[Tag, str] = {
    tag: MOTIVO_POR_REGRA_CHECKIN[regra] for tag, regra in REGRA_POR_TAG_CHECKIN.items()
}


def tags_selecao_checkin(resultado: ResultadoCheckin) -> tuple[TagSelecao, ...]:
    """Converte ResultadoCheckin nas entradas TagSelecao do Quadro 16."""
    return tuple(
        TagSelecao(
            tag=tag,
            regra=REGRA_POR_TAG_CHECKIN[tag],
            motivo=MOTIVO_POR_TAG_CHECKIN[tag],
        )
        for tag in resultado.tags
    )


def avaliar_checkin(
    p1: int | None = None,
    p2: int | None = None,
    p3: int | None = None,
    p4: int | None = None,
    p5: bool = False,
) -> ResultadoCheckin:
    """
    Avalia o check-in do usuário aplicando as regras R-D1 a R-D6.
    Retorna ResultadoCheckin com nível, tags na ordem de prioridade e regras acionadas.
    """
    regras_acionadas: list[str] = []
    tags_detectadas: list[Tag] = []

    # R-D1: P5 (Crise/Emergência) tem precedência absoluta
    if p5 is True:
        return ResultadoCheckin(nivel=Nivel.CRISE, tags=(), regras=("R-D1",))

    # Avaliação de limites exatos com as constantes
    if p2 is not None and p2 >= LIMITE_ANSIEDADE:
        regras_acionadas.append("R-D3")
        tags_detectadas.append(Tag.ANSIEDADE)

    if p1 is not None and p1 <= LIMITE_HUMOR:
        regras_acionadas.append("R-D2")
        tags_detectadas.append(Tag.HUMOR)

    if p4 is not None and p4 >= LIMITE_ESTRESSE:
        regras_acionadas.append("R-D5")
        tags_detectadas.append(Tag.ESTRESSE)

    if p3 is not None and p3 <= LIMITE_SONO:
        regras_acionadas.append("R-D4")
        tags_detectadas.append(Tag.SONO)

    if regras_acionadas:
        # Reordena as tags detectadas conforme a prioridade R-S1
        tags_ordenadas = tuple(tag for tag in ORDEM_TAGS if tag in tags_detectadas)
        return ResultadoCheckin(
            nivel=Nivel.AUTOCUIDADO,
            tags=tags_ordenadas,
            regras=tuple(regras_acionadas),
        )

    # R-D6: Sem risco
    return ResultadoCheckin(nivel=Nivel.AUTOCUIDADO, tags=(Tag.BEM_ESTAR,), regras=("R-D6",))
