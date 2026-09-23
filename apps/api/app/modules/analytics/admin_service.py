import uuid
from typing import Any

from sqlalchemy import case, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.adaptive.models import CompetencyRecalibration
from app.modules.analytics.admin_schemas import (
    AdminEmployeeListItem,
    AdminEmployeeListResponse,
    DepartmentAnalyticsItem,
    DepartmentAnalyticsResponse,
    DepartmentHeatmapCompetencyItem,
    DepartmentHeatmapDepartmentItem,
    DepartmentHeatmapResponse,
    RoleAnalyticsItem,
    RoleAnalyticsResponse,
    TopCourseLearningItem,
    WorkforceCompetenciesResponse,
    WorkforceCompetencyItem,
    WorkforceGapsResponse,
    WorkforceGapSummaryItem,
    WorkforceOverviewResponse,
    WorkforceTrainingOverviewResponse,
)
from app.modules.assessments.models import (
    AssessmentAttempt,
    CompetencyEvidence,
    EmployeeCompetency,
)
from app.modules.competencies.models import (
    Competency,
    CompetencyDomain,
    CompetencyRequirement,
)
from app.modules.courses.models import (
    CourseProgress,
    LearningItem,
    ModuleActivityAttempt,
)
from app.modules.departments.models import Department
from app.modules.employees.models import Employee
from app.modules.job_roles.models import JobRole
from app.modules.skill_gaps.models import SkillGap


class WorkforceAnalysisService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_workforce_overview(self) -> WorkforceOverviewResponse:
        """
        Calculates aggregate workforce metrics directly from real database records.
        """
        # 1. Total and Active Employees
        stmt_emp_counts = select(
            func.count(Employee.id).label("total"),
            func.count(case((Employee.is_active.is_(True), 1))).label("active"),
        )
        res_emp = await self.db.execute(stmt_emp_counts)
        row_emp = res_emp.one()
        total_employees = row_emp.total or 0
        active_employees = row_emp.active or 0

        # 2. Departments & Roles Counts
        res_dept_cnt = await self.db.execute(select(func.count(Department.id)))
        departments_count = res_dept_cnt.scalar() or 0

        res_roles_cnt = await self.db.execute(select(func.count(JobRole.id)))
        roles_count = res_roles_cnt.scalar() or 0

        # 3. Competencies Tracked
        res_comp_cnt = await self.db.execute(
            select(func.count(Competency.id)).where(Competency.is_active.is_(True))
        )
        competencies_tracked = res_comp_cnt.scalar() or 0

        # 4. Employees Assessed & Evaluated
        # An assessed employee has records in CompetencyEvidence or AssessmentAttempt
        stmt_assessed = select(
            func.count(distinct(CompetencyEvidence.employee_id))
        )
        res_assessed = await self.db.execute(stmt_assessed)
        employees_assessed = res_assessed.scalar() or 0

        # Fallback if no evidence yet, check attempts
        if employees_assessed == 0:
            res_att = await self.db.execute(select(func.count(distinct(AssessmentAttempt.employee_id))))
            employees_assessed = res_att.scalar() or 0

        stmt_emp_comps = select(
            func.count(distinct(EmployeeCompetency.employee_id))
        )
        res_emp_comps = await self.db.execute(stmt_emp_comps)
        employees_with_competencies = res_emp_comps.scalar() or 0

        # 5. Global Average Competency Score
        stmt_avg_score = select(func.avg(EmployeeCompetency.current_score))
        res_avg_score = await self.db.execute(stmt_avg_score)
        val_avg_score = res_avg_score.scalar()
        average_competency_score = (
            round(float(val_avg_score), 2) if val_avg_score is not None else None
        )

        # 6. Global Average Role Readiness & Employees Needing Attention
        # Fetch active employees with job roles and their role requirements
        stmt_reqs = (
            select(
                Employee.id.label("employee_id"),
                Employee.job_role_id,
                CompetencyRequirement.competency_id,
                CompetencyRequirement.required_score,
                EmployeeCompetency.current_score,
            )
            .join(JobRole, Employee.job_role_id == JobRole.id)
            .join(CompetencyRequirement, JobRole.id == CompetencyRequirement.job_role_id)
            .outerjoin(
                EmployeeCompetency,
                (EmployeeCompetency.employee_id == Employee.id)
                & (EmployeeCompetency.competency_id == CompetencyRequirement.competency_id),
            )
            .where(Employee.is_active.is_(True))
        )
        res_reqs = await self.db.execute(stmt_reqs)
        rows_reqs = res_reqs.all()

        # Group requirements by employee
        emp_readiness_map: dict[uuid.UUID, dict[str, float]] = {}
        for row in rows_reqs:
            eid = row.employee_id
            if eid not in emp_readiness_map:
                emp_readiness_map[eid] = {"sum_curr": 0.0, "sum_req": 0.0}
            curr = float(row.current_score or 0.0)
            req = float(row.required_score or 0.0)
            emp_readiness_map[eid]["sum_curr"] += min(curr, req)
            emp_readiness_map[eid]["sum_req"] += req

        readiness_percentages: list[float] = []
        low_readiness_employees: set[uuid.UUID] = set()
        for eid, data in emp_readiness_map.items():
            if data["sum_req"] > 0:
                pct = min(round((data["sum_curr"] / data["sum_req"]) * 100.0, 1), 100.0)
                readiness_percentages.append(pct)
                if pct < 70.0:
                    low_readiness_employees.add(eid)

        average_role_readiness = (
            round(sum(readiness_percentages) / len(readiness_percentages), 1)
            if readiness_percentages
            else None
        )

        # Find employees with CRITICAL or HIGH skill gaps
        stmt_crit_gaps = (
            select(distinct(SkillGap.employee_id))
            .join(Employee, SkillGap.employee_id == Employee.id)
            .where(
                Employee.is_active.is_(True),
                SkillGap.priority_level.in_(["CRITICAL", "HIGH"]),
            )
        )
        res_crit = await self.db.execute(stmt_crit_gaps)
        crit_gap_employees = set(res_crit.scalars().all())

        # Employees needing attention: either critical/high gap or low role readiness
        attention_employees = low_readiness_employees.union(crit_gap_employees)
        employees_needing_attention = len(attention_employees)

        return WorkforceOverviewResponse(
            total_employees=total_employees,
            active_employees=active_employees,
            departments_count=departments_count,
            roles_count=roles_count,
            competencies_tracked=competencies_tracked,
            employees_assessed=employees_assessed,
            employees_with_competencies=employees_with_competencies,
            average_competency_score=average_competency_score,
            average_role_readiness=average_role_readiness,
            employees_needing_attention=employees_needing_attention,
        )

    async def get_workforce_competencies(self) -> WorkforceCompetenciesResponse:
        """
        Returns competency distribution across the workforce with proficiency tiers and gap stats.
        """
        # Fetch all active competencies with domains
        stmt_comps = (
            select(Competency)
            .options(selectinload(Competency.domain))
            .where(Competency.is_active.is_(True))
            .order_by(Competency.code.asc())
        )
        res_comps = await self.db.execute(stmt_comps)
        all_comps = list(res_comps.scalars().all())

        # Aggregate EmployeeCompetency per competency
        stmt_emp_agg = (
            select(
                EmployeeCompetency.competency_id,
                func.count(EmployeeCompetency.id).label("cnt"),
                func.avg(EmployeeCompetency.current_score).label("avg_s"),
                func.min(EmployeeCompetency.current_score).label("min_s"),
                func.max(EmployeeCompetency.current_score).label("max_s"),
            )
            .group_by(EmployeeCompetency.competency_id)
        )
        res_emp_agg = await self.db.execute(stmt_emp_agg)
        emp_agg_map = {row.competency_id: row for row in res_emp_agg.all()}

        # Aggregate individual scores for proficiency distribution
        stmt_all_scores = select(
            EmployeeCompetency.competency_id,
            EmployeeCompetency.current_score,
        )
        res_all_scores = await self.db.execute(stmt_all_scores)
        score_rows = res_all_scores.all()
        score_dist_map: dict[uuid.UUID, dict[str, int]] = {}
        for row in score_rows:
            cid = row.competency_id
            if cid not in score_dist_map:
                score_dist_map[cid] = {
                    "BEGINNER": 0,
                    "DEVELOPING": 0,
                    "PROFICIENT": 0,
                    "ADVANCED": 0,
                }
            s = float(row.current_score or 0.0)
            if s <= 30.0:
                score_dist_map[cid]["BEGINNER"] += 1
            elif s <= 60.0:
                score_dist_map[cid]["DEVELOPING"] += 1
            elif s <= 85.0:
                score_dist_map[cid]["PROFICIENT"] += 1
            else:
                score_dist_map[cid]["ADVANCED"] += 1

        # Aggregate SkillGap per competency
        stmt_gap_agg = (
            select(
                SkillGap.competency_id,
                func.count(case((SkillGap.gap_score > 0, 1))).label("gap_count"),
                func.count(case((SkillGap.priority_level == "CRITICAL", 1))).label("critical_count"),
            )
            .group_by(SkillGap.competency_id)
        )
        res_gap_agg = await self.db.execute(stmt_gap_agg)
        gap_agg_map = {row.competency_id: row for row in res_gap_agg.all()}

        items: list[WorkforceCompetencyItem] = []
        for comp in all_comps:
            agg = emp_agg_map.get(comp.id)
            gaps = gap_agg_map.get(comp.id)
            dist = score_dist_map.get(
                comp.id,
                {"BEGINNER": 0, "DEVELOPING": 0, "PROFICIENT": 0, "ADVANCED": 0},
            )

            if agg and agg.cnt > 0:
                items.append(
                    WorkforceCompetencyItem(
                        competency_id=comp.id,
                        code=comp.code,
                        name=comp.name,
                        domain=comp.domain.name if comp.domain else "General",
                        employee_count=agg.cnt,
                        average_score=round(float(agg.avg_s), 2),
                        minimum_score=round(float(agg.min_s), 2),
                        maximum_score=round(float(agg.max_s), 2),
                        proficiency_distribution=dist,
                        gap_count=gaps.gap_count if gaps else 0,
                        critical_gap_count=gaps.critical_count if gaps else 0,
                    )
                )

        # Deterministic sort: highest employee count DESC, then lowest average score ASC
        items.sort(key=lambda x: (-x.employee_count, x.average_score, x.name))

        return WorkforceCompetenciesResponse(
            competencies=items,
            total_tracked=len(all_comps),
        )

    async def get_department_analytics(self) -> DepartmentAnalyticsResponse:
        """
        Compares workforce capability across departments using deterministic aggregation.
        """
        stmt_depts = select(Department).order_by(Department.name.asc())
        res_depts = await self.db.execute(stmt_depts)
        departments = list(res_depts.scalars().all())

        # Department employee counts
        stmt_emp_cnt = (
            select(
                Employee.department_id,
                func.count(Employee.id).label("cnt"),
            )
            .where(Employee.is_active.is_(True))
            .group_by(Employee.department_id)
        )
        res_emp_cnt = await self.db.execute(stmt_emp_cnt)
        dept_emp_map = {row.department_id: row.cnt for row in res_emp_cnt.all()}

        # Department average competency score
        stmt_dept_scores = (
            select(
                Employee.department_id,
                func.avg(EmployeeCompetency.current_score).label("avg_score"),
            )
            .join(Employee, EmployeeCompetency.employee_id == Employee.id)
            .where(Employee.is_active.is_(True))
            .group_by(Employee.department_id)
        )
        res_dept_scores = await self.db.execute(stmt_dept_scores)
        dept_score_map = {
            row.department_id: round(float(row.avg_score), 2)
            for row in res_dept_scores.all()
            if row.avg_score is not None
        }

        # Department role readiness
        stmt_dept_reqs = (
            select(
                Employee.department_id,
                Employee.id.label("employee_id"),
                CompetencyRequirement.required_score,
                EmployeeCompetency.current_score,
            )
            .join(JobRole, Employee.job_role_id == JobRole.id)
            .join(CompetencyRequirement, JobRole.id == CompetencyRequirement.job_role_id)
            .outerjoin(
                EmployeeCompetency,
                (EmployeeCompetency.employee_id == Employee.id)
                & (EmployeeCompetency.competency_id == CompetencyRequirement.competency_id),
            )
            .where(Employee.is_active.is_(True))
        )
        res_dept_reqs = await self.db.execute(stmt_dept_reqs)
        dept_emp_reqs: dict[uuid.UUID, dict[uuid.UUID, dict[str, float]]] = {}
        for row in res_dept_reqs.all():
            did = row.department_id
            eid = row.employee_id
            if did not in dept_emp_reqs:
                dept_emp_reqs[did] = {}
            if eid not in dept_emp_reqs[did]:
                dept_emp_reqs[did][eid] = {"sum_curr": 0.0, "sum_req": 0.0}
            curr = float(row.current_score or 0.0)
            req = float(row.required_score or 0.0)
            dept_emp_reqs[did][eid]["sum_curr"] += min(curr, req)
            dept_emp_reqs[did][eid]["sum_req"] += req

        dept_readiness_map: dict[uuid.UUID, float] = {}
        for did, emps in dept_emp_reqs.items():
            readiness_vals = [
                min(round((v["sum_curr"] / v["sum_req"]) * 100.0, 1), 100.0)
                for v in emps.values()
                if v["sum_req"] > 0
            ]
            if readiness_vals:
                dept_readiness_map[did] = round(
                    sum(readiness_vals) / len(readiness_vals), 1
                )

        # Department skill gaps aggregation
        stmt_dept_gaps = (
            select(
                Employee.department_id,
                func.avg(SkillGap.gap_score).label("avg_gap"),
                func.count(case((SkillGap.priority_level == "CRITICAL", 1))).label("crit_cnt"),
                func.count(case((SkillGap.priority_level == "HIGH", 1))).label("high_cnt"),
            )
            .join(Employee, SkillGap.employee_id == Employee.id)
            .where(Employee.is_active.is_(True))
            .group_by(Employee.department_id)
        )
        res_dept_gaps = await self.db.execute(stmt_dept_gaps)
        dept_gap_map = {row.department_id: row for row in res_dept_gaps.all()}

        # Top strengths & gaps per department
        stmt_comp_by_dept = (
            select(
                Employee.department_id,
                Competency.name.label("comp_name"),
                func.avg(EmployeeCompetency.current_score).label("avg_score"),
            )
            .join(Employee, EmployeeCompetency.employee_id == Employee.id)
            .join(Competency, EmployeeCompetency.competency_id == Competency.id)
            .where(Employee.is_active.is_(True))
            .group_by(Employee.department_id, Competency.name)
            .order_by(Employee.department_id, func.avg(EmployeeCompetency.current_score).desc())
        )
        res_comp_by_dept = await self.db.execute(stmt_comp_by_dept)
        dept_strengths_map: dict[uuid.UUID, list[str]] = {}
        for row in res_comp_by_dept.all():
            did = row.department_id
            if did not in dept_strengths_map:
                dept_strengths_map[did] = []
            if len(dept_strengths_map[did]) < 3:
                dept_strengths_map[did].append(row.comp_name)

        stmt_gaps_by_dept = (
            select(
                Employee.department_id,
                Competency.name.label("comp_name"),
                func.avg(SkillGap.gap_score).label("avg_gap"),
            )
            .join(Employee, SkillGap.employee_id == Employee.id)
            .join(Competency, SkillGap.competency_id == Competency.id)
            .where(Employee.is_active.is_(True), SkillGap.gap_score > 0)
            .group_by(Employee.department_id, Competency.name)
            .order_by(Employee.department_id, func.avg(SkillGap.gap_score).desc())
        )
        res_gaps_by_dept = await self.db.execute(stmt_gaps_by_dept)
        dept_gaps_map: dict[uuid.UUID, list[str]] = {}
        for row in res_gaps_by_dept.all():
            did = row.department_id
            if did not in dept_gaps_map:
                dept_gaps_map[did] = []
            if len(dept_gaps_map[did]) < 3:
                dept_gaps_map[did].append(row.comp_name)

        dept_items: list[DepartmentAnalyticsItem] = []
        for dept in departments:
            gaps_info = dept_gap_map.get(dept.id)
            avg_gap = (
                round(float(gaps_info.avg_gap), 2)
                if (gaps_info and gaps_info.avg_gap is not None)
                else None
            )

            dept_items.append(
                DepartmentAnalyticsItem(
                    department_id=dept.id,
                    department_name=dept.name,
                    department_code=dept.code,
                    employee_count=dept_emp_map.get(dept.id, 0),
                    average_competency_score=dept_score_map.get(dept.id),
                    average_role_readiness=dept_readiness_map.get(dept.id),
                    average_skill_gap_score=avg_gap,
                    critical_gap_count=gaps_info.crit_cnt if gaps_info else 0,
                    high_gap_count=gaps_info.high_cnt if gaps_info else 0,
                    top_competency_strengths=dept_strengths_map.get(dept.id, []),
                    top_competency_gaps=dept_gaps_map.get(dept.id, []),
                )
            )

        return DepartmentAnalyticsResponse(departments=dept_items)

    async def get_department_heatmap(self) -> DepartmentHeatmapResponse:
        """
        Generates Department × Competency heatmap matrix with average scores and gap levels.
        """
        # Fetch active departments and competencies
        stmt_depts = select(Department).order_by(Department.name.asc())
        res_depts = await self.db.execute(stmt_depts)
        departments = list(res_depts.scalars().all())

        stmt_comps = (
            select(Competency)
            .options(selectinload(Competency.domain))
            .where(Competency.is_active.is_(True))
            .order_by(Competency.code.asc())
        )
        res_comps = await self.db.execute(stmt_comps)
        competencies = list(res_comps.scalars().all())

        # Map department employees
        stmt_dept_emp = select(
            Employee.department_id,
            func.count(Employee.id).label("cnt"),
        ).where(Employee.is_active.is_(True)).group_by(Employee.department_id)
        res_dept_emp = await self.db.execute(stmt_dept_emp)
        dept_emp_counts = {row.department_id: row.cnt for row in res_dept_emp.all()}

        # Average scores per department x competency
        stmt_scores = (
            select(
                Employee.department_id,
                EmployeeCompetency.competency_id,
                func.count(EmployeeCompetency.id).label("emp_cnt"),
                func.avg(EmployeeCompetency.current_score).label("avg_s"),
            )
            .join(Employee, EmployeeCompetency.employee_id == Employee.id)
            .where(Employee.is_active.is_(True))
            .group_by(Employee.department_id, EmployeeCompetency.competency_id)
        )
        res_scores = await self.db.execute(stmt_scores)
        score_matrix = {
            (row.department_id, row.competency_id): (row.emp_cnt, float(row.avg_s))
            for row in res_scores.all()
        }

        # Gap priorities per department x competency
        stmt_gaps = (
            select(
                Employee.department_id,
                SkillGap.competency_id,
                SkillGap.priority_level,
            )
            .join(Employee, SkillGap.employee_id == Employee.id)
            .where(Employee.is_active.is_(True))
        )
        res_gaps = await self.db.execute(stmt_gaps)
        priority_order = {"CRITICAL": 5, "HIGH": 4, "MEDIUM": 3, "LOW": 2, "NO_GAP": 1}
        gap_matrix: dict[tuple[uuid.UUID, uuid.UUID], str] = {}
        for row in res_gaps.all():
            key = (row.department_id, row.competency_id)
            curr = gap_matrix.get(key, "NO_GAP")
            if priority_order.get(row.priority_level, 0) > priority_order.get(curr, 0):
                gap_matrix[key] = row.priority_level

        dept_heatmap_items: list[DepartmentHeatmapDepartmentItem] = []
        for dept in departments:
            comp_items: list[DepartmentHeatmapCompetencyItem] = []
            for comp in competencies:
                sc_info = score_matrix.get((dept.id, comp.id))
                gap_lvl = gap_matrix.get((dept.id, comp.id))

                if sc_info:
                    avg_s = round(sc_info[1], 2)
                    emp_c = sc_info[0]
                    # If gap_lvl not explicitly in skill_gaps, infer from score
                    resolved_gap = gap_lvl or ("NO_GAP" if avg_s >= 75.0 else "MEDIUM")
                else:
                    avg_s = None
                    emp_c = 0
                    resolved_gap = "NO_DATA"

                comp_items.append(
                    DepartmentHeatmapCompetencyItem(
                        competency_id=comp.id,
                        competency_name=comp.name,
                        competency_code=comp.code,
                        domain_name=comp.domain.name if comp.domain else "General",
                        average_score=avg_s,
                        gap_level=resolved_gap,
                        employee_count=emp_c,
                    )
                )

            dept_heatmap_items.append(
                DepartmentHeatmapDepartmentItem(
                    department_id=dept.id,
                    department_name=dept.name,
                    department_code=dept.code,
                    employee_count=dept_emp_counts.get(dept.id, 0),
                    competencies=comp_items,
                )
            )

        comp_reference = [
            {
                "id": str(c.id),
                "code": c.code,
                "name": c.name,
                "domain": c.domain.name if c.domain else "General",
            }
            for c in competencies
        ]

        return DepartmentHeatmapResponse(
            departments=dept_heatmap_items,
            competencies_reference=comp_reference,
        )

    async def get_workforce_gaps(self) -> WorkforceGapsResponse:
        """
        Aggregates workforce-wide skill gaps ordered deterministically by priority and affected headcount.
        """
        # 1. Total gaps by priority level
        stmt_counts = select(
            func.count(SkillGap.id).label("total"),
            func.count(case((SkillGap.priority_level == "CRITICAL", 1))).label("critical"),
            func.count(case((SkillGap.priority_level == "HIGH", 1))).label("high"),
            func.count(case((SkillGap.priority_level == "MEDIUM", 1))).label("medium"),
            func.count(case((SkillGap.priority_level == "LOW", 1))).label("low"),
            func.count(case((SkillGap.priority_level == "NO_GAP", 1))).label("no_gap"),
        )
        res_cnt = await self.db.execute(stmt_counts)
        row_cnt = res_cnt.one()

        # 2. Top workforce gaps grouped by competency
        stmt_comp_gaps = (
            select(
                Competency.id.label("competency_id"),
                Competency.name.label("comp_name"),
                Competency.code.label("comp_code"),
                CompetencyDomain.name.label("domain_name"),
                func.count(distinct(SkillGap.employee_id)).label("affected_employees"),
                func.avg(SkillGap.gap_score).label("avg_gap"),
                func.max(
                    case(
                        (SkillGap.priority_level == "CRITICAL", 4),
                        (SkillGap.priority_level == "HIGH", 3),
                        (SkillGap.priority_level == "MEDIUM", 2),
                        (SkillGap.priority_level == "LOW", 1),
                        else_=0,
                    )
                ).label("priority_rank"),
            )
            .join(Competency, SkillGap.competency_id == Competency.id)
            .join(CompetencyDomain, Competency.domain_id == CompetencyDomain.id)
            .where(SkillGap.gap_score > 0)
            .group_by(Competency.id, Competency.name, Competency.code, CompetencyDomain.name)
        )
        res_comp_gaps = await self.db.execute(stmt_comp_gaps)
        comp_gaps_rows = res_comp_gaps.all()

        rank_to_label = {4: "CRITICAL", 3: "HIGH", 2: "MEDIUM", 1: "LOW", 0: "NO_GAP"}
        top_gaps: list[WorkforceGapSummaryItem] = []
        for row in comp_gaps_rows:
            top_gaps.append(
                WorkforceGapSummaryItem(
                    competency_id=row.competency_id,
                    competency_name=row.comp_name,
                    competency_code=row.comp_code,
                    domain_name=row.domain_name or "General",
                    affected_employees=row.affected_employees,
                    average_gap_score=round(float(row.avg_gap), 2),
                    highest_priority_level=rank_to_label.get(row.priority_rank, "NO_GAP"),
                )
            )

        # Deterministic sorting: CRITICAL -> HIGH -> MEDIUM -> LOW, then affected count DESC, then gap score DESC
        priority_weight = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "NO_GAP": 0}
        top_gaps.sort(
            key=lambda g: (
                -priority_weight.get(g.highest_priority_level, 0),
                -g.affected_employees,
                -g.average_gap_score,
                g.competency_name,
            )
        )

        return WorkforceGapsResponse(
            total_gaps=row_cnt.total or 0,
            critical_gaps=row_cnt.critical or 0,
            high_gaps=row_cnt.high or 0,
            medium_gaps=row_cnt.medium or 0,
            low_gaps=row_cnt.low or 0,
            no_gap_count=row_cnt.no_gap or 0,
            top_workforce_gaps=top_gaps,
        )

    async def get_role_analytics(self) -> RoleAnalyticsResponse:
        """
        Analyzes role and cadre readiness using authoritative requirements and employee evaluations.
        """
        stmt_roles = select(JobRole).order_by(JobRole.name.asc())
        res_roles = await self.db.execute(stmt_roles)
        roles = list(res_roles.scalars().all())

        # Employee counts per role
        stmt_role_emp = (
            select(
                Employee.job_role_id,
                func.count(Employee.id).label("cnt"),
            )
            .where(Employee.is_active.is_(True))
            .group_by(Employee.job_role_id)
        )
        res_role_emp = await self.db.execute(stmt_role_emp)
        role_emp_map = {row.job_role_id: row.cnt for row in res_role_emp.all()}

        # Average score per role
        stmt_role_scores = (
            select(
                Employee.job_role_id,
                func.avg(EmployeeCompetency.current_score).label("avg_s"),
            )
            .join(Employee, EmployeeCompetency.employee_id == Employee.id)
            .where(Employee.is_active.is_(True))
            .group_by(Employee.job_role_id)
        )
        res_role_scores = await self.db.execute(stmt_role_scores)
        role_score_map = {
            row.job_role_id: round(float(row.avg_s), 2)
            for row in res_role_scores.all()
            if row.avg_s is not None
        }

        # Role requirements count
        stmt_req_cnt = (
            select(
                CompetencyRequirement.job_role_id,
                func.count(CompetencyRequirement.id).label("cnt"),
            )
            .group_by(CompetencyRequirement.job_role_id)
        )
        res_req_cnt = await self.db.execute(stmt_req_cnt)
        role_req_cnt_map = {row.job_role_id: row.cnt for row in res_req_cnt.all()}

        # Readiness and below-target counts per role
        stmt_role_reqs = (
            select(
                Employee.job_role_id,
                Employee.id.label("employee_id"),
                CompetencyRequirement.required_score,
                EmployeeCompetency.current_score,
            )
            .join(JobRole, Employee.job_role_id == JobRole.id)
            .join(CompetencyRequirement, JobRole.id == CompetencyRequirement.job_role_id)
            .outerjoin(
                EmployeeCompetency,
                (EmployeeCompetency.employee_id == Employee.id)
                & (EmployeeCompetency.competency_id == CompetencyRequirement.competency_id),
            )
            .where(Employee.is_active.is_(True))
        )
        res_role_reqs = await self.db.execute(stmt_role_reqs)
        role_emp_reqs: dict[uuid.UUID, dict[uuid.UUID, dict[str, float]]] = {}
        for row in res_role_reqs.all():
            rid = row.job_role_id
            eid = row.employee_id
            if rid not in role_emp_reqs:
                role_emp_reqs[rid] = {}
            if eid not in role_emp_reqs[rid]:
                role_emp_reqs[rid][eid] = {"sum_curr": 0.0, "sum_req": 0.0}
            curr = float(row.current_score or 0.0)
            req = float(row.required_score or 0.0)
            role_emp_reqs[rid][eid]["sum_curr"] += min(curr, req)
            role_emp_reqs[rid][eid]["sum_req"] += req

        role_readiness_map: dict[uuid.UUID, float] = {}
        role_below_target_map: dict[uuid.UUID, int] = {}
        for rid, emps in role_emp_reqs.items():
            readiness_vals = []
            below_target = 0
            for v in emps.values():
                if v["sum_req"] > 0:
                    pct = min(round((v["sum_curr"] / v["sum_req"]) * 100.0, 1), 100.0)
                    readiness_vals.append(pct)
                    if pct < 100.0:
                        below_target += 1
            if readiness_vals:
                role_readiness_map[rid] = round(
                    sum(readiness_vals) / len(readiness_vals), 1
                )
                role_below_target_map[rid] = below_target

        # Major skill gaps per role
        stmt_role_gaps = (
            select(
                Employee.job_role_id,
                Competency.name.label("comp_name"),
                func.count(SkillGap.id).label("gap_cnt"),
            )
            .join(Employee, SkillGap.employee_id == Employee.id)
            .join(Competency, SkillGap.competency_id == Competency.id)
            .where(Employee.is_active.is_(True), SkillGap.gap_score > 0)
            .group_by(Employee.job_role_id, Competency.name)
            .order_by(Employee.job_role_id, func.count(SkillGap.id).desc())
        )
        res_role_gaps = await self.db.execute(stmt_role_gaps)
        role_gaps_map: dict[uuid.UUID, list[str]] = {}
        for row in res_role_gaps.all():
            rid = row.job_role_id
            if rid not in role_gaps_map:
                role_gaps_map[rid] = []
            if len(role_gaps_map[rid]) < 3:
                role_gaps_map[rid].append(row.comp_name)

        items: list[RoleAnalyticsItem] = []
        for role in roles:
            items.append(
                RoleAnalyticsItem(
                    role_id=role.id,
                    role_name=role.name,
                    role_code=role.code,
                    career_level=role.career_level,
                    employee_count=role_emp_map.get(role.id, 0),
                    average_competency_score=role_score_map.get(role.id),
                    average_role_readiness=role_readiness_map.get(role.id),
                    competency_requirements_count=role_req_cnt_map.get(role.id, 0),
                    major_skill_gaps=role_gaps_map.get(role.id, []),
                    employees_below_target=role_below_target_map.get(role.id, 0),
                )
            )

        return RoleAnalyticsResponse(roles=items)

    async def get_training_overview(self) -> WorkforceTrainingOverviewResponse:
        """
        Aggregates workforce learning and course participation statistics.
        """
        # Learners count
        stmt_learners = select(
            func.count(distinct(CourseProgress.employee_id))
        )
        res_learners = await self.db.execute(stmt_learners)
        total_learners = res_learners.scalar() or 0

        # Enrollments and completion
        stmt_progress = select(
            func.count(CourseProgress.id).label("total_enrollments"),
            func.count(case((CourseProgress.status == "COMPLETED", 1))).label("completed"),
            func.avg(CourseProgress.progress_percentage).label("avg_progress"),
        )
        res_progress = await self.db.execute(stmt_progress)
        row_prog = res_progress.one()
        total_enrollments = row_prog.total_enrollments or 0
        completed_courses = row_prog.completed or 0
        avg_progress = (
            round(float(row_prog.avg_progress), 1) if row_prog.avg_progress is not None else 0.0
        )

        # Learning activity attempts
        stmt_act = select(func.count(ModuleActivityAttempt.id))
        res_act = await self.db.execute(stmt_act)
        total_activities = res_act.scalar() or 0

        # Top courses by enrollment
        stmt_top_courses = (
            select(
                LearningItem.id,
                LearningItem.provider_item_id,
                LearningItem.title,
                LearningItem.provider,
                func.count(CourseProgress.id).label("enrolled_cnt"),
                func.count(case((CourseProgress.status == "COMPLETED", 1))).label("completed_cnt"),
                func.avg(CourseProgress.progress_percentage).label("avg_prog"),
            )
            .join(CourseProgress, LearningItem.id == CourseProgress.learning_item_id)
            .group_by(LearningItem.id, LearningItem.provider_item_id, LearningItem.title, LearningItem.provider)
            .order_by(func.count(CourseProgress.id).desc())
            .limit(10)
        )
        res_top_courses = await self.db.execute(stmt_top_courses)
        top_courses: list[TopCourseLearningItem] = []
        for row in res_top_courses.all():
            enrolled = row.enrolled_cnt or 0
            completed = row.completed_cnt or 0
            comp_rate = round((completed / enrolled * 100.0), 1) if enrolled > 0 else 0.0
            top_courses.append(
                TopCourseLearningItem(
                    course_id=row.id,
                    course_code=row.provider_item_id,
                    title=row.title,
                    provider=row.provider,
                    enrolled_count=enrolled,
                    completed_count=completed,
                    completion_rate=comp_rate,
                    average_progress=round(float(row.avg_prog or 0.0), 1),
                )
            )

        # Competency growth count
        stmt_growth = select(
            func.count(distinct(CompetencyRecalibration.employee_id))
        ).where(CompetencyRecalibration.delta > 0)
        res_growth = await self.db.execute(stmt_growth)
        growth_count = res_growth.scalar() or 0

        return WorkforceTrainingOverviewResponse(
            total_learners=total_learners,
            total_enrollments=total_enrollments,
            completed_courses_count=completed_courses,
            average_learning_progress=avg_progress,
            total_learning_activities=total_activities,
            top_courses=top_courses,
            employees_with_competency_growth=growth_count,
        )

    async def get_admin_employee_list(self) -> AdminEmployeeListResponse:
        """
        Returns an overview list of employees for administrator drill-down analysis.
        """
        stmt = (
            select(Employee)
            .options(
                selectinload(Employee.department),
                selectinload(Employee.job_role),
            )
            .where(Employee.is_active.is_(True))
            .order_by(Employee.employee_code.asc())
        )
        res = await self.db.execute(stmt)
        employees = list(res.scalars().all())

        # Average score per employee
        stmt_scores = select(
            EmployeeCompetency.employee_id,
            func.avg(EmployeeCompetency.current_score).label("avg_s"),
        ).group_by(EmployeeCompetency.employee_id)
        res_scores = await self.db.execute(stmt_scores)
        score_map = {
            row.employee_id: round(float(row.avg_s), 2)
            for row in res_scores.all()
            if row.avg_s is not None
        }

        # Role readiness per employee
        stmt_emp_reqs = (
            select(
                Employee.id.label("employee_id"),
                CompetencyRequirement.required_score,
                EmployeeCompetency.current_score,
            )
            .join(JobRole, Employee.job_role_id == JobRole.id)
            .join(CompetencyRequirement, JobRole.id == CompetencyRequirement.job_role_id)
            .outerjoin(
                EmployeeCompetency,
                (EmployeeCompetency.employee_id == Employee.id)
                & (EmployeeCompetency.competency_id == CompetencyRequirement.competency_id),
            )
            .where(Employee.is_active.is_(True))
        )
        res_emp_reqs = await self.db.execute(stmt_emp_reqs)
        emp_reqs_data: dict[uuid.UUID, dict[str, float]] = {}
        for row in res_emp_reqs.all():
            eid = row.employee_id
            if eid not in emp_reqs_data:
                emp_reqs_data[eid] = {"sum_curr": 0.0, "sum_req": 0.0}
            curr = float(row.current_score or 0.0)
            req = float(row.required_score or 0.0)
            emp_reqs_data[eid]["sum_curr"] += min(curr, req)
            emp_reqs_data[eid]["sum_req"] += req

        readiness_map: dict[uuid.UUID, float] = {}
        for eid, v in emp_reqs_data.items():
            if v["sum_req"] > 0:
                readiness_map[eid] = min(
                    round((v["sum_curr"] / v["sum_req"]) * 100.0, 1), 100.0
                )

        # Critical gaps per employee
        stmt_gaps = (
            select(
                SkillGap.employee_id,
                func.count(case((SkillGap.priority_level == "CRITICAL", 1))).label("crit_cnt"),
            )
            .group_by(SkillGap.employee_id)
        )
        res_gaps = await self.db.execute(stmt_gaps)
        crit_gap_map = {row.employee_id: row.crit_cnt for row in res_gaps.all()}

        items: list[AdminEmployeeListItem] = []
        for emp in employees:
            avg_s = score_map.get(emp.id)
            readiness = readiness_map.get(emp.id)
            crit_gaps = crit_gap_map.get(emp.id, 0)
            needs_att = crit_gaps > 0 or (readiness is not None and readiness < 70.0)

            items.append(
                AdminEmployeeListItem(
                    id=emp.id,
                    employee_code=emp.employee_code,
                    full_name=emp.full_name,
                    designation=emp.designation,
                    department_name=emp.department.name if emp.department else "Unassigned",
                    role_name=emp.job_role.name if emp.job_role else "Unassigned",
                    average_competency=avg_s,
                    role_readiness=readiness,
                    critical_gaps_count=crit_gaps,
                    needs_attention=needs_att,
                )
            )

        return AdminEmployeeListResponse(employees=items, total=len(items))
