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
from app.domain.material import Material
from app.domain.recomendacao import Recomendacao
from app.domain.users import Role, User
from app.infrastructure.database import get_session
from app.main import app
from app.rules.checkin import MOTIVO_POR_REGRA_CHECKIN


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

    def add(self, checkin: Checkin) -> None:
        self._checkins.append(checkin)

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

    def list_by_user(self, user_id: uuid.UUID, limit: int = 30) -> list[Checkin]:
        user_checkins = [c for c in self._checkins if c.user_id == user_id]
        # Mais recente para o mais antigo (DESC) por data
        user_checkins.sort(key=lambda c: (c.data, c.criado_em), reverse=True)
        return user_checkins[:limit]


class FakeRecomendacaoRepository:
    def __init__(
        self,
        materiais: list[Material] | None = None,
        recomendacoes: list[Recomendacao] | None = None,
    ) -> None:
        self._materiais: list[Material] = (
            list(materiais)
            if materiais is not None
            else [
                Material(
                    id=1,
                    slug="ansiedade-opas",
                    titulo="Faça o que importa em tempos de estresse",
                    url="https://www.paho.org/pt/documentos/faca-que-importa",
                    fonte="OPAS/OMS",
                    resumo="Guia ilustrado da OMS.",
                    tags=[Tag.ANSIEDADE, Tag.ESTRESSE],
                    ativo=True,
                    revisado_em=date(2026, 11, 9),
                ),
                Material(
                    id=2,
                    slug="sono-ms",
                    titulo="Durma Bem, Viva Melhor",
                    url="https://bvsms.saude.gov.br/durma-bem",
                    fonte="Ministério da Saúde",
                    resumo="Hábitos que ajudam a dormir melhor.",
                    tags=[Tag.SONO],
                    ativo=True,
                    revisado_em=date(2026, 11, 9),
                ),
                Material(
                    id=3,
                    slug="bem-estar-ms",
                    titulo="Saúde Mental – Saúde de A a Z",
                    url="https://www.gov.br/saude/saude-mental",
                    fonte="Ministério da Saúde",
                    resumo="Explica o que é saúde mental.",
                    tags=[Tag.BEM_ESTAR, Tag.AJUDA_PROFISSIONAL],
                    ativo=True,
                    revisado_em=date(2026, 11, 9),
                ),
            ]
        )
        self._recomendacoes: list[Recomendacao] = list(recomendacoes) if recomendacoes else []

    def add(self, recomendacao: Recomendacao) -> None:
        self._recomendacoes.append(recomendacao)

    def add_all(self, recomendacoes) -> None:
        self._recomendacoes.extend(recomendacoes)

    def list_by_checkin(self, checkin_id: uuid.UUID) -> list[Recomendacao]:
        itens = [r for r in self._recomendacoes if r.checkin_id == checkin_id]
        itens.sort(key=lambda r: (r.criado_em, r.id))
        return itens

    def get_last_displayed_by_user(self, user_id: uuid.UUID) -> dict[int, datetime]:
        ultimas: dict[int, datetime] = {}
        for r in self._recomendacoes:
            if r.user_id == user_id:
                atual = ultimas.get(r.material_id)
                if atual is None or r.criado_em > atual:
                    ultimas[r.material_id] = r.criado_em
        return ultimas

    def list_active_materials(self) -> list[Material]:
        return [m for m in self._materiais if m.ativo]


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

    result = service.get_by_id(checkin_id=checkin.id, user_id=user.id)
    assert result.id == checkin.id
    assert result.user_id == user.id


def test_service_get_checkin_detail_not_found():
    user = _make_user()
    repo = FakeCheckinRepository([])
    service = CheckinService(repo)

    with pytest.raises(CheckinNotFoundError):
        service.get_by_id(checkin_id=uuid.uuid4(), user_id=user.id)


def test_service_get_checkin_detail_other_user_raises_not_found():
    """Critério TS-03 / T08: acessar check-in alheio deve levantar CheckinNotFoundError."""
    user_a = _make_user("a@example.com")
    user_b = _make_user("b@example.com")
    checkin_a = _make_checkin(user_id=user_a.id, checkin_date=date(2026, 10, 20))

    repo = FakeCheckinRepository([checkin_a])
    service = CheckinService(repo)

    with pytest.raises(CheckinNotFoundError):
        service.get_by_id(checkin_id=checkin_a.id, user_id=user_b.id)


def test_service_list_checkins_limits():
    user = _make_user()
    checkins = [
        _make_checkin(user_id=user.id, checkin_date=date(2026, 9, 1) + timedelta(days=i))
        for i in range(35)
    ]
    repo = FakeCheckinRepository(checkins)
    service = CheckinService(repo)

    # limit=5
    items = service.list(user_id=user.id, limit=5)
    assert len(items) == 5
    assert items[0].data == date(2026, 9, 1) + timedelta(days=34)  # DESC: mais recente primeiro

    # limit máximo segundo R12 é 30
    items = service.list(user_id=user.id, limit=50)
    assert len(items) == 30


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


def test_api_post_and_get_today_checkin_with_recomendacoes_ti03():
    user = _make_user()
    repo = FakeCheckinRepository()
    rec_repo = FakeRecomendacaoRepository()
    service = CheckinService(checkins=repo, recomendacoes=rec_repo)

    app.dependency_overrides[get_current_session] = lambda: _make_session(user)
    app.dependency_overrides[get_checkin_service] = lambda: service

    try:
        with TestClient(app) as test_client:
            payload = {"p1": 4, "p2": 3, "p3": 1, "p4": 0, "p5": False}
            post_resp = test_client.post("/api/checkins", json=payload)
            assert post_resp.status_code == 201
            post_body = post_resp.json()
            assert post_body["nivel"] == "autocuidado"
            assert post_body["tags"] == ["ansiedade", "sono"]
            assert len(post_body["recomendacoes"]) == 2
            assert [r["regra"] for r in post_body["recomendacoes"]] == ["R-D3", "R-D4"]
            assert [r["motivo"] for r in post_body["recomendacoes"]] == [
                MOTIVO_POR_REGRA_CHECKIN["R-D3"],
                MOTIVO_POR_REGRA_CHECKIN["R-D4"],
            ]
            assert len(rec_repo._recomendacoes) == 2

            today_resp = test_client.get("/api/checkins/hoje")
            assert today_resp.status_code == 200
            assert today_resp.json() == {
                **payload,
                "nivel": "autocuidado",
                "tags": ["ansiedade", "sono"],
                "recomendacoes": post_body["recomendacoes"],
            }
    finally:
        app.dependency_overrides.pop(get_current_session, None)
        app.dependency_overrides.pop(get_checkin_service, None)


def test_api_post_checkin_crise_produces_no_recomendacoes_ti05():
    user = _make_user()
    repo = FakeCheckinRepository()
    rec_repo = FakeRecomendacaoRepository()
    service = CheckinService(checkins=repo, recomendacoes=rec_repo)

    app.dependency_overrides[get_current_session] = lambda: _make_session(user)
    app.dependency_overrides[get_checkin_service] = lambda: service

    try:
        with TestClient(app) as test_client:
            payload = {"p1": 2, "p2": 3, "p3": 1, "p4": 2, "p5": True}
            post_resp = test_client.post("/api/checkins", json=payload)
            assert post_resp.status_code == 201
            assert post_resp.json() == {"nivel": "crise", "tags": [], "recomendacoes": []}
            assert rec_repo._recomendacoes == []
    finally:
        app.dependency_overrides.pop(get_current_session, None)
        app.dependency_overrides.pop(get_checkin_service, None)
