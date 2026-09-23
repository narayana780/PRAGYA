import uuid

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PragyaException
from app.modules.training_history.models import TrainingHistory
from app.modules.training_history.repository import TrainingHistoryRepository


class TrainingHistoryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = TrainingHistoryRepository(session)

    async def get_employee_training_history(
        self, employee_id: uuid.UUID
    ) -> list[TrainingHistory]:
        # Validate employee exists first
        from app.modules.employees.repository import EmployeeRepository

        emp_repo = EmployeeRepository(self.session)
        employee = await emp_repo.get_by_id(employee_id)
        if not employee:
            raise PragyaException(
                code="EMPLOYEE_NOT_FOUND",
                message=f"Employee with ID {employee_id} was not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return await self.repository.list_by_employee_id(employee_id)
