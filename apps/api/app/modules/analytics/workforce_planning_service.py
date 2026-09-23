import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import case, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.analytics.admin_service import WorkforceAnalysisService
from app.modules.analytics.emerging_skills_service import EmergingSkillsService
from app.modules.analytics.service import PerformanceAnalysisService
from app.modules.analytics.training_effectiveness_service import TrainingEffectivenessService
from app.modules.analytics.workforce_planning_schemas import (
    CompetencyCapacityForecastItem,
    CompetencyCapacityForecastResponse,
    DepartmentCapacityForecastItem,
    DepartmentCapacityForecastResponse,
    EmployeePlanningDrilldownResponse,
    EmployeePlanningTrajectoryPoint,
    ForecastMethodology,
    PlanningDataQuality,
    PlanningRecommendationItem,
    PlanningRecommendationsResponse,
    RoleCapacityForecastItem,
    RoleCapacityForecastResponse,
    WorkforceCapacityForecastResponse,
    WorkforceCapacityMetrics,
    WorkforcePlanningOverviewResponse,
    WorkforcePopulationMetrics,
    WorkforceTrendPeriod,
    WorkforceTrendsResponse,
)
from app.modules.assessments.models import (
    AssessmentAttempt,
    CompetencyEvidence,
    EmployeeCompetency,
)
from app.modules.competencies.models import (
    Competency,
    CompetencyRequirement,
)
from app.modules.courses.models import (
    CourseProgress,
    LearningItem,
    LearningItemCompetency,
)
from app.modules.adaptive.models import CompetencyRecalibration
from app.modules.departments.models import Department
from app.modules.employees.models import Employee
from app.modules.job_roles.models import JobRole
from app.modules.skill_gaps.models import SkillGap


class WorkforcePlanningService:
    """
    Deterministic workforce planning and capacity forecasting engine.
    Uses authoritative internal PRAGYA assessment, course progress, skill gap,
    and emerging skill signals. Never invents external labor-market numbers.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.workforce_service = WorkforceAnalysisService(db)
        self.emerging_service = EmergingSkillsService(db)
        self.training_service = TrainingEffectivenessService(db)
        self.perf_service = PerformanceAnalysisService(db)

    async def get_workforce_planning_overview(self) -> WorkforcePlanningOverviewResponse:
        """
        Aggregate workforce capacity metrics and data-quality baseline.
        """
        # 1. Population headcounts
        overview = await self.workforce_service.get_workforce_overview()
        
        # 2. Employees with active skill gaps
        res_gaps = await self.db.execute(
            select(func.count(distinct(SkillGap.employee_id))).where(SkillGap.gap_score > 0)
        )
        emp_with_gaps = res_gaps.scalar() or 0

        # 3. Employees currently learning
        res_learning = await self.db.execute(
            select(func.count(distinct(CourseProgress.employee_id))).where(
                CourseProgress.status.in_(["IN_PROGRESS", "STARTED", "ENROLLED"])
            )
        )
        emp_learning = res_learning.scalar() or 0

        # 4. Employees with observed improvement
        res_improving = await self.db.execute(
            select(func.count(distinct(CompetencyRecalibration.employee_id))).where(
                CompetencyRecalibration.new_score > CompetencyRecalibration.previous_score
            )
        )
        emp_improving = res_improving.scalar() or 0

        # 5. Total historical records for data-quality audit
        res_ev_cnt = await self.db.execute(select(func.count(CompetencyEvidence.id)))
        ev_count = res_ev_cnt.scalar() or 0

        res_hist_cnt = await self.db.execute(select(func.count(CompetencyRecalibration.id)))
        hist_count = res_hist_cnt.scalar() or 0
        total_records = ev_count + hist_count

        # Overall planning pressure index (0-100)
        tot_emp = max(1, overview.total_employees)
        gap_ratio = min(1.0, emp_with_gaps / tot_emp)
        readiness_deficit = max(0.0, (100.0 - overview.average_role_readiness) / 100.0)
        overall_pressure = round(min(100.0, (gap_ratio * 0.5 + readiness_deficit * 0.5) * 100.0), 1)

        quality_grade = "HIGH" if total_records >= 10 else ("MEDIUM" if total_records >= 3 else "LOW")
        dq_status = "SUFFICIENT" if total_records > 0 else "INSUFFICIENT_DATA"

        return WorkforcePlanningOverviewResponse(
            status="OK",
            population=WorkforcePopulationMetrics(
                total_employees=overview.total_employees,
                active_employees=overview.active_employees,
                departments_count=overview.departments_count,
                roles_count=overview.roles_count,
                competencies_tracked=overview.competencies_tracked,
            ),
            capacity=WorkforceCapacityMetrics(
                employees_with_gaps=emp_with_gaps,
                employees_learning=emp_learning,
                employees_with_improvement=emp_improving,
                average_role_readiness=overview.average_role_readiness,
                overall_planning_pressure=overall_pressure,
            ),
            data_quality=PlanningDataQuality(
                historical_periods=max(1, 1 if total_records > 0 else 0),
                records_used=total_records,
                status=dq_status,
                quality_grade=quality_grade,
            ),
        )

    async def get_workforce_planning_trends(self) -> WorkforceTrendsResponse:
        """
        Historical workforce competency trends aggregated periodically.
        Returns INSUFFICIENT_DATA when records do not support temporal analysis.
        """
        # Query recalibration history grouped by calendar month
        stmt = (
            select(
                func.to_char(CompetencyRecalibration.created_at, 'YYYY-MM').label("period"),
                func.min(CompetencyRecalibration.created_at).label("period_start"),
                func.max(CompetencyRecalibration.created_at).label("period_end"),
                func.avg(CompetencyRecalibration.new_score).label("avg_score"),
                func.count(distinct(CompetencyRecalibration.employee_id)).label("emp_count"),
                func.count(case((CompetencyRecalibration.new_score >= 70.0, 1))).label("meeting_target"),
                func.count(case((CompetencyRecalibration.new_score < 70.0, 1))).label("below_target"),
                func.avg(case((CompetencyRecalibration.new_score > CompetencyRecalibration.previous_score, 
                              CompetencyRecalibration.new_score - CompetencyRecalibration.previous_score))).label("avg_improvement"),
            )
            .group_by("period")
            .order_by("period")
        )
        res = await self.db.execute(stmt)
        rows = res.all()

        if not rows:
            # Fallback check on CompetencyEvidence
            ev_stmt = (
                select(
                    func.to_char(CompetencyEvidence.recorded_at, 'YYYY-MM').label("period"),
                    func.min(CompetencyEvidence.recorded_at).label("period_start"),
                    func.max(CompetencyEvidence.recorded_at).label("period_end"),
                    func.avg(CompetencyEvidence.normalized_score).label("avg_score"),
                    func.count(distinct(CompetencyEvidence.employee_id)).label("emp_count"),
                    func.count(case((CompetencyEvidence.normalized_score >= 70.0, 1))).label("meeting_target"),
                    func.count(case((CompetencyEvidence.normalized_score < 70.0, 1))).label("below_target"),
                )
                .group_by("period")
                .order_by("period")
            )
            ev_res = await self.db.execute(ev_stmt)
            ev_rows = ev_res.all()

            if not ev_rows:
                return WorkforceTrendsResponse(
                    status="INSUFFICIENT_DATA",
                    message="Insufficient historical competency snapshots recorded to form longitudinal trends.",
                    periods_count=0,
                    trends=[],
                    data_quality=PlanningDataQuality(
                        historical_periods=0,
                        records_used=0,
                        status="INSUFFICIENT_DATA",
                        quality_grade="LOW",
                    ),
                )

            periods = []
            for r in ev_rows:
                periods.append(
                    WorkforceTrendPeriod(
                        period=r.period or "Historical",
                        period_start=r.period_start.isoformat() if r.period_start else "N/A",
                        period_end=r.period_end.isoformat() if r.period_end else "N/A",
                        average_competency_score=round(float(r.avg_score or 0.0), 1),
                        employees_meeting_target=int(r.meeting_target or 0),
                        employees_below_target=int(r.below_target or 0),
                        active_skill_gaps=0,
                        learning_participation=int(r.emp_count or 0),
                        observed_improvement=0.0,
                    )
                )

            return WorkforceTrendsResponse(
                status="OK",
                periods_count=len(periods),
                trends=periods,
                data_quality=PlanningDataQuality(
                    historical_periods=len(periods),
                    records_used=sum(p.learning_participation for p in periods),
                    status="SUFFICIENT",
                    quality_grade="MEDIUM",
                ),
            )

        periods = []
        for r in rows:
            periods.append(
                WorkforceTrendPeriod(
                    period=r.period or "Snapshot",
                    period_start=r.period_start.isoformat() if r.period_start else "N/A",
                    period_end=r.period_end.isoformat() if r.period_end else "N/A",
                    average_competency_score=round(float(r.avg_score or 0.0), 1),
                    employees_meeting_target=int(r.meeting_target or 0),
                    employees_below_target=int(r.below_target or 0),
                    active_skill_gaps=int(r.below_target or 0),
                    learning_participation=int(r.emp_count or 0),
                    observed_improvement=round(float(r.avg_improvement or 0.0), 1),
                )
            )

        return WorkforceTrendsResponse(
            status="OK",
            periods_count=len(periods),
            trends=periods,
            data_quality=PlanningDataQuality(
                historical_periods=len(periods),
                records_used=sum(p.learning_participation for p in periods),
                status="SUFFICIENT",
                quality_grade="HIGH" if len(periods) >= 3 else "MEDIUM",
            ),
        )

    async def get_capacity_forecast(self) -> WorkforceCapacityForecastResponse:
        """
        Explainable deterministic capacity forecast.
        Synthesizes gap pressure, emerging skill signals, and observed training velocity.
        """
        overview = await self.workforce_service.get_workforce_overview()
        total_emp = max(1, overview.total_employees)

        # Current qualified capacity = employees with role readiness >= 70%
        emp_stmt = select(Employee.id).where(Employee.is_active.is_(True))
        emp_res = await self.db.execute(emp_stmt)
        active_ids = [row[0] for row in emp_res.all()]

        ready_count = 0
        for eid in active_ids:
            # Check employee readiness
            try:
                perf = await self.perf_service.get_employee_performance(eid)
                if perf and perf.overall.target_readiness_percentage is not None and perf.overall.target_readiness_percentage >= 70.0:
                    ready_count += 1
                elif perf and perf.overall.current_score >= 70.0:
                    ready_count += 1
            except Exception:
                pass

        current_capacity = ready_count
        current_cap_pct = round((current_capacity / total_emp) * 100.0, 1)
        estimated_requirement = total_emp  # 100% cadre readiness goal
        capacity_gap = max(0, estimated_requirement - current_capacity)

        # Projected gap calculation:
        # projected_gap = capacity_gap + (workforce_gaps * 0.15) - (learning_velocity * 0.3)
        res_gaps = await self.db.execute(
            select(func.count(distinct(SkillGap.employee_id))).where(SkillGap.gap_score > 0)
        )
        gap_pop = res_gaps.scalar() or 0

        res_learning = await self.db.execute(
            select(func.count(distinct(CourseProgress.employee_id))).where(CourseProgress.status == "COMPLETED")
        )
        completed_learners = res_learning.scalar() or 0

        projected_gap = max(0, int(round(capacity_gap + (gap_pop * 0.2) - (completed_learners * 0.4))))

        # Pressure index
        pressure_idx = round(min(100.0, max(0.0, (projected_gap / total_emp) * 100.0)), 1)

        # Priority competencies, roles, and departments
        comp_fc = await self.get_competency_capacity_forecast()
        prio_comps = [c.name for c in comp_fc.competencies[:3] if c.planning_pressure >= 20.0]

        role_fc = await self.get_role_capacity_forecast()
        prio_roles = [r.role_name for r in role_fc.roles[:3] if r.projected_capacity_pressure >= 20.0]

        dept_fc = await self.get_department_capacity_forecast()
        prio_depts = [d.department_name for d in dept_fc.departments[:3] if d.projected_capacity_pressure >= 20.0]

        return WorkforceCapacityForecastResponse(
            current_capacity=current_capacity,
            total_workforce=total_emp,
            current_capacity_percentage=current_cap_pct,
            estimated_capacity_requirement=estimated_requirement,
            capacity_gap=capacity_gap,
            projected_gap=projected_gap,
            overall_pressure_index=pressure_idx,
            priority_competencies=prio_comps,
            priority_roles=prio_roles,
            priority_departments=prio_depts,
            methodology=ForecastMethodology(),
        )

    async def get_competency_capacity_forecast(self) -> CompetencyCapacityForecastResponse:
        """
        Evaluates capacity pressure across individual competencies.
        """
        # Query active competencies with domain
        comps_stmt = select(Competency).where(Competency.is_active.is_(True)).order_by(Competency.name)
        comps_res = await self.db.execute(comps_stmt)
        competencies = comps_res.scalars().all()

        total_emp_res = await self.db.execute(select(func.count(Employee.id)).where(Employee.is_active.is_(True)))
        total_emp = max(1, total_emp_res.scalar() or 1)

        # Pre-fetch emerging skill signals
        emerging_resp = await self.emerging_service.get_emerging_skills_signals()
        emerging_map = {item.competency_id: item.signal_score for item in emerging_resp.skills}

        # Pre-fetch gap populations
        gap_stmt = (
            select(SkillGap.competency_id, func.count(distinct(SkillGap.employee_id)))
            .where(SkillGap.gap_score > 0)
            .group_by(SkillGap.competency_id)
        )
        gap_res = await self.db.execute(gap_stmt)
        gap_map = {row[0]: row[1] for row in gap_res.all()}

        # Pre-fetch learning enrollments per competency
        learn_stmt = (
            select(LearningItemCompetency.competency_id, func.count(distinct(CourseProgress.employee_id)))
            .join(CourseProgress, CourseProgress.learning_item_id == LearningItemCompetency.learning_item_id)
            .group_by(LearningItemCompetency.competency_id)
        )
        learn_res = await self.db.execute(learn_stmt)
        learn_map = {row[0]: row[1] for row in learn_res.all()}

        # Pre-fetch assessed employee scores meeting target (>=70)
        cov_stmt = (
            select(
                EmployeeCompetency.competency_id,
                func.count(distinct(EmployeeCompetency.employee_id)).label("total_assessed"),
                func.count(case((EmployeeCompetency.current_score >= 70.0, 1))).label("meeting_target"),
            )
            .group_by(EmployeeCompetency.competency_id)
        )
        cov_res = await self.db.execute(cov_stmt)
        cov_map = {row[0]: (row[1], row[2]) for row in cov_res.all()}

        items: List[CompetencyCapacityForecastItem] = []
        for comp in competencies:
            assessed, meeting = cov_map.get(comp.id, (0, 0))
            coverage_pct = round((meeting / max(1, assessed)) * 100.0, 1) if assessed > 0 else 0.0
            gap_pop = gap_map.get(comp.id, 0)
            learn_demand = learn_map.get(comp.id, 0)
            emerging_score = emerging_map.get(comp.id, 0.0)

            # Deterministic multi-factor pressure calculation
            gap_pressure = min(100.0, (gap_pop / total_emp) * 100.0)
            demand_pressure = min(100.0, (learn_demand / total_emp) * 100.0)
            coverage_deficit = max(0.0, 80.0 - coverage_pct)

            composite_pressure = round(
                min(
                    100.0,
                    0.35 * gap_pressure
                    + 0.25 * demand_pressure
                    + 0.20 * emerging_score
                    + 0.20 * coverage_deficit,
                ),
                1,
            )

            # Assign explainable status
            if assessed == 0 and gap_pop == 0:
                status = "INSUFFICIENT_DATA"
            elif composite_pressure >= 50.0:
                status = "HIGH_DEFICIT"
            elif composite_pressure >= 25.0:
                status = "MODERATE_DEFICIT"
            else:
                status = "BALANCED"

            rationale = []
            if gap_pop > 0:
                rationale.append(f"{gap_pop} active officer gap(s) identified ({gap_pressure:.0f}% workforce deficit)")
            if learn_demand > 0:
                rationale.append(f"{learn_demand} officer(s) actively training")
            if emerging_score >= 40.0:
                rationale.append(f"High horizon scanning score ({emerging_score:.1f})")
            if coverage_pct < 60.0 and assessed > 0:
                rationale.append(f"Sub-optimal workforce coverage ({coverage_pct:.1f}%)")
            if not rationale:
                rationale.append("Adequate competency baseline across cadre")

            items.append(
                CompetencyCapacityForecastItem(
                    competency_id=comp.id,
                    name=comp.name,
                    domain=comp.domain.name if comp.domain else "General",
                    current_coverage=coverage_pct,
                    target_coverage=80.0,
                    gap_population=gap_pop,
                    learning_demand=learn_demand,
                    emerging_signal=emerging_score,
                    planning_pressure=composite_pressure,
                    status=status,
                    rationale=rationale,
                )
            )

        # Sort descending by planning pressure
        items.sort(key=lambda x: x.planning_pressure, reverse=True)

        return CompetencyCapacityForecastResponse(
            total_competencies=len(items),
            competencies=items,
            data_quality=PlanningDataQuality(
                historical_periods=1,
                records_used=len(items),
                status="SUFFICIENT",
                quality_grade="HIGH",
            ),
        )

    async def get_role_capacity_forecast(self) -> RoleCapacityForecastResponse:
        """
        Evaluates cadre capacity pressure per job role.
        """
        roles_stmt = select(JobRole).order_by(JobRole.name)
        roles_res = await self.db.execute(roles_stmt)
        roles = roles_res.scalars().all()

        role_analytics = await self.workforce_service.get_role_analytics()
        role_map = {item.role_id: item for item in role_analytics.roles}

        items: List[RoleCapacityForecastItem] = []
        for role in roles:
            analytics = role_map.get(role.id)
            emp_count = analytics.employee_count if analytics else 0
            req_count = analytics.competency_requirements_count if analytics else 0
            readiness = (analytics.average_role_readiness or 0.0) if analytics else 0.0

            # Employees meeting target
            meeting = int(round((readiness / 100.0) * emp_count)) if emp_count > 0 else 0
            below = max(0, emp_count - meeting)

            # Query critical gaps for this role
            gaps_stmt = (
                select(func.count(distinct(SkillGap.id)))
                .join(Employee, Employee.id == SkillGap.employee_id)
                .where(Employee.job_role_id == role.id, SkillGap.gap_score > 0)
            )
            gaps_res = await self.db.execute(gaps_stmt)
            critical_gaps = gaps_res.scalar() or 0

            # Learning demand
            learn_stmt = (
                select(func.count(distinct(CourseProgress.employee_id)))
                .join(Employee, Employee.id == CourseProgress.employee_id)
                .where(Employee.job_role_id == role.id, CourseProgress.status.in_(["IN_PROGRESS", "STARTED"]))
            )
            learn_res = await self.db.execute(learn_stmt)
            learn_demand = learn_res.scalar() or 0

            # Capacity pressure = readiness deficit adjusted by critical gap ratio
            readiness_deficit = max(0.0, 100.0 - readiness)
            gap_factor = min(100.0, (critical_gaps / max(1, emp_count)) * 50.0)
            pressure = round(min(100.0, 0.6 * readiness_deficit + 0.4 * gap_factor), 1)

            if pressure >= 50.0:
                status = "HIGH_PRESSURE"
            elif pressure >= 25.0:
                status = "MODERATE_PRESSURE"
            else:
                status = "ADEQUATE"

            rationale = []
            if below > 0:
                rationale.append(f"{below} officer(s) currently below proficiency benchmark")
            if critical_gaps > 0:
                rationale.append(f"{critical_gaps} unresolved skill gap(s) logged")
            if learn_demand > 0:
                rationale.append(f"{learn_demand} officer(s) in active upskilling")
            if not rationale:
                rationale.append("High role readiness and requirement fulfillment")

            items.append(
                RoleCapacityForecastItem(
                    role_id=role.id,
                    role_name=role.name,
                    cadre_level=role.career_level,
                    employee_count=emp_count,
                    required_competencies_count=req_count,
                    employees_meeting_target=meeting,
                    employees_below_target=below,
                    critical_skill_gaps=critical_gaps,
                    learning_demand=learn_demand,
                    readiness_signal=round(readiness, 1),
                    projected_capacity_pressure=pressure,
                    status=status,
                    rationale=rationale,
                )
            )

        items.sort(key=lambda x: x.projected_capacity_pressure, reverse=True)

        return RoleCapacityForecastResponse(
            total_roles=len(items),
            roles=items,
            data_quality=PlanningDataQuality(
                historical_periods=1,
                records_used=len(items),
                status="SUFFICIENT",
                quality_grade="HIGH",
            ),
        )

    async def get_department_capacity_forecast(self) -> DepartmentCapacityForecastResponse:
        """
        Evaluates departmental capacity pressure.
        """
        dept_analytics = await self.workforce_service.get_department_analytics()

        items: List[DepartmentCapacityForecastItem] = []
        for d in dept_analytics.departments:
            # Query active learning in department
            learn_stmt = (
                select(func.count(distinct(CourseProgress.employee_id)))
                .join(Employee, Employee.id == CourseProgress.employee_id)
                .where(Employee.department_id == d.department_id, CourseProgress.status.in_(["IN_PROGRESS", "STARTED"]))
            )
            learn_res = await self.db.execute(learn_stmt)
            learn_demand = learn_res.scalar() or 0

            # Capacity pressure
            avg_score = d.average_competency_score or 0.0
            score_deficit = max(0.0, 80.0 - avg_score)
            total_gaps = d.critical_gap_count + d.high_gap_count
            gap_density = min(100.0, (total_gaps / max(1, d.employee_count)) * 50.0)
            pressure = round(min(100.0, 0.5 * score_deficit + 0.5 * gap_density), 1)

            if pressure >= 50.0:
                status = "HIGH_PRESSURE"
            elif pressure >= 25.0:
                status = "MODERATE_PRESSURE"
            else:
                status = "BALANCED"

            rationale = []
            if total_gaps > 0:
                rationale.append(f"{total_gaps} departmental skill gap(s) recorded")
            if avg_score < 70.0:
                rationale.append(f"Average proficiency ({avg_score:.1f}) below ministry benchmark")
            if learn_demand > 0:
                rationale.append(f"{learn_demand} officer(s) in active training")
            if not rationale:
                rationale.append("Strong departmental capacity alignment")

            items.append(
                DepartmentCapacityForecastItem(
                    department_id=d.department_id,
                    department_name=d.department_name,
                    code=d.department_code,
                    workforce_size=d.employee_count,
                    competency_coverage=round(avg_score, 1),
                    major_skill_gaps=total_gaps,
                    learning_demand=learn_demand,
                    emerging_skill_pressure=round(pressure * 0.8, 1),
                    projected_capacity_pressure=pressure,
                    status=status,
                    rationale=rationale,
                )
            )

        items.sort(key=lambda x: x.projected_capacity_pressure, reverse=True)

        return DepartmentCapacityForecastResponse(
            total_departments=len(items),
            departments=items,
            data_quality=PlanningDataQuality(
                historical_periods=1,
                records_used=len(items),
                status="SUFFICIENT",
                quality_grade="HIGH",
            ),
        )

    async def get_planning_recommendations(self) -> PlanningRecommendationsResponse:
        """
        Generates deterministic, actionable workforce planning recommendations.
        """
        recs: List[PlanningRecommendationItem] = []

        # 1. Top Deficit Competency
        comp_fc = await self.get_competency_capacity_forecast()
        high_comp = [c for c in comp_fc.competencies if c.planning_pressure >= 40.0]
        if high_comp:
            top_c = high_comp[0]
            recs.append(
                PlanningRecommendationItem(
                    id=f"rec-comp-{top_c.competency_id}",
                    type="COMPETENCY_TRAINING",
                    title=f"Prioritize Cadre-Wide Training in {top_c.name}",
                    priority="HIGH",
                    affected_population=top_c.gap_population,
                    evidence_signals=top_c.rationale,
                    rationale=f"{top_c.name} demonstrates a capacity pressure index of {top_c.planning_pressure:.1f} with {top_c.gap_population} active officer deficits.",
                    suggested_action=f"Mandate enrollment in targeted {top_c.name} iGOT/NSSTA curriculum for all officers with recorded skill gaps.",
                    data_quality_status="SUFFICIENT",
                )
            )

        # 2. High Pressure Cadre Role
        role_fc = await self.get_role_capacity_forecast()
        high_roles = [r for r in role_fc.roles if r.projected_capacity_pressure >= 30.0]
        if high_roles:
            top_r = high_roles[0]
            recs.append(
                PlanningRecommendationItem(
                    id=f"rec-role-{top_r.role_id}",
                    type="ROLE_CAPACITY",
                    title=f"Augment Capacity for {top_r.role_name}",
                    priority="HIGH" if top_r.projected_capacity_pressure >= 50.0 else "MEDIUM",
                    affected_population=top_r.employees_below_target,
                    evidence_signals=top_r.rationale,
                    rationale=f"Cadre role {top_r.role_name} has {top_r.employees_below_target} officers below proficiency threshold.",
                    suggested_action=f"Deploy mandatory role-specific modular learning paths and practical lab simulations.",
                    data_quality_status="SUFFICIENT",
                )
            )

        # 3. Department Focus
        dept_fc = await self.get_department_capacity_forecast()
        high_depts = [d for d in dept_fc.departments if d.projected_capacity_pressure >= 30.0]
        if high_depts:
            top_d = high_depts[0]
            recs.append(
                PlanningRecommendationItem(
                    id=f"rec-dept-{top_d.department_id}",
                    type="DEPARTMENT_FOCUS",
                    title=f"Focus Departmental Upskilling in {top_d.department_name}",
                    priority="MEDIUM",
                    affected_population=top_d.major_skill_gaps,
                    evidence_signals=top_d.rationale,
                    rationale=f"{top_d.department_name} exhibits {top_d.major_skill_gaps} unresolved gaps and {top_d.competency_coverage:.1f} average score.",
                    suggested_action=f"Coordinate with departmental nodal officer to review pending course completions.",
                    data_quality_status="SUFFICIENT",
                )
            )

        # 4. Emerging Skills Horizon Monitoring
        emerging_resp = await self.emerging_service.get_emerging_skills_signals()
        if emerging_resp.skills:
            top_e = emerging_resp.skills[0]
            if top_e.signal_score >= 35.0:
                recs.append(
                    PlanningRecommendationItem(
                        id=f"rec-horizon-{top_e.competency_id}",
                        type="HORIZON_MONITORING",
                        title=f"Institutionalize Horizon Capability: {top_e.name}",
                        priority="MEDIUM",
                        affected_population=top_e.affected_employees,
                        evidence_signals=[f"Emerging signal score {top_e.signal_score:.1f}"] + top_e.signals,
                        rationale=f"{top_e.name} displays strong internal demand velocity and forward-looking strategic relevance.",
                        suggested_action="Incorporate specialized statistical computing and AI methodology modules into upcoming training cycles.",
                        data_quality_status="SUFFICIENT",
                    )
                )

        # 5. Scheduled Reassessment
        overview = await self.workforce_service.get_workforce_overview()
        recs.append(
            PlanningRecommendationItem(
                id="rec-reassessment-scheduled",
                type="REASSESSMENT",
                title="Conduct Quarterly Cadre Competency Reassessment",
                priority="LOW",
                affected_population=overview.active_employees,
                evidence_signals=[f"{overview.active_employees} active officers tracked", f"Current readiness {overview.average_role_readiness:.1f}%"],
                rationale="Periodic closed-loop adaptive recalibration ensures longitudinal evidence updates and maintains planning accuracy.",
                suggested_action="Schedule automated computerized adaptive assessment invitations for active personnel.",
                data_quality_status="SUFFICIENT",
            )
        )

        return PlanningRecommendationsResponse(
            total_recommendations=len(recs),
            recommendations=recs,
            data_quality=PlanningDataQuality(
                historical_periods=1,
                records_used=len(recs),
                status="SUFFICIENT",
                quality_grade="HIGH",
            ),
        )

    async def get_employee_planning_drilldown(self, employee_id: uuid.UUID) -> Optional[EmployeePlanningDrilldownResponse]:
        """
        Individual employee capacity and planning drilldown.
        """
        emp_stmt = (
            select(Employee)
            .options(selectinload(Employee.department), selectinload(Employee.job_role))
            .where(Employee.id == employee_id)
        )
        emp_res = await self.db.execute(emp_stmt)
        employee = emp_res.scalar_one_or_none()
        if not employee:
            return None

        # Employee performance and readiness
        perf = None
        try:
            perf = await self.perf_service.get_employee_performance(employee_id)
        except Exception:
            pass
        current_avg = perf.overall.current_score if perf else 0.0
        role_readiness = (
            perf.overall.target_readiness_percentage
            if (perf and perf.overall.target_readiness_percentage is not None)
            else current_avg
        )

        # Active gaps
        gaps_stmt = select(func.count(SkillGap.id)).where(
            SkillGap.employee_id == employee_id,
            SkillGap.gap_score > 0,
        )
        gaps_res = await self.db.execute(gaps_stmt)
        active_gaps = gaps_res.scalar() or 0

        # Completed courses
        courses_stmt = select(func.count(CourseProgress.id)).where(
            CourseProgress.employee_id == employee_id,
            CourseProgress.status == "COMPLETED",
        )
        courses_res = await self.db.execute(courses_stmt)
        completed_courses = courses_res.scalar() or 0

        # Observed improvement points from recalibration history
        hist_stmt = (
            select(
                CompetencyRecalibration.created_at,
                CompetencyRecalibration.new_score,
                CompetencyRecalibration.previous_score,
                Competency.name.label("comp_name"),
            )
            .join(Competency, Competency.id == CompetencyRecalibration.competency_id)
            .where(CompetencyRecalibration.employee_id == employee_id)
            .order_by(CompetencyRecalibration.created_at)
        )
        hist_res = await self.db.execute(hist_stmt)
        hist_rows = hist_res.all()

        trajectory: List[EmployeePlanningTrajectoryPoint] = []
        total_improvement = 0.0
        for r in hist_rows:
            diff = max(0.0, float((r.new_score or 0.0) - (r.previous_score or 0.0)))
            total_improvement += diff
            trajectory.append(
                EmployeePlanningTrajectoryPoint(
                    timestamp=r.created_at.isoformat() if r.created_at else datetime.now(timezone.utc).isoformat(),
                    competency_name=r.comp_name,
                    score=round(float(r.new_score or 0.0), 1),
                    source="Recalibration",
                )
            )

        if not trajectory:
            # Fallback to CompetencyEvidence
            ev_stmt = (
                select(
                    CompetencyEvidence.recorded_at,
                    CompetencyEvidence.normalized_score,
                    Competency.name.label("comp_name"),
                    CompetencyEvidence.evidence_type,
                )
                .join(Competency, Competency.id == CompetencyEvidence.competency_id)
                .where(CompetencyEvidence.employee_id == employee_id)
                .order_by(CompetencyEvidence.recorded_at)
            )
            ev_res = await self.db.execute(ev_stmt)
            for r in ev_res.all():
                trajectory.append(
                    EmployeePlanningTrajectoryPoint(
                        timestamp=r.recorded_at.isoformat() if r.recorded_at else datetime.now(timezone.utc).isoformat(),
                        competency_name=r.comp_name,
                        score=round(float(r.normalized_score or 0.0), 1),
                        source=r.evidence_type.value if hasattr(r.evidence_type, "value") else str(r.evidence_type),
                    )
                )

        # Readiness indicator
        if role_readiness >= 75.0:
            indicator = "READY"
        elif role_readiness >= 50.0:
            indicator = "DEVELOPING"
        else:
            indicator = "AT_RISK"

        signals = []
        if active_gaps > 0:
            signals.append(f"{active_gaps} unresolved skill gap(s) require intervention")
        if completed_courses > 0:
            signals.append(f"{completed_courses} training module(s) completed successfully")
        if total_improvement > 0:
            signals.append(f"{total_improvement:.1f} cumulative score improvement points observed")
        if not signals:
            signals.append("Baseline assessment verified; regular monitoring indicated")

        return EmployeePlanningDrilldownResponse(
            employee_id=employee.id,
            full_name=employee.full_name,
            employee_code=employee.employee_code,
            designation=employee.designation,
            department_name=employee.department.name if employee.department else None,
            role_name=employee.job_role.name if employee.job_role else None,
            current_average_score=round(current_avg, 1),
            role_readiness_percentage=round(role_readiness, 1),
            active_gaps_count=active_gaps,
            learning_modules_completed=completed_courses,
            observed_improvement_points=round(total_improvement, 1),
            readiness_indicator=indicator,
            historical_trajectory=trajectory,
            planning_signals=signals,
        )
