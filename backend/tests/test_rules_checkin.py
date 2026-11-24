from datetime import UTC, datetime, timedelta, timezone

import pytest

from app.domain.checkin import Nivel, Tag
from app.rules.checkin import avaliar_checkin
from app.rules.selecao import MaterialCatalogo, Sugestao, TagSelecao, selecionar_materiais


# Sobrescreve fixtures de banco do conftest.py para testes unitários puros de regras.
@pytest.fixture(scope="session", autouse=True)
def database():
    yield


@pytest.fixture(autouse=True)
def clean_tables():
    yield


def test_example_from_ti03():
    resultado = avaliar_checkin(4, 3, 1, 0, False)

    assert resultado.nivel == Nivel.AUTOCUIDADO
    assert resultado.tags == (Tag.ANSIEDADE, Tag.SONO)
    assert resultado.regras == ("R-D3", "R-D4")


def test_rd1_risk_takes_precedence_and_has_no_tags():
    resultado = avaliar_checkin(1, 3, 1, 3, True)

    assert resultado.nivel == Nivel.CRISE
    assert resultado.tags == ()
    assert resultado.regras == ("R-D1",)


@pytest.mark.parametrize(
    ("respostas", "tags", "regras"),
    [
        # Os dois lados de cada valor-limite.
        ((2, 1, 3, 1), (Tag.HUMOR,), ("R-D2",)),
        ((3, 1, 3, 1), (Tag.BEM_ESTAR,), ("R-D6",)),
        ((5, 2, 5, 0), (Tag.ANSIEDADE,), ("R-D3",)),
        ((5, 1, 5, 0), (Tag.BEM_ESTAR,), ("R-D6",)),
        ((5, 0, 2, 0), (Tag.SONO,), ("R-D4",)),
        ((5, 0, 3, 0), (Tag.BEM_ESTAR,), ("R-D6",)),
        ((5, 0, 5, 2), (Tag.ESTRESSE,), ("R-D5",)),
        ((5, 0, 5, 1), (Tag.BEM_ESTAR,), ("R-D6",)),
        # Todas as regras: tags na ordem de prioridade de R-S1.
        (
            (1, 3, 1, 3),
            (Tag.ANSIEDADE, Tag.HUMOR, Tag.ESTRESSE, Tag.SONO),
            ("R-D3", "R-D2", "R-D5", "R-D4"),
        ),
    ],
)
def test_thresholds(respostas, tags, regras):
    resultado = avaliar_checkin(*respostas, False)

    assert resultado.nivel == Nivel.AUTOCUIDADO
    assert resultado.tags == tags
    assert resultado.regras == regras


@pytest.mark.parametrize(
    "respostas",
    [
        (None, None, None, None),
        (None, 1, 3, 1),
        (3, None, 3, 1),
        (3, 1, None, 1),
        (3, 1, 3, None),
    ],
)
def test_unanswered_question_does_not_trigger_its_rule(respostas):
    resultado = avaliar_checkin(*respostas, False)

    assert resultado.nivel == Nivel.AUTOCUIDADO
    assert resultado.tags == (Tag.BEM_ESTAR,)


# ==============================================================================
# TU-06: Seleção de conteúdo (Quadro 20 e Quadro 26 da Visão v2.7)
# ==============================================================================
@pytest.fixture
def catalogo_tu06() -> list[MaterialCatalogo]:
    """Catálogo fixo com 2 materiais por tag (1 ativo, 1 inativo) em ordem inversa à R-S1."""
    return [
        MaterialCatalogo(11, {Tag.BEM_ESTAR}, ativo=True),
        MaterialCatalogo(12, {Tag.BEM_ESTAR}, ativo=False),
        MaterialCatalogo(9, {Tag.SONO}, ativo=True),
        MaterialCatalogo(10, {Tag.SONO}, ativo=False),
        MaterialCatalogo(7, {Tag.ESTRESSE}, ativo=True),
        MaterialCatalogo(8, {Tag.ESTRESSE}, ativo=False),
        MaterialCatalogo(5, {Tag.HUMOR}, ativo=True),
        MaterialCatalogo(6, {Tag.HUMOR}, ativo=False),
        MaterialCatalogo(3, {Tag.ANSIEDADE}, ativo=True),
        MaterialCatalogo(4, {Tag.ANSIEDADE}, ativo=False),
        MaterialCatalogo(1, {Tag.AJUDA_PROFISSIONAL}, ativo=True),
        MaterialCatalogo(2, {Tag.AJUDA_PROFISSIONAL}, ativo=False),
    ]


def test_tu06_rs1_ordem_prioridade_com_ajuda_profissional(catalogo_tu06):
    tags_fora_de_ordem = [
        TagSelecao(Tag.BEM_ESTAR, "R-D6", "Motivo bem-estar"),
        TagSelecao(Tag.SONO, "R-D4", "Motivo sono"),
        TagSelecao(Tag.ESTRESSE, "R-D5", "Motivo estresse"),
        TagSelecao(Tag.HUMOR, "R-D2", "Motivo humor"),
        TagSelecao(Tag.ANSIEDADE, "R-D3", "Motivo ansiedade"),
        TagSelecao(Tag.AJUDA_PROFISSIONAL, "R-A3", "Motivo ajuda"),
    ]

    res = selecionar_materiais(tags_fora_de_ordem, catalogo_tu06, {}, limite=6)

    assert [s.material_id for s in res] == [1, 3, 5, 7, 9, 11]

    # Apenas AJUDA_PROFISSIONAL (N2) não deve cair em BEM_ESTAR mesmo com limite=2.
    res_n2 = selecionar_materiais(
        [TagSelecao(Tag.AJUDA_PROFISSIONAL, "R-A2", "Motivo N2")],
        catalogo_tu06,
        {},
        limite=2,
    )
    assert res_n2 == [Sugestao(1, "R-A2", "Motivo N2")]

    # Prioridade independe do ID numérico ou da ordem no catálogo.
    catalogo_custom = [
        MaterialCatalogo(10, {"ansiedade"}, ativo=True),
        MaterialCatalogo(99, {"ajuda_profissional"}, ativo=True),
    ]
    res_custom = selecionar_materiais(
        [
            TagSelecao(Tag.ANSIEDADE, "R-A3", "Motivo ansiedade"),
            TagSelecao(Tag.AJUDA_PROFISSIONAL, "R-A3", "Motivo ajuda"),
        ],
        catalogo_custom,
        {},
        limite=2,
    )
    assert [s.material_id for s in res_custom] == [99, 10]


def test_tu06_rs1_material_inativo_nunca_sugerido(catalogo_tu06):
    # Mesmo com o material ativo (9) já recomendado antes e o inativo (10) nunca exibido,
    # o material inativo não é escolhido.
    res = selecionar_materiais(
        [TagSelecao(Tag.SONO, "R-D4", "Motivo sono")],
        catalogo_tu06,
        {9: datetime(2026, 11, 10, 8, 0, tzinfo=UTC)},
        limite=3,
    )
    assert res == [Sugestao(9, "R-D4", "Motivo sono")]

    # Catálogo só com inativos para a tag não sugere o inativo (nem mesmo com menor ID).
    apenas_inativos = [
        MaterialCatalogo(1, {Tag.ANSIEDADE}, ativo=False),
        MaterialCatalogo(50, {Tag.ANSIEDADE}, ativo=True),
    ]
    res_ativo = selecionar_materiais(
        [TagSelecao(Tag.ANSIEDADE, "R-D3", "Motivo ansiedade")],
        apenas_inativos,
        {},
        limite=3,
    )
    assert [s.material_id for s in res_ativo] == [50]


def test_tu06_rs2_nunca_recomendado_depois_mais_antigo_e_desempate_menor_id():
    fuso_brt = timezone(timedelta(hours=-3))
    catalogo = [
        MaterialCatalogo(10, {Tag.ANSIEDADE}, ativo=True),  # nunca recomendado (ID 10)
        MaterialCatalogo(2, {Tag.ANSIEDADE}, ativo=True),  # nunca recomendado (ID 2)
        MaterialCatalogo(30, {Tag.ANSIEDADE}, ativo=True),  # mais recente
        MaterialCatalogo(20, {Tag.ANSIEDADE}, ativo=True),  # empate antigo (ID 20)
        MaterialCatalogo(3, {Tag.ANSIEDADE}, ativo=True),  # empate antigo (ID 3)
        MaterialCatalogo(15, {Tag.ANSIEDADE}, ativo=True),  # intermediário
    ]
    ultimas_exibicoes = {
        30: datetime(2026, 11, 15, 12, 0, tzinfo=UTC),
        20: datetime(2026, 11, 10, 9, 0, tzinfo=UTC),
        3: datetime(2026, 11, 10, 6, 0, tzinfo=fuso_brt),  # == 09:00 UTC
        15: datetime(2026, 11, 12, 12, 0),  # naive assumido como UTC
    }

    ordem_escolhida: list[int] = []
    base_nova_exibicao = datetime(2026, 11, 20, 12, 0, tzinfo=UTC)
    for rodada in range(len(catalogo)):
        res = selecionar_materiais(
            [TagSelecao(Tag.ANSIEDADE, "R-D3", "Motivo ansiedade")],
            catalogo,
            ultimas_exibicoes,
            limite=3,
        )
        assert len(res) == 1
        escolhido = res[0].material_id
        ordem_escolhida.append(escolhido)
        ultimas_exibicoes[escolhido] = base_nova_exibicao + timedelta(minutes=rodada)

    # Ordem esperada: nunca recomendados (2 antes de 10), depois 2026-11-10 (3 antes de 20),
    # depois 2026-11-12 (15) e por fim 2026-11-15 (30) — sem janela de bloqueio.
    assert ordem_escolhida == [2, 10, 3, 20, 15, 30]


def test_tu06_rs2_rs4_um_material_por_tag_com_multiplos_ativos():
    catalogo_ansiedade = [
        MaterialCatalogo(1, {Tag.ANSIEDADE}, ativo=True),
        MaterialCatalogo(2, {Tag.ANSIEDADE}, ativo=True),
        MaterialCatalogo(3, {Tag.ANSIEDADE}, ativo=True),
    ]
    ultimas = {
        1: datetime(2026, 11, 15, 12, 0, tzinfo=UTC),
        2: datetime(2026, 11, 10, 12, 0, tzinfo=UTC),
    }

    # Só 1 material é escolhido por tag (o nunca recomendado primeiro).
    res_nunca = selecionar_materiais(
        [TagSelecao(Tag.ANSIEDADE, "R-D3", "Motivo ansiedade")],
        catalogo_ansiedade,
        ultimas,
        limite=3,
    )
    assert res_nunca == [Sugestao(3, "R-D3", "Motivo ansiedade")]

    # Quando todos já foram exibidos, escolhe apenas o mais antigo (ID 2).
    ultimas[3] = datetime(2026, 11, 18, 12, 0, tzinfo=UTC)
    res_antigo = selecionar_materiais(
        [TagSelecao(Tag.ANSIEDADE, "R-D3", "Motivo ansiedade")],
        catalogo_ansiedade,
        ultimas,
        limite=3,
    )
    assert res_antigo == [Sugestao(2, "R-D3", "Motivo ansiedade")]

    # Cenário TI-03: [ANSIEDADE, SONO] com vários ativos de ansiedade traz 1 de cada tag.
    catalogo_ti03 = [
        *catalogo_ansiedade,
        MaterialCatalogo(30, {Tag.SONO}, ativo=True),
        MaterialCatalogo(31, {Tag.SONO}, ativo=True),
    ]
    ultimas_ti03 = {
        1: datetime(2026, 11, 15, 12, 0, tzinfo=UTC),
        2: datetime(2026, 11, 10, 12, 0, tzinfo=UTC),
        30: datetime(2026, 11, 11, 12, 0, tzinfo=UTC),
    }
    res_ti03 = selecionar_materiais(
        [
            TagSelecao(Tag.ANSIEDADE, "R-D3", "Motivo ansiedade"),
            TagSelecao(Tag.SONO, "R-D4", "Motivo sono"),
        ],
        catalogo_ti03,
        ultimas_ti03,
        limite=3,
    )
    assert res_ti03 == [
        Sugestao(3, "R-D3", "Motivo ansiedade"),
        Sugestao(31, "R-D4", "Motivo sono"),
    ]

    # Com 4 tags e múltiplos ativos por tag, retorna 1 das 3 primeiras e descarta a 4ª (R-S4).
    catalogo_quatro_tags = [
        *catalogo_ti03,
        MaterialCatalogo(10, {Tag.HUMOR}, ativo=True),
        MaterialCatalogo(11, {Tag.HUMOR}, ativo=True),
        MaterialCatalogo(20, {Tag.ESTRESSE}, ativo=True),
        MaterialCatalogo(21, {Tag.ESTRESSE}, ativo=True),
    ]
    res_quatro = selecionar_materiais(
        [
            TagSelecao(Tag.SONO, "R-D4", "Motivo sono"),
            TagSelecao(Tag.ESTRESSE, "R-D5", "Motivo estresse"),
            TagSelecao(Tag.HUMOR, "R-D2", "Motivo humor"),
            TagSelecao(Tag.ANSIEDADE, "R-D3", "Motivo ansiedade"),
        ],
        catalogo_quatro_tags,
        ultimas_ti03,
        limite=3,
    )
    assert [s.material_id for s in res_quatro] == [3, 10, 20]


def test_tu06_rs3_material_com_duas_tags_aparece_uma_vez():
    catalogo = [
        MaterialCatalogo(10, {"ansiedade", "sono"}, ativo=True),
        MaterialCatalogo(20, {"sono"}, ativo=True),
        MaterialCatalogo(30, {"sono"}, ativo=True),
    ]
    tags = [
        TagSelecao(Tag.SONO, "R-D4", "Você indicou que dormiu mal na última noite."),
        TagSelecao(
            Tag.ANSIEDADE,
            "R-D3",
            "Você indicou ter se sentido bastante ou extremamente ansioso(a) hoje.",
        ),
    ]

    res = selecionar_materiais(tags, catalogo, {}, limite=3)

    assert res == [
        Sugestao(
            10,
            "R-D3",
            "Você indicou ter se sentido bastante ou extremamente ansioso(a) hoje.",
        ),
        Sugestao(20, "R-D4", "Você indicou que dormiu mal na última noite."),
    ]


def test_tu06_rs4_limite_tres_padrao_e_limite_dois_n2(catalogo_tu06):
    tags_checkin = [
        TagSelecao(Tag.SONO, "R-D4", "Motivo sono"),
        TagSelecao(Tag.ESTRESSE, "R-D5", "Motivo estresse"),
        TagSelecao(Tag.HUMOR, "R-D2", "Motivo humor"),
        TagSelecao(Tag.ANSIEDADE, "R-D3", "Motivo ansiedade"),
    ]
    res_padrao = selecionar_materiais(tags_checkin, catalogo_tu06, {})
    assert [s.material_id for s in res_padrao] == [3, 5, 7]

    # Limite 2 (nível N2): descarta tags excedentes por prioridade.
    tags_n2 = [
        TagSelecao(Tag.HUMOR, "R-A3", "Motivo humor"),
        TagSelecao(Tag.ANSIEDADE, "R-A3", "Motivo ansiedade"),
        TagSelecao(Tag.AJUDA_PROFISSIONAL, "R-A2", "Motivo N2"),
    ]
    res_n2_tags = selecionar_materiais(tags_n2, catalogo_tu06, {}, limite=2)
    assert [s.material_id for s in res_n2_tags] == [1, 3]

    # Apenas 1 material é escolhido por tag mesmo quando há vários ativos e limite=2.
    catalogo_ajuda = [MaterialCatalogo(i, {Tag.AJUDA_PROFISSIONAL}, True) for i in (1, 2, 3)]
    res_n2_mesma_tag = selecionar_materiais(
        [TagSelecao(Tag.AJUDA_PROFISSIONAL, "R-A2", "Motivo N2")],
        catalogo_ajuda,
        {},
        limite=2,
    )
    assert [s.material_id for s in res_n2_mesma_tag] == [1]

    assert selecionar_materiais(tags_checkin, catalogo_tu06, {}, limite=0) == []
    assert selecionar_materiais(tags_checkin, catalogo_tu06, {}, limite=-1) == []


@pytest.mark.parametrize(
    ("tag", "regra", "motivo", "id_esperado"),
    [
        (Tag.HUMOR, "R-D2", "Você indicou humor ruim ou muito ruim hoje.", 5),
        (
            Tag.ANSIEDADE,
            "R-D3",
            "Você indicou ter se sentido bastante ou extremamente ansioso(a) hoje.",
            3,
        ),
        (Tag.SONO, "R-D4", "Você indicou que dormiu mal na última noite.", 9),
        (
            Tag.ESTRESSE,
            "R-D5",
            "Você indicou ter se sentido bastante ou extremamente sobrecarregado(a).",
            7,
        ),
        (Tag.BEM_ESTAR, "R-D6", "Você não indicou dificuldades marcantes hoje.", 11),
    ],
)
def test_tu06_rs5_checkin_preserva_regra_e_motivo_quadro_16(
    catalogo_tu06, tag, regra, motivo, id_esperado
):
    res = selecionar_materiais([TagSelecao(tag, regra, motivo)], catalogo_tu06, {})

    assert res == [Sugestao(id_esperado, regra, motivo)]


def test_tu06_rs5_avaliacao_preserva_regra_e_motivo_quadro_18(catalogo_tu06):
    # R-A2 (N2)
    motivo_a2 = (
        "Suas respostas indicam sintomas intensos. Este material explica onde buscar atendimento."
    )
    res_a2 = selecionar_materiais(
        [TagSelecao(Tag.AJUDA_PROFISSIONAL, "R-A2", motivo_a2)],
        catalogo_tu06,
        {},
        limite=2,
    )
    assert res_a2 == [Sugestao(1, "R-A2", motivo_a2)]

    # R-A3 (N1)
    motivo_a3_ajuda = (
        "Suas respostas indicam que conversar com um profissional de saúde pode ajudar."
    )
    motivo_a3_humor = "Seu resultado no PHQ-9 ficou na faixa moderada ou acima."
    motivo_a3_ans = "Seu resultado no GAD-7 ficou na faixa moderada ou acima."
    res_a3 = selecionar_materiais(
        [
            TagSelecao(Tag.HUMOR, "R-A3", motivo_a3_humor),
            TagSelecao(Tag.ANSIEDADE, "R-A3", motivo_a3_ans),
            TagSelecao(Tag.AJUDA_PROFISSIONAL, "R-A3", motivo_a3_ajuda),
        ],
        catalogo_tu06,
        {},
        limite=3,
    )
    assert res_a3 == [
        Sugestao(1, "R-A3", motivo_a3_ajuda),
        Sugestao(3, "R-A3", motivo_a3_ans),
        Sugestao(5, "R-A3", motivo_a3_humor),
    ]

    # R-A4 (N0 com sintomas leves e N0 mínimo)
    motivo_a4_ans = "Seu resultado no GAD-7 ficou na faixa leve."
    motivo_a4_humor = "Seu resultado no PHQ-9 ficou na faixa leve."
    res_a4_leve = selecionar_materiais(
        [
            TagSelecao(Tag.HUMOR, "R-A4", motivo_a4_humor),
            TagSelecao(Tag.ANSIEDADE, "R-A4", motivo_a4_ans),
        ],
        catalogo_tu06,
        {},
        limite=3,
    )
    assert res_a4_leve == [
        Sugestao(3, "R-A4", motivo_a4_ans),
        Sugestao(5, "R-A4", motivo_a4_humor),
    ]

    motivo_a4_bem_estar = (
        "Suas respostas não indicaram sintomas marcantes nas últimas duas semanas."
    )
    res_a4_minimo = selecionar_materiais(
        [TagSelecao(Tag.BEM_ESTAR, "R-A4", motivo_a4_bem_estar)],
        catalogo_tu06,
        {},
        limite=3,
    )
    assert res_a4_minimo == [Sugestao(11, "R-A4", motivo_a4_bem_estar)]


def test_tu06_rs6_sem_material_disponivel_retorna_vazio_sem_fallback(catalogo_tu06):
    # Catálogo vazio, sem tags ou apenas com materiais inativos.
    assert selecionar_materiais([TagSelecao(Tag.SONO, "R-D4", "Motivo sono")], [], {}) == []
    assert selecionar_materiais([], catalogo_tu06, {}) == []
    todos_inativos = [MaterialCatalogo(m.material_id, m.tags, ativo=False) for m in catalogo_tu06]
    assert (
        selecionar_materiais(
            [TagSelecao(Tag.BEM_ESTAR, "R-D6", "Motivo bem-estar")], todos_inativos, {}
        )
        == []
    )

    # Tag sem material ativo disponível: não recorre a BEM_ESTAR nem a material sem tag.
    catalogo_sem_sono_ativo = [
        MaterialCatalogo(10, {Tag.SONO}, ativo=False),
        MaterialCatalogo(11, {Tag.BEM_ESTAR}, ativo=True),
        MaterialCatalogo(99, set(), ativo=True),
    ]
    assert (
        selecionar_materiais(
            [TagSelecao(Tag.SONO, "R-D4", "Motivo sono")],
            catalogo_sem_sono_ativo,
            {},
            limite=3,
        )
        == []
    )

    # Não completa o limite restante com BEM_ESTAR nem com material sem tag.
    catalogo_parcial = [
        MaterialCatalogo(3, {Tag.ANSIEDADE}, ativo=True),
        MaterialCatalogo(11, {Tag.BEM_ESTAR}, ativo=True),
        MaterialCatalogo(99, set(), ativo=True),
    ]
    assert selecionar_materiais(
        [TagSelecao(Tag.ANSIEDADE, "R-D3", "Motivo ansiedade")],
        catalogo_parcial,
        {},
        limite=3,
    ) == [Sugestao(3, "R-D3", "Motivo ansiedade")]
