import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.competencies.models import Competency
from app.modules.courses.models import LearningItem, LearningItemCompetency
from app.modules.recommendations.models import (
    LearningPath,
    LearningPathItem,
    LearningRecommendation,
)


class RecommendationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_learning_items(
        self,
        provider: str | None = None,
        difficulty: str | None = None,
        competency_id: uuid.UUID | None = None,
        format_type: str | None = None,
        search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[LearningItem], int]:
        stmt = (
            select(LearningItem)
            .options(
                selectinload(LearningItem.competency_mappings)
                .selectinload(LearningItemCompetency.competency)
                .selectinload(Competency.domain)
            )
            .where(LearningItem.is_active.is_(True))
        )

        def _is_valid_filter(val: object) -> bool:
            if val is None:
                return False
            s = str(val).strip()
            return bool(s) and s.upper() not in ("ALL", "NONE", "NULL", "UNDEFINED")

        if _is_valid_filter(provider):
            stmt = stmt.where(func.upper(LearningItem.provider) == str(provider).strip().upper())

        if _is_valid_filter(difficulty):
            stmt = stmt.where(func.upper(LearningItem.difficulty) == str(difficulty).strip().upper())

        if _is_valid_filter(format_type):
            stmt = stmt.where(func.upper(LearningItem.format) == str(format_type).strip().upper())

        if _is_valid_filter(competency_id):
            stmt = stmt.join(LearningItem.competency_mappings).where(
                LearningItemCompetency.competency_id == competency_id
            )

        if search:
            q = f"%{search.strip()}%"
            stmt = stmt.where(
                LearningItem.title.ilike(q) | LearningItem.description.ilike(q)
            )

        # Total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_res = await self.db.execute(count_stmt)
        total = count_res.scalar_one() or 0

        stmt = stmt.order_by(LearningItem.title).limit(limit).offset(offset)
        res = await self.db.execute(stmt)
        items = list(res.scalars().unique().all())
        return items, total

    async def get_learning_item_by_id(self, item_id: uuid.UUID) -> LearningItem | None:
        stmt = (
            select(LearningItem)
            .options(
                selectinload(LearningItem.competency_mappings)
                .selectinload(LearningItemCompetency.competency)
                .selectinload(Competency.domain)
            )
            .where(LearningItem.id == item_id)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_recommendations(
        self,
        employee_id: uuid.UUID,
        priority: str | None = None,
        provider: str | None = None,
        competency: str | None = None,
        item_type: str | None = None,
        language: str | None = None,
        status: str = "ACTIVE",
    ) -> list[LearningRecommendation]:
        stmt = (
            select(LearningRecommendation)
            .options(
                selectinload(LearningRecommendation.learning_item)
                .selectinload(LearningItem.competency_mappings)
                .selectinload(LearningItemCompetency.competency)
                .selectinload(Competency.domain),
                selectinload(LearningRecommendation.target_competency)
                .selectinload(Competency.domain),
                selectinload(LearningRecommendation.gap),
            )
            .join(LearningRecommendation.learning_item)
            .where(
                LearningRecommendation.employee_id == employee_id,
                LearningRecommendation.status == status,
            )
            .execution_options(populate_existing=True)
        )

        if priority:
            stmt = stmt.where(
                func.upper(LearningRecommendation.priority_level) == priority.upper()
            )

        if provider:
            stmt = stmt.where(
                func.upper(LearningItem.provider) == provider.upper()
            )

        if item_type:
            stmt = stmt.where(
                func.upper(LearningItem.type) == item_type.upper()
            )

        if language:
            stmt = stmt.where(
                func.upper(LearningItem.language) == language.upper()
            )

        if competency:
            stmt = stmt.join(LearningRecommendation.target_competency).where(
                Competency.name.ilike(f"%{competency}%")
                | Competency.code.ilike(f"%{competency}%")
            )

        stmt = stmt.order_by(LearningRecommendation.rank.asc())
        res = await self.db.execute(stmt)
        return list(res.scalars().unique().all())

    async def get_recommendation_by_id(
        self, recommendation_id: uuid.UUID
    ) -> LearningRecommendation | None:
        stmt = (
            select(LearningRecommendation)
            .options(
                selectinload(LearningRecommendation.learning_item)
                .selectinload(LearningItem.competency_mappings)
                .selectinload(LearningItemCompetency.competency)
                .selectinload(Competency.domain),
                selectinload(LearningRecommendation.target_competency)
                .selectinload(Competency.domain),
                selectinload(LearningRecommendation.gap),
            )
            .where(LearningRecommendation.id == recommendation_id)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def save_recommendations(
        self, employee_id: uuid.UUID, recommendations: list[LearningRecommendation]
    ) -> list[LearningRecommendation]:
        # Delete existing active recommendations
        stmt_del = (
            delete(LearningRecommendation)
            .where(
                LearningRecommendation.employee_id == employee_id,
                LearningRecommendation.status == "ACTIVE",
            )
            .execution_options(synchronize_session="fetch")
        )
        await self.db.execute(stmt_del)

        for rec in recommendations:
            self.db.add(rec)

        await self.db.commit()
        return await self.list_recommendations(employee_id)

    async def get_learning_path(
        self, employee_id: uuid.UUID
    ) -> LearningPath | None:
        stmt = (
            select(LearningPath)
            .options(
                selectinload(LearningPath.target_role),
                selectinload(LearningPath.items)
                .selectinload(LearningPathItem.learning_item)
                .selectinload(LearningItem.competency_mappings)
                .selectinload(LearningItemCompetency.competency)
                .selectinload(Competency.domain),
                selectinload(LearningPath.items)
                .selectinload(LearningPathItem.target_competency)
                .selectinload(Competency.domain),
            )
            .where(
                LearningPath.employee_id == employee_id,
                LearningPath.status == "IN_PROGRESS",
            )
            .order_by(LearningPath.generated_at.desc())
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def save_learning_path(
        self, learning_path: LearningPath
    ) -> LearningPath:
        # Archive any previous in-progress path for this employee
        stmt_archive = (
            select(LearningPath)
            .where(
                LearningPath.employee_id == learning_path.employee_id,
                LearningPath.status == "IN_PROGRESS",
            )
        )
        res = await self.db.execute(stmt_archive)
        existing = res.scalars().all()
        for p in existing:
            p.status = "ARCHIVED"

        self.db.add(learning_path)
        await self.db.commit()
        return await self.get_learning_path(learning_path.employee_id)  # type: ignore
