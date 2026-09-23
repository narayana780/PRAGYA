import uuid

from fastapi import status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import PragyaException
from app.modules.assessments.models import EmployeeCompetency
from app.modules.competencies.constants import score_to_proficiency_level
from app.modules.competencies.models import (
    CompetencyRequirement,
    ProficiencyLevel,
)
from app.modules.employees.models import Employee
from app.modules.skill_gaps.constants import (
    calculate_priority_score,
    generate_gap_explanation,
    get_confidence_flag,
)
from app.modules.skill_gaps.models import SkillGap
from app.modules.skill_gaps.repository import SkillGapRepository
from app.modules.skill_gaps.schemas import (
    PriorityBreakdown,
    SkillGapResponse,
    SkillGapSummaryResponse,
)


class SkillGapService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SkillGapRepository(db)

    def _to_response(self, gap: SkillGap) -> SkillGapResponse:
        _, _, breakdown = calculate_priority_score(
            gap_score=gap.gap_score,
            criticality=gap.criticality,
            task_relevance=gap.task_relevance,
            mission_urgency=gap.mission_urgency,
            confidence=gap.confidence,
        )

        return SkillGapResponse(
            id=gap.id,
            employee_id=gap.employee_id,
            competency_id=gap.competency_id,
            competency_code=gap.competency.code if gap.competency else "",
            competency_name=gap.competency.name if gap.competency else "",
            domain_name=gap.competency.domain.name if gap.competency and gap.competency.domain else "",
            domain_code=gap.competency.domain.code if gap.competency and gap.competency.domain else "",
            current_score=gap.current_score,
            required_score=gap.required_score,
            gap_score=gap.gap_score,
            current_level_id=gap.current_level_id,
            current_level_number=gap.current_level.level_number if gap.current_level else None,
            current_level_name=gap.current_level.name if gap.current_level else None,
            required_level_id=gap.required_level_id,
            required_level_number=gap.required_level.level_number if gap.required_level else 1,
            required_level_name=gap.required_level.name if gap.required_level else "Awareness",
            confidence=gap.confidence,
            confidence_flag=gap.confidence_flag,
            criticality=gap.criticality,
            task_relevance=gap.task_relevance,
            mission_urgency=gap.mission_urgency,
            priority_score=gap.priority_score,
            priority_level=gap.priority_level,
            role_relevance=gap.role_relevance,
            explanation=gap.explanation,
            calculated_at=gap.calculated_at,
            updated_at=gap.updated_at,
            priority_breakdown=PriorityBreakdown(**breakdown),
        )

    async def _get_proficiency_level_by_score(self, score: float) -> ProficiencyLevel | None:
        lvl_num, _ = score_to_proficiency_level(score)
        stmt = select(ProficiencyLevel).where(ProficiencyLevel.level_number == lvl_num)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def recalculate_employee_gaps(self, employee_id: uuid.UUID) -> list[SkillGapResponse]:
        # 1. Fetch employee
        stmt_emp = (
            select(Employee)
            .options(selectinload(Employee.job_role))
            .where(Employee.id == employee_id)
            .execution_options(populate_existing=True)
        )
        res_emp = await self.db.execute(stmt_emp)
        employee = res_emp.scalar_one_or_none()
        if not employee:
            raise PragyaException(
                code="EMPLOYEE_NOT_FOUND",
                message=f"Employee {employee_id} not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if not employee.job_role_id:
            return []

        role_name = employee.job_role.name if employee.job_role else "Assigned Role"

        # 2. Fetch role requirements
        stmt_reqs = (
            select(CompetencyRequirement)
            .options(
                selectinload(CompetencyRequirement.competency),
                selectinload(CompetencyRequirement.required_level),
            )
            .where(CompetencyRequirement.job_role_id == employee.job_role_id)
        )
        res_reqs = await self.db.execute(stmt_reqs)
        requirements = list(res_reqs.scalars().all())

        # Clean up any gaps for competencies no longer in the active role requirements
        active_comp_ids = {req.competency_id for req in requirements}
        if active_comp_ids:
            stmt_del = (
                delete(SkillGap)
                .where(
                    SkillGap.employee_id == employee_id,
                    SkillGap.competency_id.notin_(active_comp_ids),
                )
                .execution_options(synchronize_session="fetch")
            )
            await self.db.execute(stmt_del)
            await self.db.commit()

        # 3. Fetch employee demonstrated competencies
        stmt_comps = select(EmployeeCompetency).where(EmployeeCompetency.employee_id == employee_id)
        res_comps = await self.db.execute(stmt_comps)
        employee_comps = {c.competency_id: c for c in res_comps.scalars().all()}

        calculated_gaps = []

        for req in requirements:
            emp_comp = employee_comps.get(req.competency_id)
            current_score = emp_comp.current_score if emp_comp else 0.0
            confidence = emp_comp.confidence if emp_comp else 0.0

            current_level = (
                await self._get_proficiency_level_by_score(current_score)
                if emp_comp
                else None
            )

            required_score = float(req.required_score)
            gap_score = max(round(required_score - current_score, 2), 0.0)

            priority_score, priority_level, _ = calculate_priority_score(
                gap_score=gap_score,
                criticality=req.criticality,
                task_relevance=req.task_relevance,
                mission_urgency=req.mission_urgency,
                confidence=confidence,
            )

            confidence_flag = get_confidence_flag(confidence)
            competency_name = req.competency.name if req.competency else "Competency"

            explanation = generate_gap_explanation(
                competency_name=competency_name,
                role_name=role_name,
                current_score=current_score,
                required_score=required_score,
                gap_score=gap_score,
                priority_level=priority_level,
                criticality=req.criticality,
                task_relevance=req.task_relevance,
                mission_urgency=req.mission_urgency,
                confidence=confidence,
            )

            gap_record = SkillGap(
                employee_id=employee_id,
                competency_id=req.competency_id,
                current_score=current_score,
                required_score=required_score,
                gap_score=gap_score,
                current_level_id=current_level.id if current_level else None,
                required_level_id=req.required_level_id,
                confidence=confidence,
                confidence_flag=confidence_flag,
                criticality=req.criticality,
                task_relevance=req.task_relevance,
                mission_urgency=req.mission_urgency,
                priority_score=priority_score,
                priority_level=priority_level,
                role_relevance=req.rationale,
                explanation=explanation,
            )

            persisted = await self.repo.upsert(gap_record)
            calculated_gaps.append(persisted)

        # Reload with relationships
        persisted_gaps = await self.repo.list_by_employee(employee_id)
        return [self._to_response(g) for g in persisted_gaps]

    async def recalculate_gap(
        self, employee_id: uuid.UUID, competency_id: uuid.UUID
    ) -> SkillGapResponse | None:
        stmt_emp = (
            select(Employee)
            .options(selectinload(Employee.job_role))
            .where(Employee.id == employee_id)
        )
        res_emp = await self.db.execute(stmt_emp)
        employee = res_emp.scalar_one_or_none()
        if not employee or not employee.job_role_id:
            return None

        role_name = employee.job_role.name if employee.job_role else "Assigned Role"

        stmt_req = (
            select(CompetencyRequirement)
            .options(
                selectinload(CompetencyRequirement.competency),
                selectinload(CompetencyRequirement.required_level),
            )
            .where(
                CompetencyRequirement.job_role_id == employee.job_role_id,
                CompetencyRequirement.competency_id == competency_id,
            )
        )
        res_req = await self.db.execute(stmt_req)
        requirement = res_req.scalar_one_or_none()
        if not requirement:
            return None

        stmt_comp = select(EmployeeCompetency).where(
            EmployeeCompetency.employee_id == employee_id,
            EmployeeCompetency.competency_id == competency_id,
        )
        res_comp = await self.db.execute(stmt_comp)
        emp_comp = res_comp.scalar_one_or_none()

        current_score = emp_comp.current_score if emp_comp else 0.0
        confidence = emp_comp.confidence if emp_comp else 0.0
        current_level = (
            await self._get_proficiency_level_by_score(current_score) if emp_comp else None
        )

        required_score = float(requirement.required_score)
        gap_score = max(round(required_score - current_score, 2), 0.0)

        priority_score, priority_level, _ = calculate_priority_score(
            gap_score=gap_score,
            criticality=requirement.criticality,
            task_relevance=requirement.task_relevance,
            mission_urgency=requirement.mission_urgency,
            confidence=confidence,
        )

        confidence_flag = get_confidence_flag(confidence)
        competency_name = requirement.competency.name if requirement.competency else "Competency"

        explanation = generate_gap_explanation(
            competency_name=competency_name,
            role_name=role_name,
            current_score=current_score,
            required_score=required_score,
            gap_score=gap_score,
            priority_level=priority_level,
            criticality=requirement.criticality,
            task_relevance=requirement.task_relevance,
            mission_urgency=requirement.mission_urgency,
            confidence=confidence,
        )

        gap_record = SkillGap(
            employee_id=employee_id,
            competency_id=competency_id,
            current_score=current_score,
            required_score=required_score,
            gap_score=gap_score,
            current_level_id=current_level.id if current_level else None,
            required_level_id=requirement.required_level_id,
            confidence=confidence,
            confidence_flag=confidence_flag,
            criticality=requirement.criticality,
            task_relevance=requirement.task_relevance,
            mission_urgency=requirement.mission_urgency,
            priority_score=priority_score,
            priority_level=priority_level,
            role_relevance=requirement.rationale,
            explanation=explanation,
        )

        await self.repo.upsert(gap_record)
        reloaded = await self.repo.get_by_employee_and_competency(employee_id, competency_id)
        return self._to_response(reloaded) if reloaded else None

    async def get_employee_gaps(
        self,
        employee_id: uuid.UUID,
        priority: str | None = None,
        domain: str | None = None,
        competency: str | None = None,
        confidence: str | None = None,
    ) -> list[SkillGapResponse]:
        # If no gaps exist yet, trigger initial calculation
        existing = await self.repo.list_by_employee(employee_id)
        if not existing:
            await self.recalculate_employee_gaps(employee_id)

        gaps = await self.repo.list_by_employee(
            employee_id=employee_id,
            priority=priority,
            domain=domain,
            competency=competency,
            confidence=confidence,
        )
        return [self._to_response(g) for g in gaps]

    async def get_gap_detail(
        self, employee_id: uuid.UUID, competency_id: uuid.UUID
    ) -> SkillGapResponse:
        gap = await self.repo.get_by_employee_and_competency(employee_id, competency_id)
        if not gap:
            # Try to calculate on-demand
            gap_resp = await self.recalculate_gap(employee_id, competency_id)
            if gap_resp:
                return gap_resp
            raise PragyaException(
                code="SKILL_GAP_NOT_FOUND",
                message=f"Skill gap for competency {competency_id} not found for employee {employee_id}",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return self._to_response(gap)

    async def get_summary(self, employee_id: uuid.UUID) -> SkillGapSummaryResponse:
        gaps = await self.get_employee_gaps(employee_id)
        if not gaps:
            return SkillGapSummaryResponse(
                total_competencies=0,
                gaps_count=0,
                critical_count=0,
                high_count=0,
                medium_count=0,
                low_count=0,
                no_gap_count=0,
                average_gap=0.0,
                highest_priority_gap=None,
                last_calculated_at=None,
            )

        total = len(gaps)
        gaps_count = sum(1 for g in gaps if g.gap_score > 0.0)
        critical_count = sum(1 for g in gaps if g.priority_level == "CRITICAL")
        high_count = sum(1 for g in gaps if g.priority_level == "HIGH")
        medium_count = sum(1 for g in gaps if g.priority_level == "MEDIUM")
        low_count = sum(1 for g in gaps if g.priority_level == "LOW")
        no_gap_count = sum(1 for g in gaps if g.priority_level == "NO_GAP")

        avg_gap = round(sum(g.gap_score for g in gaps) / total, 1) if total > 0 else 0.0

        # Highest priority gap (only among active gaps if possible)
        active_gaps = [g for g in gaps if g.gap_score > 0.0]
        highest_gap = (
            max(active_gaps, key=lambda x: x.priority_score)
            if active_gaps
            else (max(gaps, key=lambda x: x.priority_score) if gaps else None)
        )

        last_calc = max(g.calculated_at for g in gaps) if gaps else None

        return SkillGapSummaryResponse(
            total_competencies=total,
            gaps_count=gaps_count,
            critical_count=critical_count,
            high_count=high_count,
            medium_count=medium_count,
            low_count=low_count,
            no_gap_count=no_gap_count,
            average_gap=avg_gap,
            highest_priority_gap=highest_gap,
            last_calculated_at=last_calc,
        )
