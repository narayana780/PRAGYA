import math
import uuid

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PragyaException
from app.modules.competencies.repository import CompetencyRepository
from app.modules.competencies.schemas import (
    CompetencyDetailResponse,
    CompetencyDomainResponse,
    CompetencyRelationshipResponse,
    CompetencySummaryResponse,
    PaginatedCompetenciesResponse,
    ProficiencyLevelResponse,
    RoleCompetencyRequirementResponse,
    RoleRequiringCompetencyResponse,
)
from app.modules.job_roles.repository import JobRoleRepository


class CompetencyService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = CompetencyRepository(session)
        self.job_role_repo = JobRoleRepository(session)

    async def list_domains(self) -> list[CompetencyDomainResponse]:
        domains_with_count = await self.repository.list_domains()
        return [
            CompetencyDomainResponse(
                id=domain.id,
                code=domain.code,
                name=domain.name,
                description=domain.description,
                display_order=domain.display_order,
                is_active=domain.is_active,
                competency_count=count,
                created_at=domain.created_at,
                updated_at=domain.updated_at,
            )
            for domain, count in domains_with_count
        ]

    async def list_proficiency_levels(self) -> list[ProficiencyLevelResponse]:
        levels = await self.repository.list_proficiency_levels()
        return [ProficiencyLevelResponse.model_validate(lvl) for lvl in levels]

    async def list_competencies(
        self,
        domain_code: str | None = None,
        is_active: bool | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> PaginatedCompetenciesResponse:
        page = max(1, page)
        page_size = max(1, min(100, page_size))
        skip = (page - 1) * page_size

        items, total = await self.repository.list_competencies(
            domain_code=domain_code,
            is_active=is_active,
            search=search,
            skip=skip,
            limit=page_size,
        )

        total_pages = math.ceil(total / page_size) if total > 0 else 0

        summary_items = [
            CompetencySummaryResponse(
                id=c.id,
                code=c.code,
                name=c.name,
                domain_id=c.domain_id,
                domain_code=c.domain.code if c.domain else None,
                domain_name=c.domain.name if c.domain else None,
                short_description=c.short_description,
                version=c.version,
                is_active=c.is_active,
                source_reference=c.source_reference,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in items
        ]

        return PaginatedCompetenciesResponse(
            items=summary_items,
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        )

    async def get_competency(
        self, competency_id: uuid.UUID
    ) -> CompetencyDetailResponse:
        competency = await self.repository.get_competency_by_id(competency_id)
        if not competency:
            raise PragyaException(
                code="COMPETENCY_NOT_FOUND",
                message=f"Competency with ID '{competency_id}' was not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        prerequisites = [
            CompetencyRelationshipResponse(
                id=rel.id,
                source_competency_id=rel.source_competency_id,
                source_competency_name=rel.source_competency.name
                if rel.source_competency
                else None,
                source_competency_code=rel.source_competency.code
                if rel.source_competency
                else None,
                target_competency_id=rel.target_competency_id,
                target_competency_name=rel.target_competency.name
                if rel.target_competency
                else None,
                target_competency_code=rel.target_competency.code
                if rel.target_competency
                else None,
                relationship_type=rel.relationship_type,
                strength=rel.strength,
            )
            for rel in competency.incoming_relationships
        ]

        requiring_roles = [
            RoleRequiringCompetencyResponse(
                job_role_id=req.job_role_id,
                job_role_name=req.job_role.name,
                job_role_code=req.job_role.code,
                career_level=req.job_role.career_level,
                required_level_number=req.required_level.level_number,
                required_level_name=req.required_level.name,
                criticality=req.criticality,
                rationale=req.rationale,
            )
            for req in competency.requirements
            if req.job_role and req.required_level
        ]

        return CompetencyDetailResponse(
            id=competency.id,
            code=competency.code,
            name=competency.name,
            domain_id=competency.domain_id,
            domain_code=competency.domain.code if competency.domain else None,
            domain_name=competency.domain.name if competency.domain else None,
            description=competency.description,
            short_description=competency.short_description,
            learning_objectives=competency.learning_objectives,
            measurement_guidance=competency.measurement_guidance,
            aliases=competency.aliases,
            version=competency.version,
            is_active=competency.is_active,
            source_reference=competency.source_reference,
            created_at=competency.created_at,
            updated_at=competency.updated_at,
            prerequisites=prerequisites,
            requiring_roles=requiring_roles,
        )

    async def get_competencies_by_domain(
        self, domain_id: uuid.UUID
    ) -> list[CompetencySummaryResponse]:
        domain = await self.repository.get_domain_by_id(domain_id)
        if not domain:
            raise PragyaException(
                code="DOMAIN_NOT_FOUND",
                message=f"Competency domain with ID '{domain_id}' was not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        competencies = await self.repository.list_by_domain_id(domain_id)
        return [
            CompetencySummaryResponse(
                id=c.id,
                code=c.code,
                name=c.name,
                domain_id=c.domain_id,
                domain_code=domain.code,
                domain_name=domain.name,
                short_description=c.short_description,
                version=c.version,
                is_active=c.is_active,
                source_reference=c.source_reference,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in competencies
        ]

    async def get_role_competencies(
        self, job_role_id: uuid.UUID
    ) -> list[RoleCompetencyRequirementResponse]:
        role = await self.job_role_repo.get_by_id(job_role_id)
        if not role:
            raise PragyaException(
                code="JOB_ROLE_NOT_FOUND",
                message=f"Job role with ID '{job_role_id}' was not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        requirements = await self.repository.get_role_requirements(job_role_id)
        return [
            RoleCompetencyRequirementResponse(
                id=req.id,
                job_role_id=req.job_role_id,
                job_role_name=req.job_role.name,
                job_role_code=req.job_role.code,
                competency_id=req.competency_id,
                competency_name=req.competency.name,
                competency_code=req.competency.code,
                domain_code=req.competency.domain.code
                if req.competency.domain
                else "UNKNOWN",
                domain_name=req.competency.domain.name
                if req.competency.domain
                else "Unknown",
                required_level_id=req.required_level_id,
                required_level_number=req.required_level.level_number,
                required_level_name=req.required_level.name,
                required_score=req.required_score,
                criticality=req.criticality,
                task_relevance=req.task_relevance,
                priority=req.priority,
                rationale=req.rationale,
                source_reference=req.source_reference,
            )
            for req in requirements
        ]

    async def get_role_competency(
        self, job_role_id: uuid.UUID, competency_id: uuid.UUID
    ) -> RoleCompetencyRequirementResponse:
        role = await self.job_role_repo.get_by_id(job_role_id)
        if not role:
            raise PragyaException(
                code="JOB_ROLE_NOT_FOUND",
                message=f"Job role with ID '{job_role_id}' was not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        req = await self.repository.get_role_requirement(job_role_id, competency_id)
        if not req:
            raise PragyaException(
                code="REQUIREMENT_NOT_FOUND",
                message=f"No competency requirement found for role '{job_role_id}' and competency '{competency_id}'.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return RoleCompetencyRequirementResponse(
            id=req.id,
            job_role_id=req.job_role_id,
            job_role_name=req.job_role.name,
            job_role_code=req.job_role.code,
            competency_id=req.competency_id,
            competency_name=req.competency.name,
            competency_code=req.competency.code,
            domain_code=req.competency.domain.code
            if req.competency.domain
            else "UNKNOWN",
            domain_name=req.competency.domain.name
            if req.competency.domain
            else "Unknown",
            required_level_id=req.required_level_id,
            required_level_number=req.required_level.level_number,
            required_level_name=req.required_level.name,
            required_score=req.required_score,
            criticality=req.criticality,
            task_relevance=req.task_relevance,
            priority=req.priority,
            rationale=req.rationale,
            source_reference=req.source_reference,
        )

    async def get_roles_requiring_competency(
        self, competency_id: uuid.UUID
    ) -> list[RoleRequiringCompetencyResponse]:
        competency = await self.repository.get_competency_by_id(competency_id)
        if not competency:
            raise PragyaException(
                code="COMPETENCY_NOT_FOUND",
                message=f"Competency with ID '{competency_id}' was not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        reqs = await self.repository.get_roles_requiring_competency(competency_id)
        return [
            RoleRequiringCompetencyResponse(
                job_role_id=r.job_role_id,
                job_role_name=r.job_role.name,
                job_role_code=r.job_role.code,
                career_level=r.job_role.career_level,
                required_level_number=r.required_level.level_number,
                required_level_name=r.required_level.name,
                criticality=r.criticality,
                rationale=r.rationale,
            )
            for r in reqs
        ]
