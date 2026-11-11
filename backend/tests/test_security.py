"""Segurança e vazamento de dados: TS-01 (rotas protegidas) e TS-04 (campos sensíveis)."""

import re
import uuid

import pytest

from app.main import app
from tests.conftest import find_sensitive_keys

# Única fonte de verdade das rotas públicas (Arquitetura, Quadro 6; Visão, Quadro 8).
PUBLIC_ROUTES = {
    ("POST", "/api/auth/cadastro"),
    ("POST", "/api/auth/login"),
    ("GET", "/api/health"),
    ("GET", "/api/terms"),
}

# Operações HTTP do contrato OpenAPI, sem depender de estruturas internas do router.
HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}

CHECKIN = {"p1": 2, "p2": 3, "p3": 1, "p4": 0, "p5": False}


def _api_routes() -> set[tuple[str, str]]:
    return {
        (method.upper(), path)
        for path, operations in app.openapi()["paths"].items()
        for method in operations
        if method in HTTP_METHODS
    }


def _protected_routes() -> list[tuple[str, str]]:
    return sorted(_api_routes() - PUBLIC_ROUTES)


def _concrete(path: str) -> str:
    return re.sub(r"\{[^}]+\}", str(uuid.uuid4()), path)


def test_ts01_public_list_matches_existing_routes():
    existing = _api_routes()
    assert existing >= PUBLIC_ROUTES, "Rota pública listada no teste não existe mais"


def test_ts01_there_are_protected_routes_to_check():
    assert len(_protected_routes()) >= 4


@pytest.mark.parametrize(("method", "path"), _protected_routes())
def test_ts01_protected_routes_require_authentication(client, method, path):
    # Sem corpo e sem token: a autenticação deve vir antes da validação (401, não 422).
    response = client.request(method, _concrete(path))
    assert response.status_code == 401, f"{method} {path} respondeu {response.status_code}"
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.parametrize(("method", "path"), _protected_routes())
def test_ts01_protected_routes_reject_malformed_token(client, method, path):
    response = client.request(
        method, _concrete(path), headers={"Authorization": "Bearer nao-e-um-jwt"}
    )
    assert response.status_code == 401


def test_ts04_helper_detects_sensitive_keys_at_any_level():
    payload = {"a": [{"b": {"Password_Hash": "x"}}], "senha": "y", "ok": 1}
    assert set(find_sensitive_keys(payload)) == {"$.senha", "$.a[0].b.Password_Hash"}
    assert find_sensitive_keys({"id": 1, "email": "a@b.c", "created_at": "x"}) == []


def test_ts04_me_returns_only_public_fields(client, auth_headers):
    body = client.get("/api/me", headers=auth_headers).json()
    assert set(body) == {"id", "email", "criado_em"}


def test_ts04_all_endpoints_responses_have_no_sensitive_fields(client, registered_user):
    """Percorre o contrato; o `client` da suíte já varre cada resposta JSON recebida."""
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/terms").status_code == 200
    login = client.post("/api/auth/login", json=registered_user)
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    assert client.get("/api/me", headers=headers).status_code == 200
    created = client.post("/api/checkins", json=CHECKIN, headers=headers)
    assert created.status_code == 201
    assert client.post("/api/checkins", json=CHECKIN, headers=headers).status_code == 409
    history = client.get("/api/checkins", headers=headers)
    assert history.status_code == 200
    assert len(history.json()) == 1
    assert client.get("/api/checkins/hoje", headers=headers).status_code == 200
    checkin_id = history.json()[0]["id"]
    assert client.get(f"/api/checkins/{checkin_id}", headers=headers).status_code == 200
    assert client.get(f"/api/checkins/{uuid.uuid4()}", headers=headers).status_code == 404
    assert client.post("/api/auth/logout", headers=headers).status_code == 204
    assert client.get("/api/me", headers=headers).status_code == 401


@pytest.mark.parametrize(
    ("path", "payload", "status_code"),
    [
        ("cadastro", {"email": "invalido", "password": "segredo-ts04"}, 422),
        (
            "cadastro",
            {
                "email": "a@example.com",
                "password": "curta",
                "accept_terms": True,
                "maior_de_idade": True,
            },
            422,
        ),
        (
            "cadastro",
            {
                "email": "a@example.com",
                "password": "z" * 129,
                "accept_terms": True,
                "maior_de_idade": True,
            },
            422,
        ),
        ("login", {"email": "a@example.com"}, 422),
        ("login", {"email": "invalido", "password": "segredo-ts04"}, 422),
        ("login", {"email": "a@example.com", "password": "segredo-ts04"}, 401),
    ],
)
def test_ts04_error_responses_do_not_echo_the_password(client, path, payload, status_code):
    response = client.post(f"/api/auth/{path}", json=payload)
    assert response.status_code == status_code
    if "password" in payload:
        assert payload["password"] not in response.text
    if status_code == 422:
        details = response.json()["detail"]
        assert details
        assert all(set(error) == {"type", "loc", "msg"} for error in details)
