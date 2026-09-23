import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.analytics.schemas import (
    EmployeePerformanceResponse,
    EmployeeTimelineResponse,
)
from app.modules.analytics.service import PerformanceAnalysisService

router = APIRouter(prefix="/employees", tags=["Performance Analytics"])


@router.get(
    "/{employee_id}/performance",
    response_model=EmployeePerformanceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get unified employee performance analysis",
    description=(
        "Returns authoritative, unified performance analytics for an employee covering "
        "baseline diagnostic scores, current demonstrated competency levels, job role targets, "
        "longitudinal improvement metrics, top strengths, priority focus gaps, and learning modality statistics."
    ),
)
async def get_employee_performance(
    employee_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> EmployeePerformanceResponse:
    service = PerformanceAnalysisService(db)
    return await service.get_employee_performance(employee_id)


@router.get(
    "/{employee_id}/history/timeline",
    response_model=EmployeeTimelineResponse,
    status_code=status.HTTP_200_OK,
    summary="Get employee longitudinal activity timeline",
    description=(
        "Returns a chronological timeline of real employee learning and assessment events, "
        "including diagnostic assessments, AI quizzes, CAT sessions, virtual labs, "
        "course completions, competency recalibrations, and score updates."
    ),
)
async def get_employee_timeline(
    employee_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    event_type: Annotated[
        str | None,
        Query(
            description=(
                "Filter by event type (DIAGNOSTIC_ASSESSMENT, QUIZ, ADAPTIVE_ASSESSMENT, "
                "VIRTUAL_LAB, COURSE_ACTIVITY, COMPETENCY_RECALIBRATION, SCORE_UPDATE)"
            )
        ),
    ] = None,
    limit: Annotated[
        int,
        Query(description="Maximum number of timeline events to return", ge=1, le=500),
    ] = 100,
) -> EmployeeTimelineResponse:
    service = PerformanceAnalysisService(db)
    return await service.get_employee_timeline(employee_id, event_type=event_type, limit=limit)
