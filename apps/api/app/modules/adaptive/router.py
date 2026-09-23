import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.adaptive.schemas import (
    AdaptiveQuestionPresentation,
    AdaptiveSessionCreateRequest,
    AdaptiveSessionSummary,
    AdaptiveSubmitAnswerRequest,
    AdaptiveSubmitAnswerResponse,
    RecalibrationResultResponse,
)
from app.modules.adaptive.service import AdaptiveAssessmentService
from app.modules.employees.service import EmployeeService

router = APIRouter(prefix="/adaptive-assessments", tags=["Adaptive Assessment"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_employee_id(
    db: DbSession,
    x_employee_id: Annotated[str | None, Header()] = None,
) -> uuid.UUID:
    """Resolve current authenticated employee context with X-Employee-Id override for tests."""
    if x_employee_id:
        try:
            return uuid.UUID(x_employee_id.strip())
        except ValueError:
            pass
    service = EmployeeService(db)
    me = await service.get_me()
    return me.id


CurrentEmployeeId = Annotated[uuid.UUID, Depends(get_current_employee_id)]


@router.post(
    "",
    response_model=AdaptiveSessionSummary,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new adaptive assessment session",
)
async def create_session(
    req: AdaptiveSessionCreateRequest,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> AdaptiveSessionSummary:
    service = AdaptiveAssessmentService(db)
    return await service.create_session(employee_id, req)


@router.get(
    "/{session_id}",
    response_model=AdaptiveSessionSummary,
    summary="Get adaptive assessment session details and current state",
)
async def get_session(
    session_id: uuid.UUID,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> AdaptiveSessionSummary:
    service = AdaptiveAssessmentService(db)
    return await service.get_session(employee_id, session_id)


@router.post(
    "/{session_id}/questions/next",
    response_model=AdaptiveQuestionPresentation,
    summary="Get next adaptive question adapted to current difficulty",
)
async def get_next_question(
    session_id: uuid.UUID,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> AdaptiveQuestionPresentation:
    service = AdaptiveAssessmentService(db)
    return await service.get_next_question(employee_id, session_id)


@router.post(
    "/{session_id}/responses",
    response_model=AdaptiveSubmitAnswerResponse,
    summary="Submit answer to current question with single-step difficulty adaptation",
)
async def submit_response(
    session_id: uuid.UUID,
    req: AdaptiveSubmitAnswerRequest,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> AdaptiveSubmitAnswerResponse:
    service = AdaptiveAssessmentService(db)
    return await service.submit_response(employee_id, session_id, req)


@router.post(
    "/{session_id}/complete",
    response_model=RecalibrationResultResponse,
    summary="Complete adaptive assessment and execute closed-loop competency recalibration",
)
async def complete_session(
    session_id: uuid.UUID,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> RecalibrationResultResponse:
    service = AdaptiveAssessmentService(db)
    return await service.complete_session(employee_id, session_id)


@router.get(
    "/{session_id}/result",
    response_model=RecalibrationResultResponse,
    summary="Get recalibration analytics and updated skill gap priority",
)
async def get_result(
    session_id: uuid.UUID,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> RecalibrationResultResponse:
    service = AdaptiveAssessmentService(db)
    return await service.get_result(employee_id, session_id)
