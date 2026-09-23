import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.departments.schemas import DepartmentResponse
from app.modules.departments.service import DepartmentService

router = APIRouter(prefix="/departments", tags=["Departments"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("", response_model=list[DepartmentResponse])
async def list_departments(
    db: DbSession,
) -> list[DepartmentResponse]:
    """Retrieve all active departments in the Statistical System."""
    service = DepartmentService(db)
    return await service.list_departments()


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: uuid.UUID,
    db: DbSession,
) -> DepartmentResponse:
    """Retrieve details of a specific department by ID."""
    service = DepartmentService(db)
    return await service.get_department(department_id)
