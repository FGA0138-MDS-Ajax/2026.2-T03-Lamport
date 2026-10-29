import uuid
from datetime import UTC, date, datetime, timedelta
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_checkin_service, get_current_session
from app.application.auth import AuthenticatedSession
from app.application.checkins import CheckinService
from app.core.security import TokenClaims
from app.domain.checkin import Checkin, Nivel, Tag
from app.domain.errors import CheckinNotFoundError
from app.domain.users import Role, User
from app.infrastructure.database import get_session
from app.main import app


# Sobrescreve as fixtures do conftest.py para testes unitários/em memória
@pytest.fixture(scope="session", autouse=True)
def database():
    yield


@pytest.fixture(autouse=True)
def clean_tables():
    yield


@pytest.fixture(autouse=True)
def _mock_session_dependency():
    mock_session = MagicMock()
    app.dependency_overrides[get_session] = lambda: mock_session
    yield
    app.dependency_overrides.pop(get_session, None)


class FakeCheckinRepository:
    def __init__(self, checkins: list[Checkin] | None = None) -> None:
        self._checkins: list[Checkin] = list(checkins) if checkins else []

    def get_by_id_for_user(self, checkin_id: uuid.UUID, user_id: uuid.UUID) -> Checkin | None:
        for c in self._checkins:
            if c.id == checkin_id and c.user_id == user_id:
                return c
        return None

    def list_by_user(
        self,
        user_id: uuid.UUID,
        limit: int = 20,
        offset: int = 0,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> tuple[list[Checkin], int]:
        user_checkins = [c for c in self._checkins if c.user_id == user_id]
        if from_date is not None:
            user_checkins = [c for c in user_checkins if c.data >= from_date]
        if to_date is not None:
            user_checkins = [c for c in user_checkins if c.data <= to_date]

        # Mais recente para o mais antigo (DESC)
        user_checkins.sort(key=lambda c: (c.data, c.criado_em), reverse=True)
        total = len(user_checkins)
        return user_checkins[offset : offset + limit], total


def _make_user(email: str = "user@example.com") -> User:
    return User(
        id=uuid.uuid4(),
        email=email,
        password_hash="test-hash",
        role=Role.USER,
    )


def _make_session(user: User) -> AuthenticatedSession:
    claims = TokenClaims(
        subject=user.id,
        jti="test-jti",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    return AuthenticatedSession(user=user, claims=claims)


def _make_checkin(
    user_id: uuid.UUID,
    checkin_date: date,
    humor: int = 3,
    ansiedade: int = 1,
    sono: int = 4,
    sobrecarga: int = 0,
    pensamento_risco: bool = False,
    nivel: Nivel = Nivel.AUTOCUIDADO,
    tags: list[Tag] | None = None,
) -> Checkin:
    return Checkin(
        id=uuid.uuid4(),
        user_id=user_id,
        data=checkin_date,
        humor=humor,
        ansiedade=ansiedade,
        sono=sono,
        sobrecarga=sobrecarga,
        pensamento_risco=pensamento_risco,
        nivel=nivel,
        tags=tags or [Tag.BEM_ESTAR],
    )


# ---------------------------------------------------------------------------
# Testes Unitários do CheckinService
# ---------------------------------------------------------------------------


def test_service_get_checkin_detail_success():
    user = _make_user()
    checkin = _make_checkin(user_id=user.id, checkin_date=date(2026, 10, 20))
    repo = FakeCheckinRepository([checkin])
    service = CheckinService(repo)

    result = service.get_checkin_detail(checkin_id=checkin.id, user_id=user.id)
    assert result.id == checkin.id
    assert result.user_id == user.id


def test_service_get_checkin_detail_not_found():
    user = _make_user()
    repo = FakeCheckinRepository([])
    service = CheckinService(repo)

    with pytest.raises(CheckinNotFoundError):
        service.get_checkin_detail(checkin_id=uuid.uuid4(), user_id=user.id)


def test_service_get_checkin_detail_other_user_raises_not_found():
    """Critério T08: acessar check-in de outro usuário deve levantar CheckinNotFoundError."""
    user_a = _make_user("a@example.com")
    user_b = _make_user("b@example.com")
    checkin_a = _make_checkin(user_id=user_a.id, checkin_date=date(2026, 10, 20))

    repo = FakeCheckinRepository([checkin_a])
    service = CheckinService(repo)

    with pytest.raises(CheckinNotFoundError):
        service.get_checkin_detail(checkin_id=checkin_a.id, user_id=user_b.id)


def test_service_list_checkins_pagination_and_limits():
    user = _make_user()
    checkins = [
        _make_checkin(user_id=user.id, checkin_date=date(2026, 10, i)) for i in range(1, 11)
    ]
    repo = FakeCheckinRepository(checkins)
    service = CheckinService(repo)

    # limit=5, offset=0
    items, total = service.list_checkins(user_id=user.id, limit=5, offset=0)
    assert len(items) == 5
    assert total == 10
    assert items[0].data == date(2026, 10, 10)  # DESC: mais recente primeiro

    # limit > 100 é limitado a 100
    items, total = service.list_checkins(user_id=user.id, limit=500, offset=0)
    assert len(items) == 10


def test_service_list_checkins_date_filters():
    user = _make_user()
    checkins = [
        _make_checkin(user_id=user.id, checkin_date=date(2026, 10, i)) for i in range(1, 16)
    ]
    repo = FakeCheckinRepository(checkins)
    service = CheckinService(repo)

    items, total = service.list_checkins(
        user_id=user.id,
        from_date=date(2026, 10, 5),
        to_date=date(2026, 10, 10),
    )
    assert total == 6
    assert all(date(2026, 10, 5) <= c.data <= date(2026, 10, 10) for c in items)


# ---------------------------------------------------------------------------
# Testes da API (Rotas GET /api/checkins e GET /api/checkins/{id})
# ---------------------------------------------------------------------------


def test_api_checkins_requires_authentication():
    with TestClient(app) as test_client:
        response = test_client.get("/api/checkins")
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"


def test_api_checkin_by_id_requires_authentication():
    with TestClient(app) as test_client:
        response = test_client.get(f"/api/checkins/{uuid.uuid4()}")
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"


def test_api_list_checkins_empty():
    user = _make_user()
    repo = FakeCheckinRepository([])
    service = CheckinService(repo)

    app.dependency_overrides[get_current_session] = lambda: _make_session(user)
    app.dependency_overrides[get_checkin_service] = lambda: service

    try:
        with TestClient(app) as test_client:
            response = test_client.get("/api/checkins")
            assert response.status_code == 200
            data = response.json()
            assert data["items"] == []
            assert data["total"] == 0
            assert data["limit"] == 20
            assert data["offset"] == 0
    finally:
        app.dependency_overrides.pop(get_current_session, None)
        app.dependency_overrides.pop(get_checkin_service, None)


def test_api_list_checkins_ordered_desc_and_paginated():
    user = _make_user()
    checkins = [
        _make_checkin(user_id=user.id, checkin_date=date(2026, 10, 1)),
        _make_checkin(user_id=user.id, checkin_date=date(2026, 10, 15)),
        _make_checkin(user_id=user.id, checkin_date=date(2026, 10, 8)),
    ]
    repo = FakeCheckinRepository(checkins)
    service = CheckinService(repo)

    app.dependency_overrides[get_current_session] = lambda: _make_session(user)
    app.dependency_overrides[get_checkin_service] = lambda: service

    try:
        with TestClient(app) as test_client:
            response = test_client.get("/api/checkins?limit=2&offset=0")
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 3
            assert len(data["items"]) == 2
            # Ordenado DESC: 15/10 depois 08/10
            assert data["items"][0]["data"] == "2026-10-15"
            assert data["items"][1]["data"] == "2026-10-08"
    finally:
        app.dependency_overrides.pop(get_current_session, None)
        app.dependency_overrides.pop(get_checkin_service, None)


def test_api_list_checkins_with_from_and_to_filters():
    user = _make_user()
    checkins = [
        _make_checkin(user_id=user.id, checkin_date=date(2026, 10, 2)),
        _make_checkin(user_id=user.id, checkin_date=date(2026, 10, 10)),
        _make_checkin(user_id=user.id, checkin_date=date(2026, 10, 20)),
    ]
    repo = FakeCheckinRepository(checkins)
    service = CheckinService(repo)

    app.dependency_overrides[get_current_session] = lambda: _make_session(user)
    app.dependency_overrides[get_checkin_service] = lambda: service

    try:
        with TestClient(app) as test_client:
            response = test_client.get("/api/checkins?from=2026-10-05&to=2026-10-15")
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert len(data["items"]) == 1
            assert data["items"][0]["data"] == "2026-10-10"
    finally:
        app.dependency_overrides.pop(get_current_session, None)
        app.dependency_overrides.pop(get_checkin_service, None)


def test_api_get_checkin_by_id_owner_success():
    user = _make_user()
    checkin = _make_checkin(
        user_id=user.id,
        checkin_date=date(2026, 10, 28),
        humor=4,
        ansiedade=1,
        sono=5,
        sobrecarga=0,
        pensamento_risco=False,
        nivel=Nivel.AUTOCUIDADO,
        tags=[Tag.HUMOR, Tag.BEM_ESTAR],
    )
    repo = FakeCheckinRepository([checkin])
    service = CheckinService(repo)

    app.dependency_overrides[get_current_session] = lambda: _make_session(user)
    app.dependency_overrides[get_checkin_service] = lambda: service

    try:
        with TestClient(app) as test_client:
            response = test_client.get(f"/api/checkins/{checkin.id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == str(checkin.id)
            assert data["data"] == "2026-10-28"
            assert data["humor"] == 4
            assert data["pensamento_risco"] is False
            assert data["nivel"] == "autocuidado"
            assert "humor" in data["tags"]
    finally:
        app.dependency_overrides.pop(get_current_session, None)
        app.dependency_overrides.pop(get_checkin_service, None)


def test_api_get_checkin_by_id_other_user_returns_404():
    """Critério de segurança T08: se o check-in for de outro usuário, retorna 404 (nunca 403)."""
    user_a = _make_user("a@example.com")
    user_b = _make_user("b@example.com")
    checkin_a = _make_checkin(user_id=user_a.id, checkin_date=date(2026, 10, 28))

    repo = FakeCheckinRepository([checkin_a])
    service = CheckinService(repo)

    # Usuário B tenta acessar o check-in do Usuário A
    app.dependency_overrides[get_current_session] = lambda: _make_session(user_b)
    app.dependency_overrides[get_checkin_service] = lambda: service

    try:
        with TestClient(app) as test_client:
            response = test_client.get(f"/api/checkins/{checkin_a.id}")
            assert response.status_code == 404
            assert response.json() == {"detail": "Check-in not found"}
    finally:
        app.dependency_overrides.pop(get_current_session, None)
        app.dependency_overrides.pop(get_checkin_service, None)


def test_api_get_checkin_by_id_nonexistent_returns_404():
    user = _make_user()
    repo = FakeCheckinRepository([])
    service = CheckinService(repo)

    app.dependency_overrides[get_current_session] = lambda: _make_session(user)
    app.dependency_overrides[get_checkin_service] = lambda: service

    try:
        with TestClient(app) as test_client:
            response = test_client.get(f"/api/checkins/{uuid.uuid4()}")
            assert response.status_code == 404
            assert response.json() == {"detail": "Check-in not found"}
    finally:
        app.dependency_overrides.pop(get_current_session, None)
        app.dependency_overrides.pop(get_checkin_service, None)
