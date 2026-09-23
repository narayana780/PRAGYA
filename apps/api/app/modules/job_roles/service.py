import uuid

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PragyaException
from app.modules.job_roles.models import JobRole
from app.modules.job_roles.repository import JobRoleRepository


class JobRoleService:
    def __init__(self, session: AsyncSession):
        self.repository = JobRoleRepository(session)

    async def list_job_roles(self) -> list[JobRole]:
        return await self.repository.list_active()

    async def get_job_role(self, job_role_id: uuid.UUID) -> JobRole:
        job_role = await self.repository.get_by_id(job_role_id)
        if not job_role:
            raise PragyaException(
                code="JOB_ROLE_NOT_FOUND",
                message=f"Job role with ID {job_role_id} was not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return job_role
