import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.job_roles.schemas import JobRoleResponse
from app.modules.job_roles.service import JobRoleService

router = APIRouter(prefix="/job-roles", tags=["Job Roles"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("", response_model=list[JobRoleResponse])
async def list_job_roles(
    db: DbSession,
) -> list[JobRoleResponse]:
    """Retrieve all active official cadre job roles."""
    service = JobRoleService(db)
    return await service.list_job_roles()


@router.get("/{job_role_id}", response_model=JobRoleResponse)
async def get_job_role(
    job_role_id: uuid.UUID,
    db: DbSession,
) -> JobRoleResponse:
    """Retrieve details of a specific job role by ID."""
    service = JobRoleService(db)
    return await service.get_job_role(job_role_id)
