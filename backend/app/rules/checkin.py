"""Regras do check-in diário (Visão, Quadro 16). Funções puras: sem banco, rede ou relógio."""

from app.domain.checkin import Nivel, ResultadoCheckin, Tag

# Valores-limite das regras R-D2 a R-D5. Alterá-los exige aprovação do PO.
LIMITE_HUMOR = 2  # R-D2: P1 <= 2
LIMITE_ANSIEDADE = 2  # R-D3: P2 >= 2
LIMITE_SONO = 2  # R-D4: P3 <= 2
LIMITE_SOBRECARGA = 2  # R-D5: P4 >= 2

# Ordem de prioridade das tags (Visão, R-S1).
ORDEM_TAGS = (
    Tag.AJUDA_PROFISSIONAL,
    Tag.ANSIEDADE,
    Tag.HUMOR,
    Tag.ESTRESSE,
    Tag.SONO,
    Tag.BEM_ESTAR,
)


def avaliar_checkin(
    p1: int | None, p2: int | None, p3: int | None, p4: int | None, p5: bool
) -> ResultadoCheckin:
    """Aplica R-D1 a R-D6. Resposta nula não aciona a regra da pergunta."""
    if p5:
        return ResultadoCheckin(nivel=Nivel.CRISE, tags=(), regras=("R-D1",))

    acionadas: dict[Tag, str] = {}
    if p1 is not None and p1 <= LIMITE_HUMOR:
        acionadas[Tag.HUMOR] = "R-D2"
    if p2 is not None and p2 >= LIMITE_ANSIEDADE:
        acionadas[Tag.ANSIEDADE] = "R-D3"
    if p3 is not None and p3 <= LIMITE_SONO:
        acionadas[Tag.SONO] = "R-D4"
    if p4 is not None and p4 >= LIMITE_SOBRECARGA:
        acionadas[Tag.ESTRESSE] = "R-D5"
    if not acionadas:
        acionadas[Tag.BEM_ESTAR] = "R-D6"

    tags = tuple(tag for tag in ORDEM_TAGS if tag in acionadas)
    return ResultadoCheckin(
        nivel=Nivel.AUTOCUIDADO,
        tags=tags,
        regras=tuple(acionadas[tag] for tag in tags),
    )
