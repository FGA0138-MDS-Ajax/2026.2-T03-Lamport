import uuid
import zoneinfo
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

    def get_by_user_and_date(self, user_id: uuid.UUID, data: date) -> Checkin | None:
        for c in self._checkins:
            if c.user_id == user_id and c.data == data:
                return c
        return None

    def list_by_user(
        self,
        user_id: uuid.UUID,
        limit: int = 30,
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
    """Critério TS-03 / T08: acessar check-in alheio deve levantar CheckinNotFoundError."""
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
        _make_checkin(user_id=user.id, checkin_date=date(2026, 9, 1) + timedelta(days=i))
        for i in range(35)
    ]
    repo = FakeCheckinRepository(checkins)
    service = CheckinService(repo)

    # limit=5, offset=0
    items = service.list_checkins(user_id=user.id, limit=5, offset=0)
    assert len(items) == 5
    assert items[0].data == date(2026, 9, 1) + timedelta(days=34)  # DESC: mais recente primeiro

    # limit máximo segundo R12 é 30
    items = service.list_checkins(user_id=user.id, limit=50, offset=0)
    assert len(items) == 30


def test_service_list_checkins_date_filters():
    user = _make_user()
    checkins = [
        _make_checkin(user_id=user.id, checkin_date=date(2026, 10, i)) for i in range(1, 16)
    ]
    repo = FakeCheckinRepository(checkins)
    service = CheckinService(repo)

    items = service.list_checkins(
        user_id=user.id,
        from_date=date(2026, 10, 5),
        to_date=date(2026, 10, 10),
    )
    assert len(items) == 6
    assert all(date(2026, 10, 5) <= c.data <= date(2026, 10, 10) for c in items)


def test_service_get_today_checkin():
    user = _make_user()
    today = datetime.now(zoneinfo.ZoneInfo("America/Sao_Paulo")).date()
    checkin = _make_checkin(user_id=user.id, checkin_date=today)
    repo = FakeCheckinRepository([checkin])
    service = CheckinService(repo)

    result = service.get_today_checkin(user_id=user.id, today=today)
    assert result.id == checkin.id

    with pytest.raises(CheckinNotFoundError):
        service.get_today_checkin(user_id=uuid.uuid4(), today=today)


# ---------------------------------------------------------------------------
# Testes da API (Rotas GET /api/checkins, GET /api/checkins/hoje e GET /api/checkins/{id})
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


def test_api_checkin_today_requires_authentication():
    with TestClient(app) as test_client:
        response = test_client.get("/api/checkins/hoje")
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
            assert data == []
    finally:
        app.dependency_overrides.pop(get_current_session, None)
        app.dependency_overrides.pop(get_checkin_service, None)


def test_api_list_checkins_ordered_desc_and_p1_p5_schema():
    user = _make_user()
    checkins = [
        _make_checkin(
            user_id=user.id,
            checkin_date=date(2026, 10, 1),
            humor=5,
            ansiedade=0,
            sono=4,
            sobrecarga=1,
            pensamento_risco=False,
        ),
        _make_checkin(
            user_id=user.id,
            checkin_date=date(2026, 10, 15),
            humor=2,
            ansiedade=3,
            sono=1,
            sobrecarga=2,
            pensamento_risco=True,
        ),
    ]
    repo = FakeCheckinRepository(checkins)
    service = CheckinService(repo)

    app.dependency_overrides[get_current_session] = lambda: _make_session(user)
    app.dependency_overrides[get_checkin_service] = lambda: service

    try:
        with TestClient(app) as test_client:
            response = test_client.get("/api/checkins?limite=2")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            # Mais recente primeiro (15/10)
            item1 = data[0]
            assert item1["data"] == "2026-10-15"
            assert item1["p1"] == 2
            assert item1["p2"] == 3
            assert item1["p3"] == 1
            assert item1["p4"] == 2
            assert item1["p5"] is True

            # Segundo item (01/10)
            item2 = data[1]
            assert item2["data"] == "2026-10-01"
            assert item2["p1"] == 5
            assert item2["p2"] == 0
            assert item2["p3"] == 4
            assert item2["p4"] == 1
            assert item2["p5"] is False
    finally:
        app.dependency_overrides.pop(get_current_session, None)
        app.dependency_overrides.pop(get_checkin_service, None)


def test_api_list_checkins_isolation_ts_03():
    """Critério TS-03: usuário B não deve ver check-ins do usuário A na listagem."""
    user_a = _make_user("a@example.com")
    user_b = _make_user("b@example.com")

    checkin_a = _make_checkin(user_id=user_a.id, checkin_date=date(2026, 10, 10))
    checkin_b = _make_checkin(user_id=user_b.id, checkin_date=date(2026, 10, 12))

    repo = FakeCheckinRepository([checkin_a, checkin_b])
    service = CheckinService(repo)

    app.dependency_overrides[get_current_session] = lambda: _make_session(user_b)
    app.dependency_overrides[get_checkin_service] = lambda: service

    try:
        with TestClient(app) as test_client:
            response = test_client.get("/api/checkins")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["id"] == str(checkin_b.id)
            assert not any(item["id"] == str(checkin_a.id) for item in data)
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
            assert data["p1"] == 4
            assert data["p2"] == 1
            assert data["p3"] == 5
            assert data["p4"] == 0
            assert data["p5"] is False
            assert data["nivel"] == "autocuidado"
            assert "humor" in data["tags"]
    finally:
        app.dependency_overrides.pop(get_current_session, None)
        app.dependency_overrides.pop(get_checkin_service, None)


def test_api_get_checkin_by_id_other_user_returns_404():
    """Critério de segurança TS-03: se o check-in for de outro usuário, retorna 404."""
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


def test_api_get_today_checkin_found_and_not_found():
    user = _make_user()
    today = datetime.now(zoneinfo.ZoneInfo("America/Sao_Paulo")).date()
    checkin = _make_checkin(
        user_id=user.id,
        checkin_date=today,
        humor=4,
        ansiedade=0,
        sono=5,
        sobrecarga=0,
        pensamento_risco=False,
    )
    repo = FakeCheckinRepository([checkin])
    service = CheckinService(repo)

    app.dependency_overrides[get_current_session] = lambda: _make_session(user)
    app.dependency_overrides[get_checkin_service] = lambda: service

    try:
        with TestClient(app) as test_client:
            # 1. Usuário fez check-in hoje -> 200
            response = test_client.get("/api/checkins/hoje")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == str(checkin.id)
            assert data["p1"] == 4
            assert data["p5"] is False

            # 2. Usuário que ainda não fez check-in hoje -> 404
            other_user = _make_user("other@example.com")
            app.dependency_overrides[get_current_session] = lambda: _make_session(other_user)
            resp_not_found = test_client.get("/api/checkins/hoje")
            assert resp_not_found.status_code == 404
            assert resp_not_found.json() == {"detail": "Check-in not found"}
    finally:
        app.dependency_overrides.pop(get_current_session, None)
        app.dependency_overrides.pop(get_checkin_service, None)
