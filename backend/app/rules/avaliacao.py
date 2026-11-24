"""Regras da avaliação quinzenal (PHQ-9 e GAD-7).

Funções puras: sem banco de dados, rede, relógio ou aleatoriedade
(Visão, seção 4.5.2 e Quadros 17 e 18; Arquitetura, Quadro 5).
"""

from collections.abc import Sequence

from app.domain.avaliacao import ORIENTACAO_POR_NIVEL, Faixa, ResultadoAvaliacao
from app.domain.checkin import Nivel, Tag

# Valores-limite das regras R-A2 a R-A4. Alterá-los exige aprovação do PO.
LIMITE_CORTE = 10  # R-A3: PHQ-9 >= 10 ou GAD-7 >= 10
LIMITE_PHQ9_GRAVE = 20  # R-A2: PHQ-9 >= 20
LIMITE_GAD7_GRAVE = 15  # R-A2: GAD-7 >= 15
LIMITE_LEVE = 5  # R-A4: escore >= 5 ativa a tag de sintoma leve

# Limite de materiais por avaliação conforme R-S4 (Quadro 20 da Visão v2.7).
LIMITE_RECOMENDACOES_PADRAO = 3
LIMITE_RECOMENDACOES_PRIORITARIO = 2

# Ordem de prioridade das tags (Visão, R-S1).
ORDEM_TAGS = (
    Tag.AJUDA_PROFISSIONAL,
    Tag.ANSIEDADE,
    Tag.HUMOR,
    Tag.ESTRESSE,
    Tag.SONO,
    Tag.BEM_ESTAR,
)

# Quadro 18 (Visão v2.7, seção 4.5.2, decisão DP-1): motivo exibido ao usuário por regra e tag.
MOTIVO_POR_REGRA_E_TAG_AVALIACAO: dict[tuple[str, Tag], str] = {
    (
        "R-A2",
        Tag.AJUDA_PROFISSIONAL,
    ): "Suas respostas indicam sintomas intensos. Este material explica onde buscar atendimento.",
    (
        "R-A3",
        Tag.AJUDA_PROFISSIONAL,
    ): "Suas respostas indicam que conversar com um profissional de saúde pode ajudar.",
    (
        "R-A3",
        Tag.HUMOR,
    ): "Seu resultado no PHQ-9 ficou na faixa moderada ou acima.",
    (
        "R-A3",
        Tag.ANSIEDADE,
    ): "Seu resultado no GAD-7 ficou na faixa moderada ou acima.",
    (
        "R-A4",
        Tag.HUMOR,
    ): "Seu resultado no PHQ-9 ficou na faixa leve.",
    (
        "R-A4",
        Tag.ANSIEDADE,
    ): "Seu resultado no GAD-7 ficou na faixa leve.",
    (
        "R-A4",
        Tag.BEM_ESTAR,
    ): "Suas respostas não indicaram sintomas marcantes nas últimas duas semanas.",
}


def pontuar(respostas: Sequence[int], n_itens: int) -> int:
    """Calcula a soma das respostas de um instrumento.

    Lança ValueError se o tamanho for diferente de n_itens ou
    se algum valor estiver fora do intervalo 0 a 3.
    """
    if n_itens not in (7, 9):
        raise ValueError(f"Número de itens inválido: {n_itens}. Esperado 7 ou 9.")
    if len(respostas) != n_itens:
        raise ValueError(f"Esperado {n_itens} itens, recebido {len(respostas)}.")

    for idx, r in enumerate(respostas):
        if not isinstance(r, int) or isinstance(r, bool) or r < 0 or r > 3:
            raise ValueError(
                f"Item {idx + 1} inválido ({r!r}). Cada resposta deve ser um inteiro entre 0 e 3."
            )

    return sum(respostas)


def faixa_phq9(escore: int) -> Faixa:
    """Retorna a faixa de gravidade do PHQ-9 conforme Quadro 17 da Visão."""
    if not isinstance(escore, int) or isinstance(escore, bool) or not (0 <= escore <= 27):
        raise ValueError(f"Escore PHQ-9 deve estar entre 0 e 27, recebido {escore!r}.")

    if escore <= 4:
        return Faixa.MINIMA
    if escore <= 9:
        return Faixa.LEVE
    if escore <= 14:
        return Faixa.MODERADA
    if escore <= 19:
        return Faixa.MODERADAMENTE_GRAVE
    return Faixa.GRAVE


def faixa_gad7(escore: int) -> Faixa:
    """Retorna a faixa de gravidade do GAD-7 conforme Quadro 17 da Visão."""
    if not isinstance(escore, int) or isinstance(escore, bool) or not (0 <= escore <= 21):
        raise ValueError(f"Escore GAD-7 deve estar entre 0 e 21, recebido {escore!r}.")

    if escore <= 4:
        return Faixa.MINIMA
    if escore <= 9:
        return Faixa.LEVE
    if escore <= 14:
        return Faixa.MODERADA
    return Faixa.GRAVE


def decidir_avaliacao(phq9: Sequence[int], gad7: Sequence[int]) -> ResultadoAvaliacao:
    """Aplica a tabela de decisão da avaliação quinzenal (R-A1 a R-A4).

    Avaliada de cima para baixo: a primeira regra verdadeira define o nível.
    R-A1 (item 9 do PHQ-9 >= 1) tem precedência sobre qualquer escore total.
    """
    escore_phq9 = pontuar(phq9, 9)
    escore_gad7 = pontuar(gad7, 7)

    faixa_p = faixa_phq9(escore_phq9)
    faixa_g = faixa_gad7(escore_gad7)

    # R-A1: Item 9 do PHQ-9 >= 1 (índice 8)
    if phq9[8] >= 1:
        return ResultadoAvaliacao(
            escore_phq9=escore_phq9,
            escore_gad7=escore_gad7,
            faixa_phq9=faixa_p,
            faixa_gad7=faixa_g,
            nivel=Nivel.CRISE,
            tags=(),
            regras=("R-A1",),
        )

    # R-A2: PHQ-9 >= 20 ou GAD-7 >= 15
    if escore_phq9 >= LIMITE_PHQ9_GRAVE or escore_gad7 >= LIMITE_GAD7_GRAVE:
        return ResultadoAvaliacao(
            escore_phq9=escore_phq9,
            escore_gad7=escore_gad7,
            faixa_phq9=faixa_p,
            faixa_gad7=faixa_g,
            nivel=Nivel.PRIORITARIO,
            tags=(Tag.AJUDA_PROFISSIONAL,),
            regras=("R-A2",),
        )

    # R-A3: PHQ-9 >= 10 ou GAD-7 >= 10
    if escore_phq9 >= LIMITE_CORTE or escore_gad7 >= LIMITE_CORTE:
        tags_set = {Tag.AJUDA_PROFISSIONAL}
        if escore_phq9 >= LIMITE_CORTE:
            tags_set.add(Tag.HUMOR)
        if escore_gad7 >= LIMITE_CORTE:
            tags_set.add(Tag.ANSIEDADE)

        tags = tuple(tag for tag in ORDEM_TAGS if tag in tags_set)
        return ResultadoAvaliacao(
            escore_phq9=escore_phq9,
            escore_gad7=escore_gad7,
            faixa_phq9=faixa_p,
            faixa_gad7=faixa_g,
            nivel=Nivel.ATENCAO,
            tags=tags,
            regras=("R-A3",),
        )

    # R-A4: Nenhuma das anteriores (AUTOCUIDADO)
    tags_set = set()
    if LIMITE_LEVE <= escore_phq9 <= 9:
        tags_set.add(Tag.HUMOR)
    if LIMITE_LEVE <= escore_gad7 <= 9:
        tags_set.add(Tag.ANSIEDADE)
    if not tags_set:
        tags_set.add(Tag.BEM_ESTAR)

    tags = tuple(tag for tag in ORDEM_TAGS if tag in tags_set)
    return ResultadoAvaliacao(
        escore_phq9=escore_phq9,
        escore_gad7=escore_gad7,
        faixa_phq9=faixa_p,
        faixa_gad7=faixa_g,
        nivel=Nivel.AUTOCUIDADO,
        tags=tags,
        regras=("R-A4",),
    )


def orientacao_avaliacao(nivel: Nivel) -> str:
    """Retorna o texto 'O que o usuário vê' do Quadro 18 para o nível da avaliação."""
    return ORIENTACAO_POR_NIVEL[nivel]


def limite_recomendacoes_avaliacao(nivel: Nivel) -> int:
    """Retorna o limite de materiais da R-S4 (2 para N2, 3 nos demais níveis sem crise)."""
    if nivel == Nivel.CRISE:
        return 0
    if nivel == Nivel.PRIORITARIO:
        return LIMITE_RECOMENDACOES_PRIORITARIO
    return LIMITE_RECOMENDACOES_PADRAO


def tags_selecao_avaliacao(resultado: ResultadoAvaliacao):
    """Converte ResultadoAvaliacao nas entradas TagSelecao do Quadro 18 (DP-1)."""
    from app.rules.selecao import TagSelecao

    if resultado.nivel == Nivel.CRISE or not resultado.tags or not resultado.regras:
        return ()
    regra = resultado.regras[0]
    return tuple(
        TagSelecao(
            tag=tag,
            regra=regra,
            motivo=MOTIVO_POR_REGRA_E_TAG_AVALIACAO[(regra, tag)],
        )
        for tag in resultado.tags
    )
