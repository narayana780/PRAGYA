"""
Virtual Lab REST API Endpoints
Conforms strictly to Stage 12 specification.
"""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.employees.service import EmployeeService
from app.modules.labs.schemas import (
    LabActionEvaluationResult,
    LabActionSubmitRequest,
    LabCompleteResponse,
    LabHintRequest,
    LabHintResponse,
    LabResultDetail,
    LabScenarioDetail,
    LabScenarioSummary,
    LabSessionResponse,
)
from app.modules.labs.service import LabService

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_employee_id(
    db: DbSession,
    x_employee_id: Annotated[str | None, Header()] = None,
) -> uuid.UUID:
    """Resolves authenticated employee context with header override for testing."""
    if x_employee_id:
        try:
            return uuid.UUID(x_employee_id.strip())
        except ValueError:
            pass
    service = EmployeeService(db)
    me = await service.get_me()
    return me.id


CurrentEmployeeId = Annotated[uuid.UUID, Depends(get_current_employee_id)]

# -----------------------------------------------------------------------------
# Labs Scenarios Router (/api/v1/labs)
# -----------------------------------------------------------------------------
labs_router = APIRouter(prefix="/labs", tags=["Virtual Labs"])


@labs_router.get(
    "",
    response_model=list[LabScenarioSummary],
    summary="List available statistical virtual lab scenarios",
)
async def list_scenarios(
    db: DbSession,
    competency_id: uuid.UUID | None = Query(None, description="Filter by competency ID"),
    scenario_type: str | None = Query(None, description="Filter by scenario type"),
    difficulty: str | None = Query(None, description="Filter by difficulty"),
    status: str = Query("READY", description="Scenario status"),
) -> list[LabScenarioSummary]:
    service = LabService(db)
    return await service.list_scenarios(
        competency_id=competency_id,
        scenario_type=scenario_type,
        difficulty=difficulty,
        status=status,
    )


@labs_router.get(
    "/{scenario_id}",
    response_model=LabScenarioDetail,
    summary="Get scenario specifications, instructions, and synthetic dataset",
)
async def get_scenario(
    scenario_id: uuid.UUID,
    db: DbSession,
) -> LabScenarioDetail:
    service = LabService(db)
    return await service.get_scenario_detail(scenario_id)


@labs_router.post(
    "/{scenario_id}/sessions",
    response_model=LabSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new interactive virtual lab session",
)
async def start_session(
    scenario_id: uuid.UUID,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> LabSessionResponse:
    service = LabService(db)
    return await service.start_session(employee_id=employee_id, scenario_id=scenario_id)


@labs_router.get(
    "/sessions/my",
    response_model=list[LabSessionResponse],
    summary="List virtual lab sessions for current employee",
)
async def list_my_sessions(
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> list[LabSessionResponse]:
    service = LabService(db)
    return await service.get_employee_sessions(employee_id)


# -----------------------------------------------------------------------------
# Lab Sessions Execution Router (/api/v1/lab-sessions)
# -----------------------------------------------------------------------------
lab_sessions_router = APIRouter(prefix="/lab-sessions", tags=["Virtual Lab Sessions"])


@lab_sessions_router.get(
    "/{session_id}",
    response_model=LabSessionResponse,
    summary="Get session execution state and action history",
)
async def get_session(
    session_id: uuid.UUID,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> LabSessionResponse:
    service = LabService(db)
    return await service.get_session(employee_id=employee_id, session_id=session_id)


@lab_sessions_router.post(
    "/{session_id}/actions",
    response_model=LabActionEvaluationResult,
    summary="Submit and evaluate a controlled analytical action",
)
async def submit_action(
    session_id: uuid.UUID,
    req: LabActionSubmitRequest,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> LabActionEvaluationResult:
    service = LabService(db)
    return await service.submit_action(employee_id=employee_id, session_id=session_id, req=req)


@lab_sessions_router.post(
    "/{session_id}/complete",
    response_model=LabCompleteResponse,
    summary="Complete virtual lab session and record competency evidence",
)
async def complete_session(
    session_id: uuid.UUID,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> LabCompleteResponse:
    service = LabService(db)
    return await service.complete_session(employee_id=employee_id, session_id=session_id)


@lab_sessions_router.get(
    "/{session_id}/result",
    response_model=LabResultDetail,
    summary="Get comprehensive completion report, score, and educational feedback",
)
async def get_result(
    session_id: uuid.UUID,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> LabResultDetail:
    service = LabService(db)
    return await service.get_result(employee_id=employee_id, session_id=session_id)


@lab_sessions_router.post(
    "/{session_id}/hint",
    response_model=LabHintResponse,
    summary="Request a deterministic educational hint for the current step",
)
async def get_hint(
    session_id: uuid.UUID,
    req: LabHintRequest,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> LabHintResponse:
    service = LabService(db)
    return await service.get_hint(employee_id=employee_id, session_id=session_id, step_number=req.step_number)


@lab_sessions_router.post(
    "/{session_id}/abandon",
    response_model=LabSessionResponse,
    summary="Abandon a virtual lab session",
)
async def abandon_session(
    session_id: uuid.UUID,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> LabSessionResponse:
    service = LabService(db)
    return await service.abandon_session(employee_id=employee_id, session_id=session_id)
