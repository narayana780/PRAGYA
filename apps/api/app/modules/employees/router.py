import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.employees.schemas import EmployeeResponse, EmployeeUpdateRequest
from app.modules.employees.service import EmployeeService

router = APIRouter(prefix="/employees", tags=["Employees"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("/me", response_model=EmployeeResponse)
async def get_current_employee_me(
    db: DbSession,
) -> EmployeeResponse:
    """Retrieve current primary demo officer profile (Ananya Sharma - EMP-0001)."""
    service = EmployeeService(db)
    return await service.get_me()


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee_by_id(
    employee_id: uuid.UUID,
    db: DbSession,
) -> EmployeeResponse:
    """Retrieve an employee profile by unique ID."""
    service = EmployeeService(db)
    return await service.get_employee(employee_id)


@router.patch("/{employee_id}", response_model=EmployeeResponse)
async def update_employee_profile(
    employee_id: uuid.UUID,
    update_data: EmployeeUpdateRequest,
    db: DbSession,
) -> EmployeeResponse:
    """Update editable fields of an employee profile."""
    service = EmployeeService(db)
    return await service.update_employee(employee_id, update_data)
