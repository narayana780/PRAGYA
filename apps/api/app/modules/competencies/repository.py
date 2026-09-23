import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.competencies.models import (
    Competency,
    CompetencyDomain,
    CompetencyRelationship,
    CompetencyRequirement,
    ProficiencyLevel,
)


class CompetencyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_domains(self) -> list[tuple[CompetencyDomain, int]]:
        """List all active domains along with their competency counts."""
        stmt = (
            select(
                CompetencyDomain,
                func.count(Competency.id).label("competency_count"),
            )
            .outerjoin(
                Competency,
                (Competency.domain_id == CompetencyDomain.id)
                & (Competency.is_active == True),
            )
            .group_by(CompetencyDomain.id)
            .order_by(CompetencyDomain.display_order)
        )
        result = await self.session.execute(stmt)
        return list(result.all())

    async def get_domain_by_id(self, domain_id: uuid.UUID) -> CompetencyDomain | None:
        stmt = select(CompetencyDomain).where(CompetencyDomain.id == domain_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_domain_by_code(self, code: str) -> CompetencyDomain | None:
        stmt = select(CompetencyDomain).where(CompetencyDomain.code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_proficiency_levels(self) -> list[ProficiencyLevel]:
        """Returns the 5 canonical proficiency levels ordered by level_number."""
        stmt = select(ProficiencyLevel).order_by(ProficiencyLevel.level_number)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_competencies(
        self,
        domain_code: str | None = None,
        is_active: bool | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Competency], int]:
        """List competencies with optional search, domain filter, and pagination."""
        query = select(Competency).options(selectinload(Competency.domain))
        count_query = select(func.count(Competency.id))

        filters = []
        if domain_code:
            query = query.join(Competency.domain)
            count_query = count_query.join(Competency.domain)
            filters.append(CompetencyDomain.code == domain_code)

        if is_active is not None:
            filters.append(Competency.is_active == is_active)

        if search:
            search_pattern = f"%{search.strip()}%"
            filters.append(
                or_(
                    Competency.name.ilike(search_pattern),
                    Competency.code.ilike(search_pattern),
                    Competency.description.ilike(search_pattern),
                    Competency.short_description.ilike(search_pattern),
                )
            )

        if filters:
            query = query.where(*filters)
            count_query = count_query.where(*filters)

        total_res = await self.session.execute(count_query)
        total = total_res.scalar_one()

        query = query.order_by(Competency.code).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_competency_by_id(self, competency_id: uuid.UUID) -> Competency | None:
        stmt = (
            select(Competency)
            .options(
                selectinload(Competency.domain),
                selectinload(Competency.outgoing_relationships).selectinload(
                    CompetencyRelationship.target_competency
                ),
                selectinload(Competency.incoming_relationships).selectinload(
                    CompetencyRelationship.source_competency
                ),
                selectinload(Competency.requirements).selectinload(
                    CompetencyRequirement.job_role
                ),
                selectinload(Competency.requirements).selectinload(
                    CompetencyRequirement.required_level
                ),
            )
            .where(Competency.id == competency_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_competency_by_code(self, code: str) -> Competency | None:
        stmt = (
            select(Competency)
            .options(selectinload(Competency.domain))
            .where(Competency.code == code)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_domain_id(self, domain_id: uuid.UUID) -> list[Competency]:
        stmt = (
            select(Competency)
            .options(selectinload(Competency.domain))
            .where(
                Competency.domain_id == domain_id,
                Competency.is_active == True,
            )
            .order_by(Competency.code)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_role_requirements(
        self, job_role_id: uuid.UUID
    ) -> list[CompetencyRequirement]:
        """Fetch all competencies required for a specific job role."""
        stmt = (
            select(CompetencyRequirement)
            .options(
                selectinload(CompetencyRequirement.job_role),
                selectinload(CompetencyRequirement.competency).selectinload(
                    Competency.domain
                ),
                selectinload(CompetencyRequirement.required_level),
            )
            .where(CompetencyRequirement.job_role_id == job_role_id)
            .order_by(
                CompetencyRequirement.priority,
                CompetencyRequirement.required_score.desc(),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_role_requirement(
        self, job_role_id: uuid.UUID, competency_id: uuid.UUID
    ) -> CompetencyRequirement | None:
        stmt = (
            select(CompetencyRequirement)
            .options(
                selectinload(CompetencyRequirement.job_role),
                selectinload(CompetencyRequirement.competency).selectinload(
                    Competency.domain
                ),
                selectinload(CompetencyRequirement.required_level),
            )
            .where(
                CompetencyRequirement.job_role_id == job_role_id,
                CompetencyRequirement.competency_id == competency_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_roles_requiring_competency(
        self, competency_id: uuid.UUID
    ) -> list[CompetencyRequirement]:
        stmt = (
            select(CompetencyRequirement)
            .options(
                selectinload(CompetencyRequirement.job_role),
                selectinload(CompetencyRequirement.required_level),
            )
            .where(CompetencyRequirement.competency_id == competency_id)
            .order_by(CompetencyRequirement.required_score.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
