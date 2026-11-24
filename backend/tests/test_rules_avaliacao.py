"""Testes unitários das regras da avaliação quinzenal (PHQ-9 e GAD-7).

Cobre TU-01 a TU-04 (Quadro 26 da Visão) e os perfis de referência A a E (Quadro 19).
"""

import uuid
from datetime import UTC, date, datetime, timedelta
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_avaliacao_service, get_current_session
from app.application.auth import AuthenticatedSession
from app.application.avaliacoes import AvaliacaoService
from app.core.security import TokenClaims
from app.domain.avaliacao import ORIENTACAO_POR_NIVEL, Avaliacao, Faixa
from app.domain.checkin import Nivel, Tag
from app.domain.material import Material
from app.domain.recomendacao import Recomendacao
from app.domain.users import Role, User
from app.infrastructure.database import get_session
from app.main import app
from app.rules.avaliacao import (
    MOTIVO_POR_REGRA_E_TAG_AVALIACAO,
    decidir_avaliacao,
    faixa_gad7,
    faixa_phq9,
    limite_recomendacoes_avaliacao,
    orientacao_avaliacao,
    pontuar,
    tags_selecao_avaliacao,
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


def test_orientacao_limite_e_tags_selecao_quadro_18():
    assert orientacao_avaliacao(Nivel.CRISE) == ORIENTACAO_POR_NIVEL[Nivel.CRISE]
    assert orientacao_avaliacao(Nivel.PRIORITARIO) == ORIENTACAO_POR_NIVEL[Nivel.PRIORITARIO]
    assert orientacao_avaliacao(Nivel.ATENCAO) == ORIENTACAO_POR_NIVEL[Nivel.ATENCAO]
    assert orientacao_avaliacao(Nivel.AUTOCUIDADO) == ORIENTACAO_POR_NIVEL[Nivel.AUTOCUIDADO]

    assert limite_recomendacoes_avaliacao(Nivel.CRISE) == 0
    assert limite_recomendacoes_avaliacao(Nivel.PRIORITARIO) == 2
    assert limite_recomendacoes_avaliacao(Nivel.ATENCAO) == 3
    assert limite_recomendacoes_avaliacao(Nivel.AUTOCUIDADO) == 3

    res_d = decidir_avaliacao([0, 0, 0, 0, 0, 0, 0, 0, 1], [0] * 7)
    assert tags_selecao_avaliacao(res_d) == ()

    res_b = decidir_avaliacao([2, 2, 1, 1, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 0, 0])
    tags_b = tags_selecao_avaliacao(res_b)
    assert [(t.tag, t.regra, t.motivo) for t in tags_b] == [
        (
            Tag.AJUDA_PROFISSIONAL,
            "R-A3",
            MOTIVO_POR_REGRA_E_TAG_AVALIACAO[("R-A3", Tag.AJUDA_PROFISSIONAL)],
        ),
        (
            Tag.HUMOR,
            "R-A3",
            MOTIVO_POR_REGRA_E_TAG_AVALIACAO[("R-A3", Tag.HUMOR)],
        ),
    ]


class _FakeAvaliacaoRepository:
    def __init__(self) -> None:
        self.items: list[Avaliacao] = []

    def add(self, avaliacao: Avaliacao) -> None:
        self.items.append(avaliacao)

    def get_by_id_for_user(self, avaliacao_id: uuid.UUID, user_id: uuid.UUID) -> Avaliacao | None:
        for item in self.items:
            if item.id == avaliacao_id and item.user_id == user_id:
                return item
        return None

    def list_by_user(self, user_id: uuid.UUID, limit: int | None = None) -> list[Avaliacao]:
        owned = [item for item in self.items if item.user_id == user_id]
        return owned[:limit] if limit is not None else owned


class _FakeRecomendacaoRepository:
    def __init__(self) -> None:
        self.items: list[Recomendacao] = []
        self.materiais: list[Material] = [
            Material(
                id=1,
                slug="saude-mental-ms",
                titulo="Saúde Mental – Saúde de A a Z",
                url="https://www.gov.br/saude/saude-mental",
                fonte="Ministério da Saúde",
                resumo="Explica o que é saúde mental.",
                tags=[Tag.AJUDA_PROFISSIONAL, Tag.BEM_ESTAR],
                ativo=True,
                revisado_em=date(2026, 11, 9),
            ),
            Material(
                id=2,
                slug="depressao-ms",
                titulo="Depressão – Saúde de A a Z",
                url="https://www.gov.br/saude/depressao",
                fonte="Ministério da Saúde",
                resumo="Apresenta o que é a depressão.",
                tags=[Tag.HUMOR],
                ativo=True,
                revisado_em=date(2026, 11, 9),
            ),
            Material(
                id=3,
                slug="faca-o-que-importa-opas",
                titulo="Faça o que importa em tempos de estresse",
                url="https://www.paho.org/pt/documentos/faca-que-importa",
                fonte="OPAS/OMS",
                resumo="Guia ilustrado da OMS.",
                tags=[Tag.ANSIEDADE, Tag.ESTRESSE],
                ativo=True,
                revisado_em=date(2026, 11, 9),
            ),
        ]

    def add(self, recomendacao: Recomendacao) -> None:
        self.items.append(recomendacao)

    def add_all(self, recomendacoes) -> None:
        self.items.extend(recomendacoes)

    def list_by_checkin(self, checkin_id: uuid.UUID) -> list[Recomendacao]:
        return [r for r in self.items if r.checkin_id == checkin_id]

    def list_by_avaliacao(self, avaliacao_id: uuid.UUID) -> list[Recomendacao]:
        return [r for r in self.items if r.avaliacao_id == avaliacao_id]

    def get_last_displayed_by_user(self, user_id: uuid.UUID) -> dict[int, datetime]:
        return {}

    def list_active_materials(self) -> list[Material]:
        return [m for m in self.materiais if m.ativo]


@pytest.mark.parametrize(
    ("phq9", "gad7", "escore_p", "escore_g", "faixa_p", "faixa_g", "nivel", "regra", "n_recs"),
    [
        ([0] * 9, [0] * 7, 0, 0, "minima", "minima", "autocuidado", "R-A4", 1),
        (
            [2, 2, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 0, 0],
            10,
            5,
            "moderada",
            "leve",
            "atencao",
            "R-A3",
            2,
        ),
        (
            [3, 3, 2, 2, 2, 2, 2, 2, 0],
            [3, 3, 2, 2, 2, 2, 1],
            18,
            15,
            "moderadamente_grave",
            "grave",
            "prioritario",
            "R-A2",
            1,
        ),
        ([0, 0, 0, 0, 0, 0, 0, 0, 1], [0] * 7, 1, 0, "minima", "minima", "crise", "R-A1", 0),
        (
            [1, 1, 1, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 0],
            5,
            6,
            "leve",
            "leve",
            "autocuidado",
            "R-A4",
            2,
        ),
    ],
)
def test_api_post_avaliacoes_perfis_a_a_e_em_memoria(
    phq9, gad7, escore_p, escore_g, faixa_p, faixa_g, nivel, regra, n_recs
):
    user = User(id=uuid.uuid4(), email="u@example.com", password_hash="h", role=Role.USER)
    session = AuthenticatedSession(
        user=user,
        claims=TokenClaims(
            subject=user.id, jti="jti", expires_at=datetime.now(UTC) + timedelta(hours=1)
        ),
    )
    av_repo = _FakeAvaliacaoRepository()
    rec_repo = _FakeRecomendacaoRepository()
    service = AvaliacaoService(avaliacoes=av_repo, recomendacoes=rec_repo)

    app.dependency_overrides[get_session] = lambda: MagicMock()
    app.dependency_overrides[get_current_session] = lambda: session
    app.dependency_overrides[get_avaliacao_service] = lambda: service

    try:
        with TestClient(app) as test_client:
            resp = test_client.post("/api/avaliacoes", json={"phq9": phq9, "gad7": gad7})
            assert resp.status_code == 201
            body = resp.json()
            assert body["escore_phq9"] == escore_p
            assert body["escore_gad7"] == escore_g
            assert body["faixa_phq9"] == faixa_p
            assert body["faixa_gad7"] == faixa_g
            assert body["nivel"] == nivel
            assert body["orientacao"] == ORIENTACAO_POR_NIVEL[Nivel(nivel)]
            assert len(body["recomendacoes"]) == n_recs
            assert len(rec_repo.items) == n_recs
            assert all(r["regra"] == regra for r in body["recomendacoes"])
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize(
    "invalid_payload",
    [
        {"phq9": [0] * 8, "gad7": [0] * 7},
        {"phq9": [0] * 10, "gad7": [0] * 7},
        {"phq9": [0] * 9, "gad7": [0] * 6},
        {"phq9": [4, 0, 0, 0, 0, 0, 0, 0, 0], "gad7": [0] * 7},
        {"phq9": [-1, 0, 0, 0, 0, 0, 0, 0, 0], "gad7": [0] * 7},
        {"phq9": [0] * 9, "gad7": [0, 0, 0, 0, 0, 0, 4]},
        {"phq9": [0] * 9, "gad7": [0, 0, 0, 0, 0, 0, -1]},
        {"phq9": [True, 0, 0, 0, 0, 0, 0, 0, 0], "gad7": [0] * 7},
    ],
)
def test_api_post_avaliacoes_entradas_invalidas_retornam_422_em_memoria(invalid_payload):
    user = User(id=uuid.uuid4(), email="u@example.com", password_hash="h", role=Role.USER)
    session = AuthenticatedSession(
        user=user,
        claims=TokenClaims(
            subject=user.id, jti="jti", expires_at=datetime.now(UTC) + timedelta(hours=1)
        ),
    )
    service = AvaliacaoService(
        avaliacoes=_FakeAvaliacaoRepository(),
        recomendacoes=_FakeRecomendacaoRepository(),
    )

    app.dependency_overrides[get_session] = lambda: MagicMock()
    app.dependency_overrides[get_current_session] = lambda: session
    app.dependency_overrides[get_avaliacao_service] = lambda: service

    try:
        with TestClient(app) as test_client:
            resp = test_client.post("/api/avaliacoes", json=invalid_payload)
            assert resp.status_code == 422
    finally:
        app.dependency_overrides.clear()
