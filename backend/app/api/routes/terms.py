from fastapi import APIRouter

from app.api.schemas import TermsResponse
from app.core.config import get_settings

router = APIRouter(prefix="/terms", tags=["terms"])


@router.get("")
def read_terms() -> TermsResponse:
    return TermsResponse(version=get_settings().terms_version)
