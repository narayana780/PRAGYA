import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CompetencyDomainResponse(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    description: str | None = None
    display_order: int = 0
    is_active: bool = True
    competency_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProficiencyLevelResponse(BaseModel):
    id: uuid.UUID
    level_number: int
    name: str
    description: str
    minimum_score: int
    maximum_score: int
    display_order: int = 0
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class CompetencyRelationshipResponse(BaseModel):
    id: uuid.UUID
    source_competency_id: uuid.UUID
    source_competency_name: str | None = None
    source_competency_code: str | None = None
    target_competency_id: uuid.UUID
    target_competency_name: str | None = None
    target_competency_code: str | None = None
    relationship_type: str
    strength: float = 1.0

    model_config = ConfigDict(from_attributes=True)


class CompetencySummaryResponse(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    domain_id: uuid.UUID
    domain_code: str | None = None
    domain_name: str | None = None
    short_description: str
    version: str = "1.0"
    is_active: bool = True
    source_reference: str = "SIH26101"
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoleRequiringCompetencyResponse(BaseModel):
    job_role_id: uuid.UUID
    job_role_name: str
    job_role_code: str
    career_level: str
    required_level_number: int
    required_level_name: str
    criticality: str
    rationale: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CompetencyDetailResponse(CompetencySummaryResponse):
    description: str
    learning_objectives: str | None = None
    measurement_guidance: str | None = None
    aliases: str | None = None
    prerequisites: list[CompetencyRelationshipResponse] = []
    requiring_roles: list[RoleRequiringCompetencyResponse] = []


class PaginatedCompetenciesResponse(BaseModel):
    items: list[CompetencySummaryResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


class RoleCompetencyRequirementResponse(BaseModel):
    id: uuid.UUID
    job_role_id: uuid.UUID
    job_role_name: str
    job_role_code: str
    competency_id: uuid.UUID
    competency_name: str
    competency_code: str
    domain_code: str
    domain_name: str
    required_level_id: uuid.UUID
    required_level_number: int
    required_level_name: str
    required_score: int
    criticality: str
    task_relevance: str
    priority: int
    rationale: str | None = None
    source_reference: str

    model_config = ConfigDict(from_attributes=True)
