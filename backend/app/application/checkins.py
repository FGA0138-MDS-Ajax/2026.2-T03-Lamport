import uuid
import zoneinfo
from datetime import date, datetime

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

    def get_today_checkin(self, user_id: uuid.UUID, today: date | None = None) -> Checkin:
        if today is None:
            today = datetime.now(zoneinfo.ZoneInfo("America/Sao_Paulo")).date()

        get_fn = getattr(self.checkins, "get_by_user_and_date", None)
        if callable(get_fn):
            checkin = get_fn(user_id=user_id, data=today)
        else:
            items, _ = self.checkins.list_by_user(
                user_id=user_id, from_date=today, to_date=today, limit=1
            )
            checkin = items[0] if items else None

        if checkin is None:
            raise CheckinNotFoundError
        return checkin

    def list_checkins(
        self,
        user_id: uuid.UUID,
        limit: int = 30,
        offset: int = 0,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[Checkin]:
        limit = max(1, min(limit, 30))
        offset = max(0, offset)
        items, _ = self.checkins.list_by_user(
            user_id=user_id,
            limit=limit,
            offset=offset,
            from_date=from_date,
            to_date=to_date,
        )
        return items
