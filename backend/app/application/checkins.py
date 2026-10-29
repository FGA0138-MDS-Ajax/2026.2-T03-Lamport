import logging
import uuid

from app.domain.checkins import (
    Checkin,
    CheckinRepository,
    avaliar_checkin,
    today_in_checkin_timezone,
)
from app.domain.errors import CheckinAlreadyDoneError

logger = logging.getLogger(__name__)


class CheckinService:
    def __init__(self, checkins: CheckinRepository) -> None:
        self.checkins = checkins

    def create(
        self,
        user_id: uuid.UUID,
        humor: int | None,
        ansiedade: int | None,
        sono: int | None,
        sobrecarga: int | None,
        pensamento_risco: bool,
    ) -> Checkin:
        today = today_in_checkin_timezone()
        if self.checkins.exists_for_date(user_id, today):
            raise CheckinAlreadyDoneError

        nivel, tags = avaliar_checkin(humor, ansiedade, sono, sobrecarga, pensamento_risco)
        checkin = Checkin(
            user_id=user_id,
            data=today,
            humor=humor,
            ansiedade=ansiedade,
            sono=sono,
            sobrecarga=sobrecarga,
            pensamento_risco=pensamento_risco,
            nivel=nivel,
            tags=tags,
        )
        self.checkins.add(checkin)
        logger.info("Check-in created id=%s user_id=%s", checkin.id, user_id)
        return checkin