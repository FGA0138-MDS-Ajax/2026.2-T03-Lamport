from app.domain.checkin import Nivel, ResultadoCheckin, Tag

# Constantes Originais (Aviso: Alterar exige aprovação do PO)
LIMITE_HUMOR = 2
LIMITE_ANSIEDADE = 2
LIMITE_SONO = 2
LIMITE_ESTRESSE = 2

# R-S1 (Prioridade de tags para exibição e materiais)
ORDEM_TAGS = (Tag.ANSIEDADE, Tag.HUMOR, Tag.ESTRESSE, Tag.SONO)


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
        nivel_calculado = Nivel.ATENCAO if len(regras_acionadas) <= 2 else Nivel.PRIORITARIO
        return ResultadoCheckin(
            nivel=nivel_calculado,
            tags=tags_ordenadas,
            regras=tuple(regras_acionadas),
        )

    # R-D6: Sem risco
    return ResultadoCheckin(nivel=Nivel.AUTOCUIDADO, tags=(Tag.BEM_ESTAR,), regras=("R-D6",))
