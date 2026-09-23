import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PriorityBreakdown(BaseModel):
    gap_component: float
    criticality_component: float
    task_relevance_component: float
    mission_urgency_component: float
    confidence_component: float


class SkillGapResponse(BaseModel):
    id: uuid.UUID
    employee_id: uuid.UUID
    competency_id: uuid.UUID
    competency_code: str
    competency_name: str
    domain_name: str
    domain_code: str
    current_score: float
    required_score: float
    gap_score: float
    current_level_id: uuid.UUID | None = None
    current_level_number: int | None = None
    current_level_name: str | None = None
    required_level_id: uuid.UUID
    required_level_number: int
    required_level_name: str
    confidence: float
    confidence_flag: str
    criticality: str
    task_relevance: str
    mission_urgency: str
    priority_score: float
    priority_level: str
    role_relevance: str | None = None
    explanation: str
    calculated_at: datetime
    updated_at: datetime
    priority_breakdown: PriorityBreakdown | None = None

    model_config = ConfigDict(from_attributes=True)


class SkillGapSummaryResponse(BaseModel):
    total_competencies: int
    gaps_count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    no_gap_count: int
    average_gap: float
    highest_priority_gap: SkillGapResponse | None = None
    last_calculated_at: datetime | None = None
