import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class LearningItemCompetencyMapping(BaseModel):
    competency_id: uuid.UUID
    competency_code: str | None = None
    competency_name: str | None = None
    domain_name: str | None = None
    coverage_level: str
    learning_outcome: str | None = None


class LearningItemResponse(BaseModel):
    id: uuid.UUID
    provider: str
    provider_item_id: str
    title: str
    description: str
    type: str
    difficulty: str
    level: int
    duration_minutes: int
    language: str
    format: str
    url: str | None = None
    prerequisites: list[dict[str, Any]] = []
    is_active: bool
    source_mode: str
    item_metadata: dict[str, Any] = {}
    competencies: list[LearningItemCompetencyMapping] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecommendationBreakdown(BaseModel):
    gap_priority_component: float
    semantic_match_component: float
    level_fit_component: float
    outcome_coverage_component: float
    prerequisite_fit_component: float
    duration_fit_component: float
    novelty_component: float


class RecommendationReasonResponse(BaseModel):
    summary: str
    gap_reason: str
    role_reason: str
    competency_reason: str
    level_reason: str
    novelty_reason: str


class LearningRecommendationResponse(BaseModel):
    id: uuid.UUID
    employee_id: uuid.UUID
    learning_item_id: uuid.UUID
    target_competency_id: uuid.UUID
    target_competency_name: str
    target_competency_code: str
    domain_name: str
    learning_item: LearningItemResponse
    gap_id: uuid.UUID | None = None
    gap_score: float | None = None
    score: float
    rank: int
    reason: str
    structured_reason: RecommendationReasonResponse
    priority_breakdown: RecommendationBreakdown
    matched_competencies: list[dict[str, Any]] = []
    priority_level: str
    status: str
    expires_at: datetime | None = None
    generated_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LearningPathItemResponse(BaseModel):
    id: uuid.UUID
    learning_item_id: uuid.UUID
    sequence_order: int
    reason: str
    target_competency_id: uuid.UUID
    target_competency_name: str | None = None
    target_competency_code: str | None = None
    estimated_duration: int
    status: str
    learning_item: LearningItemResponse

    model_config = ConfigDict(from_attributes=True)


class LearningPathResponse(BaseModel):
    id: uuid.UUID
    employee_id: uuid.UUID
    target_role_id: uuid.UUID | None = None
    target_role_name: str | None = None
    title: str
    description: str
    status: str
    items: list[LearningPathItemResponse] = []
    generated_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProviderInfoResponse(BaseModel):
    provider: str
    name: str
    mode: str
    status: str
    description: str
    catalogue_count: int = 0
