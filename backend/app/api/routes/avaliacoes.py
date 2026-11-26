import uuid

from fastapi import APIRouter, status

from app.api.deps import AvaliacaoServiceDep, CurrentSession
from app.api.schemas import (
    AvaliacaoCreate,
    AvaliacaoCreatedResponse,
    AvaliacaoDetailResponse,
    AvaliacaoItemResponse,
)
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


@router.get(
    "",
    response_model=list[AvaliacaoItemResponse],
    summary="Histórico de avaliações do usuário",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Token ausente, inválido ou revogado"},
    },
)
def list_avaliacoes(session: CurrentSession, service: AvaliacaoServiceDep) -> list[Avaliacao]:
    return service.list(user_id=session.user.id)


@router.get(
    "/{avaliacao_id}",
    response_model=AvaliacaoDetailResponse,
    summary="Resultado de uma avaliação por ID",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Token ausente, inválido ou revogado"},
        status.HTTP_404_NOT_FOUND: {"description": "Avaliação não encontrada"},
    },
)
def read_avaliacao_by_id(
    avaliacao_id: uuid.UUID,
    session: CurrentSession,
    service: AvaliacaoServiceDep,
) -> Avaliacao:
    return service.get_by_id(avaliacao_id=avaliacao_id, user_id=session.user.id)
