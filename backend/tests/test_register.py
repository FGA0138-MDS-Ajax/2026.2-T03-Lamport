import pytest
from sqlalchemy import select

from app.core.security import verify_password
from app.infrastructure.models import ConsentModel, UserModel

VALID_PAYLOAD = {
    "email": "ana@example.com",
    "password": "senha-segura-123",
    "accept_terms": True,
}


def test_register_creates_user(client, db_session):
    response = client.post("/api/auth/register", json=VALID_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "ana@example.com"
    assert body["role"] == "user"
    assert set(body) == {"id", "email", "role", "created_at"}

    user = db_session.scalar(select(UserModel).where(UserModel.email == "ana@example.com"))
    assert user is not None
    assert str(user.id) == body["id"]


def test_register_stores_only_password_hash(client, db_session):
    client.post("/api/auth/register", json=VALID_PAYLOAD)

    user = db_session.scalar(select(UserModel))
    assert user.password_hash != VALID_PAYLOAD["password"]
    assert user.password_hash.startswith("$argon2id$")
    assert verify_password(VALID_PAYLOAD["password"], user.password_hash)


def test_register_records_terms_consent(client, db_session):
    response = client.post("/api/auth/register", json=VALID_PAYLOAD)

    consent = db_session.scalar(select(ConsentModel))
    assert str(consent.user_id) == response.json()["id"]
    assert consent.purpose == "terms_of_use"
    assert consent.version == "2026-10"


def test_register_normalizes_email(client):
    response = client.post(
        "/api/auth/register", json={**VALID_PAYLOAD, "email": "  Ana@Example.COM "}
    )

    assert response.status_code == 201
    assert response.json()["email"] == "ana@example.com"


@pytest.mark.parametrize("email", ["ana@example.com", "ANA@example.com"])
def test_register_rejects_duplicate_email(client, db_session, email):
    client.post("/api/auth/register", json=VALID_PAYLOAD)

    response = client.post("/api/auth/register", json={**VALID_PAYLOAD, "email": email})

    assert response.status_code == 409
    assert response.json() == {"detail": "E-mail already registered"}
    assert len(db_session.scalars(select(UserModel)).all()) == 1


@pytest.mark.parametrize("missing", ["email", "password", "accept_terms"])
def test_register_requires_fields(client, missing):
    payload = {key: value for key, value in VALID_PAYLOAD.items() if key != missing}

    response = client.post("/api/auth/register", json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "changes",
    [
        {"email": "not-an-email"},
        {"email": "ana@"},
        {"password": "curta"},
        {"password": "x" * 129},
    ],
)
def test_register_rejects_invalid_format(client, db_session, changes):
    response = client.post("/api/auth/register", json={**VALID_PAYLOAD, **changes})

    assert response.status_code == 422
    assert db_session.scalars(select(UserModel)).all() == []


def test_register_requires_terms_acceptance(client, db_session):
    response = client.post("/api/auth/register", json={**VALID_PAYLOAD, "accept_terms": False})

    assert response.status_code == 422
    assert response.json() == {"detail": "Terms of use must be accepted"}
    assert db_session.scalars(select(UserModel)).all() == []
