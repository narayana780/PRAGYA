import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# Dataset Schemas
# -----------------------------------------------------------------------------

class LabDatasetSummary(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    scenario_type: str
    row_count: int
    is_synthetic: bool = True
    schema_definition: dict[str, Any]

    model_config = {"from_attributes": True}


class LabDatasetDetail(LabDatasetSummary):
    dataset_json: list[dict[str, Any]]

    model_config = {"from_attributes": True}


# -----------------------------------------------------------------------------
# Scenario Schemas
# -----------------------------------------------------------------------------

class LabScenarioStepInfo(BaseModel):
    step_number: int
    title: str
    description: str
    task_instructions: str
    action_type: str
    expected_controls: list[str] = Field(default_factory=list)


class LabScenarioSummary(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    scenario_type: str
    competency_id: uuid.UUID
    competency_name: str | None = None
    competency_code: str | None = None
    difficulty: str
    estimated_minutes: int
    learning_objectives: list[str]
    status: str
    dataset_id: uuid.UUID
    dataset_row_count: int = 0
    is_synthetic: bool = True
    created_at: datetime

    model_config = {"from_attributes": True}


class LabScenarioDetail(LabScenarioSummary):
    instructions: dict[str, Any]
    dataset: LabDatasetDetail

    model_config = {"from_attributes": True}


# -----------------------------------------------------------------------------
# Session & Action Schemas
# -----------------------------------------------------------------------------

class LabSessionCreateRequest(BaseModel):
    notes: str | None = None


class LabActionResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    step_number: int
    action_type: str
    action_payload: dict[str, Any]
    is_correct: bool
    score_awarded: float
    feedback: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LabSessionResponse(BaseModel):
    id: uuid.UUID
    employee_id: uuid.UUID
    scenario_id: uuid.UUID
    scenario_title: str
    scenario_type: str
    difficulty: str
    competency_id: uuid.UUID
    competency_name: str | None = None
    status: str
    current_step: int
    total_steps: int
    score: float | None = None
    percentage: float | None = None
    confidence: float | None = None
    started_at: datetime
    completed_at: datetime | None = None
    actions: list[LabActionResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class LabActionSubmitRequest(BaseModel):
    step_number: int = Field(..., ge=1, le=10)
    action_type: str = Field(..., min_length=2, max_length=100)
    action_payload: dict[str, Any] = Field(default_factory=dict)


class LabActionEvaluationResult(BaseModel):
    action_id: uuid.UUID
    session_id: uuid.UUID
    step_number: int
    action_type: str
    is_correct: bool
    score_awarded: float
    feedback: str
    current_score: float
    next_step: int
    is_completed: bool
    data_preview: list[dict[str, Any]] | None = None
    metrics: dict[str, Any] | None = None


class LabCompleteResponse(BaseModel):
    session_id: uuid.UUID
    scenario_id: uuid.UUID
    scenario_title: str | None = None
    scenario_type: str | None = None
    difficulty: str | None = None
    total_score: float
    percentage: float
    passed: bool
    confidence: float
    competency_id: uuid.UUID | None = None
    competency_name: str | None = None
    evidence_id: uuid.UUID | None = None
    actions_completed: int = 0
    correct_actions: int = 0
    incorrect_actions: int = 0
    actions_history: list[LabActionResponse] = Field(default_factory=list)
    learning_feedback: list[str] = Field(default_factory=list)
    summary_metrics: dict[str, Any] = Field(default_factory=dict)
    completed_at: datetime
    message: str


class LabResultDetail(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    scenario_id: uuid.UUID
    scenario_title: str
    scenario_type: str
    difficulty: str
    total_score: float
    percentage: float
    passed: bool
    confidence: float
    competency_id: uuid.UUID | None
    competency_name: str | None
    evidence_id: uuid.UUID | None
    actions_completed: int
    correct_actions: int
    incorrect_actions: int
    actions_history: list[LabActionResponse] = Field(default_factory=list)
    learning_feedback: list[str] = Field(default_factory=list)
    summary_metrics: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class LabHintRequest(BaseModel):
    step_number: int = Field(..., ge=1, le=10)


class LabHintResponse(BaseModel):
    step_number: int
    hint: str
    guidance: str
