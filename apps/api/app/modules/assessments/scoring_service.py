import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.assessments.constants import (
    calculate_confidence_score,
    normalize_experience,
    normalize_self_assessment,
    renormalize_weights,
)
from app.modules.assessments.models import EmployeeCompetency
from app.modules.assessments.repository import AssessmentRepository


class CompetencyScoringService:
    @staticmethod
    def normalize_experience(years: float) -> float:
        return normalize_experience(years)

    @staticmethod
    def normalize_self_assessment(level: int) -> float:
        return normalize_self_assessment(level)

    @staticmethod
    def renormalize_weights(available_types: list[str]) -> dict[str, float]:
        return renormalize_weights(available_types)

    @staticmethod
    def calculate_confidence(
        evidence_count: int,
        available_types: list[str],
        scores: list[float] | None = None,
    ):
        return calculate_confidence_score(evidence_count, available_types, scores)

    @staticmethod
    async def calculate_competency(
        employee_id: uuid.UUID,
        competency_id: uuid.UUID,
        db: AsyncSession,
        change_reason: str = "Evidence recalculation",
        trigger_evidence_id: uuid.UUID | None = None,
    ) -> EmployeeCompetency | None:
        """Collect all evidence for (employee_id, competency_id), renormalize available weights,
        compute continuous 0-100 score and confidence, and audit in score history.
        """
        all_evidence = await AssessmentRepository.get_employee_competency_evidence(
            employee_id, competency_id, db
        )
        if not all_evidence:
            return None

        # Group by evidence type, taking the most recent record for each type
        latest_by_type: dict[str, Any] = {}
        for ev in all_evidence:
            if ev.evidence_type not in latest_by_type:
                latest_by_type[ev.evidence_type] = ev

        available_types = list(latest_by_type.keys())
        reweighted = renormalize_weights(available_types)

        # Calculate weighted score & update contribution on active evidence
        total_score = 0.0
        scores: list[float] = []
        for ev_type, ev in latest_by_type.items():
            weight = reweighted.get(ev_type, 0.0)
            contrib = round(ev.normalized_score * weight, 2)
            ev.weight_used = round(weight, 4)
            ev.contribution = contrib
            total_score += contrib
            scores.append(ev.normalized_score)

        final_score = round(min(100.0, max(0.0, total_score)), 1)
        conf_score, conf_label = calculate_confidence_score(
            len(all_evidence), available_types, scores
        )

        # Check previous state for audit log
        existing = await AssessmentRepository.get_employee_competency(
            employee_id, competency_id, db
        )
        prev_score = existing.current_score if existing else None
        prev_conf = existing.confidence if existing else None

        # Upsert employee competency record
        record = await AssessmentRepository.upsert_employee_competency(
            employee_id=employee_id,
            competency_id=competency_id,
            current_score=final_score,
            confidence=conf_score,
            confidence_label=conf_label.value,
            evidence_count=len(all_evidence),
            db=db,
        )

        # Audit transition in score history if changed or newly created
        if prev_score is None or prev_score != final_score or prev_conf != conf_score:
            await AssessmentRepository.record_score_history(
                employee_id=employee_id,
                competency_id=competency_id,
                previous_score=prev_score,
                new_score=final_score,
                previous_confidence=prev_conf,
                new_confidence=conf_score,
                change_reason=change_reason,
                trigger_evidence_id=trigger_evidence_id,
                db=db,
            )

        # Trigger downstream skill gap recalculation
        try:
            from sqlalchemy.exc import SQLAlchemyError

            from app.core.exceptions import PragyaException
            from app.modules.skill_gaps.service import SkillGapService

            gap_service = SkillGapService(db)
            await gap_service.recalculate_gap(employee_id, competency_id)
        except (SQLAlchemyError, PragyaException) as exc:
            import logging
            logging.getLogger(__name__).warning("Failed to recalculate skill gap for %s: %s", employee_id, exc)

        return record

    @staticmethod
    async def calculate_all_employee_competencies(
        employee_id: uuid.UUID,
        db: AsyncSession,
    ) -> list[EmployeeCompetency]:
        """Recalculate all competencies for which employee has evidence."""
        all_ev = await AssessmentRepository.get_all_employee_evidence(employee_id, db)
        comp_ids = {ev.competency_id for ev in all_ev}
        results = []
        for cid in comp_ids:
            res = await CompetencyScoringService.calculate_competency(
                employee_id, cid, db, change_reason="Batch evidence recalibration"
            )
            if res:
                results.append(res)
        return results
