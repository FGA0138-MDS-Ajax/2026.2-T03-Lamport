from fastapi import APIRouter, status

from app.api.deps import CheckinServiceDep, CurrentSession
from app.api.schemas import CheckinCreate, CheckinResponse
from app.domain.checkins import Checkin

router = APIRouter(prefix="/checkins", tags=["checkins"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=CheckinResponse,
    summary="Registrar check-in diário",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Token ausente, inválido ou revogado"},
        status.HTTP_409_CONFLICT: {"description": "O usuário já fez o check-in de hoje"},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Resposta fora da faixa ou pensamento_risco ausente"
        },
    },
)
def create_checkin(
    payload: CheckinCreate, session: CurrentSession, service: CheckinServiceDep
) -> Checkin:
    return service.create(
        user_id=session.user.id,
        humor=payload.humor,
        ansiedade=payload.ansiedade,
        sono=payload.sono,
        sobrecarga=payload.sobrecarga,
        pensamento_risco=payload.pensamento_risco,
    )