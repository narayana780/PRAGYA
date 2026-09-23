import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.employees.models import Employee


class EmployeeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, employee_id: uuid.UUID) -> Employee | None:
        result = await self.session.execute(
            select(Employee)
            .options(
                selectinload(Employee.department),
                selectinload(Employee.job_role),
                selectinload(Employee.target_role),
                selectinload(Employee.training_history),
            )
            .where(Employee.id == employee_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, employee_code: str) -> Employee | None:
        result = await self.session.execute(
            select(Employee)
            .options(
                selectinload(Employee.department),
                selectinload(Employee.job_role),
                selectinload(Employee.target_role),
                selectinload(Employee.training_history),
            )
            .where(Employee.employee_code == employee_code)
        )
        return result.scalar_one_or_none()

    async def get_primary_demo(self) -> Employee | None:
        # Look for EMP-0001 first, or fallback to first active
        employee = await self.get_by_code("EMP-0001")
        if employee:
            return employee
        result = await self.session.execute(
            select(Employee)
            .options(
                selectinload(Employee.department),
                selectinload(Employee.job_role),
                selectinload(Employee.target_role),
                selectinload(Employee.training_history),
            )
            .where(Employee.is_active == True)
            .order_by(Employee.created_at)
        )
        return result.scalars().first()

    async def list_all(self) -> list[Employee]:
        result = await self.session.execute(
            select(Employee)
            .options(
                selectinload(Employee.department),
                selectinload(Employee.job_role),
                selectinload(Employee.target_role),
                selectinload(Employee.training_history),
            )
            .order_by(Employee.employee_code)
        )
        return list(result.scalars().all())

    async def create(self, employee: Employee) -> Employee:
        self.session.add(employee)
        await self.session.flush()
        return employee

    async def update(self, employee: Employee, update_data: dict[str, Any]) -> Employee:
        for key, value in update_data.items():
            setattr(employee, key, value)
        await self.session.flush()
        await self.session.refresh(employee)
        return employee
