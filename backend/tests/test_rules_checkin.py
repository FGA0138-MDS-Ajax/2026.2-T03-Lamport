import pytest

from app.domain.checkin import Nivel, Tag
from app.rules.checkin import avaliar_checkin


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
