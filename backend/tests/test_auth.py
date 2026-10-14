import os
from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import get_settings
from app.core.security import ALGORITHM


def test_login_returns_token(client, registered_user):
    response = client.post("/api/auth/login", json=registered_user)

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] > 0
    assert body["access_token"]


def test_login_is_case_insensitive_on_email(client, registered_user):
    response = client.post(
        "/api/auth/login",
        json={**registered_user, "email": registered_user["email"].upper()},
    )

    assert response.status_code == 200


def test_login_rejects_wrong_password(client, registered_user):
    response = client.post(
        "/api/auth/login", json={**registered_user, "password": "senha-errada-123"}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid e-mail or password"}


def test_login_rejects_unknown_user_with_same_message(client):
    response = client.post(
        "/api/auth/login", json={"email": "ninguem@example.com", "password": "qualquer-senha"}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid e-mail or password"}


def test_me_requires_authentication(client):
    response = client.get("/api/users/me")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_rejects_invalid_token(client):
    response = client.get("/api/users/me", headers={"Authorization": "Bearer invalid.token"})

    assert response.status_code == 401


def test_me_rejects_expired_token(client, auth_headers):
    me = client.get("/api/users/me", headers=auth_headers).json()
    past = datetime.now(UTC) - timedelta(minutes=5)
    expired = jwt.encode(
        {"sub": me["id"], "jti": "expired", "iat": past - timedelta(hours=1), "exp": past},
        os.environ["SECRET_KEY"],
        algorithm=ALGORITHM,
    )

    response = client.get("/api/users/me", headers={"Authorization": f"Bearer {expired}"})

    assert response.status_code == 401


def test_me_rejects_token_signed_with_other_key(client, auth_headers):
    me = client.get("/api/users/me", headers=auth_headers).json()
    forged = jwt.encode(
        {"sub": me["id"], "jti": "forged", "exp": datetime.now(UTC) + timedelta(hours=1)},
        "another-secret-key-with-at-least-32-chars",
        algorithm=ALGORITHM,
    )

    response = client.get("/api/users/me", headers={"Authorization": f"Bearer {forged}"})

    assert response.status_code == 401


def test_me_returns_authenticated_user(client, registered_user, auth_headers):
    response = client.get("/api/users/me", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == registered_user["email"]
    assert "password" not in body
    assert "password_hash" not in body


def test_logout_revokes_token(client, auth_headers):
    response = client.post("/api/auth/logout", headers=auth_headers)

    assert response.status_code == 204
    assert client.get("/api/users/me", headers=auth_headers).status_code == 401
    assert client.post("/api/auth/logout", headers=auth_headers).status_code == 401


def test_logout_keeps_other_sessions_active(client, registered_user, auth_headers):
    other = client.post("/api/auth/login", json=registered_user).json()["access_token"]

    client.post("/api/auth/logout", headers=auth_headers)

    response = client.get("/api/users/me", headers={"Authorization": f"Bearer {other}"})
    assert response.status_code == 200


def test_logout_requires_authentication(client):
    assert client.post("/api/auth/logout").status_code == 401


def test_health(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_terms_returns_current_version(client):
    response = client.get("/api/terms")

    assert response.status_code == 200
    assert response.json() == {"version": get_settings().terms_version}
