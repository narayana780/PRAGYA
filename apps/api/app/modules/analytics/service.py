import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import PragyaException
from app.modules.adaptive.models import (
    AdaptiveAssessmentSession,
    CompetencyRecalibration,
)
from app.modules.analytics.schemas import (
    AdaptiveModalitySummary,
    CompetencyFocusItem,
    CompetencyPerformanceDetail,
    CompetencyStrengthItem,
    CourseModalitySummary,
    DiagnosticModalitySummary,
    EmployeePerformanceResponse,
    EmployeeTimelineResponse,
    LabModalitySummary,
    ModalitiesSummary,
    OverallPerformanceSummary,
    PerformanceCountsSummary,
    QuizModalitySummary,
    TimelineEventItem,
)
from app.modules.assessments.models import (
    Assessment,
    AssessmentAttempt,
    CompetencyEvidence,
    CompetencyScoreHistory,
    EmployeeCompetency,
)
from app.modules.competencies.models import (
    Competency,
    CompetencyRequirement,
)
from app.modules.courses.models import (
    CourseProgress,
    ModuleActivityAttempt,
)
from app.modules.employees.models import Employee
from app.modules.labs.models import LabScenario, LabSession
from app.modules.quizzes.models import QuizAttempt
from app.modules.skill_gaps.service import SkillGapService


class PerformanceAnalysisService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_employee_performance(
        self, employee_id: uuid.UUID
    ) -> EmployeePerformanceResponse:
        # 1. Verify Employee Existence
        stmt_emp = (
            select(Employee)
            .options(
                selectinload(Employee.department),
                selectinload(Employee.job_role),
            )
            .where(Employee.id == employee_id)
        )
        res_emp = await self.db.execute(stmt_emp)
        employee = res_emp.scalar_one_or_none()
        if not employee:
            raise PragyaException(
                code="EMPLOYEE_NOT_FOUND",
                message=f"Employee with ID '{employee_id}' was not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # 2. Query Role Competency Requirements if role exists
        requirements_map: dict[uuid.UUID, CompetencyRequirement] = {}
        if employee.job_role_id:
            stmt_req = (
                select(CompetencyRequirement)
                .options(selectinload(CompetencyRequirement.competency))
                .where(CompetencyRequirement.job_role_id == employee.job_role_id)
            )
            res_req = await self.db.execute(stmt_req)
            requirements_map = {r.competency_id: r for r in res_req.scalars().all()}

        # 3. Query Employee Authoritative Competencies
        stmt_emp_comp = (
            select(EmployeeCompetency)
            .options(
                selectinload(EmployeeCompetency.competency).selectinload(Competency.domain)
            )
            .where(EmployeeCompetency.employee_id == employee_id)
        )
        res_emp_comp = await self.db.execute(stmt_emp_comp)
        emp_comp_list = list(res_emp_comp.scalars().all())
        emp_comp_map = {c.competency_id: c for c in emp_comp_list}

        # 4. Fetch Diagnostic & Earliest Evidence for Baselines
        stmt_diag_evidence = (
            select(CompetencyEvidence)
            .where(
                CompetencyEvidence.employee_id == employee_id,
                CompetencyEvidence.evidence_type == "DIAGNOSTIC",
            )
            .order_by(CompetencyEvidence.recorded_at.asc())
        )
        res_diag = await self.db.execute(stmt_diag_evidence)
        diag_evidence_list = list(res_diag.scalars().all())

        # Baseline map: earliest diagnostic normalized_score
        baseline_map: dict[uuid.UUID, float] = {}
        for ev in diag_evidence_list:
            if ev.competency_id not in baseline_map:
                baseline_map[ev.competency_id] = round(float(ev.normalized_score), 2)

        # Fallback baseline: check any earliest evidence if no diagnostic
        stmt_all_evidence = (
            select(CompetencyEvidence)
            .where(CompetencyEvidence.employee_id == employee_id)
            .order_by(CompetencyEvidence.recorded_at.asc())
        )
        res_all_ev = await self.db.execute(stmt_all_evidence)
        all_evidence_list = list(res_all_ev.scalars().all())
        for ev in all_evidence_list:
            if ev.competency_id not in baseline_map:
                baseline_map[ev.competency_id] = round(float(ev.normalized_score), 2)

        # 5. Union of Competencies: demonstrated competencies + role required competencies
        all_competency_ids = set(emp_comp_map.keys()) | set(requirements_map.keys())

        # Fetch missing competency definitions if any requirement wasn't demonstrated yet
        missing_comp_ids = [cid for cid in all_competency_ids if cid not in emp_comp_map]
        missing_comp_map: dict[uuid.UUID, Competency] = {}
        if missing_comp_ids:
            stmt_missing = (
                select(Competency)
                .options(selectinload(Competency.domain))
                .where(Competency.id.in_(missing_comp_ids))
            )
            res_missing = await self.db.execute(stmt_missing)
            missing_comp_map = {c.id: c for c in res_missing.scalars().all()}

        # 6. Build CompetencyPerformanceDetail items
        competencies_detail: list[CompetencyPerformanceDetail] = []
        improved_count = 0
        declined_count = 0
        mastered_count = 0
        needing_focus_count = 0

        for comp_id in all_competency_ids:
            emp_comp = emp_comp_map.get(comp_id)
            req = requirements_map.get(comp_id)

            if emp_comp:
                competency = emp_comp.competency
                current_score = round(float(emp_comp.current_score), 2)
                confidence = round(float(emp_comp.confidence), 2)
                confidence_label = emp_comp.confidence_label or "LOW"
                last_assessed_at = emp_comp.last_assessed_at
                evidence_count = emp_comp.evidence_count
            else:
                competency = missing_comp_map.get(comp_id)
                current_score = 0.0
                confidence = 0.0
                confidence_label = "LOW"
                last_assessed_at = None
                evidence_count = 0

            if not competency:
                continue

            target_score = float(req.required_score) if req else None
            baseline_score = baseline_map.get(comp_id)

            # Improvement points and percentage
            if baseline_score is not None:
                improvement_points = round(current_score - baseline_score, 2)
                if baseline_score > 0:
                    improvement_percentage = round(
                        ((current_score - baseline_score) / baseline_score) * 100, 1
                    )
                else:
                    improvement_percentage = 100.0 if current_score > 0 else 0.0
            else:
                improvement_points = 0.0
                improvement_percentage = 0.0

            # Deterministic Status Derivation
            effective_target = target_score if target_score is not None else 80.0
            if baseline_score is None:
                status_str = "NO_BASELINE"
            elif current_score >= effective_target and current_score >= 80.0:
                status_str = "MASTERED"
                mastered_count += 1
            elif current_score > baseline_score:
                status_str = "IMPROVING"
                improved_count += 1
            elif current_score < baseline_score:
                status_str = "NEEDS_FOCUS"
                declined_count += 1
                needing_focus_count += 1
            else:
                status_str = "STABLE"

            # Check if role gap is severe
            if req and status_str != "MASTERED":
                gap = max(float(req.required_score) - current_score, 0.0)
                if req.criticality in ("CRITICAL", "HIGH") and gap > 10.0:
                    status_str = "NEEDS_FOCUS"
                    if status_str != "NEEDS_FOCUS":
                        needing_focus_count += 1

            competencies_detail.append(
                CompetencyPerformanceDetail(
                    competency_id=competency.id,
                    competency_code=competency.code,
                    competency_name=competency.name,
                    domain_id=competency.domain_id,
                    domain_name=competency.domain.name if competency.domain else None,
                    baseline_score=baseline_score,
                    current_score=current_score,
                    target_score=target_score,
                    improvement_points=improvement_points,
                    improvement_percentage=improvement_percentage,
                    status=status_str,
                    confidence=confidence,
                    confidence_label=confidence_label,
                    last_assessed_at=last_assessed_at,
                    evidence_count=evidence_count,
                )
            )

        # Sort competencies deterministically by domain display, then code
        competencies_detail.sort(
            key=lambda c: (c.domain_name or "", c.competency_code)
        )

        # 7. Aggregate Overall Performance
        evaluated_comps = [c for c in competencies_detail if c.current_score > 0 or c.evidence_count > 0]
        comps_with_baseline = [c for c in competencies_detail if c.baseline_score is not None]

        if comps_with_baseline:
            avg_baseline = round(
                sum(c.baseline_score for c in comps_with_baseline) / len(comps_with_baseline),
                2,
            )
            avg_current_for_baseline = round(
                sum(c.current_score for c in comps_with_baseline) / len(comps_with_baseline),
                2,
            )
            overall_improvement_pts = round(
                avg_current_for_baseline - avg_baseline, 2
            )
            if avg_baseline > 0:
                overall_improvement_pct = round(
                    ((avg_current_for_baseline - avg_baseline) / avg_baseline) * 100, 1
                )
            else:
                overall_improvement_pct = 100.0 if avg_current_for_baseline > 0 else 0.0
        else:
            avg_baseline = None
            overall_improvement_pts = 0.0
            overall_improvement_pct = 0.0

        avg_current = (
            round(sum(c.current_score for c in competencies_detail) / len(competencies_detail), 2)
            if competencies_detail
            else 0.0
        )

        role_required_comps = [c for c in competencies_detail if c.target_score is not None]
        avg_target = (
            round(sum(c.target_score for c in role_required_comps) / len(role_required_comps), 2)
            if role_required_comps
            else None
        )

        target_readiness_pct = None
        if role_required_comps and avg_target and avg_target > 0:
            sum_curr_role = sum(c.current_score for c in role_required_comps)
            sum_target_role = sum(c.target_score for c in role_required_comps)
            target_readiness_pct = min(
                round((sum_curr_role / sum_target_role) * 100, 1), 100.0
            )

        overall_summary = OverallPerformanceSummary(
            baseline_score=avg_baseline,
            current_score=avg_current,
            target_score=avg_target,
            improvement_points=overall_improvement_pts,
            improvement_percentage=overall_improvement_pct,
            competencies_evaluated=len(evaluated_comps),
            competencies_with_baseline=len(comps_with_baseline),
            target_readiness_percentage=target_readiness_pct,
        )

        # 8. Top 3 Strongest Competencies
        # Sort by: current_score DESC, improvement_points DESC, competency_name ASC
        strength_candidates = [c for c in competencies_detail if c.current_score > 0]
        if not strength_candidates:
            strength_candidates = competencies_detail

        sorted_strengths = sorted(
            strength_candidates,
            key=lambda c: (-c.current_score, -c.improvement_points, c.competency_name),
        )

        strongest_competencies: list[CompetencyStrengthItem] = []
        for idx, item in enumerate(sorted_strengths[:3]):
            strongest_competencies.append(
                CompetencyStrengthItem(
                    competency_id=item.competency_id,
                    competency_code=item.competency_code,
                    competency_name=item.competency_name,
                    domain_name=item.domain_name,
                    current_score=item.current_score,
                    improvement_points=item.improvement_points,
                    rank=idx + 1,
                    highlight=(
                        f"Demonstrated proficiency score of {item.current_score:.1f}"
                        + (f" (+{item.improvement_points:.1f} pts growth)" if item.improvement_points > 0 else "")
                    ),
                )
            )

        # 9. Top 3 Priority Focus Areas (Using Authoritative Skill Gap Engine)
        skill_gap_service = SkillGapService(self.db)
        existing_gaps = await skill_gap_service.get_employee_gaps(employee_id)

        focus_competencies: list[CompetencyFocusItem] = []
        if existing_gaps:
            priority_rank = {
                "CRITICAL": 1,
                "HIGH": 2,
                "MEDIUM": 3,
                "LOW": 4,
                "NO_GAP": 5,
            }
            sorted_gaps = sorted(
                existing_gaps,
                key=lambda g: (
                    priority_rank.get(g.priority_level, 6),
                    -g.priority_score,
                    -g.gap_score,
                    g.competency_name,
                ),
            )
            for gap in sorted_gaps[:3]:
                focus_competencies.append(
                    CompetencyFocusItem(
                        competency_id=gap.competency_id,
                        competency_code=gap.competency_code,
                        competency_name=gap.competency_name,
                        domain_name=gap.domain_name,
                        current_score=gap.current_score,
                        target_score=gap.required_score,
                        gap_score=gap.gap_score,
                        priority_level=gap.priority_level,
                        priority_score=gap.priority_score,
                        explanation=gap.explanation or f"Priority gap of {gap.gap_score:.1f} points against role requirement.",
                    )
                )
        else:
            # Fallback if no skill gaps: competencies with status NEEDS_FOCUS or lowest scores
            needs_focus_candidates = sorted(
                competencies_detail,
                key=lambda c: (
                    0 if c.status == "NEEDS_FOCUS" else 1,
                    c.current_score,
                    c.competency_name,
                ),
            )
            for item in needs_focus_candidates[:3]:
                focus_competencies.append(
                    CompetencyFocusItem(
                        competency_id=item.competency_id,
                        competency_code=item.competency_code,
                        competency_name=item.competency_name,
                        domain_name=item.domain_name,
                        current_score=item.current_score,
                        target_score=item.target_score,
                        gap_score=max((item.target_score or 70.0) - item.current_score, 0.0),
                        priority_level="MEDIUM" if item.current_score < 50 else "LOW",
                        priority_score=50.0,
                        explanation=f"Competency score of {item.current_score:.1f} requires reinforcement.",
                    )
                )

        # 10. Modality Analytics (Real Backend Data Only)
        # Modality A: Diagnostic
        stmt_diag_attempts = (
            select(AssessmentAttempt)
            .join(Assessment)
            .where(
                AssessmentAttempt.employee_id == employee_id,
                Assessment.assessment_type == "DIAGNOSTIC",
            )
            .order_by(AssessmentAttempt.started_at.desc())
        )
        res_diag_att = await self.db.execute(stmt_diag_attempts)
        diag_attempts = list(res_diag_att.scalars().all())
        completed_diag = [a for a in diag_attempts if a.status == "COMPLETED"]
        avg_diag_score = (
            round(sum(a.percentage for a in completed_diag) / len(completed_diag), 1)
            if completed_diag
            else None
        )
        latest_diag_score = completed_diag[0].percentage if completed_diag else None
        diag_modality = DiagnosticModalitySummary(
            attempts_count=len(diag_attempts),
            completed_count=len(completed_diag),
            average_score=avg_diag_score,
            latest_score=latest_diag_score,
            status=(
                "COMPLETED"
                if completed_diag
                else ("IN_PROGRESS" if diag_attempts else "NO_DATA")
            ),
        )

        # Modality B: Quizzes
        stmt_quiz = (
            select(QuizAttempt)
            .where(QuizAttempt.employee_id == employee_id)
            .order_by(QuizAttempt.started_at.desc())
        )
        res_quiz = await self.db.execute(stmt_quiz)
        quiz_attempts = list(res_quiz.scalars().all())
        completed_quizzes = [
            q for q in quiz_attempts if q.status == "COMPLETED" and q.percentage is not None
        ]
        avg_quiz_pct = (
            round(sum(q.percentage for q in completed_quizzes) / len(completed_quizzes), 1)
            if completed_quizzes
            else None
        )
        best_quiz_pct = (
            round(max((q.percentage for q in completed_quizzes), default=0.0), 1)
            if completed_quizzes
            else None
        )
        quiz_pass_count = sum(1 for q in completed_quizzes if (q.percentage or 0) >= 70.0)
        quiz_pass_rate = (
            round((quiz_pass_count / len(completed_quizzes)) * 100, 1)
            if completed_quizzes
            else None
        )
        quiz_modality = QuizModalitySummary(
            attempts_count=len(quiz_attempts),
            completed_count=len(completed_quizzes),
            average_percentage=avg_quiz_pct,
            best_percentage=best_quiz_pct,
            pass_rate=quiz_pass_rate,
            status=(
                "COMPLETED"
                if completed_quizzes
                else ("IN_PROGRESS" if quiz_attempts else "NO_DATA")
            ),
        )

        # Modality C: Adaptive Assessment (CAT)
        stmt_adaptive = (
            select(AdaptiveAssessmentSession)
            .where(AdaptiveAssessmentSession.employee_id == employee_id)
            .order_by(AdaptiveAssessmentSession.started_at.desc())
        )
        res_adaptive = await self.db.execute(stmt_adaptive)
        adaptive_sessions = list(res_adaptive.scalars().all())
        completed_adaptive = [
            s for s in adaptive_sessions if s.status == "COMPLETED"
        ]
        avg_confidence = (
            round(
                sum(s.confidence for s in completed_adaptive) / len(completed_adaptive), 2
            )
            if completed_adaptive
            else None
        )
        adaptive_comp_count = len({s.competency_id for s in adaptive_sessions})
        adaptive_modality = AdaptiveModalitySummary(
            sessions_count=len(adaptive_sessions),
            completed_count=len(completed_adaptive),
            average_confidence=avg_confidence,
            competencies_evaluated_count=adaptive_comp_count,
            status=(
                "COMPLETED"
                if completed_adaptive
                else ("IN_PROGRESS" if adaptive_sessions else "NO_DATA")
            ),
        )

        # Modality D: Virtual Labs
        stmt_labs = (
            select(LabSession)
            .options(selectinload(LabSession.result))
            .where(LabSession.employee_id == employee_id)
            .order_by(LabSession.started_at.desc())
        )
        res_labs = await self.db.execute(stmt_labs)
        lab_sessions = list(res_labs.scalars().all())
        completed_labs = [
            s for s in lab_sessions if s.status == "COMPLETED" and s.result is not None
        ]
        avg_lab_score = (
            round(sum(s.result.percentage for s in completed_labs) / len(completed_labs), 1)
            if completed_labs
            else None
        )
        passed_labs = sum(1 for s in completed_labs if s.result.passed)
        lab_pass_rate = (
            round((passed_labs / len(completed_labs)) * 100, 1) if completed_labs else None
        )
        distinct_scenarios = len({s.scenario_id for s in completed_labs})
        lab_modality = LabModalitySummary(
            sessions_count=len(lab_sessions),
            completed_count=len(completed_labs),
            average_score=avg_lab_score,
            pass_rate=lab_pass_rate,
            completed_scenarios_count=distinct_scenarios,
            status=(
                "COMPLETED"
                if completed_labs
                else ("IN_PROGRESS" if lab_sessions else "NO_DATA")
            ),
        )

        # Modality E: Courses
        stmt_courses = (
            select(CourseProgress)
            .where(CourseProgress.employee_id == employee_id)
            .order_by(CourseProgress.enrolled_at.desc())
        )
        res_courses = await self.db.execute(stmt_courses)
        course_records = list(res_courses.scalars().all())
        completed_courses = [c for c in course_records if c.status == "COMPLETED"]
        avg_course_progress = (
            round(sum(c.progress_percentage for c in course_records) / len(course_records), 1)
            if course_records
            else None
        )
        all_completed_modules = set()
        for c in course_records:
            if c.completed_modules:
                for m in c.completed_modules:
                    all_completed_modules.add(f"{c.learning_item_id}_{m}")
        course_modality = CourseModalitySummary(
            enrolled_courses_count=len(course_records),
            completed_courses_count=len(completed_courses),
            average_progress_percentage=avg_course_progress,
            completed_modules_count=len(all_completed_modules),
            status=(
                "COMPLETED"
                if completed_courses
                else ("IN_PROGRESS" if course_records else "NO_DATA")
            ),
        )

        modalities = ModalitiesSummary(
            diagnostic=diag_modality,
            quizzes=quiz_modality,
            adaptive_assessment=adaptive_modality,
            virtual_labs=lab_modality,
            courses=course_modality,
        )

        summary_counts = PerformanceCountsSummary(
            competencies_improved=improved_count,
            competencies_declined=declined_count,
            competencies_mastered=mastered_count,
            competencies_needing_focus=needing_focus_count,
            total_competencies=len(competencies_detail),
        )

        return EmployeePerformanceResponse(
            employee_id=employee.id,
            employee_name=employee.full_name,
            job_role_id=employee.job_role_id,
            job_role_name=employee.job_role.name if employee.job_role else None,
            department_name=employee.department.name if employee.department else None,
            overall=overall_summary,
            competencies=competencies_detail,
            strongest_competencies=strongest_competencies,
            focus_competencies=focus_competencies,
            modalities=modalities,
            summary=summary_counts,
            generated_at=datetime.now(timezone.utc),
        )

    async def get_employee_timeline(
        self,
        employee_id: uuid.UUID,
        event_type: str | None = None,
        limit: int = 100,
    ) -> EmployeeTimelineResponse:
        # 1. Verify Employee Existence
        stmt_emp = select(Employee.id).where(Employee.id == employee_id)
        res_emp = await self.db.execute(stmt_emp)
        if not res_emp.scalar_one_or_none():
            raise PragyaException(
                code="EMPLOYEE_NOT_FOUND",
                message=f"Employee with ID '{employee_id}' was not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        events: list[TimelineEventItem] = []

        # 2. Diagnostic Assessments
        stmt_diag = (
            select(AssessmentAttempt)
            .options(selectinload(AssessmentAttempt.assessment))
            .where(AssessmentAttempt.employee_id == employee_id)
        )
        res_diag = await self.db.execute(stmt_diag)
        for a in res_diag.scalars().all():
            event_ts = a.completed_at or a.started_at
            if not event_ts:
                continue
            title_name = a.assessment.title if a.assessment else "Diagnostic Assessment"
            pct = a.percentage if a.percentage is not None else 0.0
            raw = a.raw_score if a.raw_score is not None else 0.0
            events.append(
                TimelineEventItem(
                    id=f"diag_{a.id}",
                    timestamp=event_ts,
                    type="DIAGNOSTIC_ASSESSMENT",
                    title=f"Diagnostic Milestone: {title_name}",
                    description=f"Completed assessment achieving {pct:.1f}% ({raw:.1f} pts).",
                    score=a.raw_score,
                    max_score=100.0,
                    percentage=a.percentage,
                    source="Diagnostic Assessment Engine",
                    status=a.status,
                )
            )

        # 3. AI Quiz Attempts
        stmt_quizzes = (
            select(QuizAttempt)
            .options(selectinload(QuizAttempt.quiz))
            .where(QuizAttempt.employee_id == employee_id)
        )
        res_quizzes = await self.db.execute(stmt_quizzes)
        for q in res_quizzes.scalars().all():
            event_ts = q.completed_at or q.started_at
            if not event_ts:
                continue
            quiz_title = q.quiz.title if q.quiz else "Competency Quiz"
            q_pct = q.percentage if q.percentage is not None else 0.0
            events.append(
                TimelineEventItem(
                    id=f"quiz_{q.id}",
                    timestamp=event_ts,
                    type="QUIZ",
                    title=f"Quiz Completion: {quiz_title}",
                    description=f"Scored {q_pct:.1f}% ({'Passed' if q_pct >= 70.0 else 'Attempted'}).",
                    score=q.score,
                    max_score=100.0,
                    percentage=q.percentage,
                    source="AI Quiz Engine",
                    status=q.status,
                )
            )

        # 4. Adaptive Assessment Sessions (CAT)
        stmt_adaptive = (
            select(AdaptiveAssessmentSession)
            .options(selectinload(AdaptiveAssessmentSession.competency))
            .where(AdaptiveAssessmentSession.employee_id == employee_id)
        )
        res_adaptive = await self.db.execute(stmt_adaptive)
        for s in res_adaptive.scalars().all():
            event_ts = s.completed_at or s.started_at
            if not event_ts:
                continue
            comp_name = s.competency.name if s.competency else "Competency"
            conf_val = round((s.confidence or 0.0) * 100, 1)
            events.append(
                TimelineEventItem(
                    id=f"cat_{s.id}",
                    timestamp=event_ts,
                    type="ADAPTIVE_ASSESSMENT",
                    title=f"CAT Session: {comp_name}",
                    description=f"Recalibrated to proficiency level '{s.current_level}' with {conf_val:.1f}% confidence.",
                    score=conf_val,
                    max_score=100.0,
                    percentage=conf_val,
                    competency_id=s.competency_id,
                    competency_name=comp_name,
                    source="Adaptive Assessment Engine",
                    status=s.status,
                    metadata={"level": s.current_level, "confidence": s.confidence},
                )
            )

        # 5. Virtual Lab Sessions
        stmt_labs = (
            select(LabSession)
            .options(
                selectinload(LabSession.scenario).selectinload(LabScenario.competency),
                selectinload(LabSession.result),
            )
            .where(LabSession.employee_id == employee_id)
        )
        res_labs = await self.db.execute(stmt_labs)
        for l in res_labs.scalars().all():
            event_ts = l.completed_at or l.started_at
            if not event_ts:
                continue
            scenario_title = l.scenario.title if l.scenario else "Lab Simulation"
            score_val = l.result.total_score if l.result else l.score
            pct_val = (l.result.percentage if l.result else l.percentage) or 0.0
            passed_bool = l.result.passed if l.result else (pct_val >= 70.0)
            events.append(
                TimelineEventItem(
                    id=f"lab_{l.id}",
                    timestamp=event_ts,
                    type="VIRTUAL_LAB",
                    title=f"Virtual Lab: {scenario_title}",
                    description=f"Simulation finished with {pct_val:.1f}% ({'Verified Passed' if passed_bool else 'Attempted'}).",
                    score=score_val,
                    max_score=100.0,
                    percentage=pct_val,
                    competency_id=l.scenario.competency_id if l.scenario else None,
                    competency_name=l.scenario.competency.name if l.scenario and l.scenario.competency else None,
                    source="Virtual Lab Simulation",
                    status="PASSED" if passed_bool else l.status,
                )
            )

        # 6. Course Activities & Module Milestones
        stmt_acts = (
            select(ModuleActivityAttempt)
            .options(selectinload(ModuleActivityAttempt.learning_item))
            .where(ModuleActivityAttempt.employee_id == employee_id)
        )
        res_acts = await self.db.execute(stmt_acts)
        for m in res_acts.scalars().all():
            event_ts = m.created_at
            if not event_ts:
                continue
            item_title = m.learning_item.title if m.learning_item else "Course"
            act_pct = m.percentage if m.percentage is not None else 0.0
            events.append(
                TimelineEventItem(
                    id=f"act_{m.id}",
                    timestamp=event_ts,
                    type="COURSE_ACTIVITY",
                    title=f"Module {m.module_id} Check: {item_title}",
                    description=f"Evaluated practical scenario check scoring {act_pct:.1f}%.",
                    score=m.score,
                    max_score=m.max_score,
                    percentage=m.percentage,
                    source="Course Progression",
                    status="PASSED" if m.passed else "ATTEMPTED",
                )
            )

        # 7. Competency Recalibrations
        stmt_recal = (
            select(CompetencyRecalibration)
            .options(selectinload(CompetencyRecalibration.competency))
            .where(CompetencyRecalibration.employee_id == employee_id)
        )
        res_recal = await self.db.execute(stmt_recal)
        for r in res_recal.scalars().all():
            event_ts = r.created_at
            if not event_ts:
                continue
            comp_name = r.competency.name if r.competency else "Competency"
            delta_prefix = "+" if (r.delta or 0.0) >= 0 else ""
            prev_val = r.previous_score if r.previous_score is not None else 0.0
            new_val = r.new_score if r.new_score is not None else 0.0
            delta_val = r.delta if r.delta is not None else 0.0
            events.append(
                TimelineEventItem(
                    id=f"recal_{r.id}",
                    timestamp=event_ts,
                    type="COMPETENCY_RECALIBRATION",
                    title=f"Recalibration: {comp_name}",
                    description=f"Recalibrated from {prev_val:.1f} to {new_val:.1f} ({delta_prefix}{delta_val:.1f} pts) - {r.reason}",
                    score=r.new_score,
                    max_score=100.0,
                    percentage=r.new_score,
                    competency_id=r.competency_id,
                    competency_name=comp_name,
                    source="Recalibration Engine",
                    status="RECALIBRATED",
                    metadata={"delta": r.delta, "confidence": r.confidence},
                )
            )

        # 8. Competency Score History
        stmt_hist = (
            select(CompetencyScoreHistory)
            .options(selectinload(CompetencyScoreHistory.competency))
            .where(CompetencyScoreHistory.employee_id == employee_id)
        )
        res_hist = await self.db.execute(stmt_hist)
        for h in res_hist.scalars().all():
            event_ts = h.created_at
            if not event_ts:
                continue
            comp_name = h.competency.name if h.competency else "Competency"
            new_val = h.new_score if h.new_score is not None else 0.0
            events.append(
                TimelineEventItem(
                    id=f"hist_{h.id}",
                    timestamp=event_ts,
                    type="SCORE_UPDATE",
                    title=f"Score Transition: {comp_name}",
                    description=f"Demonstrated level shifted to {new_val:.1f}: {h.change_reason}",
                    score=h.new_score,
                    max_score=100.0,
                    percentage=h.new_score,
                    competency_id=h.competency_id,
                    competency_name=comp_name,
                    source="Competency Architecture",
                    status="UPDATED",
                )
            )


        # Sort chronologically, newest first (timestamp DESC)
        events.sort(key=lambda e: e.timestamp, reverse=True)

        # Filter by event_type if specified
        if event_type:
            target_type = event_type.upper()
            events = [e for e in events if e.type.upper() == target_type]

        # Apply limit
        events = events[:limit]

        return EmployeeTimelineResponse(
            employee_id=employee_id,
            total_events=len(events),
            events=events,
        )
