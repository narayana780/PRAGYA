import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PragyaException
from app.db.session import get_db
from app.modules.recommendations.providers.registry import ProviderRegistry
from app.modules.recommendations.repository import RecommendationRepository
from app.modules.recommendations.schemas import (
    LearningItemResponse,
    LearningPathResponse,
    LearningRecommendationResponse,
    ProviderInfoResponse,
)
from app.modules.recommendations.service import (
    LearningPathService,
    RecommendationService,
)

router = APIRouter(tags=["Learning Recommendations"])


# =============================================================================
# PROVIDER ENDPOINTS
# =============================================================================

@router.get(
    "/providers",
    response_model=list[ProviderInfoResponse],
    summary="List available learning providers and integration mode",
)
@router.get(
    "/recommendations/providers",
    response_model=list[ProviderInfoResponse],
    include_in_schema=False,
)
async def list_providers(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ProviderInfoResponse]:
    registry = ProviderRegistry(db)
    infos = await registry.list_provider_infos()
    return [
        ProviderInfoResponse(
            provider=i.provider,
            name=i.name,
            mode=i.mode,
            status=i.status,
            description=i.description,
            catalogue_count=i.catalogue_count,
        )
        for i in infos
    ]


# =============================================================================
# LEARNING ITEM CATALOGUE ENDPOINTS
# =============================================================================

@router.get(
    "/learning-items",
    response_model=dict,
    summary="Search and discover learning items across all providers",
)
@router.get(
    "/recommendations/learning-items",
    response_model=dict,
    include_in_schema=False,
)
async def list_learning_items(
    db: Annotated[AsyncSession, Depends(get_db)],
    provider: str | None = Query(None, description="Filter by provider: IGOT, NSSTA_TPAC, PRAGYA"),
    difficulty: str | None = Query(None, description="Filter by difficulty"),
    competency_id: str | None = Query(None, description="Filter by competency UUID"),
    format_type: str | None = Query(None, description="Filter by format"),
    format: str | None = Query(None, description="Alias for format_type"),
    search: str | None = Query(None, description="Keyword search in title or description"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    skip: int | None = Query(None, description="Alias for offset"),
) -> dict:
    eff_offset = skip if skip is not None else offset
    eff_format = format or format_type
    eff_comp_id: uuid.UUID | None = None
    if competency_id is not None:
        s_comp = str(competency_id).strip()
        if s_comp and s_comp.upper() not in ("ALL", "NONE", "NULL", "UNDEFINED"):
            try:
                eff_comp_id = uuid.UUID(s_comp)
            except ValueError:
                eff_comp_id = None

    repo = RecommendationRepository(db)
    items, total = await repo.list_learning_items(
        provider=provider,
        difficulty=difficulty,
        competency_id=eff_comp_id,
        format_type=eff_format,
        search=search,
        limit=limit,
        offset=eff_offset,
    )
    svc = RecommendationService(db)
    return {
        "items": [svc._to_item_response(it) for it in items],
        "total": total,
        "limit": limit,
        "offset": eff_offset,
    }


@router.get(
    "/learning-items/{learning_item_id}",
    response_model=LearningItemResponse,
    summary="Get learning item metadata and mapped competencies",
)
@router.get(
    "/recommendations/learning-items/{learning_item_id}",
    response_model=LearningItemResponse,
    include_in_schema=False,
)
async def get_learning_item(
    learning_item_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LearningItemResponse:
    repo = RecommendationRepository(db)
    item = await repo.get_learning_item_by_id(learning_item_id)
    if not item:
        raise PragyaException(
            code="LEARNING_ITEM_NOT_FOUND",
            message=f"Learning item {learning_item_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    svc = RecommendationService(db)
    return svc._to_item_response(item)


# =============================================================================
# EMPLOYEE RECOMMENDATIONS ENDPOINTS
# =============================================================================

@router.get(
    "/employees/{employee_id}/recommendations",
    response_model=list[LearningRecommendationResponse],
    summary="Get personalized learning recommendations for an employee",
)
@router.get(
    "/recommendations/employee/{employee_id}",
    response_model=list[LearningRecommendationResponse],
    include_in_schema=False,
)
async def get_employee_recommendations(
    employee_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    priority: str | None = Query(None, description="Filter by priority: CRITICAL, HIGH, MEDIUM, LOW"),
    provider: str | None = Query(None, description="Filter by provider: IGOT, NSSTA_TPAC, PRAGYA"),
    competency: str | None = Query(None, description="Filter by competency code or name"),
    type: str | None = Query(None, description="Filter by type: COURSE, PROGRAMME, LAB"),
    language: str | None = Query(None, description="Filter by language"),
) -> list[LearningRecommendationResponse]:
    svc = RecommendationService(db)
    return await svc.get_employee_recommendations(
        employee_id=employee_id,
        priority=priority,
        provider=provider,
        competency=competency,
        item_type=type,
        language=language,
    )


@router.post(
    "/employees/{employee_id}/recommendations/generate",
    response_model=list[LearningRecommendationResponse],
    summary="Regenerate learning recommendations based on latest skill gaps",
)
@router.post(
    "/recommendations/generate",
    response_model=list[LearningRecommendationResponse],
    include_in_schema=False,
)
async def generate_employee_recommendations(
    employee_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[LearningRecommendationResponse]:
    svc = RecommendationService(db)
    return await svc.generate_recommendations(employee_id)


@router.get(
    "/employees/{employee_id}/recommendations/{recommendation_id}",
    response_model=LearningRecommendationResponse,
    summary="Get detailed breakdown for a specific recommendation",
)
@router.get(
    "/recommendations/{recommendation_id}",
    response_model=LearningRecommendationResponse,
    include_in_schema=False,
)
async def get_single_recommendation(
    employee_id: uuid.UUID,
    recommendation_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LearningRecommendationResponse:
    svc = RecommendationService(db)
    return await svc.get_recommendation_by_id(employee_id, recommendation_id)


@router.post(
    "/employees/{employee_id}/recommendations/{recommendation_id}/start",
    response_model=LearningRecommendationResponse,
    summary="Mark recommendation as started",
)
@router.patch(
    "/recommendations/{recommendation_id}/start",
    response_model=LearningRecommendationResponse,
    include_in_schema=False,
)
async def start_recommendation(
    employee_id: uuid.UUID,
    recommendation_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LearningRecommendationResponse:
    svc = RecommendationService(db)
    return await svc.update_status(employee_id, recommendation_id, "STARTED")


@router.post(
    "/employees/{employee_id}/recommendations/{recommendation_id}/dismiss",
    response_model=LearningRecommendationResponse,
    summary="Dismiss a recommendation",
)
@router.patch(
    "/recommendations/{recommendation_id}/dismiss",
    response_model=LearningRecommendationResponse,
    include_in_schema=False,
)
async def dismiss_recommendation(
    employee_id: uuid.UUID,
    recommendation_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LearningRecommendationResponse:
    svc = RecommendationService(db)
    return await svc.update_status(employee_id, recommendation_id, "DISMISSED")


# =============================================================================
# LEARNING PATH ENDPOINTS
# =============================================================================

@router.get(
    "/employees/{employee_id}/learning-path",
    response_model=LearningPathResponse | None,
    summary="Get active progressive learning pathway for an employee",
)
@router.get(
    "/recommendations/employee/{employee_id}/path",
    response_model=LearningPathResponse | None,
    include_in_schema=False,
)
async def get_learning_path(
    employee_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LearningPathResponse | None:
    path_svc = LearningPathService(db)
    return await path_svc.get_learning_path(employee_id)


@router.post(
    "/employees/{employee_id}/learning-path/generate",
    response_model=LearningPathResponse,
    summary="Generate progressive learning pathway for an employee",
)
@router.post(
    "/recommendations/generate-path",
    response_model=LearningPathResponse,
    include_in_schema=False,
)
async def generate_learning_path(
    employee_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LearningPathResponse:
    path_svc = LearningPathService(db)
    return await path_svc.generate_learning_path(employee_id)
