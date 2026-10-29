import uuid
from datetime import date

from fastapi import APIRouter, Query

from app.api.deps import CheckinServiceDep, CurrentSession
from app.api.schemas import CheckinPaginationResponse, CheckinResponse

router = APIRouter(prefix="/checkins", tags=["checkins"])


@router.get("", response_model=CheckinPaginationResponse)
def list_checkins(
    session: CurrentSession,
    service: CheckinServiceDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
) -> CheckinPaginationResponse:
    items, total = service.list_checkins(
        user_id=session.user.id,
        limit=limit,
        offset=offset,
        from_date=from_date,
        to_date=to_date,
    )
    return CheckinPaginationResponse(
        items=[CheckinResponse.model_validate(c) for c in items],
        total=total,
        limit=limit,
        offset=offset,
    )


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
