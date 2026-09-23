import math
import uuid
from collections import defaultdict
from datetime import datetime
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.analytics.training_effectiveness_schemas import (
    CompetencyImprovementSummary,
    CourseEffectivenessItem,
    CourseEffectivenessResponse,
    EmployeeCourseEffectivenessItem,
    EmployeeTrainingEffectivenessResponse,
    OverallTrainingEffectivenessResponse,
    RecommendationEffectivenessResponse,
    RecommendationOutcomesSummary,
)
from app.modules.assessments.models import (
    CompetencyEvidence,
    CompetencyScoreHistory,
    EmployeeCompetency,
)
from app.modules.competencies.models import Competency, CompetencyDomain
from app.modules.courses.models import (
    CourseProgress,
    LearningItem,
    LearningItemCompetency,
)
from app.modules.employees.models import Employee
from app.modules.recommendations.models import LearningRecommendation


class TrainingEffectivenessService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # -------------------------------------------------------------------------
    # 15.3 & 15.4: BASELINE & POST-TRAINING SCORE RESOLUTION
    # -------------------------------------------------------------------------

    async def _resolve_learner_pre_score(
        self,
        employee_id: uuid.UUID,
        competency_id: uuid.UUID,
        reference_time: datetime,
        completion_time: datetime | None = None,
    ) -> float | None:
        """
        Identifies the employee's authoritative competency score before training.
        Uses historical score history <= reference_time (enrollment).
        If none, falls back to score history prior to completion_time or earliest evidence.
        Returns None (NO_BASELINE) if no record exists. Never fabricates a score.
        """
        # 1. Latest score before or at enrollment
        stmt = (
            select(CompetencyScoreHistory.new_score)
            .where(
                CompetencyScoreHistory.employee_id == employee_id,
                CompetencyScoreHistory.competency_id == competency_id,
                CompetencyScoreHistory.created_at <= reference_time,
            )
            .order_by(desc(CompetencyScoreHistory.created_at))
            .limit(1)
        )
        res = await self.db.execute(stmt)
        score = res.scalar_one_or_none()
        if score is not None:
            return round(float(score), 2)

        # 2. If completion time exists and enrollment was coincident, check before completion
        if completion_time is not None:
            stmt_comp = (
                select(CompetencyScoreHistory.previous_score)
                .where(
                    CompetencyScoreHistory.employee_id == employee_id,
                    CompetencyScoreHistory.competency_id == competency_id,
                    CompetencyScoreHistory.created_at >= completion_time,
                )
                .order_by(CompetencyScoreHistory.created_at.asc())
                .limit(1)
            )
            res_comp = await self.db.execute(stmt_comp)
            prev = res_comp.scalar_one_or_none()
            if prev is not None:
                return round(float(prev), 2)

        # 3. Check CompetencyEvidence prior to reference time
        stmt_ev = (
            select(CompetencyEvidence.normalized_score)
            .where(
                CompetencyEvidence.employee_id == employee_id,
                CompetencyEvidence.competency_id == competency_id,
                CompetencyEvidence.recorded_at <= reference_time,
            )
            .order_by(desc(CompetencyEvidence.recorded_at))
            .limit(1)
        )
        res_ev = await self.db.execute(stmt_ev)
        ev_score = res_ev.scalar_one_or_none()
        if ev_score is not None:
            return round(float(ev_score), 2)

        return None

    async def _resolve_learner_post_score(
        self,
        employee_id: uuid.UUID,
        competency_id: uuid.UUID,
        completion_time: datetime | None,
    ) -> float | None:
        """
        Identifies the employee's competency state after training.
        Post-training evidence/score must occur on or after the completion event.
        Returns None (NO_POST_DATA) if training not completed or no subsequent evidence.
        """
        if completion_time is None:
            return None

        # 1. Latest score history on or after completion
        stmt = (
            select(CompetencyScoreHistory.new_score)
            .where(
                CompetencyScoreHistory.employee_id == employee_id,
                CompetencyScoreHistory.competency_id == competency_id,
                CompetencyScoreHistory.created_at >= completion_time,
            )
            .order_by(desc(CompetencyScoreHistory.created_at))
            .limit(1)
        )
        res = await self.db.execute(stmt)
        score = res.scalar_one_or_none()
        if score is not None:
            return round(float(score), 2)

        # 2. Check EmployeeCompetency current score if updated_at >= completion_time
        stmt_curr = select(EmployeeCompetency).where(
            EmployeeCompetency.employee_id == employee_id,
            EmployeeCompetency.competency_id == competency_id,
        )
        res_curr = await self.db.execute(stmt_curr)
        emp_comp = res_curr.scalar_one_or_none()
        if emp_comp is not None and emp_comp.updated_at is not None:
            if emp_comp.updated_at >= completion_time:
                return round(float(emp_comp.current_score), 2)

        return None

    # -------------------------------------------------------------------------
    # 15.6 & 15.7: COURSE EFFECTIVENESS
    # -------------------------------------------------------------------------

    async def get_course_effectiveness(self) -> CourseEffectivenessResponse:
        """
        Calculates empirical course effectiveness benchmarks across all learning items.
        """
        # Load all learning items with competency mappings
        stmt_courses = (
            select(LearningItem)
            .options(
                selectinload(LearningItem.competency_mappings).selectinload(
                    LearningItemCompetency.competency
                )
            )
            .order_by(LearningItem.title.asc())
        )
        res_courses = await self.db.execute(stmt_courses)
        courses = list(res_courses.scalars().all())

        # Load all course progress records
        stmt_progress = (
            select(CourseProgress)
            .order_by(CourseProgress.enrolled_at.asc())
        )
        res_progress = await self.db.execute(stmt_progress)
        all_progress = list(res_progress.scalars().all())

        # Group progress by course_id
        progress_by_course: dict[uuid.UUID, list[CourseProgress]] = defaultdict(list)
        for p in all_progress:
            progress_by_course[p.learning_item_id].append(p)

        items: list[CourseEffectivenessItem] = []

        for course in courses:
            progs = progress_by_course.get(course.id, [])
            enrolled = len(progs)
            completed = sum(1 for p in progs if p.status == "COMPLETED")
            comp_rate = round((completed / enrolled * 100.0), 1) if enrolled > 0 else 0.0

            # Target competencies
            target_comps = [
                m.competency for m in course.competency_mappings if m.competency is not None
            ]
            comp_names = [c.name for c in target_comps]

            # Calculate duration hours
            duration_hours: float | None = None
            if course.duration_minutes and course.duration_minutes > 0:
                duration_hours = round(course.duration_minutes / 60.0, 1)

            # Analyze measurable learners
            pre_scores: list[float] = []
            post_scores: list[float] = []
            improvements: list[float] = []

            for p in progs:
                if p.status != "COMPLETED" or not target_comps:
                    continue

                # Evaluate over the course's target competencies
                learner_pre_list = []
                learner_post_list = []

                for comp in target_comps:
                    pre = await self._resolve_learner_pre_score(
                        p.employee_id, comp.id, p.enrolled_at, p.completed_at
                    )
                    post = await self._resolve_learner_post_score(
                        p.employee_id, comp.id, p.completed_at
                    )
                    if pre is not None and post is not None:
                        learner_pre_list.append(pre)
                        learner_post_list.append(post)

                if learner_pre_list and learner_post_list:
                    avg_p_pre = sum(learner_pre_list) / len(learner_pre_list)
                    avg_p_post = sum(learner_post_list) / len(learner_post_list)
                    pre_scores.append(avg_p_pre)
                    post_scores.append(avg_p_post)
                    improvements.append(avg_p_post - avg_p_pre)

            measurable_count = len(improvements)

            if measurable_count > 0:
                avg_pre = round(sum(pre_scores) / measurable_count, 2)
                avg_post = round(sum(post_scores) / measurable_count, 2)
                avg_imp = round(sum(improvements) / measurable_count, 2)

                if avg_pre > 0:
                    imp_pct = round(((avg_post - avg_pre) / avg_pre) * 100.0, 2)
                else:
                    imp_pct = 100.0 if avg_post > 0 else 0.0

                # 15.7 Effectiveness index: average improvement / duration hours
                eff_index: float | None = None
                if duration_hours is not None and duration_hours > 0:
                    eff_index = round(avg_imp / duration_hours, 2)

                if avg_imp >= 15.0:
                    eff_status = "HIGH_EFFECTIVENESS"
                elif avg_imp >= 5.0:
                    eff_status = "MODERATE_EFFECTIVENESS"
                else:
                    eff_status = "LOW_EFFECTIVENESS"
            else:
                avg_pre = None
                avg_post = None
                avg_imp = None
                imp_pct = None
                eff_index = None
                eff_status = "NO_DATA" if enrolled == 0 else "INSUFFICIENT_DATA"

            items.append(
                CourseEffectivenessItem(
                    course_id=course.id,
                    course_code=course.provider_item_id,
                    title=course.title,
                    provider=course.provider,
                    duration_hours=duration_hours,
                    enrolled_count=enrolled,
                    completed_count=completed,
                    completion_rate=comp_rate,
                    measurable_learners=measurable_count,
                    average_pre_score=avg_pre,
                    average_post_score=avg_post,
                    average_improvement=avg_imp,
                    improvement_percentage=imp_pct,
                    effectiveness_index=eff_index,
                    effectiveness_status=eff_status,
                    competencies_affected=comp_names,
                )
            )

        # Sort deterministically: highest improvement first, then completed count, then title
        items.sort(
            key=lambda x: (
                x.average_improvement if x.average_improvement is not None else -999.0,
                x.completed_count,
                x.title,
            ),
            reverse=True,
        )

        return CourseEffectivenessResponse(courses=items, total_courses=len(items))

    # -------------------------------------------------------------------------
    # 15.8: RECOMMENDATION ANALYTICS
    # -------------------------------------------------------------------------

    async def get_recommendation_effectiveness(self) -> RecommendationEffectivenessResponse:
        """
        Analyzes the full recommendation outcome lifecycle without modifying ranking logic.
        """
        stmt = (
            select(LearningRecommendation)
            .options(
                selectinload(LearningRecommendation.learning_item),
                selectinload(LearningRecommendation.target_competency),
            )
            .order_by(LearningRecommendation.generated_at.desc())
        )
        res = await self.db.execute(stmt)
        recs = list(res.scalars().all())

        issued = len(recs)
        started = sum(1 for r in recs if r.status in ("STARTED", "COMPLETED"))
        completed = sum(1 for r in recs if r.status == "COMPLETED")

        by_priority: dict[str, int] = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
        }
        for r in recs:
            p = r.priority_level or "MEDIUM"
            by_priority[p] = by_priority.get(p, 0) + 1

        # Analyze measurable recommendations
        measurable_count = 0
        improved_count = 0
        improvement_points: list[float] = []

        for r in recs:
            if r.status != "COMPLETED":
                continue

            pre = await self._resolve_learner_pre_score(
                r.employee_id,
                r.target_competency_id,
                r.generated_at,
                r.updated_at,
            )
            post = await self._resolve_learner_post_score(
                r.employee_id,
                r.target_competency_id,
                r.updated_at,
            )

            if pre is not None and post is not None:
                measurable_count += 1
                diff = post - pre
                improvement_points.append(diff)
                if diff > 0:
                    improved_count += 1

        start_rate = round((started / issued * 100.0), 1) if issued > 0 else 0.0
        comp_rate = round((completed / started * 100.0), 1) if started > 0 else 0.0
        imp_rate = round((improved_count / completed * 100.0), 1) if completed > 0 else 0.0
        avg_imp = (
            round(sum(improvement_points) / len(improvement_points), 2)
            if improvement_points
            else None
        )

        summary = RecommendationOutcomesSummary(
            recommendations_issued=issued,
            recommendations_started=started,
            recommendations_completed=completed,
            measurable_recommendations=measurable_count,
            recommendations_with_improvement=improved_count,
            start_rate=start_rate,
            completion_rate=comp_rate,
            improvement_rate=imp_rate,
            average_observed_improvement=avg_imp,
            by_priority=by_priority,
        )

        return RecommendationEffectivenessResponse(summary=summary)

    # -------------------------------------------------------------------------
    # 15.9: OVERALL TRAINING EFFECTIVENESS
    # -------------------------------------------------------------------------

    async def get_overall_effectiveness(self) -> OverallTrainingEffectivenessResponse:
        """
        Global training effectiveness overview integrating course progress,
        competency score delta tracking, and recommendation outcomes.
        """
        # Enrollments and learners
        res_learners = await self.db.execute(
            select(func.count(func.distinct(CourseProgress.employee_id)))
        )
        total_learners = res_learners.scalar() or 0

        res_prog = await self.db.execute(
            select(
                func.count(CourseProgress.id).label("total"),
                func.count(func.nullif(CourseProgress.status != "COMPLETED", True)).label(
                    "completed"
                ),
            )
        )
        row_prog = res_prog.one()
        total_enrollments = row_prog.total or 0
        completed_enrollments = row_prog.completed or 0
        comp_rate = (
            round((completed_enrollments / total_enrollments * 100.0), 1)
            if total_enrollments > 0
            else 0.0
        )

        # Courses and recommendation effectiveness
        course_res = await self.get_course_effectiveness()
        rec_res = await self.get_recommendation_effectiveness()

        # Measurable interventions across courses
        total_measurable = sum(c.measurable_learners for c in course_res.courses)
        courses_with_imp = [
            c for c in course_res.courses if c.average_improvement is not None
        ]
        effective_interventions = sum(
            c.measurable_learners for c in courses_with_imp if (c.average_improvement or 0) > 0
        )

        all_improvements = [
            c.average_improvement
            for c in courses_with_imp
            if c.average_improvement is not None
        ]
        all_pcts = [
            c.improvement_percentage
            for c in courses_with_imp
            if c.improvement_percentage is not None
        ]

        avg_imp = (
            round(sum(all_improvements) / len(all_improvements), 2)
            if all_improvements
            else None
        )
        avg_pct = (
            round(sum(all_pcts) / len(all_pcts), 2)
            if all_pcts
            else None
        )

        # Competency improvements breakdown
        stmt_comps = (
            select(Competency)
            .options(selectinload(Competency.domain))
            .where(Competency.is_active.is_(True))
            .order_by(Competency.name.asc())
        )
        res_comps = await self.db.execute(stmt_comps)
        competencies = list(res_comps.scalars().all())

        # Find all completed course progress items and check associated competencies
        stmt_completed_progs = (
            select(CourseProgress)
            .options(
                selectinload(CourseProgress.learning_item)
                .selectinload(LearningItem.competency_mappings)
                .selectinload(LearningItemCompetency.competency)
            )
            .where(CourseProgress.status == "COMPLETED")
        )
        res_cp = await self.db.execute(stmt_completed_progs)
        completed_progs = list(res_cp.scalars().all())

        comp_learner_deltas: dict[uuid.UUID, list[tuple[float, float]]] = defaultdict(list)

        for cp in completed_progs:
            if not cp.learning_item or not cp.learning_item.competency_mappings:
                continue
            for mapping in cp.learning_item.competency_mappings:
                cid = mapping.competency_id
                pre = await self._resolve_learner_pre_score(
                    cp.employee_id, cid, cp.enrolled_at, cp.completed_at
                )
                post = await self._resolve_learner_post_score(
                    cp.employee_id, cid, cp.completed_at
                )
                if pre is not None and post is not None:
                    comp_learner_deltas[cid].append((pre, post))

        comp_summaries: list[CompetencyImprovementSummary] = []
        competencies_improved_count = 0

        for comp in competencies:
            deltas = comp_learner_deltas.get(comp.id, [])
            measurable_learners = len(deltas)
            if measurable_learners > 0:
                pre_avg = round(sum(d[0] for d in deltas) / measurable_learners, 2)
                post_avg = round(sum(d[1] for d in deltas) / measurable_learners, 2)
                imp_avg = round(post_avg - pre_avg, 2)
                pct_avg = (
                    round(((post_avg - pre_avg) / pre_avg) * 100.0, 2)
                    if pre_avg > 0
                    else (100.0 if post_avg > 0 else 0.0)
                )
                if imp_avg > 0:
                    competencies_improved_count += 1
            else:
                pre_avg = None
                post_avg = None
                imp_avg = None
                pct_avg = None

            comp_summaries.append(
                CompetencyImprovementSummary(
                    competency_id=comp.id,
                    competency_code=comp.code,
                    competency_name=comp.name,
                    domain_name=comp.domain.name if comp.domain else "Statistical Framework",
                    measurable_learners=measurable_learners,
                    average_pre_score=pre_avg,
                    average_post_score=post_avg,
                    average_improvement=imp_avg,
                    improvement_percentage=pct_avg,
                )
            )

        # Sort competency summaries deterministically by observed improvement desc
        comp_summaries.sort(
            key=lambda x: (
                x.average_improvement if x.average_improvement is not None else -999.0,
                x.measurable_learners,
                x.competency_name,
            ),
            reverse=True,
        )

        top_courses = [c for c in course_res.courses if c.average_improvement is not None][:5]

        return OverallTrainingEffectivenessResponse(
            total_learners=total_learners,
            total_enrollments=total_enrollments,
            completed_enrollments=completed_enrollments,
            completion_rate=comp_rate,
            measurable_interventions=total_measurable,
            effective_interventions=effective_interventions,
            average_observed_improvement=avg_imp,
            average_improvement_percentage=avg_pct,
            competencies_improved_count=competencies_improved_count,
            competency_improvements=comp_summaries,
            top_effective_courses=top_courses,
            recommendation_summary=rec_res.summary,
        )

    # -------------------------------------------------------------------------
    # 15.9: EMPLOYEE DRILL-DOWN EFFECTIVENESS
    # -------------------------------------------------------------------------

    async def get_employee_training_effectiveness(
        self, employee_id: uuid.UUID
    ) -> EmployeeTrainingEffectivenessResponse:
        """
        Administrator drill-down for one employee's training outcomes.
        """
        # Load employee
        stmt_emp = select(Employee).where(Employee.id == employee_id)
        res_emp = await self.db.execute(stmt_emp)
        emp = res_emp.scalar_one_or_none()
        if not emp:
            raise ValueError(f"Employee {employee_id} not found")

        # Load course progress
        stmt_prog = (
            select(CourseProgress)
            .options(
                selectinload(CourseProgress.learning_item)
                .selectinload(LearningItem.competency_mappings)
                .selectinload(LearningItemCompetency.competency)
            )
            .where(CourseProgress.employee_id == employee_id)
            .order_by(CourseProgress.enrolled_at.desc())
        )
        res_prog = await self.db.execute(stmt_prog)
        progs = list(res_prog.scalars().all())

        items: list[EmployeeCourseEffectivenessItem] = []
        improvements: list[float] = []

        for p in progs:
            if not p.learning_item:
                continue

            target_comps = [
                m.competency
                for m in p.learning_item.competency_mappings
                if m.competency is not None
            ]

            if not target_comps:
                items.append(
                    EmployeeCourseEffectivenessItem(
                        course_id=p.learning_item_id,
                        course_title=p.learning_item.title,
                        status=p.status,
                        enrolled_at=p.enrolled_at,
                        completed_at=p.completed_at,
                        competency_name="Unspecified",
                        pre_training_score=None,
                        post_training_score=None,
                        improvement_points=None,
                        improvement_percentage=None,
                        status_label="NO_DATA",
                    )
                )
                continue

            for comp in target_comps:
                pre = await self._resolve_learner_pre_score(
                    p.employee_id, comp.id, p.enrolled_at, p.completed_at
                )
                post = await self._resolve_learner_post_score(
                    p.employee_id, comp.id, p.completed_at
                )

                if pre is None:
                    label = "NO_BASELINE"
                    diff = None
                    pct = None
                elif post is None:
                    label = "NO_POST_DATA"
                    diff = None
                    pct = None
                else:
                    diff = round(post - pre, 2)
                    if pre > 0:
                        pct = round(((post - pre) / pre) * 100.0, 2)
                    else:
                        pct = 100.0 if post > 0 else 0.0
                    improvements.append(diff)

                    if diff > 0:
                        label = "OBSERVED_IMPROVEMENT"
                    elif diff == 0:
                        label = "NO_CHANGE"
                    else:
                        label = "DECLINE"

                items.append(
                    EmployeeCourseEffectivenessItem(
                        course_id=p.learning_item_id,
                        course_title=p.learning_item.title,
                        status=p.status,
                        enrolled_at=p.enrolled_at,
                        completed_at=p.completed_at,
                        competency_name=comp.name,
                        pre_training_score=pre,
                        post_training_score=post,
                        improvement_points=diff,
                        improvement_percentage=pct,
                        status_label=label,
                    )
                )

        avg_imp = (
            round(sum(improvements) / len(improvements), 2)
            if improvements
            else None
        )

        return EmployeeTrainingEffectivenessResponse(
            employee_id=emp.id,
            employee_code=emp.employee_code,
            full_name=emp.full_name,
            designation=emp.designation,
            interventions=items,
            total_interventions=len(items),
            average_observed_improvement=avg_imp,
        )
