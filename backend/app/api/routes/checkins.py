import uuid
from datetime import date

from fastapi import APIRouter, Query

from app.api.deps import CheckinServiceDep, CurrentSession
from app.api.schemas import CheckinResponse

router = APIRouter(prefix="/checkins", tags=["checkins"])


@router.get("", response_model=list[CheckinResponse])
def list_checkins(
    session: CurrentSession,
    service: CheckinServiceDep,
    limite: int = Query(default=30, ge=1, le=30, alias="limite"),
    limit: int | None = Query(default=None, ge=1, le=30),
    offset: int = Query(default=0, ge=0),
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
) -> list[CheckinResponse]:
    effective_limit = limit if limit is not None else limite
    items = service.list_checkins(
        user_id=session.user.id,
        limit=effective_limit,
        offset=offset,
        from_date=from_date,
        to_date=to_date,
    )
    return [CheckinResponse.model_validate(c) for c in items]


@router.get("/hoje", response_model=CheckinResponse)
def get_today_checkin(
    session: CurrentSession,
    service: CheckinServiceDep,
) -> CheckinResponse:
    checkin = service.get_today_checkin(user_id=session.user.id)
    return CheckinResponse.model_validate(checkin)


@router.get("/{checkin_id}", response_model=CheckinResponse)
def get_checkin(
    checkin_id: uuid.UUID,
    session: CurrentSession,
    service: CheckinServiceDep,
) -> CheckinResponse:
    checkin = service.get_checkin_detail(
        checkin_id=checkin_id,
        user_id=session.user.id,
    )
    return CheckinResponse.model_validate(checkin)
