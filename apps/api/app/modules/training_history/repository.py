import uuid

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.training_history.models import TrainingHistory


class TrainingHistoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_employee_id(
        self, employee_id: uuid.UUID
    ) -> list[TrainingHistory]:
        result = await self.session.execute(
            select(TrainingHistory)
            .where(TrainingHistory.employee_id == employee_id)
            .order_by(
                desc(TrainingHistory.completed_at), desc(TrainingHistory.created_at)
            )
        )
        return list(result.scalars().all())

    async def create(self, record: TrainingHistory) -> TrainingHistory:
        self.session.add(record)
        await self.session.flush()
        return record
