import uuid
from datetime import UTC, date, datetime

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from app.domain.checkin import Checkin, CheckinDiario, Nivel, Tag
from app.domain.errors import CheckinAlreadyExistsError
from app.domain.users import Role
from app.infrastructure.models import Base, CheckinModel, UserModel
from app.infrastructure.repositories import SqlCheckinRepository


@pytest.fixture(scope="session", autouse=True)
def database():
    yield


@pytest.fixture(autouse=True)
def clean_tables():
    yield


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


@pytest.fixture
def user_id(session):
    u_id = uuid.uuid4()
    session.add(
        UserModel(
            id=u_id,
            email="user@example.com",
            password_hash="hashed_pw",
            role=Role.USER,
        )
    )
    session.commit()
    return u_id


@pytest.fixture
def other_user_id(session):
    u_id = uuid.uuid4()
    session.add(
        UserModel(
            id=u_id,
            email="other@example.com",
            password_hash="hashed_pw",
            role=Role.USER,
        )
    )
    session.commit()
    return u_id


def test_add_and_get_by_id(session, user_id):
    repo = SqlCheckinRepository(session)
    checkin_id = uuid.uuid4()
    now = datetime.now(UTC)

    checkin = Checkin(
        id=checkin_id,
        user_id=user_id,
        data=date(2026, 10, 29),
        pensamento_risco=False,
        humor=4,
        ansiedade=1,
        sono=5,
        sobrecarga=2,
        nivel=Nivel.AUTOCUIDADO,
        tags=[Tag.HUMOR, Tag.SONO],
        criado_em=now,
    )
    repo.add(checkin)

    retrieved = repo.get_by_id_for_user(checkin_id, user_id)
    assert retrieved is not None
    assert retrieved.id == checkin_id
    assert retrieved.user_id == user_id
    assert retrieved.data == date(2026, 10, 29)
    assert retrieved.pensamento_risco is False
    assert retrieved.humor == 4
    assert retrieved.ansiedade == 1
    assert retrieved.sono == 5
    assert retrieved.sobrecarga == 2
    assert retrieved.nivel == Nivel.AUTOCUIDADO
    assert retrieved.tags == [Tag.HUMOR, Tag.SONO]


def test_checkindiario_alias(session, user_id):
    repo = SqlCheckinRepository(session)
    # Testa instanciação usando a classe alias CheckinDiario da Figura 6
    checkin = CheckinDiario(
        user_id=user_id,
        data=date(2026, 10, 30),
        pensamento_risco=False,
        humor=3,
        nivel=Nivel.AUTOCUIDADO,
    )
    repo.add(checkin)
    retrieved = repo.get_by_id_for_user(checkin.id, user_id)
    assert retrieved is not None
    assert isinstance(retrieved, CheckinDiario)


def test_add_with_nullable_fields(session, user_id):
    repo = SqlCheckinRepository(session)
    checkin = Checkin(
        user_id=user_id,
        data=date(2026, 10, 28),
        pensamento_risco=False,
        humor=None,
        ansiedade=None,
        sono=None,
        sobrecarga=None,
        tags=[],
    )
    repo.add(checkin)

    retrieved = repo.get_by_id_for_user(checkin.id, user_id)
    assert retrieved is not None
    assert retrieved.humor is None
    assert retrieved.ansiedade is None
    assert retrieved.sono is None
    assert retrieved.sobrecarga is None
    assert retrieved.tags == []


def test_get_by_id_other_user_returns_none(session, user_id, other_user_id):
    repo = SqlCheckinRepository(session)
    checkin = Checkin(
        user_id=user_id,
        data=date(2026, 10, 29),
        pensamento_risco=False,
    )
    repo.add(checkin)

    # User B should NOT be able to access User A's check-in
    assert repo.get_by_id_for_user(checkin.id, other_user_id) is None


def test_get_by_user_and_date(session, user_id):
    repo = SqlCheckinRepository(session)
    target_date = date(2026, 10, 25)
    checkin = Checkin(
        user_id=user_id,
        data=target_date,
        pensamento_risco=False,
    )
    repo.add(checkin)

    found = repo.get_by_user_and_date(user_id, target_date)
    assert found is not None
    assert found.id == checkin.id

    not_found = repo.get_by_user_and_date(user_id, date(2026, 10, 26))
    assert not_found is None


def test_unique_constraint_same_user_same_date(session, user_id, other_user_id):
    repo = SqlCheckinRepository(session)
    checkin_day = date(2026, 10, 29)

    first = Checkin(
        user_id=user_id,
        data=checkin_day,
        pensamento_risco=False,
    )
    repo.add(first)

    duplicate = Checkin(
        user_id=user_id,
        data=checkin_day,
        pensamento_risco=True,
    )
    with pytest.raises(CheckinAlreadyExistsError):
        repo.add(duplicate)

    # Another user on the same date should succeed
    other_checkin = Checkin(
        user_id=other_user_id,
        data=checkin_day,
        pensamento_risco=False,
    )
    repo.add(other_checkin)
    assert repo.get_by_user_and_date(other_user_id, checkin_day) is not None


def test_list_by_user_pagination_and_ordering(session, user_id):
    repo = SqlCheckinRepository(session)
    d1 = Checkin(user_id=user_id, data=date(2026, 10, 1), pensamento_risco=False)
    d2 = Checkin(user_id=user_id, data=date(2026, 10, 2), pensamento_risco=False)
    d3 = Checkin(user_id=user_id, data=date(2026, 10, 3), pensamento_risco=False)

    repo.add(d1)
    repo.add(d2)
    repo.add(d3)

    # Order should be DESC: d3, d2, d1
    items, total = repo.list_by_user(user_id, limit=2, offset=0)
    assert total == 3
    assert len(items) == 2
    assert items[0].data == date(2026, 10, 3)
    assert items[1].data == date(2026, 10, 2)

    # Second page
    page2, total2 = repo.list_by_user(user_id, limit=2, offset=2)
    assert total2 == 3
    assert len(page2) == 1
    assert page2[0].data == date(2026, 10, 1)


def test_list_by_user_date_filters(session, user_id):
    repo = SqlCheckinRepository(session)
    for day in range(1, 6):
        repo.add(Checkin(user_id=user_id, data=date(2026, 10, day), pensamento_risco=False))

    items, total = repo.list_by_user(
        user_id,
        from_date=date(2026, 10, 2),
        to_date=date(2026, 10, 4),
    )
    assert total == 3
    assert [c.data for c in items] == [
        date(2026, 10, 4),
        date(2026, 10, 3),
        date(2026, 10, 2),
    ]


def test_cascade_delete_user_removes_checkins(session, user_id):
    repo = SqlCheckinRepository(session)
    checkin = Checkin(
        user_id=user_id,
        data=date(2026, 10, 29),
        pensamento_risco=False,
    )
    repo.add(checkin)
    assert repo.get_by_id_for_user(checkin.id, user_id) is not None

    # Exclui o usuário (Requisito R04 - ON DELETE CASCADE)
    user = session.get(UserModel, user_id)
    session.delete(user)
    session.commit()

    # O check-in deve ter sido removido automaticamente pelo banco
    assert session.get(CheckinModel, checkin.id) is None
