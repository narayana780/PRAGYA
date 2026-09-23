import uuid
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class WorkforceOverviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_employees: int = Field(description="Total registered personnel in the system")
    active_employees: int = Field(description="Active personnel currently deployed")
    departments_count: int = Field(description="Number of official organizational departments")
    roles_count: int = Field(description="Number of designated statistical and administrative roles")
    competencies_tracked: int = Field(description="Total competencies defined in framework")
    employees_assessed: int = Field(description="Employees with at least one recorded assessment or evidence")
    employees_with_competencies: int = Field(description="Employees with evaluated competency scores")
    average_competency_score: float | None = Field(
        default=None,
        description="Global workforce average competency score (0-100), or None if no data",
    )
    average_role_readiness: float | None = Field(
        default=None,
        description="Global average readiness against designated cadre requirements (0-100), or None if no data",
    )
    employees_needing_attention: int = Field(
        description="Personnel with CRITICAL/HIGH skill gaps or role readiness below 70%"
    )


class WorkforceCompetencyItem(BaseModel):
    competency_id: uuid.UUID
    code: str
    name: str
    domain: str
    employee_count: int
    average_score: float
    minimum_score: float
    maximum_score: float
    proficiency_distribution: dict[str, int]
    gap_count: int
    critical_gap_count: int


class WorkforceCompetenciesResponse(BaseModel):
    competencies: list[WorkforceCompetencyItem]
    total_tracked: int


class DepartmentAnalyticsItem(BaseModel):
    department_id: uuid.UUID
    department_name: str
    department_code: str
    employee_count: int
    average_competency_score: float | None
    average_role_readiness: float | None
    average_skill_gap_score: float | None
    critical_gap_count: int
    high_gap_count: int
    top_competency_strengths: list[str]
    top_competency_gaps: list[str]


class DepartmentAnalyticsResponse(BaseModel):
    departments: list[DepartmentAnalyticsItem]


class DepartmentHeatmapCompetencyItem(BaseModel):
    competency_id: uuid.UUID
    competency_name: str
    competency_code: str
    domain_name: str
    average_score: float | None
    gap_level: str  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'NO_GAP', 'NO_DATA'
    employee_count: int


class DepartmentHeatmapDepartmentItem(BaseModel):
    department_id: uuid.UUID
    department_name: str
    department_code: str
    employee_count: int
    competencies: list[DepartmentHeatmapCompetencyItem]


class DepartmentHeatmapResponse(BaseModel):
    departments: list[DepartmentHeatmapDepartmentItem]
    competencies_reference: list[dict[str, Any]]


class WorkforceGapSummaryItem(BaseModel):
    competency_id: uuid.UUID
    competency_name: str
    competency_code: str
    domain_name: str
    affected_employees: int
    average_gap_score: float
    highest_priority_level: str


class WorkforceGapsResponse(BaseModel):
    total_gaps: int
    critical_gaps: int
    high_gaps: int
    medium_gaps: int
    low_gaps: int
    no_gap_count: int
    top_workforce_gaps: list[WorkforceGapSummaryItem]


class RoleAnalyticsItem(BaseModel):
    role_id: uuid.UUID
    role_name: str
    role_code: str
    career_level: str
    employee_count: int
    average_competency_score: float | None
    average_role_readiness: float | None
    competency_requirements_count: int
    major_skill_gaps: list[str]
    employees_below_target: int


class RoleAnalyticsResponse(BaseModel):
    roles: list[RoleAnalyticsItem]


class TopCourseLearningItem(BaseModel):
    course_id: uuid.UUID
    course_code: str
    title: str
    provider: str
    enrolled_count: int
    completed_count: int
    completion_rate: float
    average_progress: float


class WorkforceTrainingOverviewResponse(BaseModel):
    total_learners: int
    total_enrollments: int
    completed_courses_count: int
    average_learning_progress: float
    total_learning_activities: int
    top_courses: list[TopCourseLearningItem]
    employees_with_competency_growth: int


class AdminEmployeeListItem(BaseModel):
    id: uuid.UUID
    employee_code: str
    full_name: str
    designation: str
    department_name: str
    role_name: str
    average_competency: float | None
    role_readiness: float | None
    critical_gaps_count: int
    needs_attention: bool


class AdminEmployeeListResponse(BaseModel):
    employees: list[AdminEmployeeListItem]
    total: int
