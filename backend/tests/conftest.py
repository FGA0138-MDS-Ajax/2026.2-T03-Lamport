import os
from pathlib import Path

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://sintoniza:sintoniza@localhost:5432/sintoniza_test",
)
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["SECRET_KEY"] = "test-secret-key-with-at-least-32-characters"

import pytest  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, make_url, text  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from alembic import command  # noqa: E402
from app.infrastructure.database import get_engine  # noqa: E402
from app.main import app  # noqa: E402

ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"


def _recreate_database(url: str) -> None:
    db_url = make_url(url)
    admin = create_engine(db_url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{db_url.database}" WITH (FORCE)'))
        conn.execute(text(f'CREATE DATABASE "{db_url.database}"'))
    admin.dispose()


@pytest.fixture(scope="session", autouse=True)
def database():
    _recreate_database(TEST_DATABASE_URL)
    command.upgrade(Config(str(ALEMBIC_INI)), "head")
    yield
    get_engine().dispose()


@pytest.fixture(autouse=True)
def clean_tables():
    yield
    with get_engine().begin() as conn:
        conn.execute(text("TRUNCATE users, consents, revoked_tokens, login_attempts, checkins"))


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def db_session():
    with Session(get_engine()) as session:
        yield session


@pytest.fixture
def registered_user(client):
    credentials = {"email": "ana@example.com", "password": "senha-segura-123"}
    response = client.post("/api/auth/register", json={**credentials, "accept_terms": True})
    assert response.status_code == 201
    return credentials


@pytest.fixture
def auth_headers(client, registered_user):
    response = client.post("/api/auth/login", json=registered_user)
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
