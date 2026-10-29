import logging
from datetime import datetime

import pytest
from sqlalchemy import select

from app.domain.checkins import CHECKIN_TIMEZONE, Nivel, Tag, avaliar_checkin
from app.infrastructure.database import get_engine
from app.infrastructure.models import CheckinModel

URL = "/api/checkins"

VALID_PAYLOAD = {
    "humor": 4,
    "ansiedade": 3,
    "sono": 1,
    "sobrecarga": 0,
    "pensamento_risco": False,
}


def _today() -> str:
    return datetime.now(CHECKIN_TIMEZONE).date().isoformat()




def test_avaliar_checkin_example_from_vision():
    assert avaliar_checkin(4, 3, 1, 0, False) == (Nivel.AUTOCUIDADO, [Tag.ANSIEDADE, Tag.SONO])


def test_avaliar_checkin_risk_takes_precedence_and_has_no_tags():
    assert avaliar_checkin(2, None, None, None, True) == (Nivel.CRISE, [])


@pytest.mark.parametrize(
    ("answers", "tags"),
    [
        ((2, 1, 3, 1), [Tag.HUMOR]),
        ((3, 1, 3, 1), [Tag.BEM_ESTAR]),
        ((5, 2, 5, 0), [Tag.ANSIEDADE]),
        ((5, 1, 5, 0), [Tag.BEM_ESTAR]),
        ((5, 0, 2, 0), [Tag.SONO]),
        ((5, 0, 3, 0), [Tag.BEM_ESTAR]),
        ((5, 0, 5, 2), [Tag.ESTRESSE]),
        ((5, 0, 5, 1), [Tag.BEM_ESTAR]),
        ((1, 3, 1, 3), [Tag.ANSIEDADE, Tag.HUMOR, Tag.ESTRESSE, Tag.SONO]),
        ((None, None, None, None), [Tag.BEM_ESTAR]),
    ],
)
def test_avaliar_checkin_thresholds(answers, tags):
    nivel, result = avaliar_checkin(*answers, False)

    assert nivel == Nivel.AUTOCUIDADO
    assert result == tags




def test_create_checkin_returns_201(client, auth_headers):
    response = client.post(URL, json=VALID_PAYLOAD, headers=auth_headers)

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {
        "id",
        "data",
        "humor",
        "ansiedade",
        "sono",
        "sobrecarga",
        "pensamento_risco",
        "nivel",
        "tags",
    }
    assert body["data"] == _today()
    assert {key: body[key] for key in VALID_PAYLOAD} == VALID_PAYLOAD
    assert body["nivel"] == "autocuidado"
    assert body["tags"] == ["ansiedade", "sono"]


def test_checkin_is_saved_for_authenticated_user(client, auth_headers, db_session):
    me = client.get("/api/users/me", headers=auth_headers).json()

    response = client.post(URL, json=VALID_PAYLOAD, headers=auth_headers)

    checkin = db_session.scalar(select(CheckinModel))
    assert str(checkin.id) == response.json()["id"]
    assert str(checkin.user_id) == me["id"]
    assert checkin.data.isoformat() == _today()
    assert (checkin.humor, checkin.ansiedade, checkin.sono, checkin.sobrecarga) == (4, 3, 1, 0)
    assert checkin.pensamento_risco is False
    assert checkin.nivel == "autocuidado"
    assert checkin.tags == ["ansiedade", "sono"]


def test_risk_answer_returns_crise_without_tags(client, auth_headers):
    payload = {
        "humor": 2,
        "ansiedade": None,
        "sono": None,
        "sobrecarga": None,
        "pensamento_risco": True,
    }

    response = client.post(URL, json=payload, headers=auth_headers)

    assert response.status_code == 201
    assert response.json()["nivel"] == "crise"
    assert response.json()["tags"] == []


def test_only_pensamento_risco_is_required(client, auth_headers):
    response = client.post(URL, json={"pensamento_risco": False}, headers=auth_headers)

    assert response.status_code == 201
    body = response.json()
    assert body["humor"] is None
    assert body["tags"] == ["bem_estar"]


def test_second_checkin_on_same_day_returns_409(client, auth_headers, db_session):
    client.post(URL, json=VALID_PAYLOAD, headers=auth_headers)

    response = client.post(URL, json=VALID_PAYLOAD, headers=auth_headers)

    assert response.status_code == 409
    assert response.json() == {"detail": "Check-in already done today"}
    assert len(db_session.scalars(select(CheckinModel)).all()) == 1


def test_other_user_can_checkin_on_same_day(client, auth_headers, db_session):
    client.post(URL, json=VALID_PAYLOAD, headers=auth_headers)
    other = {"email": "bia@example.com", "password": "senha-segura-123"}
    client.post("/api/auth/register", json={**other, "accept_terms": True})
    token = client.post("/api/auth/login", json=other).json()["access_token"]

    response = client.post(URL, json=VALID_PAYLOAD, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 201
    assert len(db_session.scalars(select(CheckinModel)).all()) == 2


@pytest.mark.parametrize(
    "changes",
    [
        {"humor": 0},
        {"humor": 6},
        {"sono": 0},
        {"sono": 6},
        {"ansiedade": -1},
        {"ansiedade": 4},
        {"sobrecarga": -1},
        {"sobrecarga": 4},
        {"humor": "4"},
        {"humor": 3.5},
        {"humor": "alta"},
        {"pensamento_risco": None},
        {"pensamento_risco": "sim"},
        {"pensamento_risco": 1},
    ],
)
def test_invalid_values_return_422(client, auth_headers, db_session, changes):
    response = client.post(URL, json={**VALID_PAYLOAD, **changes}, headers=auth_headers)

    assert response.status_code == 422
    assert db_session.scalars(select(CheckinModel)).all() == []


def test_missing_pensamento_risco_returns_422(client, auth_headers):
    payload = {key: value for key, value in VALID_PAYLOAD.items() if key != "pensamento_risco"}

    response = client.post(URL, json=payload, headers=auth_headers)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "extra",
    [
        {"user_id": "00000000-0000-0000-0000-000000000000"},
        {"nivel": "crise"},
        {"tags": ["humor"]},
        {"mood_category": "ansioso", "intensity": 4},
    ],
)
def test_unknown_fields_are_rejected(client, auth_headers, db_session, extra):
    response = client.post(URL, json={**VALID_PAYLOAD, **extra}, headers=auth_headers)

    assert response.status_code == 422
    assert db_session.scalars(select(CheckinModel)).all() == []


def test_requires_authentication(client, db_session):
    response = client.post(URL, json=VALID_PAYLOAD)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert db_session.scalars(select(CheckinModel)).all() == []


def test_authentication_is_checked_before_validation(client):
    response = client.post(URL, json={"humor": 99})

    assert response.status_code == 401


def test_rejects_invalid_token(client):
    response = client.post(URL, json=VALID_PAYLOAD, headers={"Authorization": "Bearer invalid"})

    assert response.status_code == 401


def test_rejects_revoked_token(client, auth_headers, db_session):
    client.post("/api/auth/logout", headers=auth_headers)

    response = client.post(URL, json=VALID_PAYLOAD, headers=auth_headers)

    assert response.status_code == 401
    assert db_session.scalars(select(CheckinModel)).all() == []


def test_checkin_content_is_not_logged(client, auth_headers, caplog):
    with caplog.at_level(logging.DEBUG):
        response = client.post(URL, json=VALID_PAYLOAD, headers=auth_headers)

    assert response.status_code == 201
    assert response.json()["id"] in caplog.text 
    sensitive = ("humor", "ansiedade", "sono", "sobrecarga", "pensamento_risco", "autocuidado")
    assert not any(word in caplog.text for word in sensitive)


def test_database_errors_do_not_expose_parameters_in_logs():
    assert get_engine().hide_parameters is True


def test_endpoint_is_documented_in_openapi(client):
    spec = client.get("/openapi.json").json()

    operation = spec["paths"]["/api/checkins"]["post"]
    assert operation["tags"] == ["checkins"]
    assert {"201", "401", "409", "422"} <= set(operation["responses"])
    assert operation["security"]