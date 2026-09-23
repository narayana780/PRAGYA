import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class OverallPerformanceSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    baseline_score: float | None = Field(
        None, description="Average initial baseline competency score (typically diagnostic)"
    )
    current_score: float = Field(
        0.0, description="Average authoritative current competency score"
    )
    target_score: float | None = Field(
        None, description="Average role target requirement score across required competencies"
    )
    improvement_points: float = Field(
        0.0, description="Aggregate capability improvement in score points"
    )
    improvement_percentage: float = Field(
        0.0, description="Aggregate improvement percentage from baseline"
    )
    competencies_evaluated: int = Field(
        0, description="Total distinct competencies with demonstrated evidence or score"
    )
    competencies_with_baseline: int = Field(
        0, description="Number of evaluated competencies with an initial baseline record"
    )
    target_readiness_percentage: float | None = Field(
        None, description="Percentage of required role competency threshold achieved"
    )


class CompetencyPerformanceDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    competency_id: uuid.UUID
    competency_code: str
    competency_name: str
    domain_id: uuid.UUID | None = None
    domain_name: str | None = None
    baseline_score: float | None = None
    current_score: float = 0.0
    target_score: float | None = None
    improvement_points: float = 0.0
    improvement_percentage: float = 0.0
    status: str = Field(
        "NO_BASELINE",
        description="Performance status: MASTERED, IMPROVING, STABLE, NEEDS_FOCUS, NO_BASELINE",
    )
    confidence: float = 0.0
    confidence_label: str = "LOW"
    last_assessed_at: datetime | None = None
    evidence_count: int = 0


class CompetencyStrengthItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    competency_id: uuid.UUID
    competency_code: str
    competency_name: str
    domain_name: str | None = None
    current_score: float
    improvement_points: float
    rank: int
    highlight: str


class CompetencyFocusItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    competency_id: uuid.UUID
    competency_code: str
    competency_name: str
    domain_name: str | None = None
    current_score: float
    target_score: float | None = None
    gap_score: float
    priority_level: str = "LOW"
    priority_score: float = 0.0
    explanation: str


class DiagnosticModalitySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attempts_count: int = 0
    completed_count: int = 0
    average_score: float | None = None
    latest_score: float | None = None
    status: str = "NO_DATA"  # COMPLETED, IN_PROGRESS, NO_DATA


class QuizModalitySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attempts_count: int = 0
    completed_count: int = 0
    average_percentage: float | None = None
    best_percentage: float | None = None
    pass_rate: float | None = None
    status: str = "NO_DATA"  # COMPLETED, IN_PROGRESS, NO_DATA


class AdaptiveModalitySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sessions_count: int = 0
    completed_count: int = 0
    average_confidence: float | None = None
    competencies_evaluated_count: int = 0
    status: str = "NO_DATA"  # COMPLETED, IN_PROGRESS, NO_DATA


class LabModalitySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sessions_count: int = 0
    completed_count: int = 0
    average_score: float | None = None
    pass_rate: float | None = None
    completed_scenarios_count: int = 0
    status: str = "NO_DATA"  # COMPLETED, IN_PROGRESS, NO_DATA


class CourseModalitySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    enrolled_courses_count: int = 0
    completed_courses_count: int = 0
    average_progress_percentage: float | None = None
    completed_modules_count: int = 0
    status: str = "NO_DATA"  # COMPLETED, IN_PROGRESS, NO_DATA


class ModalitiesSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    diagnostic: DiagnosticModalitySummary
    quizzes: QuizModalitySummary
    adaptive_assessment: AdaptiveModalitySummary
    virtual_labs: LabModalitySummary
    courses: CourseModalitySummary


class PerformanceCountsSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    competencies_improved: int = 0
    competencies_declined: int = 0
    competencies_mastered: int = 0
    competencies_needing_focus: int = 0
    total_competencies: int = 0


class EmployeePerformanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: uuid.UUID
    employee_name: str
    job_role_id: uuid.UUID | None = None
    job_role_name: str | None = None
    department_name: str | None = None
    overall: OverallPerformanceSummary
    competencies: list[CompetencyPerformanceDetail]
    strongest_competencies: list[CompetencyStrengthItem]
    focus_competencies: list[CompetencyFocusItem]
    modalities: ModalitiesSummary
    summary: PerformanceCountsSummary
    generated_at: datetime


class TimelineEventItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    timestamp: datetime
    type: str  # DIAGNOSTIC_ASSESSMENT, QUIZ, ADAPTIVE_ASSESSMENT, VIRTUAL_LAB, COURSE_ACTIVITY, COMPETENCY_RECALIBRATION, SCORE_UPDATE
    title: str
    description: str
    score: float | None = None
    max_score: float | None = None
    percentage: float | None = None
    competency_id: uuid.UUID | None = None
    competency_name: str | None = None
    source: str
    status: str | None = None
    metadata: dict[str, Any] | None = None


class EmployeeTimelineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: uuid.UUID
    total_events: int
    events: list[TimelineEventItem]
