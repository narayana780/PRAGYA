import uuid
from typing import Any

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PragyaException
from app.core.logging import logger
from app.modules.employees.models import Employee
from app.modules.employees.repository import EmployeeRepository
from app.modules.employees.schemas import EmployeeResponse, EmployeeUpdateRequest
from app.modules.job_roles.repository import JobRoleRepository


class EmployeeService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = EmployeeRepository(session)
        self.job_role_repository = JobRoleRepository(session)

    def _to_response(self, employee: Employee) -> EmployeeResponse:
        return EmployeeResponse(
            id=employee.id,
            employee_code=employee.employee_code,
            user_id=employee.user_id,
            full_name=employee.full_name,
            designation=employee.designation,
            department_id=employee.department_id,
            department_name=employee.department.name if employee.department else None,
            department_code=employee.department.code if employee.department else None,
            job_role_id=employee.job_role_id,
            job_role_name=employee.job_role.name if employee.job_role else None,
            job_role_code=employee.job_role.code if employee.job_role else None,
            current_assignment=employee.current_assignment,
            education=employee.education,
            experience_years=employee.experience_years,
            preferred_language=employee.preferred_language,
            target_role_id=employee.target_role_id,
            target_role_name=employee.target_role.name
            if employee.target_role
            else None,
            profile_image_url=employee.profile_image_url,
            is_active=employee.is_active,
            created_at=employee.created_at,
            updated_at=employee.updated_at,
            training_count=len(employee.training_history)
            if employee.training_history
            else 0,
        )

    async def get_me(self) -> EmployeeResponse:
        employee = await self.repository.get_primary_demo()
        if not employee:
            raise PragyaException(
                code="EMPLOYEE_NOT_FOUND",
                message="Primary demo employee (EMP-0001) not found in system.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return self._to_response(employee)

    async def get_employee(self, employee_id: uuid.UUID) -> EmployeeResponse:
        employee = await self.repository.get_by_id(employee_id)
        if not employee:
            raise PragyaException(
                code="EMPLOYEE_NOT_FOUND",
                message=f"Employee with ID '{employee_id}' was not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return self._to_response(employee)

    async def update_employee(
        self, employee_id: uuid.UUID, update_data: EmployeeUpdateRequest
    ) -> EmployeeResponse:
        employee = await self.repository.get_by_id(employee_id)
        if not employee:
            raise PragyaException(
                code="EMPLOYEE_NOT_FOUND",
                message=f"Employee with ID '{employee_id}' was not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Validate target_role_id if provided
        data_to_update: dict[str, Any] = {}
        dumped = update_data.model_dump(exclude_unset=True)

        if "target_role_id" in dumped:
            target_role_id = dumped["target_role_id"]
            if target_role_id is not None:
                role = await self.job_role_repository.get_by_id(target_role_id)
                if not role:
                    raise PragyaException(
                        code="JOB_ROLE_NOT_FOUND",
                        message=f"Target job role with ID '{target_role_id}' does not exist.",
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )
            data_to_update["target_role_id"] = target_role_id

        # Validate experience if provided
        if "experience_years" in dumped:
            exp = dumped["experience_years"]
            if exp is not None and (exp < 0 or exp > 50):
                raise PragyaException(
                    code="INVALID_PROFILE_UPDATE",
                    message="Experience years must be between 0 and 50.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            data_to_update["experience_years"] = exp

        # Other allowed editable fields
        for field in ["current_assignment", "education", "preferred_language"]:
            if field in dumped:
                data_to_update[field] = dumped[field]

        if not data_to_update:
            return self._to_response(employee)

        updated_employee = await self.repository.update(employee, data_to_update)
        await self.session.commit()

        # Audit hook preparation: log structured event
        logger.info(
            f"AUDIT_EVENT: EMPLOYEE_PROFILE_UPDATED employee_id={employee_id} "
            f"updated_fields={list(data_to_update.keys())}"
        )

        # Reload with relationships
        fresh_employee = await self.repository.get_by_id(employee_id)
        return self._to_response(fresh_employee or updated_employee)
