import uuid

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PragyaException
from app.modules.departments.models import Department
from app.modules.departments.repository import DepartmentRepository


class DepartmentService:
    def __init__(self, session: AsyncSession):
        self.repository = DepartmentRepository(session)

    async def list_departments(self) -> list[Department]:
        return await self.repository.list_active()

    async def get_department(self, department_id: uuid.UUID) -> Department:
        department = await self.repository.get_by_id(department_id)
        if not department:
            raise PragyaException(
                code="DEPARTMENT_NOT_FOUND",
                message=f"Department with ID {department_id} was not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return department
