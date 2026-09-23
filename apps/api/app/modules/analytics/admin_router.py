import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin_role
from app.modules.analytics.admin_schemas import (
    AdminEmployeeListResponse,
    DepartmentAnalyticsResponse,
    DepartmentHeatmapResponse,
    RoleAnalyticsResponse,
    WorkforceCompetenciesResponse,
    WorkforceGapsResponse,
    WorkforceOverviewResponse,
    WorkforceTrainingOverviewResponse,
)
from app.modules.analytics.admin_service import WorkforceAnalysisService
from app.modules.analytics.emerging_skills_schemas import (
    EmergingSkillsResponse,
)
from app.modules.analytics.emerging_skills_service import (
    EmergingSkillsService,
)
from app.modules.analytics.training_effectiveness_schemas import (
    CourseEffectivenessResponse,
    EmployeeTrainingEffectivenessResponse,
    OverallTrainingEffectivenessResponse,
    RecommendationEffectivenessResponse,
)
from app.modules.analytics.training_effectiveness_service import (
    TrainingEffectivenessService,
)
from app.modules.analytics.workforce_planning_schemas import (
    CompetencyCapacityForecastResponse,
    DepartmentCapacityForecastResponse,
    EmployeePlanningDrilldownResponse,
    PlanningRecommendationsResponse,
    RoleCapacityForecastResponse,
    WorkforceCapacityForecastResponse,
    WorkforcePlanningOverviewResponse,
    WorkforceTrendsResponse,
)
from app.modules.analytics.workforce_planning_service import (
    WorkforcePlanningService,
)

router = APIRouter(
    prefix="/admin",
    tags=["Administrator Workforce Intelligence"],
    dependencies=[Depends(require_admin_role)],
)

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get(
    "/workforce/overview",
    response_model=WorkforceOverviewResponse,
    summary="Get Global Workforce Analytics Overview",
    description="Returns aggregate workforce headcounts, assessed counts, average competency score, and role readiness.",
)
async def get_workforce_overview(
    db: DbSession,
) -> WorkforceOverviewResponse:
    service = WorkforceAnalysisService(db)
    return await service.get_workforce_overview()


@router.get(
    "/workforce/competencies",
    response_model=WorkforceCompetenciesResponse,
    summary="Get Workforce Competency Distribution",
    description="Returns competency distribution across the workforce with proficiency tiers and gap statistics.",
)
async def get_workforce_competencies(
    db: DbSession,
) -> WorkforceCompetenciesResponse:
    service = WorkforceAnalysisService(db)
    return await service.get_workforce_competencies()


@router.get(
    "/workforce/gaps",
    response_model=WorkforceGapsResponse,
    summary="Get Workforce Skill Gaps Aggregation",
    description="Returns workforce skill gap totals and top deficient competencies prioritized deterministically.",
)
async def get_workforce_gaps(
    db: DbSession,
) -> WorkforceGapsResponse:
    service = WorkforceAnalysisService(db)
    return await service.get_workforce_gaps()


@router.get(
    "/workforce/employees",
    response_model=AdminEmployeeListResponse,
    summary="Get Workforce Personnel for Administrator Drill-Down",
    description="Returns active employee roster with competency averages and role readiness for executive drill-down.",
)
async def get_admin_employee_list(
    db: DbSession,
) -> AdminEmployeeListResponse:
    service = WorkforceAnalysisService(db)
    return await service.get_admin_employee_list()


@router.get(
    "/departments/analytics",
    response_model=DepartmentAnalyticsResponse,
    summary="Get Department Capability Analytics",
    description="Compares workforce capability, average competency scores, and skill gap levels across departments.",
)
async def get_department_analytics(
    db: DbSession,
) -> DepartmentAnalyticsResponse:
    service = WorkforceAnalysisService(db)
    return await service.get_department_analytics()


@router.get(
    "/departments/heatmap",
    response_model=DepartmentHeatmapResponse,
    summary="Get Department x Competency Heatmap Matrix",
    description="Returns Department x Competency matrix with average scores and gap levels for heatmap rendering.",
)
async def get_department_heatmap(
    db: DbSession,
) -> DepartmentHeatmapResponse:
    service = WorkforceAnalysisService(db)
    return await service.get_department_heatmap()


@router.get(
    "/roles/analytics",
    response_model=RoleAnalyticsResponse,
    summary="Get Role & Cadre Readiness Analytics",
    description="Evaluates role and cadre readiness, competency requirement coverage, and personnel below target.",
)
async def get_role_analytics(
    db: DbSession,
) -> RoleAnalyticsResponse:
    service = WorkforceAnalysisService(db)
    return await service.get_role_analytics()


@router.get(
    "/training/analytics",
    response_model=WorkforceTrainingOverviewResponse,
    summary="Get Workforce Learning Participation Overview",
    description="Returns aggregate workforce course participation, completion rates, and learning activity counts.",
)
async def get_training_analytics(
    db: DbSession,
) -> WorkforceTrainingOverviewResponse:
    service = WorkforceAnalysisService(db)
    return await service.get_training_overview()


# =============================================================================
# STAGE 15: TRAINING EFFECTIVENESS & RECOMMENDATION ANALYTICS
# =============================================================================


@router.get(
    "/training/effectiveness",
    response_model=OverallTrainingEffectivenessResponse,
    summary="Get Overall Training Effectiveness & Outcomes",
    description="Analyzes empirical competency score changes associated with training completions, measurable interventions, and recommendation outcomes.",
)
async def get_overall_training_effectiveness(
    db: DbSession,
) -> OverallTrainingEffectivenessResponse:
    service = TrainingEffectivenessService(db)
    return await service.get_overall_effectiveness()


@router.get(
    "/training/courses/effectiveness",
    response_model=CourseEffectivenessResponse,
    summary="Get Course & Learning Intervention Effectiveness",
    description="Calculates course-by-course enrollment, completion, pre-training baseline, post-training score, observed improvement points, and duration-based effectiveness index.",
)
async def get_course_effectiveness(
    db: DbSession,
) -> CourseEffectivenessResponse:
    service = TrainingEffectivenessService(db)
    return await service.get_course_effectiveness()


@router.get(
    "/recommendations/effectiveness",
    response_model=RecommendationEffectivenessResponse,
    summary="Get Learning Recommendation Lifecycle Outcomes",
    description="Evaluates recommendation lifecycle from generation to learning start, completion, subsequent evidence, and observed competency improvement.",
)
async def get_recommendation_effectiveness(
    db: DbSession,
) -> RecommendationEffectivenessResponse:
    service = TrainingEffectivenessService(db)
    return await service.get_recommendation_effectiveness()


@router.get(
    "/training/employees/{employee_id}/effectiveness",
    response_model=EmployeeTrainingEffectivenessResponse,
    summary="Get Administrator Drill-Down for Employee Training Outcomes",
    description="Returns individual learning intervention outcomes, baseline vs post scores, and observed improvement for a specific employee.",
)
async def get_employee_training_effectiveness(
    employee_id: uuid.UUID,
    db: DbSession,
) -> EmployeeTrainingEffectivenessResponse:
    service = TrainingEffectivenessService(db)
    try:
        return await service.get_employee_training_effectiveness(employee_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# =============================================================================
# STAGE 16: EMERGING SKILLS & TECHNOLOGY HORIZON SCANNING
# =============================================================================


@router.get(
    "/emerging-skills",
    response_model=EmergingSkillsResponse,
    summary="Get Emerging Statistical Skills & Technology Horizon Signals",
    description="Returns deterministic internal demand signals (gap frequency, recommendation velocity, training demand, and role coverage) identifying emerging competencies for India's Official Statistical System.",
)
async def get_emerging_skills(
    db: DbSession,
    domain_id: uuid.UUID | None = None,
) -> EmergingSkillsResponse:
    service = EmergingSkillsService(db)
    return await service.get_emerging_skills_signals(domain_id=domain_id)


# =============================================================================
# STAGE 17: PREDICTIVE WORKFORCE PLANNING & CAPACITY FORECASTING
# =============================================================================


@router.get(
    "/workforce/planning/overview",
    response_model=WorkforcePlanningOverviewResponse,
    summary="Get Workforce Planning & Capacity Baseline Overview",
    description="Returns aggregate workforce headcounts, learning velocity, active skill gap population, and data-quality indicators.",
)
async def get_workforce_planning_overview(
    db: DbSession,
) -> WorkforcePlanningOverviewResponse:
    service = WorkforcePlanningService(db)
    return await service.get_workforce_planning_overview()


@router.get(
    "/workforce/planning/trends",
    response_model=WorkforceTrendsResponse,
    summary="Get Historical Workforce Competency Trends",
    description="Aggregates longitudinal competency score history into periodic trends with data-quality sufficiency validation.",
)
async def get_workforce_planning_trends(
    db: DbSession,
) -> WorkforceTrendsResponse:
    service = WorkforcePlanningService(db)
    return await service.get_workforce_planning_trends()


@router.get(
    "/workforce/planning/forecast",
    response_model=WorkforceCapacityForecastResponse,
    summary="Get Deterministic Workforce Capacity Forecast",
    description="Computes explainable capacity projections synthesizing gap pressure, learning velocity, emerging skills, and role deficits.",
)
async def get_workforce_capacity_forecast(
    db: DbSession,
) -> WorkforceCapacityForecastResponse:
    service = WorkforcePlanningService(db)
    return await service.get_capacity_forecast()


@router.get(
    "/workforce/planning/competencies",
    response_model=CompetencyCapacityForecastResponse,
    summary="Get Competency Capacity Forecast & Pressure Ranking",
    description="Evaluates workforce coverage, learning demand, emerging signals, and capacity pressure per competency.",
)
async def get_competency_capacity_forecast(
    db: DbSession,
) -> CompetencyCapacityForecastResponse:
    service = WorkforcePlanningService(db)
    return await service.get_competency_capacity_forecast()


@router.get(
    "/workforce/planning/roles",
    response_model=RoleCapacityForecastResponse,
    summary="Get Role/Cadre Capacity Forecast",
    description="Evaluates cadre readiness, requirement deficits, and capacity pressure per job role.",
)
async def get_role_capacity_forecast(
    db: DbSession,
) -> RoleCapacityForecastResponse:
    service = WorkforcePlanningService(db)
    return await service.get_role_capacity_forecast()


@router.get(
    "/workforce/planning/departments",
    response_model=DepartmentCapacityForecastResponse,
    summary="Get Department Capacity Forecast",
    description="Evaluates workforce coverage, skill gaps, and capacity pressure per ministry department.",
)
async def get_department_capacity_forecast(
    db: DbSession,
) -> DepartmentCapacityForecastResponse:
    service = WorkforcePlanningService(db)
    return await service.get_department_capacity_forecast()


@router.get(
    "/workforce/planning/recommendations",
    response_model=PlanningRecommendationsResponse,
    summary="Get Deterministic Workforce Planning Recommendations",
    description="Generates actionable workforce interventions based on empirical gap, training, and horizon scanning signals.",
)
async def get_planning_recommendations(
    db: DbSession,
) -> PlanningRecommendationsResponse:
    service = WorkforcePlanningService(db)
    return await service.get_planning_recommendations()


@router.get(
    "/workforce/planning/employees/{employee_id}",
    response_model=EmployeePlanningDrilldownResponse,
    summary="Get Individual Employee Planning Drilldown",
    description="Returns detailed competency trajectory, readiness indicators, and planning signals for an individual officer.",
)
async def get_employee_planning_drilldown(
    employee_id: uuid.UUID,
    db: DbSession,
) -> EmployeePlanningDrilldownResponse:
    service = WorkforcePlanningService(db)
    result = await service.get_employee_planning_drilldown(employee_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee {employee_id} not found",
        )
    return result


