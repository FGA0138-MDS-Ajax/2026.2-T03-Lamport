import logging
import uuid
from collections.abc import Callable
from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.domain.checkin import Checkin, CheckinRepository
from app.domain.errors import CheckinAlreadyExistsError, CheckinNotFoundError
from app.rules.checkin import avaliar_checkin

CHECKIN_TIMEZONE = ZoneInfo("America/Sao_Paulo")

logger = logging.getLogger(__name__)


def today_in_checkin_timezone() -> date:
    return datetime.now(CHECKIN_TIMEZONE).date()


class CheckinService:
    def __init__(self, checkins: CheckinRepository, commit: Callable[[], None]) -> None:
        self.checkins = checkins
        self.commit = commit

    def create(
        self,
        user_id: uuid.UUID,
        p1: int | None,
        p2: int | None,
        p3: int | None,
        p4: int | None,
        p5: bool,
    ) -> Checkin:
        today = today_in_checkin_timezone()
        if self.checkins.get_by_user_and_date(user_id, today) is not None:
            raise CheckinAlreadyExistsError

        resultado = avaliar_checkin(p1, p2, p3, p4, p5)
        # p1 a p5 são os nomes da API; o domínio usa os nomes da Figura 6.
        checkin = Checkin(
            user_id=user_id,
            data=today,
            humor=p1,
            ansiedade=p2,
            sono=p3,
            sobrecarga=p4,
            pensamento_risco=p5,
            nivel=resultado.nivel,
            tags=list(resultado.tags),
        )
        self.checkins.add(checkin)
        self.commit()
        logger.info("Check-in created id=%s user_id=%s", checkin.id, user_id)
        return checkin

    def get_today(self, user_id: uuid.UUID) -> Checkin:
        checkin = self.checkins.get_by_user_and_date(user_id, today_in_checkin_timezone())
        if checkin is None:
            raise CheckinNotFoundError
        return checkin
