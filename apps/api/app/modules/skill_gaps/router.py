import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.skill_gaps.schemas import (
    SkillGapResponse,
    SkillGapSummaryResponse,
)
from app.modules.skill_gaps.service import SkillGapService

router = APIRouter(prefix="/employees", tags=["Skill Gaps"])


@router.get(
    "/{employee_id}/skill-gaps/summary",
    response_model=SkillGapSummaryResponse,
    status_code=status.HTTP_200_OK,
)
async def get_skill_gaps_summary(
    employee_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SkillGapSummaryResponse:
    """Retrieves high-level summary statistics of an employee's skill gaps and priority distribution."""
    service = SkillGapService(db)
    return await service.get_summary(employee_id)


@router.get(
    "/{employee_id}/skill-gaps",
    response_model=list[SkillGapResponse],
    status_code=status.HTTP_200_OK,
)
async def get_employee_skill_gaps(
    employee_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    priority: Annotated[
        str | None,
        Query(
            description="Filter by priority level (NO_GAP, LOW, MEDIUM, HIGH, CRITICAL)"
        ),
    ] = None,
    domain: Annotated[
        str | None,
        Query(description="Filter by competency domain code or name"),
    ] = None,
    competency: Annotated[
        str | None,
        Query(description="Filter by competency code or search keyword"),
    ] = None,
    confidence: Annotated[
        str | None,
        Query(
            description="Filter by confidence flag (LOW_CONFIDENCE, MEDIUM_CONFIDENCE, HIGH_CONFIDENCE, VERY_HIGH_CONFIDENCE)"
        ),
    ] = None,
) -> list[SkillGapResponse]:
    """Lists all evaluated skill gaps for an employee, comparing current demonstrated competency with role requirements."""
    service = SkillGapService(db)
    return await service.get_employee_gaps(
        employee_id=employee_id,
        priority=priority,
        domain=domain,
        competency=competency,
        confidence=confidence,
    )


@router.get(
    "/{employee_id}/skill-gaps/{competency_id}",
    response_model=SkillGapResponse,
    status_code=status.HTTP_200_OK,
)
async def get_employee_skill_gap_detail(
    employee_id: uuid.UUID,
    competency_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SkillGapResponse:
    """Retrieves detailed skill gap analysis and calculation components for a specific competency."""
    service = SkillGapService(db)
    return await service.get_gap_detail(employee_id, competency_id)


@router.post(
    "/{employee_id}/skill-gaps/recalculate",
    response_model=list[SkillGapResponse],
    status_code=status.HTTP_200_OK,
)
async def recalculate_employee_skill_gaps(
    employee_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[SkillGapResponse]:
    """Forces recalculation of all skill gaps for an employee based on latest demonstrated competency scores and role requirements."""
    service = SkillGapService(db)
    return await service.recalculate_employee_gaps(employee_id)
