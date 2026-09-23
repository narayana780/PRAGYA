import uuid
from typing import Any, List, Optional
from pydantic import BaseModel, Field


class PlanningDataQuality(BaseModel):
    historical_periods: int = Field(default=0, description="Number of historical time periods analyzed")
    records_used: int = Field(default=0, description="Total evidence and history records evaluated")
    status: str = Field(default="SUFFICIENT", description="Data sufficiency status: SUFFICIENT or INSUFFICIENT_DATA")
    quality_grade: str = Field(default="HIGH", description="Quality confidence grade: HIGH, MEDIUM, or LOW")


class WorkforcePopulationMetrics(BaseModel):
    total_employees: int = 0
    active_employees: int = 0
    departments_count: int = 0
    roles_count: int = 0
    competencies_tracked: int = 0


class WorkforceCapacityMetrics(BaseModel):
    employees_with_gaps: int = 0
    employees_learning: int = 0
    employees_with_improvement: int = 0
    average_role_readiness: float = 0.0
    overall_planning_pressure: float = 0.0


class WorkforcePlanningOverviewResponse(BaseModel):
    status: str = "OK"
    population: WorkforcePopulationMetrics
    capacity: WorkforceCapacityMetrics
    data_quality: PlanningDataQuality


class WorkforceTrendPeriod(BaseModel):
    period: str = Field(description="Time period identifier, e.g. YYYY-MM")
    period_start: str
    period_end: str
    average_competency_score: float
    employees_meeting_target: int
    employees_below_target: int
    active_skill_gaps: int
    learning_participation: int
    observed_improvement: float


class WorkforceTrendsResponse(BaseModel):
    status: str = Field(default="OK", description="OK or INSUFFICIENT_DATA")
    message: Optional[str] = None
    periods_count: int = 0
    trends: List[WorkforceTrendPeriod] = Field(default_factory=list)
    data_quality: PlanningDataQuality


class ForecastMethodology(BaseModel):
    type: str = "deterministic_workforce_projection"
    historical_window: str = "all_authoritative_history"
    signals: List[str] = Field(
        default_factory=lambda: [
            "historical_skill_gap_frequency",
            "training_demand",
            "emerging_skill_signal",
            "role_requirement_pressure",
            "observed_competency_improvement",
        ]
    )
    assumptions: List[str] = Field(
        default_factory=lambda: [
            "Deterministic multi-factor capacity scoring without unverified external market forecasting",
            "Observed improvement indicates learning velocity rather than guaranteed causation",
            "Role requirements establish baseline expected proficiency targets",
        ]
    )
    data_quality: str = "HIGH"
    limitations: List[str] = Field(
        default_factory=lambda: [
            "Planning estimates do not replace statutory cadre review boards",
            "Based strictly on internal PRAGYA assessment and course activity data",
        ]
    )


class WorkforceCapacityForecastResponse(BaseModel):
    current_capacity: int = Field(description="Currently qualified/ready workforce count")
    total_workforce: int = Field(description="Total active workforce headcount")
    current_capacity_percentage: float = Field(description="Current qualified percentage of workforce")
    estimated_capacity_requirement: int = Field(description="Estimated ready officers required across all roles")
    capacity_gap: int = Field(description="Current shortfall in ready personnel")
    projected_gap: int = Field(description="Projected deficit factoring in gaps, demand, emerging skills, and training velocity")
    overall_pressure_index: float = Field(description="Aggregate capacity pressure score 0-100")
    priority_competencies: List[str] = Field(default_factory=list)
    priority_roles: List[str] = Field(default_factory=list)
    priority_departments: List[str] = Field(default_factory=list)
    methodology: ForecastMethodology = Field(default_factory=ForecastMethodology)


class CompetencyCapacityForecastItem(BaseModel):
    competency_id: uuid.UUID
    name: str
    domain: str
    current_coverage: float = Field(description="Percentage of assessed workforce meeting minimum target")
    target_coverage: float = Field(default=80.0, description="Designated target coverage percentage")
    gap_population: int = Field(description="Number of officers with active deficit in this competency")
    learning_demand: int = Field(description="Number of learners enrolled in courses covering this competency")
    emerging_signal: float = Field(description="Stage 16 emerging skill score (0-100)")
    planning_pressure: float = Field(description="Deterministic composite capacity pressure (0-100)")
    status: str = Field(description="HIGH_DEFICIT, MODERATE_DEFICIT, BALANCED, or INSUFFICIENT_DATA")
    rationale: List[str] = Field(default_factory=list)


class CompetencyCapacityForecastResponse(BaseModel):
    total_competencies: int
    competencies: List[CompetencyCapacityForecastItem] = Field(default_factory=list)
    data_quality: PlanningDataQuality


class RoleCapacityForecastItem(BaseModel):
    role_id: uuid.UUID
    role_name: str
    cadre_level: Optional[str] = None
    employee_count: int
    required_competencies_count: int
    employees_meeting_target: int
    employees_below_target: int
    critical_skill_gaps: int
    learning_demand: int
    readiness_signal: float = Field(description="Average readiness percentage (0-100)")
    projected_capacity_pressure: float = Field(description="Projected capacity pressure (0-100)")
    status: str = Field(description="HIGH_PRESSURE, MODERATE_PRESSURE, ADEQUATE")
    rationale: List[str] = Field(default_factory=list)


class RoleCapacityForecastResponse(BaseModel):
    total_roles: int
    roles: List[RoleCapacityForecastItem] = Field(default_factory=list)
    data_quality: PlanningDataQuality


class DepartmentCapacityForecastItem(BaseModel):
    department_id: uuid.UUID
    department_name: str
    code: Optional[str] = None
    workforce_size: int
    competency_coverage: float = Field(description="Average competency proficiency in department")
    major_skill_gaps: int = Field(description="Active skill gaps in department")
    learning_demand: int = Field(description="Active course enrollments in department")
    emerging_skill_pressure: float = Field(description="Emerging skill alignment score 0-100")
    projected_capacity_pressure: float = Field(description="Projected capacity pressure 0-100")
    status: str = Field(description="HIGH_PRESSURE, MODERATE_PRESSURE, BALANCED")
    rationale: List[str] = Field(default_factory=list)


class DepartmentCapacityForecastResponse(BaseModel):
    total_departments: int
    departments: List[DepartmentCapacityForecastItem] = Field(default_factory=list)
    data_quality: PlanningDataQuality


class PlanningRecommendationItem(BaseModel):
    id: str
    type: str = Field(description="COMPETENCY_TRAINING, ROLE_CAPACITY, DEPARTMENT_FOCUS, HORIZON_MONITORING, REASSESSMENT")
    title: str
    priority: str = Field(description="HIGH, MEDIUM, LOW")
    affected_population: int
    evidence_signals: List[str] = Field(default_factory=list)
    rationale: str
    suggested_action: str
    data_quality_status: str = "SUFFICIENT"


class PlanningRecommendationsResponse(BaseModel):
    total_recommendations: int
    recommendations: List[PlanningRecommendationItem] = Field(default_factory=list)
    data_quality: PlanningDataQuality


class EmployeePlanningTrajectoryPoint(BaseModel):
    timestamp: str
    competency_name: str
    score: float
    source: str


class EmployeePlanningDrilldownResponse(BaseModel):
    employee_id: uuid.UUID
    full_name: str
    employee_code: Optional[str] = None
    designation: Optional[str] = None
    department_name: Optional[str] = None
    role_name: Optional[str] = None
    current_average_score: float
    role_readiness_percentage: float
    active_gaps_count: int
    learning_modules_completed: int
    observed_improvement_points: float
    readiness_indicator: str = Field(description="READY, DEVELOPING, or AT_RISK")
    historical_trajectory: List[EmployeePlanningTrajectoryPoint] = Field(default_factory=list)
    planning_signals: List[str] = Field(default_factory=list)
