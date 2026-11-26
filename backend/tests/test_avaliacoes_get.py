"""GET /api/avaliacoes e GET /api/avaliacoes/{id}, com o TS-03 (parte de avaliações).

Percorrem rota, serviço e consulta SQL reais no PostgreSQL de teste, sem repositório falso
(lição do DEF-05): remover o filtro por usuário em qualquer camada falha aqui.
"""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import update

from app.infrastructure.models import AvaliacaoModel
from app.seed_materiais import CAMINHO_CATALOGO, rodar_seed

URL = "/api/avaliacoes"
CAMPOS_ITEM = {"id", "data", "escore_phq9", "escore_gad7", "faixa_phq9", "faixa_gad7", "nivel"}
CAMPOS_RECOMENDACAO = {"titulo", "fonte", "resumo", "url", "regra", "motivo"}

# Perfis de referência (Visão v2.7, Quadro 19).
PERFIL_A = {"phq9": [0, 0, 0, 0, 0, 0, 0, 0, 0], "gad7": [0, 0, 0, 0, 0, 0, 0]}
PERFIL_B = {"phq9": [2, 2, 1, 1, 1, 1, 1, 1, 0], "gad7": [1, 1, 1, 1, 1, 0, 0]}
PERFIL_C = {"phq9": [3, 3, 2, 2, 2, 2, 2, 2, 0], "gad7": [3, 3, 2, 2, 2, 2, 1]}
PERFIL_D = {"phq9": [0, 0, 0, 0, 0, 0, 0, 0, 1], "gad7": [0, 0, 0, 0, 0, 0, 0]}


@pytest.fixture(autouse=True)
def catalogo_carregado(db_session):
    rodar_seed(db_session, CAMINHO_CATALOGO)


def _login(client, email: str) -> dict[str, str]:
    credentials = {"email": email, "senha": "senha-segura-123"}
    client.post(
        "/api/auth/cadastro", json={**credentials, "aceite_termos": True, "maior_de_idade": True}
    )
    token = client.post("/api/auth/login", json=credentials).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_a(client):
    return _login(client, "a@example.com")


@pytest.fixture
def user_b(client):
    return _login(client, "b@example.com")


def _create(client, headers, payload) -> dict:
    """Cria pela API e devolve o item mais recente da listagem do próprio usuário."""
    response = client.post(URL, json=payload, headers=headers)
    assert response.status_code == 201
    return client.get(URL, headers=headers).json()[0]


# --- GET /api/avaliacoes ---------------------------------------------------------------


def test_list_is_empty_without_avaliacoes(client, auth_headers):
    response = client.get(URL, headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_list_returns_item_fields_from_quadro_6(client, auth_headers):
    client.post(URL, json=PERFIL_B, headers=auth_headers)

    response = client.get(URL, headers=auth_headers)

    assert response.status_code == 200
    [item] = response.json()
    assert set(item) == CAMPOS_ITEM
    assert item["escore_phq9"] == 10
    assert item["escore_gad7"] == 5
    assert item["faixa_phq9"] == "moderada"
    assert item["faixa_gad7"] == "leve"
    assert item["nivel"] == "atencao"
    uuid.UUID(item["id"])
    datetime.strptime(item["data"], "%Y-%m-%d")


def test_list_does_not_expose_raw_answers(client, auth_headers):
    client.post(URL, json=PERFIL_B, headers=auth_headers)

    [item] = client.get(URL, headers=auth_headers).json()

    assert "phq9" not in item and "gad7" not in item
    assert not any(key.startswith("respostas") for key in item)


def test_list_returns_all_avaliacoes_most_recent_first(client, auth_headers, db_session):
    for payload in (PERFIL_A, PERFIL_B, PERFIL_C):
        assert client.post(URL, json=payload, headers=auth_headers).status_code == 201

    # Espaça as datas no banco para a ordem não depender da resolução do relógio.
    listing = client.get(URL, headers=auth_headers).json()
    base = datetime(2026, 11, 1, 15, 0, tzinfo=UTC)
    por_nivel = {item["nivel"]: item["id"] for item in listing}
    for dias, nivel in enumerate(("autocuidado", "atencao", "prioritario")):
        db_session.execute(
            update(AvaliacaoModel)
            .where(AvaliacaoModel.id == uuid.UUID(por_nivel[nivel]))
            .values(criado_em=base + timedelta(days=15 * dias))
        )
    db_session.commit()

    listing = client.get(URL, headers=auth_headers).json()

    assert [item["nivel"] for item in listing] == ["prioritario", "atencao", "autocuidado"]
    assert [item["data"] for item in listing] == ["2026-12-01", "2026-11-16", "2026-11-01"]


def test_list_data_uses_sao_paulo_date(client, auth_headers, db_session):
    item = _create(client, auth_headers, PERFIL_A)
    # 01:30 UTC de 02/11 ainda é 01/11 em America/Sao_Paulo (UTC-3).
    db_session.execute(
        update(AvaliacaoModel)
        .where(AvaliacaoModel.id == uuid.UUID(item["id"]))
        .values(criado_em=datetime(2026, 11, 2, 1, 30, tzinfo=UTC))
    )
    db_session.commit()

    [item] = client.get(URL, headers=auth_headers).json()

    assert item["data"] == "2026-11-01"


def test_list_requires_authentication(client):
    response = client.get(URL)

    assert response.status_code == 401


# --- GET /api/avaliacoes/{id} ----------------------------------------------------------


@pytest.mark.parametrize("payload", [PERFIL_A, PERFIL_B, PERFIL_C, PERFIL_D])
def test_detail_returns_same_body_as_post(client, auth_headers, payload):
    created = client.post(URL, json=payload, headers=auth_headers)
    assert created.status_code == 201
    [item] = client.get(URL, headers=auth_headers).json()

    response = client.get(f"{URL}/{item['id']}", headers=auth_headers)

    # DP-3: mesmos campos e valores da resposta de POST, incluindo as recomendações gravadas.
    assert response.status_code == 200
    assert response.json() == created.json()


def test_detail_returns_recorded_recommendations(client, auth_headers):
    created = client.post(URL, json=PERFIL_B, headers=auth_headers).json()
    [item] = client.get(URL, headers=auth_headers).json()

    body = client.get(f"{URL}/{item['id']}", headers=auth_headers).json()

    assert body["recomendacoes"]
    assert all(set(rec) == CAMPOS_RECOMENDACAO for rec in body["recomendacoes"])
    assert body["recomendacoes"] == created["recomendacoes"]
    assert body["orientacao"] == created["orientacao"]


def test_detail_does_not_regenerate_recommendations(client, auth_headers):
    """Uma nova avaliação não altera as recomendações já gravadas de uma anterior."""
    first = client.post(URL, json=PERFIL_A, headers=auth_headers).json()
    [item] = client.get(URL, headers=auth_headers).json()
    client.post(URL, json=PERFIL_A, headers=auth_headers)

    body = client.get(f"{URL}/{item['id']}", headers=auth_headers).json()

    assert body["recomendacoes"] == first["recomendacoes"]


def test_detail_crise_has_no_recommendations(client, auth_headers):
    item = _create(client, auth_headers, PERFIL_D)

    body = client.get(f"{URL}/{item['id']}", headers=auth_headers).json()

    assert body["nivel"] == "crise"
    assert body["recomendacoes"] == []


def test_detail_unknown_id_returns_404(client, auth_headers):
    response = client.get(f"{URL}/{uuid.uuid4()}", headers=auth_headers)

    assert response.status_code == 404
    assert response.json() == {"detail": "Avaliacao not found"}


def test_detail_invalid_id_returns_422(client, auth_headers):
    response = client.get(f"{URL}/nao-e-uuid", headers=auth_headers)

    assert response.status_code == 422


def test_detail_requires_authentication(client):
    response = client.get(f"{URL}/{uuid.uuid4()}")

    assert response.status_code == 401


# --- TS-03 (parte de avaliações): isolamento entre usuários ------------------------------


def test_ts03_user_b_gets_404_for_avaliacao_of_user_a(client, user_a, user_b):
    avaliacao_a = _create(client, user_a, PERFIL_C)

    response = client.get(f"{URL}/{avaliacao_a['id']}", headers=user_b)

    assert response.status_code == 404
    assert response.json() == {"detail": "Avaliacao not found"}


def test_ts03_404_for_other_user_matches_404_for_unknown_id(client, user_a, user_b):
    avaliacao_a = _create(client, user_a, PERFIL_C)

    other = client.get(f"{URL}/{avaliacao_a['id']}", headers=user_b)
    unknown = client.get(f"{URL}/{uuid.uuid4()}", headers=user_b)

    # A resposta não pode revelar se o id existe para outro usuário.
    assert other.status_code == unknown.status_code == 404
    assert other.json() == unknown.json()


def test_ts03_listing_of_user_b_does_not_contain_data_of_user_a(client, user_a, user_b):
    avaliacao_a = _create(client, user_a, PERFIL_C)

    assert client.get(URL, headers=user_b).json() == []

    avaliacao_b = _create(client, user_b, PERFIL_A)
    ids_a = [item["id"] for item in client.get(URL, headers=user_a).json()]
    ids_b = [item["id"] for item in client.get(URL, headers=user_b).json()]
    assert ids_a == [avaliacao_a["id"]]
    assert ids_b == [avaliacao_b["id"]]


def test_ts03_each_user_reads_only_own_avaliacao_by_id(client, user_a, user_b):
    avaliacao_a = _create(client, user_a, PERFIL_C)
    avaliacao_b = _create(client, user_b, PERFIL_A)

    assert client.get(f"{URL}/{avaliacao_a['id']}", headers=user_a).status_code == 200
    assert client.get(f"{URL}/{avaliacao_b['id']}", headers=user_b).status_code == 200
    assert client.get(f"{URL}/{avaliacao_b['id']}", headers=user_a).status_code == 404
    assert client.get(f"{URL}/{avaliacao_a['id']}", headers=user_b).status_code == 404


# --- Documentação ----------------------------------------------------------------------


def test_get_endpoints_are_documented_in_openapi(client):
    paths = client.get("/openapi.json").json()["paths"]

    listing = paths["/api/avaliacoes"]["get"]
    assert listing["tags"] == ["avaliacoes"]
    assert {"200", "401"} <= set(listing["responses"])
    assert listing["security"]

    detail = paths["/api/avaliacoes/{avaliacao_id}"]["get"]
    assert detail["tags"] == ["avaliacoes"]
    assert {"200", "401", "404"} <= set(detail["responses"])
    assert detail["security"]
