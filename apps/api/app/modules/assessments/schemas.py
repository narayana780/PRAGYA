import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CompetencyBriefResponse(BaseModel):
    id: uuid.UUID
    code: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class QuestionPublicResponse(BaseModel):
    id: uuid.UUID
    assessment_id: uuid.UUID
    competency_id: uuid.UUID
    question_text: str
    options: list[str]
    difficulty: str
    points: int
    order_index: int

    model_config = ConfigDict(from_attributes=True)


class QuestionReviewResponse(QuestionPublicResponse):
    correct_option: int
    explanation: str


class AssessmentResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    assessment_type: str
    status: str
    duration_minutes: int
    question_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssessmentDetailResponse(AssessmentResponse):
    competencies: list[CompetencyBriefResponse] = []


class AttemptStartRequest(BaseModel):
    employee_id: uuid.UUID


class AttemptResponse(BaseModel):
    id: uuid.UUID
    assessment_id: uuid.UUID
    employee_id: uuid.UUID
    started_at: datetime
    completed_at: datetime | None = None
    raw_score: float = 0.0
    percentage: float = 0.0
    status: str

    model_config = ConfigDict(from_attributes=True)


class AttemptDetailResponse(AttemptResponse):
    assessment_title: str
    duration_minutes: int
    questions: list[QuestionPublicResponse] = []
    answered_question_ids: list[uuid.UUID] = []


class RecordResponseRequest(BaseModel):
    question_id: uuid.UUID
    selected_option: int = Field(..., ge=0, le=3)


class RecordResponseResult(BaseModel):
    attempt_id: uuid.UUID
    question_id: uuid.UUID
    selected_option: int
    responded_at: datetime


class CompetencyBreakdownItem(BaseModel):
    competency_id: uuid.UUID
    competency_name: str
    competency_code: str
    questions_tested: int
    correct_count: int
    score_percentage: float


class CompleteAttemptResponse(BaseModel):
    attempt_id: uuid.UUID
    assessment_id: uuid.UUID
    employee_id: uuid.UUID
    status: str
    completed_at: datetime
    raw_score: float
    max_score: float
    percentage: float
    total_questions: int
    answered_questions: int
    competency_breakdown: list[CompetencyBreakdownItem]


class CompetencyEvidenceResponse(BaseModel):
    id: uuid.UUID
    employee_id: uuid.UUID
    competency_id: uuid.UUID
    evidence_type: str
    source_id: str | None = None
    raw_value: float
    normalized_score: float
    weight_used: float
    contribution: float
    confidence: float
    recorded_at: datetime
    metadata: dict[str, Any] | None = Field(default=None, validation_alias="metadata_json")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class EmployeeCompetencyResponse(BaseModel):
    id: uuid.UUID
    employee_id: uuid.UUID
    competency_id: uuid.UUID
    competency_name: str
    competency_code: str
    domain_name: str
    domain_code: str
    current_score: float
    proficiency_level_number: int
    proficiency_level_name: str
    confidence: float
    confidence_label: str
    last_assessed_at: datetime
    evidence_count: int

    model_config = ConfigDict(from_attributes=True)


class CompetencyScoreHistoryResponse(BaseModel):
    id: uuid.UUID
    employee_id: uuid.UUID
    competency_id: uuid.UUID
    competency_name: str | None = None
    previous_score: float | None = None
    new_score: float
    previous_confidence: float | None = None
    new_confidence: float
    change_reason: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SelfAssessmentRequest(BaseModel):
    competency_id: uuid.UUID
    level: int = Field(..., ge=1, le=5, description="1: Beginner, 2: Basic, 3: Working, 4: Proficient, 5: Advanced")


class SelfAssessmentResponse(BaseModel):
    competency_id: uuid.UUID
    level: int
    normalized_score: float
    new_competency_score: float
    confidence: float
    confidence_label: str
