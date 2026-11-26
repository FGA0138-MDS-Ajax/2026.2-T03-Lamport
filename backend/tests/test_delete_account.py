import hashlib
from uuid import UUID

from sqlalchemy import select

from app.infrastructure.models import (
    AvaliacaoModel,
    CheckinModel,
    ConsentModel,
    LoginAttemptModel,
    MaterialModel,
    RecomendacaoModel,
    RevokedTokenModel,
    UserModel,
)
from app.seed_materiais import CAMINHO_CATALOGO, rodar_seed


def _create_account_with_history(client, email):
    credentials = {"email": email, "senha": "senha-segura-123"}
    signup = client.post(
        "/api/auth/cadastro", json={**credentials, "aceite_termos": True, "maior_de_idade": True}
    )
    assert signup.status_code == 201

    def login():
        response = client.post("/api/auth/login", json=credentials)
        assert response.status_code == 200
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    headers = login()
    logged_out_headers = login()
    assert client.post("/api/auth/logout", headers=logged_out_headers).status_code == 204
    wrong_password = {**credentials, "senha": "senha-incorreta"}
    assert client.post("/api/auth/login", json=wrong_password).status_code == 401

    for path, answers in (
        ("/api/checkins", {"p1": 4, "p2": 3, "p3": 1, "p4": 0, "p5": False}),
        ("/api/avaliacoes", {"phq9": [0] * 9, "gad7": [0] * 7}),
    ):
        response = client.post(path, json=answers, headers=headers)
        assert response.status_code == 201
        assert response.json()["recomendacoes"]
    return UUID(signup.json()["id"]), headers, logged_out_headers


def test_ti07_delete_only_the_authenticated_account_and_its_data(client, db_session):
    rodar_seed(db_session, CAMINHO_CATALOGO)
    ana_email, bia_email = "ana@example.com", "bia@example.com"
    ana, headers, _ = _create_account_with_history(client, ana_email)
    bia, other_headers, revoked_headers = _create_account_with_history(client, bia_email)

    owner_columns = (
        UserModel.id,
        ConsentModel.user_id,
        CheckinModel.user_id,
        AvaliacaoModel.user_id,
        RecomendacaoModel.user_id,
        RevokedTokenModel.user_id,
    )
    owners_before = [list(db_session.scalars(select(column))) for column in owner_columns]
    for owners in owners_before:
        assert set(owners) == {ana, bia}
    material_ids = set(db_session.scalars(select(MaterialModel.id)))
    ana_key, bia_key = [
        hashlib.sha256(email.encode()).hexdigest() for email in (ana_email, bia_email)
    ]
    assert set(db_session.scalars(select(LoginAttemptModel.key))) == {ana_key, bia_key}

    response = client.delete("/api/me", headers=headers)
    assert response.status_code == 204
    assert response.content == b""
    for column, before in zip(owner_columns, owners_before, strict=True):
        assert list(db_session.scalars(select(column))) == [bia] * before.count(bia)
    assert list(db_session.scalars(select(LoginAttemptModel.key))) == [bia_key]
    assert set(db_session.scalars(select(MaterialModel.id))) == material_ids

    assert client.get("/api/me", headers=headers).status_code == 401
    assert client.delete("/api/me", headers=headers).status_code == 401
    assert client.get("/api/me", headers=other_headers).status_code == 200
    assert client.get("/api/me", headers=revoked_headers).status_code == 401
    assert (
        client.post(
            "/api/auth/login", json={"email": ana_email, "senha": "senha-segura-123"}
        ).status_code
        == 401
    )
