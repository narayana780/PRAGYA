import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.departments.models import Department


class DepartmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, department_id: uuid.UUID) -> Department | None:
        result = await self.session.execute(
            select(Department).where(Department.id == department_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Department | None:
        result = await self.session.execute(
            select(Department).where(Department.code == code)
        )
        return result.scalar_one_or_none()

    async def list_active(self) -> list[Department]:
        result = await self.session.execute(
            select(Department)
            .where(Department.is_active == True)
            .order_by(Department.name)
        )
        return list(result.scalars().all())

    async def create(self, department: Department) -> Department:
        self.session.add(department)
        await self.session.flush()
        return department
