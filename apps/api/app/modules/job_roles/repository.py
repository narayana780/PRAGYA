import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.job_roles.models import JobRole


class JobRoleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, job_role_id: uuid.UUID) -> JobRole | None:
        result = await self.session.execute(
            select(JobRole).where(JobRole.id == job_role_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> JobRole | None:
        result = await self.session.execute(select(JobRole).where(JobRole.code == code))
        return result.scalar_one_or_none()

    async def list_active(self) -> list[JobRole]:
        result = await self.session.execute(
            select(JobRole).where(JobRole.is_active == True).order_by(JobRole.name)
        )
        return list(result.scalars().all())

    async def create(self, job_role: JobRole) -> JobRole:
        self.session.add(job_role)
        await self.session.flush()
        return job_role
