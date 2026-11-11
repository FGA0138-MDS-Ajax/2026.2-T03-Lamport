"""Usuários fictícios do ambiente de demonstração (Visão, Quadro 25).

Uso: ``python -m app.seed_demo``

Pode ser executado mais de uma vez: usuários e check-ins já existentes são mantidos.
As contas usam uma senha conhecida e servem apenas para demonstração e testes de sistema.
"""

from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy.orm import Session

from app.api.deps import get_auth_service
from app.application.checkins import today_in_checkin_timezone
from app.domain.checkin import Checkin
from app.infrastructure.database import get_engine
from app.infrastructure.repositories import SqlCheckinRepository, SqlUserRepository
from app.rules.checkin import avaliar_checkin

DEMO_PASSWORD = "sintoniza-demo"


@dataclass(frozen=True)
class DemoUser:
    email: str
    description: str
    # Respostas (p1, p2, p3, p4, p5) dos dias anteriores, do mais antigo para ontem.
    past_checkins: tuple[tuple[int | None, int | None, int | None, int | None, bool], ...] = ()


DEMO_USERS = (
    DemoUser(
        email="demo@example.com",
        description="sem check-ins",
    ),
    DemoUser(
        email="historico@example.com",
        description="com check-ins nos 5 dias anteriores",
        past_checkins=(
            (4, 0, 4, 1, False),  # bem-estar
            (2, 1, 3, 1, False),  # humor
            (3, 2, 2, 1, False),  # ansiedade e sono
            (3, 1, 3, 3, False),  # estresse
            (None, None, None, None, False),  # só P5 respondida
        ),
    ),
)


def seed_demo_users(session: Session) -> list[tuple[DemoUser, bool]]:
    """Cria os usuários fictícios que ainda não existem. Retorna (usuário, criado agora)."""
    auth = get_auth_service(session)
    users = SqlUserRepository(session)
    checkins = SqlCheckinRepository(session)
    today = today_in_checkin_timezone()

    result = []
    for demo in DEMO_USERS:
        user = users.get_by_email(demo.email)
        created = user is None
        if created:
            user = auth.register(
                demo.email, DEMO_PASSWORD, accepted_terms=True, declared_adult=True
            )

        total = len(demo.past_checkins)
        for days_ago, (p1, p2, p3, p4, p5) in zip(
            range(total, 0, -1), demo.past_checkins, strict=True
        ):
            data = today - timedelta(days=days_ago)
            if checkins.get_by_user_and_date(user.id, data) is not None:
                continue
            avaliacao = avaliar_checkin(p1, p2, p3, p4, p5)
            checkins.add(
                Checkin(
                    user_id=user.id,
                    data=data,
                    humor=p1,
                    ansiedade=p2,
                    sono=p3,
                    sobrecarga=p4,
                    pensamento_risco=p5,
                    nivel=avaliacao.nivel,
                    tags=list(avaliacao.tags),
                )
            )
        session.commit()
        result.append((demo, created))
    return result


def main() -> None:
    with Session(get_engine(), expire_on_commit=False) as session:
        result = seed_demo_users(session)

    print(f"Usuários fictícios (senha: {DEMO_PASSWORD}):")
    for demo, created in result:
        status = "criado" if created else "já existia"
        print(f"  {demo.email:<24} {demo.description} ({status})")


if __name__ == "__main__":
    main()
