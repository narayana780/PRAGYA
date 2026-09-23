import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AdaptiveSessionCreateRequest(BaseModel):
    competency_id: uuid.UUID
    source_document_id: uuid.UUID | None = None


class AdaptiveQuestionOption(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    option_text: str
    option_order: int


class AdaptiveQuestionPresentation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    session_id: uuid.UUID
    question_text: str
    difficulty: str
    bloom_level: str
    question_number: int
    total_target_questions: int = 15
    options: list[AdaptiveQuestionOption]
    source_document_title: str | None = None
    source_page_number: int | None = None


class AdaptiveSubmitAnswerRequest(BaseModel):
    question_id: uuid.UUID
    selected_option_id: uuid.UUID
    response_time_ms: int | None = None


class AdaptiveSubmitAnswerResponse(BaseModel):
    response_id: uuid.UUID
    session_id: uuid.UUID
    question_id: uuid.UUID
    selected_option_id: uuid.UUID
    is_correct: bool
    correct_option_id: uuid.UUID
    explanation: str
    current_difficulty: str
    next_difficulty: str
    question_count: int
    confidence: float
    can_complete: bool
    should_stop: bool
    stop_reason: str | None = None


class AdaptiveSessionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID
    competency_id: uuid.UUID
    competency_name: str | None = None
    source_document_id: uuid.UUID | None = None
    source_document_title: str | None = None
    initial_level: str
    current_level: str
    question_count: int
    correct_count: int
    incorrect_count: int
    status: str
    confidence: float
    started_at: datetime
    completed_at: datetime | None = None


class RecalibrationResultResponse(BaseModel):
    session_id: uuid.UUID
    competency_id: uuid.UUID
    competency_name: str
    previous_score: float
    assessment_score: float
    recalibrated_score: float
    delta: float
    confidence: float
    reason: str
    questions_answered: int
    correct_count: int
    incorrect_count: int
    difficulty_distribution: dict[str, int] = Field(default_factory=dict)
    updated_gap_score: float | None = None
    updated_priority_level: str | None = None
    updated_priority_score: float | None = None
    completed_at: datetime
