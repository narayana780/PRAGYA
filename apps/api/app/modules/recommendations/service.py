import uuid
from typing import Any

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import PragyaException
from app.modules.assessments.models import EmployeeCompetency
from app.modules.competencies.constants import score_to_proficiency_level
from app.modules.competencies.models import Competency
from app.modules.courses.models import LearningItem
from app.modules.employees.models import Employee
from app.modules.recommendations.constants import (
    DEFAULT_RECOMMENDATION_CONFIG,
    calculate_duration_fit,
    calculate_level_fit,
    calculate_novelty_score,
    calculate_outcome_coverage,
    calculate_prerequisite_fit,
    calculate_recommendation_score,
    generate_recommendation_reason,
)
from app.modules.recommendations.matcher.keyword import KeywordSemanticMatcher
from app.modules.recommendations.models import (
    LearningPath,
    LearningPathItem,
    LearningRecommendation,
)
from app.modules.recommendations.repository import RecommendationRepository
from app.modules.recommendations.schemas import (
    LearningItemCompetencyMapping,
    LearningItemResponse,
    LearningPathItemResponse,
    LearningPathResponse,
    LearningRecommendationResponse,
    RecommendationBreakdown,
    RecommendationReasonResponse,
)
from app.modules.skill_gaps.models import SkillGap
from app.modules.training_history.models import TrainingHistory


class RecommendationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RecommendationRepository(db)
        self.matcher = KeywordSemanticMatcher()

    def _to_item_response(self, item: LearningItem) -> LearningItemResponse:
        return LearningItemResponse(
            id=item.id,
            provider=item.provider,
            provider_item_id=item.provider_item_id,
            title=item.title,
            description=item.description,
            type=item.type,
            difficulty=item.difficulty,
            level=item.level,
            duration_minutes=item.duration_minutes,
            language=item.language,
            format=item.format,
            url=item.url,
            prerequisites=item.prerequisites or [],
            is_active=item.is_active,
            source_mode=item.source_mode,
            item_metadata=item.item_metadata or {},
            competencies=[
                LearningItemCompetencyMapping(
                    competency_id=m.competency_id,
                    competency_code=m.competency.code if m.competency else None,
                    competency_name=m.competency.name if m.competency else None,
                    domain_name=m.competency.domain.name if m.competency and m.competency.domain else None,
                    coverage_level=m.coverage_level,
                    learning_outcome=m.learning_outcome,
                )
                for m in item.competency_mappings
            ],
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    def _to_rec_response(self, rec: LearningRecommendation) -> LearningRecommendationResponse:
        metadata = rec.recommendation_metadata or {}
        structured_reason = metadata.get("structured_reason", {})
        breakdown = metadata.get("priority_breakdown", {})

        return LearningRecommendationResponse(
            id=rec.id,
            employee_id=rec.employee_id,
            learning_item_id=rec.learning_item_id,
            target_competency_id=rec.target_competency_id,
            target_competency_name=rec.target_competency.name if rec.target_competency else "Competency",
            target_competency_code=rec.target_competency.code if rec.target_competency else "CODE",
            domain_name=(
                rec.target_competency.domain.name
                if rec.target_competency and rec.target_competency.domain
                else "Domain"
            ),
            learning_item=self._to_item_response(rec.learning_item),
            gap_id=rec.gap_id,
            gap_score=float(rec.gap.gap_score) if rec.gap else None,
            score=float(rec.score),
            rank=rec.rank,
            reason=rec.reason,
            structured_reason=RecommendationReasonResponse(
                summary=structured_reason.get("summary", rec.reason),
                gap_reason=structured_reason.get("gap_reason", ""),
                role_reason=structured_reason.get("role_reason", ""),
                competency_reason=structured_reason.get("competency_reason", ""),
                level_reason=structured_reason.get("level_reason", ""),
                novelty_reason=structured_reason.get("novelty_reason", ""),
            ),
            priority_breakdown=RecommendationBreakdown(
                gap_priority_component=breakdown.get("gap_priority_component", 0.0),
                semantic_match_component=breakdown.get("semantic_match_component", 0.0),
                level_fit_component=breakdown.get("level_fit_component", 0.0),
                outcome_coverage_component=breakdown.get("outcome_coverage_component", 0.0),
                prerequisite_fit_component=breakdown.get("prerequisite_fit_component", 0.0),
                duration_fit_component=breakdown.get("duration_fit_component", 0.0),
                novelty_component=breakdown.get("novelty_component", 0.0),
            ),
            matched_competencies=rec.matched_competencies or [],
            priority_level=rec.priority_level,
            status=rec.status,
            expires_at=rec.expires_at,
            generated_at=rec.generated_at,
            updated_at=rec.updated_at,
        )

    async def generate_recommendations(
        self, employee_id: uuid.UUID
    ) -> list[LearningRecommendationResponse]:
        # 1. Fetch Employee
        stmt_emp = (
            select(Employee)
            .options(
                selectinload(Employee.job_role),
                selectinload(Employee.target_role),
            )
            .where(Employee.id == employee_id)
        )
        res_emp = await self.db.execute(stmt_emp)
        employee = res_emp.scalar_one_or_none()
        if not employee:
            raise PragyaException(
                code="EMPLOYEE_NOT_FOUND",
                message=f"Employee {employee_id} not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        role_name = employee.job_role.name if employee.job_role else "Statistical Officer"

        # 2. Fetch Demonstrated Competencies
        stmt_comps = (
            select(EmployeeCompetency)
            .options(selectinload(EmployeeCompetency.competency))
            .where(EmployeeCompetency.employee_id == employee_id)
        )
        res_comps = await self.db.execute(stmt_comps)
        employee_comps = {c.competency_id: c for c in res_comps.scalars().all()}
        emp_comp_scores = {
            c.competency.code: float(c.current_score)
            for c in employee_comps.values()
            if c.competency and c.competency.code
        }

        # 3. Fetch Skill Gaps
        stmt_gaps = (
            select(SkillGap)
            .options(
                selectinload(SkillGap.competency).selectinload(Competency.domain),
                selectinload(SkillGap.current_level),
                selectinload(SkillGap.required_level),
            )
            .where(SkillGap.employee_id == employee_id)
        )
        res_gaps = await self.db.execute(stmt_gaps)
        gaps = list(res_gaps.scalars().all())

        # Filter eligible gaps (CRITICAL, HIGH, MEDIUM; exclude NO_GAP)
        eligible_gaps = [
            g for g in gaps
            if g.priority_level in DEFAULT_RECOMMENDATION_CONFIG.ELIGIBLE_PRIORITY_LEVELS and g.gap_score > 0
        ]

        if not eligible_gaps:
            # If no positive gaps exist, clear any active recommendations
            await self.repo.save_recommendations(employee_id, [])
            return []

        # 4. Fetch Training History to assess completed content
        stmt_history = select(TrainingHistory).where(TrainingHistory.employee_id == employee_id)
        res_history = await self.db.execute(stmt_history)
        history_records = list(res_history.scalars().all())
        completed_titles = {h.title.lower() for h in history_records if h.status == "COMPLETED"}
        completed_ids = {h.course_id for h in history_records if h.course_id and h.status == "COMPLETED"}

        # 5. Fetch all Active Learning Items with mappings
        learning_items, _ = await self.repo.list_learning_items(limit=500)
        if not learning_items:
            return []

        # 6. Score candidates across eligible gaps
        candidates: list[dict[str, Any]] = []

        for gap in eligible_gaps:
            comp_id = gap.competency_id
            comp_name = gap.competency.name if gap.competency else "Competency"
            comp_desc = gap.competency.short_description if gap.competency else ""
            emp_comp = employee_comps.get(comp_id)
            current_score = float(emp_comp.current_score) if emp_comp else 0.0
            emp_level, _ = (
                score_to_proficiency_level(current_score)
                if emp_comp
                else (1, "Awareness")
            )
            required_level = gap.required_level.level_number if gap.required_level else 3
            required_score = float(gap.required_score)
            gap_priority_score = float(gap.priority_score)

            for item in learning_items:
                # Check if item covers this competency directly
                mapping = next(
                    (m for m in item.competency_mappings if m.competency_id == comp_id),
                    None,
                )

                # Lexical / Semantic similarity score
                semantic_sim = self.matcher.match_competency(
                    item_title=item.title,
                    item_description=item.description,
                    competency_name=comp_name,
                    competency_description=comp_desc,
                )

                if mapping:
                    # Direct mapping: strong baseline match (85%) + semantic score (up to 15%)
                    semantic_match_score = min(85.0 + (semantic_sim * 15.0), 100.0)
                    coverage_level = mapping.coverage_level
                else:
                    # Indirect or cross-competency coverage via semantic similarity only
                    if semantic_sim < 0.35:
                        continue  # Not relevant enough
                    semantic_match_score = semantic_sim * 100.0
                    coverage_level = "WORKING"

                # Factor calculations
                level_fit = calculate_level_fit(
                    item_level=item.level,
                    emp_level=emp_level,
                    required_level=required_level,
                )

                outcome_coverage = calculate_outcome_coverage(coverage_level)

                prereq_fit = calculate_prerequisite_fit(
                    prerequisites=item.prerequisites,
                    emp_competency_scores=emp_comp_scores,
                )

                duration_fit = calculate_duration_fit(item.duration_minutes)

                is_completed = (
                    item.title.lower() in completed_titles
                    or item.provider_item_id in completed_ids
                    or str(item.id) in completed_ids
                )

                novelty = calculate_novelty_score(is_completed=is_completed)

                # Composite score
                score, breakdown = calculate_recommendation_score(
                    gap_priority_score=gap_priority_score,
                    semantic_match_score=semantic_match_score,
                    level_fit_score=level_fit,
                    outcome_coverage_score=outcome_coverage,
                    prerequisite_fit_score=prereq_fit,
                    duration_fit_score=duration_fit,
                    novelty_score=novelty,
                )

                reasons = generate_recommendation_reason(
                    competency_name=comp_name,
                    priority_level=gap.priority_level,
                    gap_score=float(gap.gap_score),
                    current_score=current_score,
                    required_score=required_score,
                    role_name=role_name,
                    item_title=item.title,
                    item_provider=item.provider,
                    coverage_level=coverage_level,
                    level_fit_score=level_fit,
                    is_completed=is_completed,
                )

                candidates.append({
                    "employee_id": employee_id,
                    "learning_item_id": item.id,
                    "target_competency_id": comp_id,
                    "gap_id": gap.id,
                    "score": score,
                    "reason": reasons["summary"],
                    "structured_reason": reasons,
                    "priority_breakdown": breakdown,
                    "matched_competencies": [
                        {
                            "competency_id": str(m.competency_id),
                            "coverage_level": m.coverage_level,
                            "competency_name": m.competency.name if m.competency else None,
                        }
                        for m in item.competency_mappings
                    ],
                    "priority_level": gap.priority_level,
                    "item_provider": item.provider,
                })

        if not candidates:
            return []

        # 7. Deduplicate: keep highest score for each learning_item
        best_per_item: dict[uuid.UUID, dict[str, Any]] = {}
        for c in candidates:
            item_id = c["learning_item_id"]
            if item_id not in best_per_item or c["score"] > best_per_item[item_id]["score"]:
                best_per_item[item_id] = c

        # 8. Sort and Rank
        ranked = sorted(best_per_item.values(), key=lambda x: x["score"], reverse=True)

        recommendations_to_persist = []
        for idx, item_data in enumerate(ranked[:15], start=1):
            rec = LearningRecommendation(
                employee_id=employee_id,
                learning_item_id=item_data["learning_item_id"],
                target_competency_id=item_data["target_competency_id"],
                gap_id=item_data["gap_id"],
                score=item_data["score"],
                rank=idx,
                reason=item_data["reason"],
                matched_competencies=item_data["matched_competencies"],
                priority_level=item_data["priority_level"],
                status="ACTIVE",
                recommendation_metadata={
                    "structured_reason": item_data["structured_reason"],
                    "priority_breakdown": item_data["priority_breakdown"],
                },
            )
            recommendations_to_persist.append(rec)

        persisted = await self.repo.save_recommendations(employee_id, recommendations_to_persist)
        return [self._to_rec_response(r) for r in persisted]

    async def get_employee_recommendations(
        self,
        employee_id: uuid.UUID,
        priority: str | None = None,
        provider: str | None = None,
        competency: str | None = None,
        item_type: str | None = None,
        language: str | None = None,
    ) -> list[LearningRecommendationResponse]:
        recs = await self.repo.list_recommendations(
            employee_id=employee_id,
            priority=priority,
            provider=provider,
            competency=competency,
            item_type=item_type,
            language=language,
        )

        # If none exist, attempt initial auto-generation
        if not recs:
            return await self.generate_recommendations(employee_id)

        return [self._to_rec_response(r) for r in recs]

    async def get_recommendation_by_id(
        self, employee_id: uuid.UUID, recommendation_id: uuid.UUID
    ) -> LearningRecommendationResponse:
        rec = await self.repo.get_recommendation_by_id(recommendation_id)
        if not rec or rec.employee_id != employee_id:
            raise PragyaException(
                code="RECOMMENDATION_NOT_FOUND",
                message=f"Recommendation {recommendation_id} not found for this employee",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return self._to_rec_response(rec)

    async def update_status(
        self, employee_id: uuid.UUID, recommendation_id: uuid.UUID, new_status: str
    ) -> LearningRecommendationResponse:
        rec = await self.repo.get_recommendation_by_id(recommendation_id)
        if not rec or rec.employee_id != employee_id:
            raise PragyaException(
                code="RECOMMENDATION_NOT_FOUND",
                message=f"Recommendation {recommendation_id} not found for this employee",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        rec.status = new_status
        await self.db.commit()
        await self.db.refresh(rec)
        return self._to_rec_response(rec)


class LearningPathService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RecommendationRepository(db)

    def _to_path_response(self, path: LearningPath) -> LearningPathResponse:
        rec_svc = RecommendationService(self.db)
        return LearningPathResponse(
            id=path.id,
            employee_id=path.employee_id,
            target_role_id=path.target_role_id,
            target_role_name=path.target_role.name if path.target_role else None,
            title=path.title,
            description=path.description,
            status=path.status,
            items=[
                LearningPathItemResponse(
                    id=it.id,
                    learning_item_id=it.learning_item_id,
                    sequence_order=it.sequence_order,
                    reason=it.reason,
                    target_competency_id=it.target_competency_id,
                    target_competency_name=it.target_competency.name if it.target_competency else None,
                    target_competency_code=it.target_competency.code if it.target_competency else None,
                    estimated_duration=it.estimated_duration,
                    status=it.status,
                    learning_item=rec_svc._to_item_response(it.learning_item),
                )
                for it in path.items
            ],
            generated_at=path.generated_at,
            updated_at=path.updated_at,
        )

    async def generate_learning_path(self, employee_id: uuid.UUID) -> LearningPathResponse:
        # Fetch Employee
        stmt_emp = select(Employee).options(selectinload(Employee.job_role), selectinload(Employee.target_role)).where(Employee.id == employee_id)
        res_emp = await self.db.execute(stmt_emp)
        employee = res_emp.scalar_one_or_none()
        if not employee:
            raise PragyaException(
                code="EMPLOYEE_NOT_FOUND",
                message=f"Employee {employee_id} not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Ensure recommendations exist
        rec_svc = RecommendationService(self.db)
        recs = await rec_svc.get_employee_recommendations(employee_id)
        if not recs:
            recs = await rec_svc.generate_recommendations(employee_id)

        # Structure progression: Foundation -> Interactive Lab -> Working / Program -> Advanced
        role_title = employee.job_role.name if employee.job_role else "Statistical Cadre"
        target_role_name = employee.target_role.name if employee.target_role else "Senior Statistical Officer"

        path = LearningPath(
            employee_id=employee_id,
            target_role_id=employee.target_role_id,
            title=f"Cadre Advancement Pathway: {role_title} to {target_role_name}",
            description=(
                f"Curated progressive learning pathway for {employee.full_name} addressing priority "
                "skill gaps through foundational modules, PRAGYA interactive labs, and advanced official survey programmes."
            ),
            status="IN_PROGRESS",
        )

        # Select items balancing provider mix and progression steps
        items_to_add: list[LearningPathItem] = []
        seen_items = set()

        # Step 1: Foundational digital course for highest priority gap
        top_rec = recs[0] if recs else None
        if top_rec and top_rec.learning_item.id not in seen_items:
            items_to_add.append(
                LearningPathItem(
                    learning_item_id=top_rec.learning_item.id,
                    sequence_order=1,
                    reason=f"Step 1 (Foundation): Establish core concepts in {top_rec.target_competency_name}.",
                    target_competency_id=top_rec.target_competency_id,
                    estimated_duration=top_rec.learning_item.duration_minutes,
                    status="NOT_STARTED",
                )
            )
            seen_items.add(top_rec.learning_item.id)

        # Step 2: PRAGYA Practice Lab
        pragya_rec = next((r for r in recs if r.learning_item.provider == "PRAGYA" and r.learning_item.id not in seen_items), None)
        if pragya_rec:
            items_to_add.append(
                LearningPathItem(
                    learning_item_id=pragya_rec.learning_item.id,
                    sequence_order=len(items_to_add) + 1,
                    reason="Step 2 (Practice Lab): Hands-on practical application in PRAGYA simulation environment.",
                    target_competency_id=pragya_rec.target_competency_id,
                    estimated_duration=pragya_rec.learning_item.duration_minutes,
                    status="NOT_STARTED",
                )
            )
            seen_items.add(pragya_rec.learning_item.id)

        # Step 3: Working / Intermediate digital course from iGOT
        igot_rec = next((r for r in recs if r.learning_item.provider == "IGOT" and r.learning_item.id not in seen_items), None)
        if igot_rec:
            items_to_add.append(
                LearningPathItem(
                    learning_item_id=igot_rec.learning_item.id,
                    sequence_order=len(items_to_add) + 1,
                    reason="Step 3 (Applied Methods): In-depth working competency development via iGOT Karmayogi.",
                    target_competency_id=igot_rec.target_competency_id,
                    estimated_duration=igot_rec.learning_item.duration_minutes,
                    status="NOT_STARTED",
                )
            )
            seen_items.add(igot_rec.learning_item.id)

        # Step 4: Advanced instructor-led programme from NSSTA / TPAC
        nssta_rec = next((r for r in recs if r.learning_item.provider == "NSSTA_TPAC" and r.learning_item.id not in seen_items), None)
        if nssta_rec:
            items_to_add.append(
                LearningPathItem(
                    learning_item_id=nssta_rec.learning_item.id,
                    sequence_order=len(items_to_add) + 1,
                    reason="Step 4 (Executive Certification): Advanced institutional training at NSSTA/TPAC.",
                    target_competency_id=nssta_rec.target_competency_id,
                    estimated_duration=nssta_rec.learning_item.duration_minutes,
                    status="NOT_STARTED",
                )
            )
            seen_items.add(nssta_rec.learning_item.id)

        # Attach items to path
        path.items = items_to_add
        saved = await self.repo.save_learning_path(path)
        return self._to_path_response(saved)

    async def get_learning_path(self, employee_id: uuid.UUID) -> LearningPathResponse | None:
        path = await self.repo.get_learning_path(employee_id)
        if not path:
            # Auto-generate first pathway if absent
            return await self.generate_learning_path(employee_id)
        return self._to_path_response(path)
