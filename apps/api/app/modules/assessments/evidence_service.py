import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.assessments.constants import (
    EvidenceType,
    normalize_experience,
    normalize_self_assessment,
)
from app.modules.assessments.models import CompetencyEvidence
from app.modules.assessments.repository import AssessmentRepository
from app.modules.assessments.scoring_service import CompetencyScoringService


class EvidenceService:
    @staticmethod
    async def create_evidence(
        employee_id: uuid.UUID,
        competency_id: uuid.UUID,
        evidence_type: str,
        raw_value: float,
        normalized_score: float,
        db: AsyncSession,
        source_id: str | None = None,
        confidence: float = 0.8,
        metadata_dict: dict[str, Any] | None = None,
        trigger_recalibration: bool = True,
        change_reason: str = "New evidence recorded",
    ) -> tuple[CompetencyEvidence, Any]:
        """Record a single evidence entry and recalibrate the employee's competency score."""
        evidence = await AssessmentRepository.create_evidence(
            employee_id=employee_id,
            competency_id=competency_id,
            evidence_type=evidence_type,
            raw_value=raw_value,
            normalized_score=normalized_score,
            weight_used=1.0,
            contribution=0.0,
            confidence=confidence,
            source_id=source_id,
            metadata_dict=metadata_dict,
            db=db,
        )

        updated_comp = None
        if trigger_recalibration:
            updated_comp = await CompetencyScoringService.calculate_competency(
                employee_id=employee_id,
                competency_id=competency_id,
                db=db,
                change_reason=change_reason,
                trigger_evidence_id=evidence.id,
            )

        return evidence, updated_comp

    @staticmethod
    async def record_self_assessment(
        employee_id: uuid.UUID,
        competency_id: uuid.UUID,
        level: int,
        db: AsyncSession,
    ) -> tuple[CompetencyEvidence, Any]:
        """Record a self-assessment level (1-5) mapped securely to 20-100 on the server."""
        normalized_score = normalize_self_assessment(level)
        level_labels = {1: "Beginner", 2: "Basic", 3: "Working", 4: "Proficient", 5: "Advanced"}

        metadata = {
            "self_assessment_level": level,
            "level_label": level_labels.get(level, "Unknown"),
            "source": "EMPLOYEE_PORTAL",
        }

        return await EvidenceService.create_evidence(
            employee_id=employee_id,
            competency_id=competency_id,
            evidence_type=EvidenceType.SELF_ASSESSMENT.value,
            raw_value=float(level),
            normalized_score=normalized_score,
            confidence=0.6,
            metadata_dict=metadata,
            change_reason=f"Self-assessment recorded: Level {level} ({level_labels.get(level)})",
            db=db,
        )

    @staticmethod
    async def record_experience_evidence(
        employee_id: uuid.UUID,
        competency_id: uuid.UUID,
        experience_years: int,
        db: AsyncSession,
    ) -> tuple[CompetencyEvidence, Any]:
        """Convert years of cadre experience into normalized contextual evidence."""
        norm_score = normalize_experience(experience_years)
        metadata = {
            "experience_years": experience_years,
            "curve": "PROTOTYPE_EXPERIENCE_CURVE",
        }
        return await EvidenceService.create_evidence(
            employee_id=employee_id,
            competency_id=competency_id,
            evidence_type=EvidenceType.EXPERIENCE.value,
            raw_value=float(experience_years),
            normalized_score=norm_score,
            confidence=0.7,
            metadata_dict=metadata,
            change_reason=f"Cadre experience registered ({experience_years} years)",
            db=db,
        )

    @staticmethod
    async def record_training_evidence(
        employee_id: uuid.UUID,
        competency_id: uuid.UUID,
        training_title: str,
        score: float | None,
        provider: str,
        db: AsyncSession,
        training_id: uuid.UUID | None = None,
    ) -> tuple[CompetencyEvidence, Any]:
        """Record verified training course evidence."""
        if score is not None and score > 0:
            norm_score = float(score)
            source_desc = "TRAINING_ASSESSMENT"
            conf = 0.85
        else:
            norm_score = 60.0  # Conservative prototype completion score
            source_desc = "TRAINING_COMPLETION"
            conf = 0.70

        metadata = {
            "training_title": training_title,
            "provider": provider,
            "source_type": source_desc,
        }
        return await EvidenceService.create_evidence(
            employee_id=employee_id,
            competency_id=competency_id,
            evidence_type=EvidenceType.TRAINING.value,
            source_id=str(training_id) if training_id else None,
            raw_value=score if score is not None else 60.0,
            normalized_score=norm_score,
            confidence=conf,
            metadata_dict=metadata,
            change_reason=f"Training verified: {training_title} ({source_desc})",
            db=db,
        )
