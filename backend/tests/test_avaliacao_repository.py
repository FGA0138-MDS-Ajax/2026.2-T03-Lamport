import uuid
from datetime import UTC, date, datetime, timedelta

import pytest

from app.domain.avaliacao import Avaliacao, Faixa
from app.domain.checkin import Nivel
from app.domain.recomendacao import Recomendacao
from app.domain.users import Role
from app.infrastructure.models import (
    AvaliacaoModel,
    MaterialModel,
    RecomendacaoModel,
    UserModel,
)
from app.infrastructure.repositories import SqlAvaliacaoRepository, SqlRecomendacaoRepository


@pytest.fixture
def repo(db_session):
    return SqlAvaliacaoRepository(db_session)


@pytest.fixture
def rec_repo(db_session):
    return SqlRecomendacaoRepository(db_session)


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


@pytest.fixture
def material(db_session):
    mat = MaterialModel(
        slug="mat-ajuda-profissional",
        titulo="Rede de Atenção Psicossocial (RAPS)",
        url="https://www.gov.br/saude/pt-br/composicao/saes/desmad/raps",
        fonte="Ministério da Saúde",
        resumo="Apresenta os serviços públicos de saúde mental do SUS.",
        tags=["ajuda_profissional"],
        ativo=True,
        revisado_em=date(2026, 11, 9),
    )
    db_session.add(mat)
    db_session.commit()
    return mat


def _make_avaliacao(
    user_id: uuid.UUID,
    *,
    respostas_phq9: list[int] | None = None,
    respostas_gad7: list[int] | None = None,
    escore_phq9: int = 10,
    escore_gad7: int = 5,
    faixa_phq9: Faixa = Faixa.MODERADA,
    faixa_gad7: Faixa = Faixa.LEVE,
    nivel: Nivel = Nivel.ATENCAO,
    criado_em: datetime | None = None,
) -> Avaliacao:
    return Avaliacao(
        user_id=user_id,
        respostas_phq9=respostas_phq9 or [2, 2, 1, 1, 1, 1, 1, 1, 0],
        respostas_gad7=respostas_gad7 or [1, 1, 1, 1, 1, 0, 0],
        escore_phq9=escore_phq9,
        escore_gad7=escore_gad7,
        faixa_phq9=faixa_phq9,
        faixa_gad7=faixa_gad7,
        nivel=nivel,
        criado_em=criado_em or datetime.now(UTC),
    )


def test_add_and_get_by_id_for_user(repo, db_session, user_id):
    instante = datetime(2026, 11, 20, 14, 30, tzinfo=UTC)
    avaliacao = _make_avaliacao(
        user_id,
        respostas_phq9=[2, 2, 1, 1, 1, 1, 1, 1, 0],
        respostas_gad7=[1, 1, 1, 1, 1, 0, 0],
        escore_phq9=10,
        escore_gad7=5,
        faixa_phq9=Faixa.MODERADA,
        faixa_gad7=Faixa.LEVE,
        nivel=Nivel.ATENCAO,
        criado_em=instante,
    )
    repo.add(avaliacao)
    db_session.commit()

    retrieved = repo.get_by_id_for_user(avaliacao.id, user_id)
    assert retrieved is not None
    assert retrieved.id == avaliacao.id
    assert retrieved.user_id == user_id
    assert retrieved.usuario_id == user_id
    assert retrieved.respostas_phq9 == [2, 2, 1, 1, 1, 1, 1, 1, 0]
    assert retrieved.respostas_gad7 == [1, 1, 1, 1, 1, 0, 0]
    assert retrieved.escore_phq9 == 10
    assert retrieved.escore_gad7 == 5
    assert retrieved.faixa_phq9 == Faixa.MODERADA
    assert retrieved.faixa_gad7 == Faixa.LEVE
    assert retrieved.nivel == Nivel.ATENCAO
    assert retrieved.criado_em == instante


def test_get_by_id_other_user_returns_none(repo, db_session, user_id, other_user_id):
    avaliacao = _make_avaliacao(user_id)
    repo.add(avaliacao)
    db_session.commit()

    assert repo.get_by_id_for_user(avaliacao.id, other_user_id) is None
    assert repo.get_by_id_for_user(uuid.uuid4(), user_id) is None


def test_list_by_user_newest_first_and_only_own_records(repo, db_session, user_id, other_user_id):
    t1 = datetime(2026, 11, 1, 10, 0, tzinfo=UTC)
    t2 = datetime(2026, 11, 15, 10, 0, tzinfo=UTC)
    t3 = datetime(2026, 11, 20, 10, 0, tzinfo=UTC)

    av_meio = _make_avaliacao(user_id, escore_phq9=5, faixa_phq9=Faixa.LEVE, criado_em=t2)
    av_antiga = _make_avaliacao(
        user_id,
        escore_phq9=0,
        escore_gad7=0,
        faixa_phq9=Faixa.MINIMA,
        faixa_gad7=Faixa.MINIMA,
        nivel=Nivel.AUTOCUIDADO,
        criado_em=t1,
    )
    av_recente = _make_avaliacao(
        user_id,
        escore_phq9=20,
        escore_gad7=15,
        faixa_phq9=Faixa.GRAVE,
        faixa_gad7=Faixa.GRAVE,
        nivel=Nivel.PRIORITARIO,
        criado_em=t3,
    )
    av_outro = _make_avaliacao(other_user_id, criado_em=t3 + timedelta(hours=1))

    # Gravadas fora de ordem cronológica para que a ordenação venha do banco.
    for av in (av_meio, av_antiga, av_outro, av_recente):
        repo.add(av)
    db_session.commit()

    lista = repo.list_by_user(user_id)
    assert [a.id for a in lista] == [av_recente.id, av_meio.id, av_antiga.id]
    assert [a.id for a in repo.list_by_user(other_user_id)] == [av_outro.id]


def test_cascade_delete_user_removes_avaliacoes(repo, db_session, user_id):
    avaliacao = _make_avaliacao(user_id)
    repo.add(avaliacao)
    db_session.commit()
    assert db_session.get(AvaliacaoModel, avaliacao.id) is not None

    # Exclui o usuário (Requisito R04 - ON DELETE CASCADE)
    user = db_session.get(UserModel, user_id)
    db_session.delete(user)
    db_session.commit()

    assert db_session.get(AvaliacaoModel, avaliacao.id) is None


def test_recomendacao_linked_to_avaliacao_and_cascade_delete(
    repo, rec_repo, db_session, user_id, material
):
    av1 = _make_avaliacao(user_id, criado_em=datetime(2026, 11, 10, 10, 0, tzinfo=UTC))
    av2 = _make_avaliacao(user_id, criado_em=datetime(2026, 11, 20, 10, 0, tzinfo=UTC))
    repo.add(av1)
    repo.add(av2)

    r1 = Recomendacao(
        user_id=user_id,
        avaliacao_id=av1.id,
        material_id=material.id,
        regra="R-A3",
        motivo="Suas respostas indicam que conversar com um profissional de saúde pode ajudar.",
    )
    r2 = Recomendacao(
        user_id=user_id,
        avaliacao_id=av2.id,
        material_id=material.id,
        regra="R-A2",
        motivo=(
            "Suas respostas indicam sintomas intensos. "
            "Este material explica onde buscar atendimento."
        ),
    )
    rec_repo.add_all([r1, r2])
    db_session.commit()

    gravadas_av1 = rec_repo.list_by_avaliacao(av1.id)
    assert len(gravadas_av1) == 1
    assert gravadas_av1[0].id == r1.id
    assert gravadas_av1[0].avaliacao_id == av1.id
    assert gravadas_av1[0].checkin_id is None
    assert gravadas_av1[0].titulo == material.titulo
    assert gravadas_av1[0].regra == "R-A3"

    # Excluir a avaliação av1 remove r1 em cascata.
    db_session.delete(db_session.get(AvaliacaoModel, av1.id))
    db_session.commit()
    assert db_session.get(RecomendacaoModel, r1.id) is None
    assert db_session.get(RecomendacaoModel, r2.id) is not None

    # Excluir o usuário remove av2 e r2 em cascata (R04).
    db_session.delete(db_session.get(UserModel, user_id))
    db_session.commit()
    assert db_session.get(AvaliacaoModel, av2.id) is None
    assert db_session.get(RecomendacaoModel, r2.id) is None
