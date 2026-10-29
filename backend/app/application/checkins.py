import uuid
from datetime import date

from app.domain.checkin import Checkin, CheckinRepository
from app.domain.errors import CheckinNotFoundError


class CheckinService:
    def __init__(self, checkins: CheckinRepository) -> None:
        self.checkins = checkins

    def get_checkin_detail(self, checkin_id: uuid.UUID, user_id: uuid.UUID) -> Checkin:
        checkin = self.checkins.get_by_id_for_user(checkin_id=checkin_id, user_id=user_id)
        if checkin is None:
            raise CheckinNotFoundError
        return checkin

    def list_checkins(
        self,
        user_id: uuid.UUID,
        limit: int = 20,
        offset: int = 0,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> tuple[list[Checkin], int]:
        limit = max(1, min(limit, 100))
        offset = max(0, offset)
        return self.checkins.list_by_user(
            user_id=user_id,
            limit=limit,
            offset=offset,
            from_date=from_date,
            to_date=to_date,
        )
