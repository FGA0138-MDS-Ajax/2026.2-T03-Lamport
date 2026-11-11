"""TS-03 (parte de check-ins) no banco de teste: isolamento entre usuários.

Os testes de `test_checkins_get.py` usam repositório falso. Estes percorrem rota, serviço
e consulta SQL reais, de modo que remover o filtro por usuário em qualquer camada falha aqui.
A parte de avaliações do TS-03 depende do endpoint `/api/avaliacoes` (Sprint 5).
"""

import uuid

import pytest

CHECKINS = "/api/checkins"
CHECKIN_A = {"p1": 4, "p2": 3, "p3": 1, "p4": 0, "p5": False}
CHECKIN_B = {"p1": 2, "p2": 1, "p3": 3, "p4": 2, "p5": False}


def _login(client, email: str) -> dict[str, str]:
    credentials = {"email": email, "password": "senha-segura-123"}
    client.post(
        "/api/auth/cadastro", json={**credentials, "accept_terms": True, "maior_de_idade": True}
    )
    token = client.post("/api/auth/login", json=credentials).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_a(client):
    return _login(client, "a@example.com")


@pytest.fixture
def user_b(client):
    return _login(client, "b@example.com")


def _create(client, headers, payload) -> str:
    response = client.post(CHECKINS, json=payload, headers=headers)
    assert response.status_code == 201
    listing = client.get(CHECKINS, headers=headers).json()
    assert len(listing) == 1
    return listing[0]["id"]


def test_ts03_user_b_gets_404_for_checkin_of_user_a(client, user_a, user_b):
    checkin_a = _create(client, user_a, CHECKIN_A)

    response = client.get(f"{CHECKINS}/{checkin_a}", headers=user_b)

    assert response.status_code == 404
    assert response.json() == {"detail": "Check-in not found"}


def test_ts03_404_for_other_user_matches_404_for_unknown_id(client, user_a, user_b):
    checkin_a = _create(client, user_a, CHECKIN_A)

    other = client.get(f"{CHECKINS}/{checkin_a}", headers=user_b)
    unknown = client.get(f"{CHECKINS}/{uuid.uuid4()}", headers=user_b)

    # A resposta não pode revelar se o id existe para outro usuário.
    assert other.status_code == unknown.status_code == 404
    assert other.json() == unknown.json()


def test_ts03_listing_of_user_b_does_not_contain_data_of_user_a(client, user_a, user_b):
    checkin_a = _create(client, user_a, CHECKIN_A)

    assert client.get(CHECKINS, headers=user_b).json() == []

    checkin_b = _create(client, user_b, CHECKIN_B)
    ids_b = [item["id"] for item in client.get(CHECKINS, headers=user_b).json()]
    ids_a = [item["id"] for item in client.get(CHECKINS, headers=user_a).json()]
    assert ids_b == [checkin_b]
    assert ids_a == [checkin_a]


def test_ts03_each_user_reads_only_own_checkin_by_id(client, user_a, user_b):
    checkin_a = _create(client, user_a, CHECKIN_A)
    checkin_b = _create(client, user_b, CHECKIN_B)

    assert client.get(f"{CHECKINS}/{checkin_a}", headers=user_a).status_code == 200
    assert client.get(f"{CHECKINS}/{checkin_b}", headers=user_b).status_code == 200
    assert client.get(f"{CHECKINS}/{checkin_b}", headers=user_a).status_code == 404
    assert client.get(f"{CHECKINS}/{checkin_a}", headers=user_b).status_code == 404


def test_ts03_today_of_user_b_is_not_the_checkin_of_user_a(client, user_a, user_b):
    _create(client, user_a, CHECKIN_A)

    assert client.get(f"{CHECKINS}/hoje", headers=user_b).status_code == 404
