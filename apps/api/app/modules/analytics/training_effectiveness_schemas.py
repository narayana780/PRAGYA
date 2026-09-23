import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CompetencyImprovementSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    competency_id: uuid.UUID
    competency_code: str
    competency_name: str
    domain_name: str
    measurable_learners: int = 0
    average_pre_score: float | None = None
    average_post_score: float | None = None
    average_improvement: float | None = None
    improvement_percentage: float | None = None


class CourseEffectivenessItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    course_id: uuid.UUID
    course_code: str
    title: str
    provider: str
    duration_hours: float | None = None
    enrolled_count: int = 0
    completed_count: int = 0
    completion_rate: float = 0.0
    measurable_learners: int = 0
    average_pre_score: float | None = None
    average_post_score: float | None = None
    average_improvement: float | None = None
    improvement_percentage: float | None = None
    effectiveness_index: float | None = None
    effectiveness_status: str = "INSUFFICIENT_DATA"
    competencies_affected: list[str] = Field(default_factory=list)


class CourseEffectivenessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    courses: list[CourseEffectivenessItem]
    total_courses: int


class RecommendationOutcomesSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recommendations_issued: int = 0
    recommendations_started: int = 0
    recommendations_completed: int = 0
    measurable_recommendations: int = 0
    recommendations_with_improvement: int = 0
    start_rate: float = 0.0
    completion_rate: float = 0.0
    improvement_rate: float = 0.0
    average_observed_improvement: float | None = None
    by_priority: dict[str, int] = Field(default_factory=dict)


class RecommendationEffectivenessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    summary: RecommendationOutcomesSummary


class OverallTrainingEffectivenessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_learners: int = 0
    total_enrollments: int = 0
    completed_enrollments: int = 0
    completion_rate: float = 0.0
    measurable_interventions: int = 0
    effective_interventions: int = 0
    average_observed_improvement: float | None = None
    average_improvement_percentage: float | None = None
    competencies_improved_count: int = 0
    competency_improvements: list[CompetencyImprovementSummary] = Field(default_factory=list)
    top_effective_courses: list[CourseEffectivenessItem] = Field(default_factory=list)
    recommendation_summary: RecommendationOutcomesSummary


class EmployeeCourseEffectivenessItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    course_id: uuid.UUID
    course_title: str
    status: str
    enrolled_at: datetime
    completed_at: datetime | None = None
    competency_name: str
    pre_training_score: float | None = None
    post_training_score: float | None = None
    improvement_points: float | None = None
    improvement_percentage: float | None = None
    status_label: str  # "OBSERVED_IMPROVEMENT", "NO_CHANGE", "DECLINE", "NO_BASELINE", "NO_POST_DATA"


class EmployeeTrainingEffectivenessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: uuid.UUID
    employee_code: str
    full_name: str
    designation: str
    interventions: list[EmployeeCourseEffectivenessItem] = Field(default_factory=list)
    total_interventions: int = 0
    average_observed_improvement: float | None = None
