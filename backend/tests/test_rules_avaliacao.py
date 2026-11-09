"""Testes unitários das regras da avaliação quinzenal (PHQ-9 e GAD-7).

Cobre TU-01 a TU-04 (Quadro 26 da Visão) e os perfis de referência A a E (Quadro 19).
"""

import pytest

from app.domain.avaliacao import Faixa
from app.domain.checkin import Nivel, Tag
from app.rules.avaliacao import (
    decidir_avaliacao,
    faixa_gad7,
    faixa_phq9,
    pontuar,
)


# Sobrescreve fixtures de banco do conftest.py para testes unitários puros de regras.
@pytest.fixture(scope="session", autouse=True)
def database():
    yield


@pytest.fixture(autouse=True)
def clean_tables():
    yield


# ==============================================================================
# TU-01: Pontuação do PHQ-9 e do GAD-7
# ==============================================================================
def test_tu01_pontuar_todos_zeros():
    assert pontuar([0] * 9, 9) == 0
    assert pontuar([0] * 7, 7) == 0


def test_tu01_pontuar_todos_tres():
    assert pontuar([3] * 9, 9) == 27
    assert pontuar([3] * 7, 7) == 21


def test_tu01_pontuar_misto_phq9():
    misto = [0, 1, 2, 3, 0, 1, 2, 3, 1]
    assert pontuar(misto, 9) == 13


@pytest.mark.parametrize(
    ("respostas", "n_itens"),
    [
        ([0] * 8, 9),  # Menos de 9 itens para PHQ-9
        ([0] * 10, 9),  # Mais de 9 itens para PHQ-9
        ([0] * 6, 7),  # Menos de 7 itens para GAD-7
        ([0] * 8, 7),  # Mais de 7 itens para GAD-7
        ([0, 1, 2, 4, 0, 0, 0, 0, 0], 9),  # Valor acima do máximo (4)
        ([0, 1, -1, 2, 0, 0, 0, 0, 0], 9),  # Valor negativo (-1)
        ([0, 0, 0, 0, 0, 0, 4], 7),  # Valor 4 no GAD-7
        ([0, 0, 0, 0, 0, 0, -1], 7),  # Valor -1 no GAD-7
        ([0, 1, True, 0, 0, 0, 0], 7),  # Booleano rejeitado
    ],
)
def test_tu01_pontuar_entradas_invalidas_lancam_value_error(respostas, n_itens):
    with pytest.raises(ValueError):
        pontuar(respostas, n_itens)


# ==============================================================================
# TU-02: Faixas do PHQ-9 nos valores-limite
# ==============================================================================
@pytest.mark.parametrize(
    ("escore", "faixa_esperada"),
    [
        (0, Faixa.MINIMA),
        (4, Faixa.MINIMA),
        (5, Faixa.LEVE),
        (9, Faixa.LEVE),
        (10, Faixa.MODERADA),
        (14, Faixa.MODERADA),
        (15, Faixa.MODERADAMENTE_GRAVE),
        (19, Faixa.MODERADAMENTE_GRAVE),
        (20, Faixa.GRAVE),
        (27, Faixa.GRAVE),
    ],
)
def test_tu02_faixas_phq9_limites(escore, faixa_esperada):
    assert faixa_phq9(escore) == faixa_esperada


@pytest.mark.parametrize("escore_invalido", [-1, 28, 100])
def test_tu02_faixa_phq9_valores_fora_da_faixa(escore_invalido):
    with pytest.raises(ValueError):
        faixa_phq9(escore_invalido)


# ==============================================================================
# TU-03: Faixas do GAD-7 nos valores-limite
# ==============================================================================
@pytest.mark.parametrize(
    ("escore", "faixa_esperada"),
    [
        (0, Faixa.MINIMA),
        (4, Faixa.MINIMA),
        (5, Faixa.LEVE),
        (9, Faixa.LEVE),
        (10, Faixa.MODERADA),
        (14, Faixa.MODERADA),
        (15, Faixa.GRAVE),
        (21, Faixa.GRAVE),
    ],
)
def test_tu03_faixas_gad7_limites(escore, faixa_esperada):
    assert faixa_gad7(escore) == faixa_esperada


@pytest.mark.parametrize("escore_invalido", [-1, 22, 50])
def test_tu03_faixa_gad7_valores_fora_da_faixa(escore_invalido):
    with pytest.raises(ValueError):
        faixa_gad7(escore_invalido)


# ==============================================================================
# TU-04: Tabela de decisão da avaliação (Quadro 26 e Quadro 18)
# ==============================================================================
def test_tu04_caso1_item9_precedencia():
    # item 9 = 1, PHQ-9 = 3 (itens 1 a 2 valem 1, item 9 vale 1), GAD-7 = 0
    phq9 = [1, 1, 0, 0, 0, 0, 0, 0, 1]
    gad7 = [0] * 7
    resultado = decidir_avaliacao(phq9, gad7)

    assert resultado.escore_phq9 == 3
    assert resultado.escore_gad7 == 0
    assert resultado.nivel == Nivel.CRISE
    assert resultado.tags == ()
    assert resultado.regras == ("R-A1",)


def test_tu04_caso2_phq9_grave():
    # PHQ-9 = 20 (itens 1..6 = 3, item 7 = 2, item 9 = 0), GAD-7 = 0
    phq9 = [3, 3, 3, 3, 3, 3, 2, 0, 0]
    gad7 = [0] * 7
    resultado = decidir_avaliacao(phq9, gad7)

    assert resultado.escore_phq9 == 20
    assert resultado.escore_gad7 == 0
    assert resultado.nivel == Nivel.PRIORITARIO
    assert resultado.tags == (Tag.AJUDA_PROFISSIONAL,)
    assert resultado.regras == ("R-A2",)


def test_tu04_caso3_gad7_grave():
    # PHQ-9 = 5 (sem item 9), GAD-7 = 15
    phq9 = [1, 1, 1, 1, 1, 0, 0, 0, 0]
    gad7 = [3, 3, 3, 3, 3, 0, 0]
    resultado = decidir_avaliacao(phq9, gad7)

    assert resultado.escore_phq9 == 5
    assert resultado.escore_gad7 == 15
    assert resultado.nivel == Nivel.PRIORITARIO
    assert resultado.tags == (Tag.AJUDA_PROFISSIONAL,)
    assert resultado.regras == ("R-A2",)


def test_tu04_caso4_phq9_atencao():
    # PHQ-9 = 10, GAD-7 = 0
    phq9 = [2, 2, 2, 2, 2, 0, 0, 0, 0]
    gad7 = [0] * 7
    resultado = decidir_avaliacao(phq9, gad7)

    assert resultado.escore_phq9 == 10
    assert resultado.escore_gad7 == 0
    assert resultado.nivel == Nivel.ATENCAO
    assert resultado.tags == (Tag.AJUDA_PROFISSIONAL, Tag.HUMOR)
    assert resultado.regras == ("R-A3",)


def test_tu04_caso5_gad7_atencao():
    # PHQ-9 = 0, GAD-7 = 10
    phq9 = [0] * 9
    gad7 = [2, 2, 2, 2, 2, 0, 0]
    resultado = decidir_avaliacao(phq9, gad7)

    assert resultado.escore_phq9 == 0
    assert resultado.escore_gad7 == 10
    assert resultado.nivel == Nivel.ATENCAO
    assert resultado.tags == (Tag.AJUDA_PROFISSIONAL, Tag.ANSIEDADE)
    assert resultado.regras == ("R-A3",)


def test_tu04_caso6_ambos_atencao():
    # PHQ-9 = 19 (item 9 = 0), GAD-7 = 14
    # PHQ-9: 3*6 + 1 = 19
    phq9 = [3, 3, 3, 3, 3, 3, 1, 0, 0]
    # GAD-7: 3*4 + 2 = 14
    gad7 = [3, 3, 3, 3, 2, 0, 0]
    resultado = decidir_avaliacao(phq9, gad7)

    assert resultado.escore_phq9 == 19
    assert resultado.escore_gad7 == 14
    assert resultado.nivel == Nivel.ATENCAO
    # Ordem R-S1: AJUDA_PROFISSIONAL -> ANSIEDADE -> HUMOR
    assert resultado.tags == (Tag.AJUDA_PROFISSIONAL, Tag.ANSIEDADE, Tag.HUMOR)
    assert resultado.regras == ("R-A3",)


def test_tu04_caso7_autocuidado_ambos_leves():
    # PHQ-9 = 9, GAD-7 = 9
    phq9 = [2, 2, 2, 2, 1, 0, 0, 0, 0]
    gad7 = [2, 2, 2, 2, 1, 0, 0]
    resultado = decidir_avaliacao(phq9, gad7)

    assert resultado.escore_phq9 == 9
    assert resultado.escore_gad7 == 9
    assert resultado.nivel == Nivel.AUTOCUIDADO
    assert resultado.tags == (Tag.ANSIEDADE, Tag.HUMOR)
    assert resultado.regras == ("R-A4",)


def test_tu04_caso8_autocuidado_ambos_minimos():
    # PHQ-9 = 4, GAD-7 = 4
    phq9 = [1, 1, 1, 1, 0, 0, 0, 0, 0]
    gad7 = [1, 1, 1, 1, 0, 0, 0]
    resultado = decidir_avaliacao(phq9, gad7)

    assert resultado.escore_phq9 == 4
    assert resultado.escore_gad7 == 4
    assert resultado.nivel == Nivel.AUTOCUIDADO
    assert resultado.tags == (Tag.BEM_ESTAR,)
    assert resultado.regras == ("R-A4",)


def test_tu04_ra1_prevalece_sobre_todas():
    # Mesmo com escores muito altos que acionariam R-A2, item 9 = 1 aciona R-A1 (CRISE).
    phq9 = [3, 3, 3, 3, 3, 3, 3, 3, 1]  # 25, item 9 = 1
    gad7 = [3, 3, 3, 3, 3, 3, 3]  # 21
    resultado = decidir_avaliacao(phq9, gad7)

    assert resultado.nivel == Nivel.CRISE
    assert resultado.tags == ()
    assert resultado.regras == ("R-A1",)


# ==============================================================================
# Quadro 19 – Perfis de respostas de referência (A a E)
# ==============================================================================
def test_perfil_a():
    phq9 = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    gad7 = [0, 0, 0, 0, 0, 0, 0]
    resultado = decidir_avaliacao(phq9, gad7)

    assert (resultado.escore_phq9, resultado.escore_gad7) == (0, 0)
    assert (resultado.faixa_phq9, resultado.faixa_gad7) == (Faixa.MINIMA, Faixa.MINIMA)
    assert resultado.nivel == Nivel.AUTOCUIDADO
    assert resultado.tags == (Tag.BEM_ESTAR,)
    assert resultado.regras == ("R-A4",)


def test_perfil_b():
    phq9 = [2, 2, 1, 1, 1, 1, 1, 1, 0]
    gad7 = [1, 1, 1, 1, 1, 0, 0]
    resultado = decidir_avaliacao(phq9, gad7)

    assert (resultado.escore_phq9, resultado.escore_gad7) == (10, 5)
    assert (resultado.faixa_phq9, resultado.faixa_gad7) == (Faixa.MODERADA, Faixa.LEVE)
    assert resultado.nivel == Nivel.ATENCAO
    assert resultado.tags == (Tag.AJUDA_PROFISSIONAL, Tag.HUMOR)
    assert resultado.regras == ("R-A3",)


def test_perfil_c():
    phq9 = [3, 3, 2, 2, 2, 2, 2, 2, 0]
    gad7 = [3, 3, 2, 2, 2, 2, 1]
    resultado = decidir_avaliacao(phq9, gad7)

    assert (resultado.escore_phq9, resultado.escore_gad7) == (18, 15)
    assert (resultado.faixa_phq9, resultado.faixa_gad7) == (
        Faixa.MODERADAMENTE_GRAVE,
        Faixa.GRAVE,
    )
    assert resultado.nivel == Nivel.PRIORITARIO
    assert resultado.tags == (Tag.AJUDA_PROFISSIONAL,)
    assert resultado.regras == ("R-A2",)


def test_perfil_d():
    phq9 = [0, 0, 0, 0, 0, 0, 0, 0, 1]
    gad7 = [0, 0, 0, 0, 0, 0, 0]
    resultado = decidir_avaliacao(phq9, gad7)

    assert (resultado.escore_phq9, resultado.escore_gad7) == (1, 0)
    assert (resultado.faixa_phq9, resultado.faixa_gad7) == (Faixa.MINIMA, Faixa.MINIMA)
    assert resultado.nivel == Nivel.CRISE
    assert resultado.tags == ()
    assert resultado.regras == ("R-A1",)


def test_perfil_e():
    phq9 = [1, 1, 1, 1, 1, 0, 0, 0, 0]
    gad7 = [1, 1, 1, 1, 1, 1, 0]
    resultado = decidir_avaliacao(phq9, gad7)

    assert (resultado.escore_phq9, resultado.escore_gad7) == (5, 6)
    assert (resultado.faixa_phq9, resultado.faixa_gad7) == (Faixa.LEVE, Faixa.LEVE)
    assert resultado.nivel == Nivel.AUTOCUIDADO
    assert resultado.tags == (Tag.ANSIEDADE, Tag.HUMOR)
    assert resultado.regras == ("R-A4",)
