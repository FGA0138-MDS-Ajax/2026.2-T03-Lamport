from fastapi import APIRouter, status

from app.api.deps import AvaliacaoServiceDep, CurrentSession
from app.api.schemas import AvaliacaoCreate, AvaliacaoCreatedResponse
from app.domain.avaliacao import Avaliacao

router = APIRouter(prefix="/avaliacoes", tags=["avaliacoes"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=AvaliacaoCreatedResponse,
    summary="Registrar avaliação quinzenal (PHQ-9 e GAD-7)",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Token ausente, inválido ou revogado"},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Respostas ausentes, tamanho inválido ou valor fora de 0..3"
        },
    },
)
def create_avaliacao(
    payload: AvaliacaoCreate,
    session: CurrentSession,
    service: AvaliacaoServiceDep,
) -> Avaliacao:
    return service.create(
        user_id=session.user.id,
        phq9=payload.phq9,
        gad7=payload.gad7,
    )
