from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update

from app.core.config import get_settings
from app.infrastructure.models import LoginAttemptModel

MAX_ATTEMPTS = get_settings().login_max_attempts


def _fail_login(client, email, times):
    for _ in range(times):
        response = client.post("/api/auth/login", json={"email": email, "password": "senha-errada"})
        assert response.status_code == 401


def test_login_is_blocked_after_too_many_failures(client, registered_user):
    _fail_login(client, registered_user["email"], MAX_ATTEMPTS)

    response = client.post("/api/auth/login", json=registered_user)

    assert response.status_code == 429
    assert response.json() == {"detail": "Too many login attempts, try again later"}
    assert response.headers["retry-after"] == str(get_settings().login_lockout_minutes * 60)


def test_unknown_email_is_blocked_the_same_way(client):
    _fail_login(client, "ninguem@example.com", MAX_ATTEMPTS)

    response = client.post(
        "/api/auth/login", json={"email": "ninguem@example.com", "password": "qualquer-senha"}
    )

    assert response.status_code == 429


def test_block_is_per_email_and_case_insensitive(client, registered_user):
    _fail_login(client, registered_user["email"].upper(), MAX_ATTEMPTS)

    blocked = client.post("/api/auth/login", json=registered_user)
    other = client.post(
        "/api/auth/login", json={"email": "outra@example.com", "password": "qualquer-senha"}
    )

    assert blocked.status_code == 429
    assert other.status_code == 401


def test_successful_login_resets_failures(client, registered_user):
    _fail_login(client, registered_user["email"], MAX_ATTEMPTS - 1)
    assert client.post("/api/auth/login", json=registered_user).status_code == 200

    _fail_login(client, registered_user["email"], MAX_ATTEMPTS - 1)

    assert client.post("/api/auth/login", json=registered_user).status_code == 200


def test_failures_outside_the_window_are_ignored(client, registered_user, db_session):
    _fail_login(client, registered_user["email"], MAX_ATTEMPTS)
    window = timedelta(minutes=get_settings().login_lockout_minutes)
    db_session.execute(
        update(LoginAttemptModel).values(attempted_at=datetime.now(UTC) - window - timedelta(1))
    )
    db_session.commit()

    assert client.post("/api/auth/login", json=registered_user).status_code == 200


def test_failed_attempts_do_not_store_the_email(client, db_session):
    _fail_login(client, "ninguem@example.com", 1)

    keys = db_session.scalars(select(LoginAttemptModel.key)).all()

    assert len(keys) == 1
    assert "ninguem" not in keys[0]
