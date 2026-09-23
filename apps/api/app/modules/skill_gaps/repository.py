import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.competencies.models import Competency, CompetencyDomain
from app.modules.skill_gaps.models import SkillGap


class SkillGapRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_employee_and_competency(
        self, employee_id: uuid.UUID, competency_id: uuid.UUID
    ) -> SkillGap | None:
        stmt = (
            select(SkillGap)
            .options(
                selectinload(SkillGap.competency).selectinload(Competency.domain),
                selectinload(SkillGap.current_level),
                selectinload(SkillGap.required_level),
            )
            .where(
                SkillGap.employee_id == employee_id,
                SkillGap.competency_id == competency_id,
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_by_employee(
        self,
        employee_id: uuid.UUID,
        priority: str | None = None,
        domain: str | None = None,
        competency: str | None = None,
        confidence: str | None = None,
    ) -> list[SkillGap]:
        stmt = (
            select(SkillGap)
            .options(
                selectinload(SkillGap.competency).selectinload(Competency.domain),
                selectinload(SkillGap.current_level),
                selectinload(SkillGap.required_level),
            )
            .where(SkillGap.employee_id == employee_id)
            .execution_options(populate_existing=True)
        )

        if priority:
            stmt = stmt.where(func.upper(SkillGap.priority_level) == priority.upper())

        if confidence:
            stmt = stmt.where(func.upper(SkillGap.confidence_flag) == confidence.upper())

        if domain:
            stmt = stmt.join(SkillGap.competency).join(Competency.domain)
            stmt = stmt.where(
                (func.upper(CompetencyDomain.code) == domain.upper())
                | (func.upper(CompetencyDomain.name) == domain.upper())
            )

        if competency:
            if not domain:
                stmt = stmt.join(SkillGap.competency)
            stmt = stmt.where(
                (func.upper(Competency.code) == competency.upper())
                | (Competency.name.ilike(f"%{competency}%"))
            )

        # Order by priority_score descending, then gap_score descending
        stmt = stmt.order_by(SkillGap.priority_score.desc(), SkillGap.gap_score.desc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def upsert(self, gap: SkillGap) -> SkillGap:
        existing = await self.get_by_employee_and_competency(
            gap.employee_id, gap.competency_id
        )
        if existing:
            existing.current_score = gap.current_score
            existing.required_score = gap.required_score
            existing.gap_score = gap.gap_score
            existing.current_level_id = gap.current_level_id
            existing.required_level_id = gap.required_level_id
            existing.confidence = gap.confidence
            existing.confidence_flag = gap.confidence_flag
            existing.criticality = gap.criticality
            existing.task_relevance = gap.task_relevance
            existing.mission_urgency = gap.mission_urgency
            existing.priority_score = gap.priority_score
            existing.priority_level = gap.priority_level
            existing.role_relevance = gap.role_relevance
            existing.explanation = gap.explanation
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            self.db.add(gap)
            await self.db.commit()
            await self.db.refresh(gap)
            return gap

    async def delete_by_employee(self, employee_id: uuid.UUID) -> None:
        stmt = select(SkillGap).where(SkillGap.employee_id == employee_id)
        res = await self.db.execute(stmt)
        for row in res.scalars().all():
            await self.db.delete(row)
        await self.db.commit()
