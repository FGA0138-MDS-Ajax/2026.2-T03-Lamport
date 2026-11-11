import pytest

from app.domain.checkin import Nivel, Tag
from app.rules.checkin import avaliar_checkin
from app.rules.selecao import MaterialCatalogo, selecionar_materiais


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


@pytest.fixture
def catalogo():
    return [
        MaterialCatalogo("m1", {"ansiedade"}, "Apoio 1"),
        MaterialCatalogo("m2", {"sono"}, "Apoio 2"),
        MaterialCatalogo("m3", {"bem_estar"}, "Apoio 3"),
    ]


def test_tu06_selecao_limite_zero_ou_catalogo_vazio(catalogo):
    assert selecionar_materiais((Tag.ANSIEDADE,), catalogo, set(), limite=0) == []
    assert selecionar_materiais((Tag.ANSIEDADE,), [], set(), limite=3) == []


def test_tu06_rs2_ignora_ultimas_exibicoes(catalogo):
    # m1 tem a tag ansiedade, mas está no bloqueio R-S2
    res = selecionar_materiais((Tag.ANSIEDADE,), catalogo, {"m1"}, limite=3)
    assert "m1" not in [r.material_id for r in res]
    # Deve cair no fallback R-S6 e pegar m3
    assert res[0].regra == "R-S6"


def test_tu06_rs3_match_exato_de_tags(catalogo):
    res = selecionar_materiais((Tag.SONO,), catalogo, set(), limite=1)
    assert len(res) == 1
    assert res[0].material_id == "m2"
    assert res[0].regra == "R-S3"


def _material(material_id: str, *tags: str) -> MaterialCatalogo:
    return MaterialCatalogo(material_id, set(tags), f"Motivo {material_id}")


def test_tu06_rs1_respeita_a_ordem_de_prioridade_das_tags():
    # Catálogo e tags em ordem diferente da prioridade: ANSIEDADE, HUMOR, ESTRESSE, SONO.
    catalogo = [
        _material("sono", "sono"),
        _material("estresse", "estresse"),
        _material("humor", "humor"),
        _material("ansiedade", "ansiedade"),
    ]
    tags = (Tag.SONO, Tag.ESTRESSE, Tag.HUMOR, Tag.ANSIEDADE)

    res = selecionar_materiais(tags, catalogo, set(), limite=4)

    assert [r.material_id for r in res] == ["ansiedade", "humor", "estresse", "sono"]


def test_tu06_rs3_material_com_duas_tags_aparece_uma_vez():
    catalogo = [_material("m1", "ansiedade", "sono"), _material("m2", "sono")]

    res = selecionar_materiais((Tag.ANSIEDADE, Tag.SONO), catalogo, set(), limite=3)

    ids = [r.material_id for r in res]
    assert ids.count("m1") == 1
    assert sorted(ids) == ["m1", "m2"]


def test_tu06_rs4_maximo_de_tres_descarta_tags_de_menor_prioridade():
    catalogo = [
        _material("ansiedade", "ansiedade"),
        _material("humor", "humor"),
        _material("estresse", "estresse"),
        _material("sono", "sono"),
    ]
    tags = (Tag.ANSIEDADE, Tag.HUMOR, Tag.ESTRESSE, Tag.SONO)

    res = selecionar_materiais(tags, catalogo, set(), limite=3)

    assert [r.material_id for r in res] == ["ansiedade", "humor", "estresse"]


def test_tu06_rs4_limite_padrao_e_tres():
    catalogo = [_material(f"m{i}", "ansiedade") for i in range(5)]

    res = selecionar_materiais((Tag.ANSIEDADE,), catalogo, set())

    assert len(res) == 3
