import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.adaptive.constants import MAX_RECALIBRATION_DELTA
from app.modules.adaptive.models import CompetencyRecalibration
from app.modules.assessments.constants import DEFAULT_EVIDENCE_WEIGHTS, renormalize_weights
from app.modules.assessments.models import CompetencyEvidence, EmployeeCompetency
from app.modules.assessments.repository import AssessmentRepository
from app.modules.competencies.models import Competency
from app.modules.skill_gaps.models import SkillGap
from app.modules.skill_gaps.service import SkillGapService


class CompetencyRecalibrationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def recalibrate_competency(
        self,
        employee_id: uuid.UUID,
        competency_id: uuid.UUID,
        session_id: uuid.UUID,
        assessment_score: float,
        confidence: float,
        question_count: int,
        metadata_dict: dict[str, Any] | None = None,
    ) -> tuple[CompetencyRecalibration, SkillGap | None]:
        """
        Executes closed-loop competency recalibration:
        1. Records ADAPTIVE_ASSESSMENT evidence without overwriting prior evidence.
        2. Aggregates all available evidence using renormalized deterministic weights.
        3. Applies anti-oscillation protection (clamping delta to MAX_RECALIBRATION_DELTA).
        4. Bounds final score in [0.0, 100.0].
        5. Writes immutable audit record to competency_recalibrations.
        6. Updates employee_competencies.
        7. Triggers Stage 6 SkillGapService.recalculate_gap().
        """
        # Fetch existing competency record
        existing = await AssessmentRepository.get_employee_competency(
            employee_id, competency_id, self.db
        )
        previous_score = existing.current_score if existing else 0.0
        previous_conf = existing.confidence if existing else 0.50

        # 1. Create ADAPTIVE_ASSESSMENT evidence
        meta = {
            "session_id": str(session_id),
            "question_count": question_count,
            "assessment_type": "ADAPTIVE_ASSESSMENT",
            **(metadata_dict or {}),
        }
        evidence = CompetencyEvidence(
            id=uuid.uuid4(),
            employee_id=employee_id,
            competency_id=competency_id,
            evidence_type="ADAPTIVE_ASSESSMENT",
            source_id=str(session_id),
            raw_value=float(assessment_score),
            normalized_score=float(assessment_score),
            weight_used=1.0,
            contribution=0.0,
            confidence=confidence,
            metadata_json=meta,
        )
        self.db.add(evidence)
        await self.db.flush()

        # 2. Collect all evidence and aggregate latest by type
        all_evidence = await AssessmentRepository.get_employee_competency_evidence(
            employee_id, competency_id, self.db
        )
        latest_by_type: dict[str, CompetencyEvidence] = {}
        for ev in all_evidence:
            if ev.evidence_type not in latest_by_type:
                latest_by_type[ev.evidence_type] = ev

        available_types = list(latest_by_type.keys())
        reweighted = renormalize_weights(available_types, custom_weights=DEFAULT_EVIDENCE_WEIGHTS)

        raw_weighted_score = 0.0
        for ev_type, ev in latest_by_type.items():
            w = reweighted.get(ev_type, 0.0)
            contrib = round(ev.normalized_score * w, 2)
            ev.weight_used = round(w, 4)
            ev.contribution = contrib
            raw_weighted_score += contrib

        raw_weighted_score = round(raw_weighted_score, 1)

        # 3. Anti-oscillation max delta protection
        raw_delta = raw_weighted_score - previous_score
        if abs(raw_delta) > MAX_RECALIBRATION_DELTA:
            clamped_delta = MAX_RECALIBRATION_DELTA if raw_delta > 0 else -MAX_RECALIBRATION_DELTA
        else:
            clamped_delta = raw_delta

        # 4. Bounded score
        final_score = round(min(100.0, max(0.0, previous_score + clamped_delta)), 1)
        actual_delta = round(final_score - previous_score, 1)

        # Combined confidence
        recalibrated_conf = round(min(1.0, max(previous_conf, confidence)), 2)

        # 5. Create audit record in competency_recalibrations
        reason = (
            f"Adaptive assessment recalibration: assessment score={assessment_score:.1f}, "
            f"raw delta={raw_delta:+.1f} pts, applied delta={actual_delta:+.1f} pts "
            f"(max delta limit={MAX_RECALIBRATION_DELTA:.0f} pts)"
        )
        recalibration_record = CompetencyRecalibration(
            id=uuid.uuid4(),
            employee_id=employee_id,
            competency_id=competency_id,
            previous_score=previous_score,
            new_score=final_score,
            delta=actual_delta,
            confidence=recalibrated_conf,
            reason=reason,
            evidence_ids=[str(e.id) for e in latest_by_type.values()],
        )
        self.db.add(recalibration_record)

        # 6. Update employee_competencies
        await AssessmentRepository.upsert_employee_competency(
            employee_id=employee_id,
            competency_id=competency_id,
            current_score=final_score,
            confidence=recalibrated_conf,
            confidence_label="HIGH" if recalibrated_conf >= 0.70 else "MEDIUM",
            evidence_count=len(all_evidence),
            db=self.db,
        )

        # Also log canonical score history
        await AssessmentRepository.record_score_history(
            employee_id=employee_id,
            competency_id=competency_id,
            previous_score=previous_score,
            new_score=final_score,
            previous_confidence=previous_conf,
            new_confidence=recalibrated_conf,
            change_reason=reason,
            trigger_evidence_id=evidence.id,
            db=self.db,
        )

        # 7. Trigger Stage 6 SkillGapService.recalculate_gap
        updated_gap: SkillGap | None = None
        try:
            gap_service = SkillGapService(self.db)
            updated_gap = await gap_service.recalculate_gap(employee_id, competency_id)
        except Exception:
            # If no target role exists or calculation fails, allow graceful continuation
            updated_gap = None

        await self.db.flush()
        return recalibration_record, updated_gap
