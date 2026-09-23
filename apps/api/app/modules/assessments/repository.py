import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.assessments.constants import AttemptStatus
from app.modules.assessments.models import (
    Assessment,
    AssessmentAttempt,
    AssessmentQuestion,
    AssessmentResponse,
    CompetencyEvidence,
    CompetencyScoreHistory,
    EmployeeCompetency,
)


class AssessmentRepository:
    @staticmethod
    async def get_assessments(db: AsyncSession) -> list[Assessment]:
        stmt = (
            select(Assessment)
            .options(
                selectinload(Assessment.competencies),
            )
            .order_by(Assessment.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_assessment_by_id(assessment_id: uuid.UUID, db: AsyncSession) -> Assessment | None:
        stmt = (
            select(Assessment)
            .options(
                selectinload(Assessment.competencies),
                selectinload(Assessment.questions).selectinload(AssessmentQuestion.competency),
            )
            .where(Assessment.id == assessment_id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_question_by_id(question_id: uuid.UUID, db: AsyncSession) -> AssessmentQuestion | None:
        stmt = select(AssessmentQuestion).where(AssessmentQuestion.id == question_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_attempt_by_id(attempt_id: uuid.UUID, db: AsyncSession) -> AssessmentAttempt | None:
        stmt = (
            select(AssessmentAttempt)
            .options(
                selectinload(AssessmentAttempt.assessment).selectinload(Assessment.questions).selectinload(AssessmentQuestion.competency),
                selectinload(AssessmentAttempt.responses),
            )
            .where(AssessmentAttempt.id == attempt_id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_attempt(
        assessment_id: uuid.UUID,
        employee_id: uuid.UUID,
        db: AsyncSession,
    ) -> AssessmentAttempt:
        attempt = AssessmentAttempt(
            assessment_id=assessment_id,
            employee_id=employee_id,
            status=AttemptStatus.IN_PROGRESS.value,
        )
        db.add(attempt)
        await db.commit()
        await db.refresh(attempt)
        return attempt

    @staticmethod
    async def record_response(
        attempt_id: uuid.UUID,
        question_id: uuid.UUID,
        selected_option: int,
        is_correct: bool,
        points_earned: float,
        db: AsyncSession,
    ) -> AssessmentResponse:
        # Check if already answered
        stmt = select(AssessmentResponse).where(
            AssessmentResponse.attempt_id == attempt_id,
            AssessmentResponse.question_id == question_id,
        )
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            existing.selected_option = selected_option
            existing.is_correct = is_correct
            existing.points_earned = points_earned
            existing.responded_at = datetime.now(UTC)
            await db.commit()
            await db.refresh(existing)
            return existing

        response = AssessmentResponse(
            attempt_id=attempt_id,
            question_id=question_id,
            selected_option=selected_option,
            is_correct=is_correct,
            points_earned=points_earned,
        )
        db.add(response)
        await db.commit()
        await db.refresh(response)
        return response

    @staticmethod
    async def update_attempt_completion(
        attempt_id: uuid.UUID,
        raw_score: float,
        percentage: float,
        db: AsyncSession,
    ) -> AssessmentAttempt | None:
        attempt = await AssessmentRepository.get_attempt_by_id(attempt_id, db)
        if not attempt:
            return None
        attempt.raw_score = raw_score
        attempt.percentage = percentage
        attempt.status = AttemptStatus.COMPLETED.value
        attempt.completed_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(attempt)
        return attempt

    @staticmethod
    async def create_evidence(
        employee_id: uuid.UUID,
        competency_id: uuid.UUID,
        evidence_type: str,
        raw_value: float,
        normalized_score: float,
        weight_used: float,
        contribution: float,
        confidence: float,
        db: AsyncSession,
        source_id: str | None = None,
        metadata_dict: dict[str, Any] | None = None,
    ) -> CompetencyEvidence:
        evidence = CompetencyEvidence(
            employee_id=employee_id,
            competency_id=competency_id,
            evidence_type=evidence_type,
            source_id=source_id,
            raw_value=raw_value,
            normalized_score=normalized_score,
            weight_used=weight_used,
            contribution=contribution,
            confidence=confidence,
            metadata_json=metadata_dict,
        )
        db.add(evidence)
        await db.commit()
        await db.refresh(evidence)
        return evidence

    @staticmethod
    async def get_employee_competency_evidence(
        employee_id: uuid.UUID,
        competency_id: uuid.UUID,
        db: AsyncSession,
    ) -> list[CompetencyEvidence]:
        stmt = (
            select(CompetencyEvidence)
            .where(
                CompetencyEvidence.employee_id == employee_id,
                CompetencyEvidence.competency_id == competency_id,
            )
            .order_by(CompetencyEvidence.recorded_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_all_employee_evidence(
        employee_id: uuid.UUID,
        db: AsyncSession,
    ) -> list[CompetencyEvidence]:
        stmt = (
            select(CompetencyEvidence)
            .where(CompetencyEvidence.employee_id == employee_id)
            .order_by(CompetencyEvidence.recorded_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_employee_competencies(
        employee_id: uuid.UUID,
        db: AsyncSession,
    ) -> list[EmployeeCompetency]:
        stmt = (
            select(EmployeeCompetency)
            .options(
                selectinload(EmployeeCompetency.competency),
            )
            .where(EmployeeCompetency.employee_id == employee_id)
            .order_by(desc(EmployeeCompetency.current_score))
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_employee_competency(
        employee_id: uuid.UUID,
        competency_id: uuid.UUID,
        db: AsyncSession,
    ) -> EmployeeCompetency | None:
        stmt = (
            select(EmployeeCompetency)
            .options(
                selectinload(EmployeeCompetency.competency),
            )
            .where(
                EmployeeCompetency.employee_id == employee_id,
                EmployeeCompetency.competency_id == competency_id,
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def upsert_employee_competency(
        employee_id: uuid.UUID,
        competency_id: uuid.UUID,
        current_score: float,
        confidence: float,
        confidence_label: str,
        evidence_count: int,
        db: AsyncSession,
    ) -> EmployeeCompetency:
        existing = await AssessmentRepository.get_employee_competency(employee_id, competency_id, db)
        if existing:
            existing.current_score = current_score
            existing.confidence = confidence
            existing.confidence_label = confidence_label
            existing.evidence_count = evidence_count
            existing.last_assessed_at = datetime.now(UTC)
            await db.commit()
            await db.refresh(existing)
            return existing

        comp = EmployeeCompetency(
            employee_id=employee_id,
            competency_id=competency_id,
            current_score=current_score,
            confidence=confidence,
            confidence_label=confidence_label,
            evidence_count=evidence_count,
        )
        db.add(comp)
        await db.commit()
        await db.refresh(comp)
        return comp

    @staticmethod
    async def record_score_history(
        employee_id: uuid.UUID,
        competency_id: uuid.UUID,
        previous_score: float | None,
        new_score: float,
        previous_confidence: float | None,
        new_confidence: float,
        change_reason: str,
        db: AsyncSession,
        trigger_evidence_id: uuid.UUID | None = None,
    ) -> CompetencyScoreHistory:
        history = CompetencyScoreHistory(
            employee_id=employee_id,
            competency_id=competency_id,
            previous_score=previous_score,
            new_score=new_score,
            previous_confidence=previous_confidence,
            new_confidence=new_confidence,
            change_reason=change_reason,
            trigger_evidence_id=trigger_evidence_id,
        )
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history

    @staticmethod
    async def get_competency_score_history(
        employee_id: uuid.UUID,
        competency_id: uuid.UUID,
        db: AsyncSession,
    ) -> list[CompetencyScoreHistory]:
        stmt = (
            select(CompetencyScoreHistory)
            .where(
                CompetencyScoreHistory.employee_id == employee_id,
                CompetencyScoreHistory.competency_id == competency_id,
            )
            .order_by(CompetencyScoreHistory.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())
