import uuid
from datetime import UTC, date, datetime, timedelta

import pytest

from app.domain.checkin import Checkin, CheckinDiario, Nivel, Tag
from app.domain.errors import CheckinAlreadyExistsError
from app.domain.recomendacao import Recomendacao
from app.domain.users import Role
from app.infrastructure.models import CheckinModel, MaterialModel, RecomendacaoModel, UserModel
from app.infrastructure.repositories import SqlCheckinRepository, SqlRecomendacaoRepository


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


@pytest.fixture
def rec_repo(db_session):
    return SqlRecomendacaoRepository(db_session)


@pytest.fixture
def sample_materials(db_session):
    m1 = MaterialModel(
        slug="mat-ansiedade",
        titulo="Material Ansiedade",
        url="https://www.gov.br/saude/ansiedade",
        fonte="Ministério da Saúde",
        resumo="Resumo sobre ansiedade.",
        tags=["ansiedade"],
        ativo=True,
        revisado_em=date(2026, 11, 9),
    )
    m2 = MaterialModel(
        slug="mat-sono",
        titulo="Material Sono",
        url="https://www.gov.br/saude/sono",
        fonte="OPAS/OMS",
        resumo="Resumo sobre sono.",
        tags=["sono"],
        ativo=True,
        revisado_em=date(2026, 11, 9),
    )
    m_inativo = MaterialModel(
        slug="mat-inativo",
        titulo="Material Inativo",
        url="https://www.gov.br/saude/inativo",
        fonte="Ministério da Saúde",
        resumo="Resumo inativo.",
        tags=["humor"],
        ativo=False,
        revisado_em=date(2026, 11, 9),
    )
    db_session.add_all([m1, m2, m_inativo])
    db_session.commit()
    return m1, m2, m_inativo


def test_recomendacao_repo_save_list_and_active_materials(
    repo, rec_repo, db_session, user_id, sample_materials
):
    m1, m2, _ = sample_materials
    checkin = Checkin(
        user_id=user_id,
        data=date(2026, 11, 18),
        pensamento_risco=False,
        nivel=Nivel.AUTOCUIDADO,
        tags=[Tag.ANSIEDADE, Tag.SONO],
    )
    repo.add(checkin)

    t0 = datetime(2026, 11, 18, 10, 0, tzinfo=UTC)
    r1 = Recomendacao(
        user_id=user_id,
        checkin_id=checkin.id,
        material_id=m1.id,
        regra="R-D3",
        motivo="Motivo ansiedade",
        criado_em=t0,
    )
    r2 = Recomendacao(
        user_id=user_id,
        checkin_id=checkin.id,
        material_id=m2.id,
        regra="R-D4",
        motivo="Motivo sono",
        criado_em=t0 + timedelta(microseconds=1),
    )
    rec_repo.add_all([r1, r2])
    db_session.commit()

    ativas = rec_repo.list_active_materials()
    assert [m.slug for m in ativas] == ["mat-ansiedade", "mat-sono"]

    gravadas = rec_repo.list_by_checkin(checkin.id)
    assert len(gravadas) == 2
    assert [r.id for r in gravadas] == [r1.id, r2.id]
    assert gravadas[0].usuario_id == user_id
    assert gravadas[0].titulo == "Material Ansiedade"
    assert gravadas[0].fonte == "Ministério da Saúde"
    assert gravadas[0].resumo == "Resumo sobre ansiedade."
    assert gravadas[0].url == "https://www.gov.br/saude/ansiedade"
    assert gravadas[0].regra == "R-D3"
    assert gravadas[0].motivo == "Motivo ansiedade"
    assert gravadas[1].titulo == "Material Sono"
    assert gravadas[1].regra == "R-D4"


def test_recomendacao_repo_ultimas_exibicoes_por_usuario(
    repo, rec_repo, db_session, user_id, other_user_id, sample_materials
):
    m1, m2, _ = sample_materials
    t_antigo = datetime(2026, 11, 10, 12, 0, tzinfo=UTC)
    t_recente = datetime(2026, 11, 15, 12, 0, tzinfo=UTC)
    t_outro_usuario = datetime(2026, 11, 18, 12, 0, tzinfo=UTC)

    rec_repo.add_all(
        [
            Recomendacao(
                user_id=user_id,
                material_id=m1.id,
                regra="R-D3",
                motivo="Antiga",
                criado_em=t_antigo,
            ),
            Recomendacao(
                user_id=user_id,
                material_id=m1.id,
                regra="R-D3",
                motivo="Recente",
                criado_em=t_recente,
            ),
            Recomendacao(
                user_id=other_user_id,
                material_id=m2.id,
                regra="R-D4",
                motivo="Outro usuário",
                criado_em=t_outro_usuario,
            ),
        ]
    )
    db_session.commit()

    ultimas = rec_repo.get_last_displayed_by_user(user_id)
    assert ultimas == {m1.id: t_recente}
    assert rec_repo.get_last_displayed_by_user(other_user_id) == {m2.id: t_outro_usuario}


def test_cascade_delete_checkin_and_user_removes_recomendacoes(
    repo, rec_repo, db_session, user_id, sample_materials
):
    m1, m2, _ = sample_materials
    c1 = Checkin(
        user_id=user_id,
        data=date(2026, 11, 17),
        pensamento_risco=False,
        nivel=Nivel.AUTOCUIDADO,
    )
    c2 = Checkin(
        user_id=user_id,
        data=date(2026, 11, 18),
        pensamento_risco=False,
        nivel=Nivel.AUTOCUIDADO,
    )
    repo.add(c1)
    repo.add(c2)
    r1 = Recomendacao(
        user_id=user_id,
        checkin_id=c1.id,
        material_id=m1.id,
        regra="R-D3",
        motivo="Motivo 1",
    )
    r2 = Recomendacao(
        user_id=user_id,
        checkin_id=c2.id,
        material_id=m2.id,
        regra="R-D4",
        motivo="Motivo 2",
    )
    rec_repo.add_all([r1, r2])
    db_session.commit()

    # Excluir o check-in c1 remove r1 em cascata.
    db_session.delete(db_session.get(CheckinModel, c1.id))
    db_session.commit()
    assert db_session.get(RecomendacaoModel, r1.id) is None
    assert db_session.get(RecomendacaoModel, r2.id) is not None

    # Excluir o usuário remove r2 em cascata (R04).
    db_session.delete(db_session.get(UserModel, user_id))
    db_session.commit()
    assert db_session.get(RecomendacaoModel, r2.id) is None
