from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app.core.deps import get_current_user_id
from app.schemas.response import Response, ResponseSchema
from app.schemas.skill_marketplace import (
    SkillsMpRecommendationsResponse,
    SkillsMpSearchResponse,
)
from app.services.marketplace import SkillsMpService

router = APIRouter(prefix="/skills/marketplace", tags=["skills"])

skillsmp_service = SkillsMpService()


@router.get(
    "/search",
    response_model=ResponseSchema[SkillsMpSearchResponse],
)
async def search_skills_marketplace(
    q: str = Query(default="", max_length=200),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=50),
    user_id: str = Depends(get_current_user_id),
) -> JSONResponse:
    _ = user_id
    result = await skillsmp_service.search(
        query=q,
        page=page,
        page_size=page_size,
    )
    return Response.success(data=result, message="SkillsMP search completed successfully")


@router.get(
    "/recommendations",
    response_model=ResponseSchema[SkillsMpRecommendationsResponse],
)
async def list_skills_marketplace_recommendations(
    limit: int = Query(default=9, ge=1, le=24),
    user_id: str = Depends(get_current_user_id),
) -> JSONResponse:
    _ = user_id
    result = await skillsmp_service.list_recommendations(limit=limit)
    return Response.success(
        data=result,
        message="SkillsMP recommendations completed successfully",
    )
