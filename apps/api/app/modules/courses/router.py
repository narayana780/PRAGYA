"""PRAGYA Course Domain REST API Router"""
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.courses.schemas import (
    AssignmentResultResponse,
    AssignmentSubmitRequest,
    CourseCompleteResponse,
    CourseProgressResponse,
    FinalAssessmentResultResponse,
    FinalAssessmentSubmitRequest,
    KnowledgeCheckResultResponse,
    KnowledgeCheckSubmitRequest,
    ProviderSyncResponse,
    RecalibrateCourseResponse,
    ResourceLaunchResponse,
    ResourceProgressResponse,
    ResourceProgressUpdateRequest,
)
from app.modules.courses.service import CourseService
from app.modules.employees.service import EmployeeService

router = APIRouter(prefix="/courses", tags=["Courses & Learning Paths"])
DbSession = Annotated[AsyncSession, Depends(get_db)]


async def resolve_employee_id(
    db: DbSession,
    employee_id: uuid.UUID | None = Query(None, description="Employee UUID query param"),
    x_employee_id: Annotated[str | None, Header()] = None,
) -> uuid.UUID:
    """Resolves target employee context with query param or header override."""
    if employee_id:
        return employee_id
    if x_employee_id:
        try:
            return uuid.UUID(x_employee_id.strip())
        except ValueError:
            pass
    service = EmployeeService(db)
    me = await service.get_me()
    return me.id


CurrentEmpId = Annotated[uuid.UUID, Depends(resolve_employee_id)]


@router.get(
    "/{course_id}/curriculum",
    summary="Get authoritative course curriculum, learning modules, and activities",
)
async def get_course_curriculum(
    course_id: uuid.UUID,
    db: DbSession,
) -> dict[str, Any]:
    svc = CourseService(db)
    return await svc.get_curriculum(course_id)


@router.get(
    "/{course_id}/progress",
    response_model=CourseProgressResponse,
    summary="Get persistent employee course progress, module unlock states, and activity completions",
)
async def get_course_progress(
    course_id: uuid.UUID,
    employee_id: CurrentEmpId,
    db: DbSession,
) -> CourseProgressResponse:
    svc = CourseService(db)
    return await svc.get_course_progress(employee_id, course_id)


@router.post(
    "/{course_id}/resources/{resource_id}/progress",
    response_model=ResourceProgressResponse,
    summary="Update learning resource watching/reading progress",
)
async def update_resource_progress(
    course_id: uuid.UUID,
    resource_id: str,
    req: ResourceProgressUpdateRequest,
    employee_id: CurrentEmpId,
    db: DbSession,
) -> ResourceProgressResponse:
    svc = CourseService(db)
    return await svc.update_resource_progress(employee_id, course_id, resource_id, req)


@router.post(
    "/{course_id}/resources/{resource_id}/launch",
    response_model=ResourceLaunchResponse,
    summary="Record learning resource launch on external provider",
)
async def launch_resource(
    course_id: uuid.UUID,
    resource_id: str,
    employee_id: CurrentEmpId,
    db: DbSession,
) -> ResourceLaunchResponse:
    svc = CourseService(db)
    return await svc.launch_resource(employee_id, course_id, resource_id)


@router.post(
    "/{course_id}/resources/{resource_id}/sync",
    response_model=ProviderSyncResponse,
    summary="Sync and verify single learning resource completion status from provider",
)
async def sync_resource(
    course_id: uuid.UUID,
    resource_id: str,
    employee_id: CurrentEmpId,
    db: DbSession,
) -> ProviderSyncResponse:
    svc = CourseService(db)
    return await svc.sync_provider_resource(employee_id, course_id, resource_id)


@router.post(
    "/{course_id}/providers/igot/sync",
    response_model=list[ProviderSyncResponse],
    summary="Sync all external iGOT learning resource completion records for this course",
)
async def sync_igot_course(
    course_id: uuid.UUID,
    employee_id: CurrentEmpId,
    db: DbSession,
) -> list[ProviderSyncResponse]:
    svc = CourseService(db)
    return await svc.sync_provider_course(employee_id, course_id)



@router.post(
    "/{course_id}/modules/{module_id}/knowledge-check",
    response_model=KnowledgeCheckResultResponse,
    summary="Submit module knowledge check answers and get scored feedback",
)
async def submit_knowledge_check(
    course_id: uuid.UUID,
    module_id: int,
    req: KnowledgeCheckSubmitRequest,
    employee_id: CurrentEmpId,
    db: DbSession,
) -> KnowledgeCheckResultResponse:
    svc = CourseService(db)
    return await svc.submit_knowledge_check(employee_id, course_id, module_id, req)


@router.post(
    "/{course_id}/modules/{module_id}/assignment",
    response_model=AssignmentResultResponse,
    summary="Submit module practical assignment decisions and generate competency evidence",
)
async def submit_assignment(
    course_id: uuid.UUID,
    module_id: int,
    req: AssignmentSubmitRequest,
    employee_id: CurrentEmpId,
    db: DbSession,
) -> AssignmentResultResponse:
    svc = CourseService(db)
    return await svc.submit_assignment(employee_id, course_id, module_id, req)


@router.post(
    "/{course_id}/final-assessment",
    response_model=FinalAssessmentResultResponse,
    summary="Submit final comprehensive course assessment",
)
async def submit_final_assessment(
    course_id: uuid.UUID,
    req: FinalAssessmentSubmitRequest,
    employee_id: CurrentEmpId,
    db: DbSession,
) -> FinalAssessmentResultResponse:
    svc = CourseService(db)
    return await svc.submit_final_assessment(employee_id, course_id, req)


@router.post(
    "/{course_id}/complete",
    response_model=CourseCompleteResponse,
    summary="Authoritative course completion validator and competency recalibration trigger",
)
async def complete_course(
    course_id: uuid.UUID,
    employee_id: CurrentEmpId,
    db: DbSession,
) -> CourseCompleteResponse:
    svc = CourseService(db)
    return await svc.complete_course(employee_id, course_id)


@router.post(
    "/{course_id}/recalibrate",
    response_model=RecalibrateCourseResponse,
    summary="Recalibrate employee competencies targeted by this course",
)
async def recalibrate_course(
    course_id: uuid.UUID,
    employee_id: CurrentEmpId,
    db: DbSession,
) -> RecalibrateCourseResponse:
    svc = CourseService(db)
    return await svc.recalibrate_course_competencies(employee_id, course_id)
