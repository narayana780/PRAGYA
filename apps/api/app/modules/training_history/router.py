import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.training_history.schemas import TrainingHistoryResponse
from app.modules.training_history.service import TrainingHistoryService

router = APIRouter(tags=["Training History"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get(
    "/employees/{employee_id}/training-history",
    response_model=list[TrainingHistoryResponse],
)
async def get_employee_training_history(
    employee_id: uuid.UUID,
    db: DbSession,
) -> list[TrainingHistoryResponse]:
    """Retrieve verified training history records for an employee."""
    service = TrainingHistoryService(db)
    records = await service.get_employee_training_history(employee_id)
    return [TrainingHistoryResponse.model_validate(r) for r in records]
