import pytest

# Importa diretamente as funções puras do seu módulo
from app.rules.checkin import Nivel, Tag, avaliar_checkin, selecionar_materiais


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
        ((2, 1, 3, 1), (Tag.HUMOR,), ("R-D2",)),
        ((3, 1, 3, 1), (Tag.BEM_ESTAR,), ("R-D6",)),
        ((5, 2, 5, 0), (Tag.ANSIEDADE,), ("R-D3",)),
        ((5, 1, 5, 0), (Tag.BEM_ESTAR,), ("R-D6",)),
        ((5, 0, 2, 0), (Tag.SONO,), ("R-D4",)),
        ((5, 0, 3, 0), (Tag.BEM_ESTAR,), ("R-D6",)),
        ((5, 0, 5, 2), (Tag.ESTRESSE,), ("R-D5",)),
        ((5, 0, 5, 1), (Tag.BEM_ESTAR,), ("R-D6",)),
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


@pytest.fixture
def catalogo_mock():
    return [
        {"material_id": "m1", "tags": (Tag.ANSIEDADE, Tag.ESTRESSE), "motivo": "Apoio ansiedade"},
        {"material_id": "m2", "tags": (Tag.SONO,), "motivo": "Melhore seu sono"},
        {"material_id": "m3", "tags": (Tag.HUMOR,), "motivo": "Apoio humor"},
        {"material_id": "m4", "tags": (Tag.BEM_ESTAR,), "motivo": "Autocuidado geral"},
        {"material_id": "m5", "tags": (Tag.ANSIEDADE,), "motivo": "Respiração"},
    ]


def test_rs2_ultimas_exibicoes_sao_ignoradas(catalogo_mock):
    sugestoes = selecionar_materiais(
        tags=(Tag.ANSIEDADE,), catalogo=catalogo_mock, ultimas_exibicoes=["m1"], limite=3
    )

    ids_sugeridos = [s["material_id"] for s in sugestoes]
    assert "m1" not in ids_sugeridos
    assert "m5" in ids_sugeridos


def test_rs3_rs4_match_de_tags_respeita_limite(catalogo_mock):
    sugestoes = selecionar_materiais(
        tags=(Tag.ANSIEDADE,), catalogo=catalogo_mock, ultimas_exibicoes=[], limite=1
    )

    assert len(sugestoes) == 1
    assert sugestoes[0]["material_id"] == "m1"
    assert "R-S" in sugestoes[0]["regra"]


def test_rs5_rs6_fallback_quando_nenhuma_tag_da_match(catalogo_mock):
    sugestoes = selecionar_materiais(
        tags=(Tag.FOCO,), catalogo=catalogo_mock, ultimas_exibicoes=[], limite=2
    )
    assert len(sugestoes) == 2
    assert sugestoes[0]["material_id"] == "m1"
    assert sugestoes[1]["material_id"] == "m2"
