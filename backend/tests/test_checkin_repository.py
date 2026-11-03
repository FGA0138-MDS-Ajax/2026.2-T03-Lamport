import uuid
from datetime import UTC, date, datetime

import pytest

from app.domain.checkin import Checkin, CheckinDiario, Nivel, Tag
from app.domain.errors import CheckinAlreadyExistsError
from app.domain.users import Role
from app.infrastructure.models import CheckinModel, UserModel
from app.infrastructure.repositories import SqlCheckinRepository


@pytest.fixture
def repo(db_session):
    return SqlCheckinRepository(db_session)


@pytest.fixture
def user_id(db_session):
    u_id = uuid.uuid4()
    db_session.add(
        UserModel(
            id=u_id,
            email="user@example.com",
            password_hash="hashed_pw",
            role=Role.USER,
        )
    )
    db_session.commit()
    return u_id


@pytest.fixture
def other_user_id(db_session):
    u_id = uuid.uuid4()
    db_session.add(
        UserModel(
            id=u_id,
            email="other@example.com",
            password_hash="hashed_pw",
            role=Role.USER,
        )
    )
    db_session.commit()
    return u_id


def test_add_and_get_by_id(repo, user_id):
    checkin_id = uuid.uuid4()
    now = datetime.now(UTC)

    checkin = Checkin(
        id=checkin_id,
        user_id=user_id,
        data=date(2026, 10, 29),
        pensamento_risco=False,
        nivel=Nivel.AUTOCUIDADO,
        humor=4,
        ansiedade=1,
        sono=5,
        sobrecarga=2,
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


def test_checkindiario_alias(repo, user_id):
    checkin = CheckinDiario(
        user_id=user_id,
        data=date(2026, 10, 30),
        pensamento_risco=False,
        nivel=Nivel.AUTOCUIDADO,
        humor=3,
    )
    repo.add(checkin)
    retrieved = repo.get_by_id_for_user(checkin.id, user_id)
    assert retrieved is not None
    assert isinstance(retrieved, CheckinDiario)


def test_add_with_nullable_fields(repo, user_id):
    checkin = Checkin(
        user_id=user_id,
        data=date(2026, 10, 28),
        pensamento_risco=False,
        nivel=Nivel.AUTOCUIDADO,
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


def test_get_by_id_other_user_returns_none(repo, user_id, other_user_id):
    checkin = Checkin(
        user_id=user_id,
        data=date(2026, 10, 29),
        pensamento_risco=False,
        nivel=Nivel.AUTOCUIDADO,
    )
    repo.add(checkin)

    # User B should NOT be able to access User A's check-in
    assert repo.get_by_id_for_user(checkin.id, other_user_id) is None


def test_get_by_user_and_date(repo, user_id):
    target_date = date(2026, 10, 25)
    checkin = Checkin(
        user_id=user_id,
        data=target_date,
        pensamento_risco=False,
        nivel=Nivel.AUTOCUIDADO,
    )
    repo.add(checkin)

    found = repo.get_by_user_and_date(user_id, target_date)
    assert found is not None
    assert found.id == checkin.id

    not_found = repo.get_by_user_and_date(user_id, date(2026, 10, 26))
    assert not_found is None


def test_unique_constraint_same_user_same_date(repo, user_id, other_user_id):
    checkin_day = date(2026, 10, 29)

    first = Checkin(
        user_id=user_id,
        data=checkin_day,
        pensamento_risco=False,
        nivel=Nivel.AUTOCUIDADO,
    )
    repo.add(first)

    duplicate = Checkin(
        user_id=user_id,
        data=checkin_day,
        pensamento_risco=True,
        nivel=Nivel.CRISE,
    )
    with pytest.raises(CheckinAlreadyExistsError):
        repo.add(duplicate)

    # Another user on the same date should succeed
    other_checkin = Checkin(
        user_id=other_user_id,
        data=checkin_day,
        pensamento_risco=False,
        nivel=Nivel.AUTOCUIDADO,
    )
    repo.add(other_checkin)
    assert repo.get_by_user_and_date(other_user_id, checkin_day) is not None


def test_list_by_user_newest_first_with_limit(repo, user_id):
    # Gravados fora de ordem para que a ordenação venha da consulta.
    for day in (2, 1, 3):
        repo.add(
            Checkin(
                user_id=user_id,
                data=date(2026, 10, day),
                pensamento_risco=False,
                nivel=Nivel.AUTOCUIDADO,
            )
        )

    assert [c.data for c in repo.list_by_user(user_id, limit=30)] == [
        date(2026, 10, 3),
        date(2026, 10, 2),
        date(2026, 10, 1),
    ]
    assert [c.data for c in repo.list_by_user(user_id, limit=2)] == [
        date(2026, 10, 3),
        date(2026, 10, 2),
    ]


def test_list_by_user_does_not_return_other_users_checkins(repo, user_id, other_user_id):
    own = Checkin(
        user_id=user_id,
        data=date(2026, 10, 1),
        pensamento_risco=False,
        nivel=Nivel.AUTOCUIDADO,
    )
    repo.add(own)
    repo.add(
        Checkin(
            user_id=other_user_id,
            data=date(2026, 10, 2),
            pensamento_risco=False,
            nivel=Nivel.AUTOCUIDADO,
        )
    )

    assert [c.id for c in repo.list_by_user(user_id, limit=30)] == [own.id]


def test_cascade_delete_user_removes_checkins(repo, db_session, user_id):
    checkin = Checkin(
        user_id=user_id,
        data=date(2026, 10, 29),
        pensamento_risco=False,
        nivel=Nivel.AUTOCUIDADO,
    )
    repo.add(checkin)
    db_session.commit()
    assert repo.get_by_id_for_user(checkin.id, user_id) is not None

    # Exclui o usuário (Requisito R04 - ON DELETE CASCADE)
    user = db_session.get(UserModel, user_id)
    db_session.delete(user)
    db_session.commit()

    # O check-in deve ter sido removido automaticamente pelo banco
    assert db_session.get(CheckinModel, checkin.id) is None
