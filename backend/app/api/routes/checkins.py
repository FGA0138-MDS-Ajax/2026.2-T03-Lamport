from fastapi import APIRouter, status

from app.api.deps import CheckinServiceDep, CurrentSession
from app.api.schemas import CheckinCreate, CheckinCreatedResponse, CheckinTodayResponse
from app.domain.checkin import Checkin

router = APIRouter(prefix="/checkins", tags=["checkins"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=CheckinCreatedResponse,
    summary="Registrar check-in diário",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Token ausente, inválido ou revogado"},
        status.HTTP_409_CONFLICT: {"description": "O usuário já fez o check-in de hoje"},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Resposta fora da faixa ou p5 ausente"
        },
    },
)
def create_checkin(
    payload: CheckinCreate, session: CurrentSession, service: CheckinServiceDep
) -> Checkin:
    return service.create(
        user_id=session.user.id,
        p1=payload.p1,
        p2=payload.p2,
        p3=payload.p3,
        p4=payload.p4,
        p5=payload.p5,
    )


# Declarada antes de qualquer rota "/{checkin_id}", para que "hoje" não seja lido como id.
@router.get(
    "/hoje",
    response_model=CheckinTodayResponse,
    summary="Check-in de hoje do usuário",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Token ausente, inválido ou revogado"},
        status.HTTP_404_NOT_FOUND: {"description": "O usuário ainda não fez o check-in de hoje"},
    },
)
def read_today_checkin(session: CurrentSession, service: CheckinServiceDep) -> Checkin:
    return service.get_today(user_id=session.user.id)
