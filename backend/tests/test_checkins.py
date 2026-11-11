import logging

import pytest
from sqlalchemy import select

from app.application.checkins import today_in_checkin_timezone
from app.infrastructure.database import get_engine
from app.infrastructure.models import CheckinModel

URL = "/api/checkins"
TODAY_URL = "/api/checkins/hoje"

# Respostas do TI-03.
VALID_PAYLOAD = {"p1": 4, "p2": 3, "p3": 1, "p4": 0, "p5": False}


def _checkins(db_session) -> list[CheckinModel]:
    return list(db_session.scalars(select(CheckinModel)))


def test_ti03_create_checkin_returns_201_with_nivel_and_tags(client, auth_headers):
    response = client.post(URL, json=VALID_PAYLOAD, headers=auth_headers)

    assert response.status_code == 201
    assert response.json() == {"nivel": "autocuidado", "tags": ["ansiedade", "sono"]}


def test_checkin_is_saved_for_authenticated_user(client, auth_headers, db_session):
    me = client.get("/api/me", headers=auth_headers).json()

    client.post(URL, json=VALID_PAYLOAD, headers=auth_headers)

    [checkin] = _checkins(db_session)
    assert str(checkin.user_id) == me["id"]
    assert checkin.data == today_in_checkin_timezone()
    assert (checkin.humor, checkin.ansiedade, checkin.sono, checkin.sobrecarga) == (4, 3, 1, 0)
    assert checkin.pensamento_risco is False
    assert checkin.nivel == "autocuidado"
    assert checkin.tags == ["ansiedade", "sono"]


def test_ti05_risk_answer_returns_crise_without_tags(client, auth_headers):
    payload = {"p1": 2, "p2": None, "p3": None, "p4": None, "p5": True}

    response = client.post(URL, json=payload, headers=auth_headers)

    assert response.status_code == 201
    assert response.json() == {"nivel": "crise", "tags": []}


def test_only_p5_is_required(client, auth_headers, db_session):
    response = client.post(URL, json={"p5": False}, headers=auth_headers)

    assert response.status_code == 201
    assert response.json()["tags"] == ["bem_estar"]
    [checkin] = _checkins(db_session)
    assert (checkin.humor, checkin.ansiedade, checkin.sono, checkin.sobrecarga) == (
        None,
        None,
        None,
        None,
    )


def test_ti04_second_checkin_on_same_day_returns_409(client, auth_headers, db_session):
    client.post(URL, json=VALID_PAYLOAD, headers=auth_headers)

    response = client.post(URL, json=VALID_PAYLOAD, headers=auth_headers)

    assert response.status_code == 409
    assert response.json() == {"detail": "Check-in already done today"}
    assert len(_checkins(db_session)) == 1


def test_other_user_can_checkin_on_same_day(client, auth_headers, db_session):
    client.post(URL, json=VALID_PAYLOAD, headers=auth_headers)
    other = {"email": "bia@example.com", "senha": "senha-segura-123"}
    client.post("/api/auth/cadastro", json={**other, "aceite_termos": True, "maior_de_idade": True})
    token = client.post("/api/auth/login", json=other).json()["access_token"]

    response = client.post(URL, json=VALID_PAYLOAD, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 201
    assert len(_checkins(db_session)) == 2


@pytest.mark.parametrize(
    "changes",
    [
        {"p1": 0},
        {"p1": 6},
        {"p3": 0},
        {"p3": 6},
        {"p2": -1},
        {"p2": 4},
        {"p4": -1},
        {"p4": 4},
        {"p1": "4"},
        {"p1": 3.5},
        {"p1": "alta"},
        {"p5": None},
        {"p5": "sim"},
        {"p5": 1},
    ],
)
def test_invalid_values_return_422(client, auth_headers, db_session, changes):
    response = client.post(URL, json={**VALID_PAYLOAD, **changes}, headers=auth_headers)

    assert response.status_code == 422
    assert _checkins(db_session) == []


def test_missing_p5_returns_422(client, auth_headers):
    payload = {key: value for key, value in VALID_PAYLOAD.items() if key != "p5"}

    response = client.post(URL, json=payload, headers=auth_headers)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "extra",
    [
        {"user_id": "00000000-0000-0000-0000-000000000000"},
        {"nivel": "crise"},
        {"tags": ["humor"]},
        {"humor": 4},
        {"pensamento_risco": False},
    ],
)
def test_unknown_fields_are_rejected(client, auth_headers, db_session, extra):
    response = client.post(URL, json={**VALID_PAYLOAD, **extra}, headers=auth_headers)

    assert response.status_code == 422
    assert _checkins(db_session) == []


def test_today_returns_checkin_of_the_day(client, auth_headers):
    client.post(URL, json=VALID_PAYLOAD, headers=auth_headers)

    response = client.get(TODAY_URL, headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {
        **VALID_PAYLOAD,
        "nivel": "autocuidado",
        "tags": ["ansiedade", "sono"],
    }


def test_today_returns_404_without_checkin(client, auth_headers):
    response = client.get(TODAY_URL, headers=auth_headers)

    assert response.status_code == 404


def test_today_does_not_return_another_users_checkin(client, auth_headers):
    client.post(URL, json=VALID_PAYLOAD, headers=auth_headers)
    other = {"email": "bia@example.com", "senha": "senha-segura-123"}
    client.post("/api/auth/cadastro", json={**other, "aceite_termos": True, "maior_de_idade": True})
    token = client.post("/api/auth/login", json=other).json()["access_token"]

    response = client.get(TODAY_URL, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404


@pytest.mark.parametrize(("method", "path"), [("post", URL), ("get", TODAY_URL)])
def test_requires_authentication(client, db_session, method, path):
    response = client.request(method, path, json=VALID_PAYLOAD)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert _checkins(db_session) == []


def test_authentication_is_checked_before_validation(client):
    response = client.post(URL, json={"p1": 99})

    assert response.status_code == 401


def test_rejects_invalid_token(client):
    response = client.post(URL, json=VALID_PAYLOAD, headers={"Authorization": "Bearer invalid"})

    assert response.status_code == 401


def test_rejects_revoked_token(client, auth_headers, db_session):
    client.post("/api/auth/logout", headers=auth_headers)

    response = client.post(URL, json=VALID_PAYLOAD, headers=auth_headers)

    assert response.status_code == 401
    assert _checkins(db_session) == []


def test_checkin_content_is_not_logged(client, auth_headers, db_session, caplog):
    with caplog.at_level(logging.DEBUG):
        response = client.post(URL, json=VALID_PAYLOAD, headers=auth_headers)

    assert response.status_code == 201
    [checkin] = _checkins(db_session)
    assert str(checkin.id) in caplog.text
    sensitive = ("humor", "ansiedade", "sono", "sobrecarga", "pensamento_risco", "autocuidado")
    assert not any(word in caplog.text for word in sensitive)


def test_database_errors_do_not_expose_parameters_in_logs():
    assert get_engine().hide_parameters is True


def test_endpoints_are_documented_in_openapi(client):
    paths = client.get("/openapi.json").json()["paths"]

    create = paths["/api/checkins"]["post"]
    assert create["tags"] == ["checkins"]
    assert {"201", "401", "409", "422"} <= set(create["responses"])
    assert create["security"]
    today = paths["/api/checkins/hoje"]["get"]
    assert {"200", "401", "404"} <= set(today["responses"])
    assert today["security"]
