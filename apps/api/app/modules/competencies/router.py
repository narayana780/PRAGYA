import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.competencies.schemas import (
    CompetencyDetailResponse,
    CompetencyDomainResponse,
    CompetencySummaryResponse,
    PaginatedCompetenciesResponse,
    ProficiencyLevelResponse,
    RoleCompetencyRequirementResponse,
    RoleRequiringCompetencyResponse,
)
from app.modules.competencies.service import CompetencyService

DbSession = Annotated[AsyncSession, Depends(get_db)]

competencies_router = APIRouter(prefix="/competencies", tags=["Competencies"])
domains_router = APIRouter(prefix="/domains", tags=["Competency Domains"])
proficiency_router = APIRouter(
    prefix="/proficiency-levels", tags=["Proficiency Levels"]
)
role_competencies_router = APIRouter(prefix="/job-roles", tags=["Job Roles"])


# -----------------------------------------------------------------------------
# Competencies Endpoints
# -----------------------------------------------------------------------------
@competencies_router.get("", response_model=PaginatedCompetenciesResponse)
async def list_competencies(
    db: DbSession,
    domain: str | None = Query(
        None, description="Filter by domain code (e.g. STATISTICAL, TECHNICAL)"
    ),
    active: bool | None = Query(None, description="Filter by active status"),
    search: str | None = Query(
        None, description="Search by code, name, or description"
    ),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
) -> PaginatedCompetenciesResponse:
    """List competencies in the dictionary with optional domain filter and search."""
    service = CompetencyService(db)
    return await service.list_competencies(
        domain_code=domain,
        is_active=active,
        search=search,
        page=page,
        page_size=page_size,
    )


@competencies_router.get("/{competency_id}", response_model=CompetencyDetailResponse)
async def get_competency(
    competency_id: uuid.UUID,
    db: DbSession,
) -> CompetencyDetailResponse:
    """Retrieve complete competency metadata, prerequisites, and requiring roles."""
    service = CompetencyService(db)
    return await service.get_competency(competency_id)


@competencies_router.get(
    "/{competency_id}/roles",
    response_model=list[RoleRequiringCompetencyResponse],
)
async def get_roles_requiring_competency(
    competency_id: uuid.UUID,
    db: DbSession,
) -> list[RoleRequiringCompetencyResponse]:
    """Retrieve all official cadre job roles that require this competency."""
    service = CompetencyService(db)
    return await service.get_roles_requiring_competency(competency_id)


# -----------------------------------------------------------------------------
# Domains Endpoints
# -----------------------------------------------------------------------------
@domains_router.get("", response_model=list[CompetencyDomainResponse])
async def list_domains(
    db: DbSession,
) -> list[CompetencyDomainResponse]:
    """List the 4 canonical competency domains with current competency counts."""
    service = CompetencyService(db)
    return await service.list_domains()


@domains_router.get(
    "/{domain_id}/competencies",
    response_model=list[CompetencySummaryResponse],
)
async def get_domain_competencies(
    domain_id: uuid.UUID,
    db: DbSession,
) -> list[CompetencySummaryResponse]:
    """Retrieve all competencies belonging to a specific domain."""
    service = CompetencyService(db)
    return await service.get_competencies_by_domain(domain_id)


# -----------------------------------------------------------------------------
# Proficiency Levels Endpoints
# -----------------------------------------------------------------------------
@proficiency_router.get("", response_model=list[ProficiencyLevelResponse])
async def list_proficiency_levels(
    db: DbSession,
) -> list[ProficiencyLevelResponse]:
    """Retrieve the 5 canonical proficiency levels and their 0-100 score ranges."""
    service = CompetencyService(db)
    return await service.list_proficiency_levels()


# -----------------------------------------------------------------------------
# Role Competency Requirements Endpoints
# -----------------------------------------------------------------------------
@role_competencies_router.get(
    "/{role_id}/competencies",
    response_model=list[RoleCompetencyRequirementResponse],
)
async def get_role_competencies(
    role_id: uuid.UUID,
    db: DbSession,
) -> list[RoleCompetencyRequirementResponse]:
    """Retrieve the competency profile and proficiency requirements for a job role."""
    service = CompetencyService(db)
    return await service.get_role_competencies(role_id)


@role_competencies_router.get(
    "/{role_id}/competencies/{competency_id}",
    response_model=RoleCompetencyRequirementResponse,
)
async def get_role_competency(
    role_id: uuid.UUID,
    competency_id: uuid.UUID,
    db: DbSession,
) -> RoleCompetencyRequirementResponse:
    """Retrieve specific role requirement for a competency."""
    service = CompetencyService(db)
    return await service.get_role_competency(role_id, competency_id)
