import logging
from datetime import UTC, datetime

import pytest
from sqlalchemy import select

from app.domain.avaliacao import ORIENTACAO_POR_NIVEL, Faixa
from app.domain.checkin import Nivel, Tag
from app.infrastructure.models import (
    AvaliacaoModel,
    MaterialModel,
    RecomendacaoModel,
    UserModel,
)
from app.rules.avaliacao import MOTIVO_POR_REGRA_E_TAG_AVALIACAO
from app.seed_materiais import CAMINHO_CATALOGO, rodar_seed

URL = "/api/avaliacoes"
CAMPOS_RECOMENDACAO = {"titulo", "fonte", "resumo", "url", "regra", "motivo"}

# Perfis de referência A a E (Visão v2.7, Quadro 19).
PERFIL_A = {"phq9": [0, 0, 0, 0, 0, 0, 0, 0, 0], "gad7": [0, 0, 0, 0, 0, 0, 0]}
PERFIL_B = {"phq9": [2, 2, 1, 1, 1, 1, 1, 1, 0], "gad7": [1, 1, 1, 1, 1, 0, 0]}
PERFIL_C = {"phq9": [3, 3, 2, 2, 2, 2, 2, 2, 0], "gad7": [3, 3, 2, 2, 2, 2, 1]}
PERFIL_D = {"phq9": [0, 0, 0, 0, 0, 0, 0, 0, 1], "gad7": [0, 0, 0, 0, 0, 0, 0]}
PERFIL_E = {"phq9": [1, 1, 1, 1, 1, 0, 0, 0, 0], "gad7": [1, 1, 1, 1, 1, 1, 0]}


@pytest.fixture(autouse=True)
def catalogo_carregado(db_session):
    rodar_seed(db_session, CAMINHO_CATALOGO)


def _avaliacoes(db_session) -> list[AvaliacaoModel]:
    return list(db_session.scalars(select(AvaliacaoModel)))


def _recomendacoes(db_session) -> list[RecomendacaoModel]:
    return list(
        db_session.scalars(
            select(RecomendacaoModel).order_by(
                RecomendacaoModel.criado_em.asc(), RecomendacaoModel.id.asc()
            )
        )
    )


@pytest.mark.parametrize(
    (
        "nome_perfil",
        "payload",
        "escore_phq9",
        "escore_gad7",
        "faixa_phq9",
        "faixa_gad7",
        "nivel",
        "regra_esperada",
        "tags_esperadas",
    ),
    [
        (
            "A",
            PERFIL_A,
            0,
            0,
            Faixa.MINIMA,
            Faixa.MINIMA,
            Nivel.AUTOCUIDADO,
            "R-A4",
            (Tag.BEM_ESTAR,),
        ),
        (
            "B",
            PERFIL_B,
            10,
            5,
            Faixa.MODERADA,
            Faixa.LEVE,
            Nivel.ATENCAO,
            "R-A3",
            (Tag.AJUDA_PROFISSIONAL, Tag.HUMOR),
        ),
        (
            "C",
            PERFIL_C,
            18,
            15,
            Faixa.MODERADAMENTE_GRAVE,
            Faixa.GRAVE,
            Nivel.PRIORITARIO,
            "R-A2",
            (Tag.AJUDA_PROFISSIONAL,),
        ),
        (
            "D",
            PERFIL_D,
            1,
            0,
            Faixa.MINIMA,
            Faixa.MINIMA,
            Nivel.CRISE,
            "R-A1",
            (),
        ),
        (
            "E",
            PERFIL_E,
            5,
            6,
            Faixa.LEVE,
            Faixa.LEVE,
            Nivel.AUTOCUIDADO,
            "R-A4",
            (Tag.ANSIEDADE, Tag.HUMOR),
        ),
    ],
)
def test_ti06_perfis_a_a_e_quadro_19_persistem_avaliacao_e_recomendacoes(
    client,
    auth_headers,
    db_session,
    nome_perfil,
    payload,
    escore_phq9,
    escore_gad7,
    faixa_phq9,
    faixa_gad7,
    nivel,
    regra_esperada,
    tags_esperadas,
):
    me = client.get("/api/me", headers=auth_headers).json()

    response = client.post(URL, json=payload, headers=auth_headers)

    assert response.status_code == 201, f"Perfil {nome_perfil} falhou"
    body = response.json()
    assert body["escore_phq9"] == escore_phq9
    assert body["escore_gad7"] == escore_gad7
    assert body["faixa_phq9"] == faixa_phq9.value
    assert body["faixa_gad7"] == faixa_gad7.value
    assert body["nivel"] == nivel.value
    assert body["orientacao"] == ORIENTACAO_POR_NIVEL[nivel]

    # Confere a avaliação persistida no banco PostgreSQL de teste.
    [avaliacao] = _avaliacoes(db_session)
    assert str(avaliacao.user_id) == me["id"]
    assert avaliacao.respostas_phq9 == payload["phq9"]
    assert avaliacao.respostas_gad7 == payload["gad7"]
    assert avaliacao.escore_phq9 == escore_phq9
    assert avaliacao.escore_gad7 == escore_gad7
    assert avaliacao.faixa_phq9 == faixa_phq9.value
    assert avaliacao.faixa_gad7 == faixa_gad7.value
    assert avaliacao.nivel == nivel.value

    recs_resposta = body["recomendacoes"]
    recs_banco = _recomendacoes(db_session)

    if nivel == Nivel.CRISE:
        # Perfil D (R-A1): sem recomendações na resposta nem no banco.
        assert recs_resposta == []
        assert recs_banco == []
        return

    if nivel == Nivel.PRIORITARIO:
        # Perfil C (R-A2): no máximo 2 materiais, todos de AJUDA_PROFISSIONAL (R-S4).
        assert 1 <= len(recs_resposta) <= 2

    assert len(recs_resposta) == len(tags_esperadas)
    assert len(recs_banco) == len(tags_esperadas)

    for rec_db, rec_api, tag_esperada in zip(
        recs_banco, recs_resposta, tags_esperadas, strict=True
    ):
        motivo_esperado = MOTIVO_POR_REGRA_E_TAG_AVALIACAO[(regra_esperada, tag_esperada)]
        assert set(rec_api) == CAMPOS_RECOMENDACAO
        assert rec_db.avaliacao_id == avaliacao.id
        assert rec_db.checkin_id is None
        assert str(rec_db.user_id) == me["id"]
        assert rec_db.regra == regra_esperada
        assert rec_db.motivo == motivo_esperado

        material = db_session.get(MaterialModel, rec_db.material_id)
        assert material is not None
        assert material.ativo is True
        assert tag_esperada.value in material.tags
        assert rec_api == {
            "titulo": material.titulo,
            "fonte": material.fonte,
            "resumo": material.resumo,
            "url": material.url,
            "regra": regra_esperada,
            "motivo": motivo_esperado,
        }


def test_rs2_avaliacao_rotaciona_materiais_com_ultimas_exibicoes(client, auth_headers, db_session):
    me = client.get("/api/me", headers=auth_headers).json()
    user = db_session.scalar(select(UserModel).where(UserModel.email == me["email"]))
    primeiro_ajuda = db_session.scalar(
        select(MaterialModel).where(MaterialModel.slug == "saude-mental-ms")
    )
    segundo_ajuda = db_session.scalar(
        select(MaterialModel).where(MaterialModel.slug == "sus-saude-mental-ms")
    )
    # Marca o primeiro material de ajuda_profissional como já exibido antes.
    db_session.add(
        RecomendacaoModel(
            user_id=user.id,
            material_id=primeiro_ajuda.id,
            regra="R-A2",
            motivo=MOTIVO_POR_REGRA_E_TAG_AVALIACAO[("R-A2", Tag.AJUDA_PROFISSIONAL)],
            criado_em=datetime(2026, 11, 10, 12, 0, tzinfo=UTC),
        )
    )
    db_session.commit()

    response = client.post(URL, json=PERFIL_C, headers=auth_headers)

    assert response.status_code == 201
    recs = response.json()["recomendacoes"]
    assert len(recs) == 1
    assert recs[0]["titulo"] == segundo_ajuda.titulo
    assert recs[0]["regra"] == "R-A2"


@pytest.mark.parametrize(
    "invalid_payload",
    [
        {"phq9": [0] * 8, "gad7": [0] * 7},  # PHQ-9 com menos de 9 itens
        {"phq9": [0] * 10, "gad7": [0] * 7},  # PHQ-9 com mais de 9 itens
        {"phq9": [0] * 9, "gad7": [0] * 6},  # GAD-7 com menos de 7 itens
        {"phq9": [0] * 9, "gad7": [0] * 8},  # GAD-7 com mais de 7 itens
        {"phq9": [4, 0, 0, 0, 0, 0, 0, 0, 0], "gad7": [0] * 7},  # valor 4 no PHQ-9
        {"phq9": [-1, 0, 0, 0, 0, 0, 0, 0, 0], "gad7": [0] * 7},  # valor -1 no PHQ-9
        {"phq9": [0] * 9, "gad7": [0, 0, 0, 0, 0, 0, 4]},  # valor 4 no GAD-7
        {"phq9": [0] * 9, "gad7": [0, 0, 0, 0, 0, 0, -1]},  # valor -1 no GAD-7
        {"phq9": [True, 0, 0, 0, 0, 0, 0, 0, 0], "gad7": [0] * 7},  # bool no PHQ-9
        {"phq9": ["0", 0, 0, 0, 0, 0, 0, 0, 0], "gad7": [0] * 7},  # str no PHQ-9
        {"phq9": [1.5, 0, 0, 0, 0, 0, 0, 0, 0], "gad7": [0] * 7},  # float no PHQ-9
        {"phq9": [None, 0, 0, 0, 0, 0, 0, 0, 0], "gad7": [0] * 7},  # None no PHQ-9
        {"phq9": [0] * 9},  # gad7 ausente
        {"gad7": [0] * 7},  # phq9 ausente
        {},  # ambos ausentes
        {**PERFIL_A, "nivel": "crise"},  # campo extra proibido
        {**PERFIL_A, "user_id": "00000000-0000-0000-0000-000000000000"},
    ],
)
def test_invalid_avaliacao_payload_returns_422(client, auth_headers, db_session, invalid_payload):
    response = client.post(URL, json=invalid_payload, headers=auth_headers)

    assert response.status_code == 422
    assert _avaliacoes(db_session) == []
    assert _recomendacoes(db_session) == []


def test_avaliacao_requires_authentication(client, db_session):
    response = client.post(URL, json=PERFIL_A)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert _avaliacoes(db_session) == []


def test_authentication_is_checked_before_validation(client):
    response = client.post(URL, json={"phq9": [99]})

    assert response.status_code == 401


def test_avaliacao_content_is_not_logged(client, auth_headers, db_session, caplog):
    with caplog.at_level(logging.DEBUG):
        response = client.post(URL, json=PERFIL_B, headers=auth_headers)

    assert response.status_code == 201
    [avaliacao] = _avaliacoes(db_session)
    assert str(avaliacao.id) in caplog.text
    sensitive = ("respostas_phq9", "respostas_gad7", "moderada", "atencao", "prioritario")
    assert not any(word in caplog.text for word in sensitive)


def test_avaliacoes_endpoint_is_documented_in_openapi(client):
    paths = client.get("/openapi.json").json()["paths"]

    create = paths["/api/avaliacoes"]["post"]
    assert create["tags"] == ["avaliacoes"]
    assert {"201", "401", "422"} <= set(create["responses"])
    assert create["security"]
