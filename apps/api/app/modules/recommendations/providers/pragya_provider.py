from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.courses.models import LearningItem, LearningItemCompetency
from app.modules.recommendations.providers.base import (
    LearningProvider,
    ProviderCompletionStatus,
    ProviderEnrollmentStatus,
    ProviderLearningItem,
)
from app.modules.training_history.models import TrainingHistory


class PragyaLearningProvider(LearningProvider):
    def __init__(self, db: AsyncSession):
        self.db = db

    @property
    def provider_code(self) -> str:
        return "PRAGYA"

    @property
    def provider_name(self) -> str:
        return "PRAGYA Internal Learning Labs"

    @property
    def source_mode(self) -> str:
        return "MOCK"

    def _to_provider_item(self, item: LearningItem) -> ProviderLearningItem:
        return ProviderLearningItem(
            id=str(item.id),
            provider=item.provider,
            provider_item_id=item.provider_item_id,
            title=item.title,
            description=item.description,
            type=item.type,
            difficulty=item.difficulty,
            level=item.level,
            duration_minutes=item.duration_minutes,
            language=item.language,
            format=item.format,
            url=item.url,
            prerequisites=item.prerequisites or [],
            competencies=[
                {
                    "competency_id": str(m.competency_id),
                    "coverage_level": m.coverage_level,
                    "learning_outcome": m.learning_outcome,
                    "competency_name": m.competency.name if m.competency else None,
                    "competency_code": m.competency.code if m.competency else None,
                }
                for m in item.competency_mappings
            ],
            is_active=item.is_active,
            source_mode=item.source_mode,
            metadata=item.item_metadata or {},
        )

    async def search_learning_items(
        self,
        query: str | None = None,
        competency_ids: list[str] | None = None,
        difficulty: str | None = None,
        level: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ProviderLearningItem]:
        stmt = (
            select(LearningItem)
            .options(
                selectinload(LearningItem.competency_mappings).selectinload(LearningItemCompetency.competency)
            )
            .where(LearningItem.provider == self.provider_code, LearningItem.is_active.is_(True))
        )

        if query:
            stmt = stmt.where(
                LearningItem.title.ilike(f"%{query}%")
                | LearningItem.description.ilike(f"%{query}%")
            )

        if difficulty:
            stmt = stmt.where(func.upper(LearningItem.difficulty) == difficulty.upper())

        if level is not None:
            stmt = stmt.where(LearningItem.level == level)

        if competency_ids:
            stmt = stmt.join(LearningItem.competency_mappings).where(
                LearningItemCompetency.competency_id.in_([c for c in competency_ids])
            )

        stmt = stmt.order_by(LearningItem.title).limit(limit).offset(offset)
        res = await self.db.execute(stmt)
        items = list(res.scalars().unique().all())
        return [self._to_provider_item(item) for item in items]

    async def get_learning_item(self, provider_item_id: str) -> ProviderLearningItem | None:
        stmt = (
            select(LearningItem)
            .options(
                selectinload(LearningItem.competency_mappings).selectinload(LearningItemCompetency.competency)
            )
            .where(
                LearningItem.provider == self.provider_code,
                (LearningItem.provider_item_id == provider_item_id) | (LearningItem.id == provider_item_id),
            )
        )
        res = await self.db.execute(stmt)
        item = res.scalar_one_or_none()
        return self._to_provider_item(item) if item else None

    async def get_learning_history(self, employee_id: str) -> list[ProviderCompletionStatus]:
        stmt = select(TrainingHistory).where(
            TrainingHistory.employee_id == employee_id,
            TrainingHistory.provider_type == self.provider_code,
        )
        res = await self.db.execute(stmt)
        records = res.scalars().all()
        return [
            ProviderCompletionStatus(
                employee_id=employee_id,
                provider_item_id=r.course_id or str(r.id),
                is_completed=(r.status == "COMPLETED"),
                completed_at=r.completed_at.isoformat() if r.completed_at else None,
                certificate_id=r.certificate_reference,
                score=float(r.score) if r.score is not None else None,
            )
            for r in records
        ]

    async def get_enrollment_status(
        self, employee_id: str, provider_item_id: str
    ) -> ProviderEnrollmentStatus:
        stmt = select(TrainingHistory).where(
            TrainingHistory.employee_id == employee_id,
            (TrainingHistory.course_id == provider_item_id) | (TrainingHistory.title.ilike(f"%{provider_item_id}%")),
        )
        res = await self.db.execute(stmt)
        r = res.scalar_one_or_none()
        if r:
            return ProviderEnrollmentStatus(
                employee_id=employee_id,
                provider_item_id=provider_item_id,
                status=r.status,
                enrolled_at=r.created_at.isoformat() if r.created_at else None,
                progress_pct=100.0 if r.status == "COMPLETED" else 50.0,
            )
        return ProviderEnrollmentStatus(
            employee_id=employee_id,
            provider_item_id=provider_item_id,
            status="NOT_ENROLLED",
        )

    async def get_completion_status(
        self, employee_id: str, provider_item_id: str
    ) -> ProviderCompletionStatus:
        stmt = select(TrainingHistory).where(
            TrainingHistory.employee_id == employee_id,
            TrainingHistory.status == "COMPLETED",
            (TrainingHistory.course_id == provider_item_id) | (TrainingHistory.title.ilike(f"%{provider_item_id}%")),
        )
        res = await self.db.execute(stmt)
        r = res.scalar_one_or_none()
        if r:
            return ProviderCompletionStatus(
                employee_id=employee_id,
                provider_item_id=provider_item_id,
                is_completed=True,
                completed_at=r.completed_at.isoformat() if r.completed_at else None,
                certificate_id=r.certificate_reference,
                score=float(r.score) if r.score is not None else None,
            )
        return ProviderCompletionStatus(
            employee_id=employee_id,
            provider_item_id=provider_item_id,
            is_completed=False,
        )
