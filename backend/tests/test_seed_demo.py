from sqlalchemy import func, select

from app.application.checkins import today_in_checkin_timezone
from app.infrastructure.models import CheckinModel, ConsentModel, UserModel
from app.seed_demo import DEMO_PASSWORD, DEMO_USERS, seed_demo_users


def test_seed_creates_demo_users_who_can_log_in(client, db_session):
    result = seed_demo_users(db_session)

    assert [created for _, created in result] == [True] * len(DEMO_USERS)
    for demo in DEMO_USERS:
        response = client.post(
            "/api/auth/login", json={"email": demo.email, "senha": DEMO_PASSWORD}
        )
        assert response.status_code == 200
    # Cada cadastro grava dois consentimentos: termos de uso e declaração de maioridade.
    consents = db_session.scalar(select(func.count()).select_from(ConsentModel))
    assert consents == 2 * len(DEMO_USERS)


def test_seed_creates_past_checkins_but_leaves_today_free(db_session):
    seed_demo_users(db_session)

    for demo in DEMO_USERS:
        user = db_session.scalar(select(UserModel).where(UserModel.email == demo.email))
        datas = db_session.scalars(
            select(CheckinModel.data).where(CheckinModel.user_id == user.id)
        ).all()
        assert len(datas) == len(demo.past_checkins)
        assert all(data < today_in_checkin_timezone() for data in datas)


def test_seed_is_idempotent(db_session):
    seed_demo_users(db_session)
    result = seed_demo_users(db_session)

    assert [created for _, created in result] == [False] * len(DEMO_USERS)
    assert db_session.scalar(select(func.count()).select_from(UserModel)) == len(DEMO_USERS)
    assert db_session.scalar(select(func.count()).select_from(CheckinModel)) == sum(
        len(demo.past_checkins) for demo in DEMO_USERS
    )
