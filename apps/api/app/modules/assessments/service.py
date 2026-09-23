import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PragyaException
from app.modules.assessments.constants import AttemptStatus, EvidenceType
from app.modules.assessments.repository import AssessmentRepository
from app.modules.assessments.schemas import (
    AssessmentDetailResponse,
    AssessmentResponse,
    AttemptDetailResponse,
    AttemptResponse,
    CompetencyBreakdownItem,
    CompetencyBriefResponse,
    CompleteAttemptResponse,
    QuestionPublicResponse,
    RecordResponseResult,
)
from app.modules.assessments.scoring_service import CompetencyScoringService
from app.modules.employees.models import Employee


class AssessmentService:
    @staticmethod
    async def get_assessments(db: AsyncSession) -> list[AssessmentResponse]:
        assessments = await AssessmentRepository.get_assessments(db)
        return [AssessmentResponse.model_validate(a) for a in assessments]

    @staticmethod
    async def get_assessment_by_id(assessment_id: uuid.UUID, db: AsyncSession) -> AssessmentDetailResponse:
        assessment = await AssessmentRepository.get_assessment_by_id(assessment_id, db)
        if not assessment:
            raise PragyaException(
                message=f"Assessment '{assessment_id}' not found",
                status_code=status.HTTP_404_NOT_FOUND,
                code="ASSESSMENT_NOT_FOUND",
            )
        comps = []
        for ac in assessment.competencies:
            if ac.competency:
                comps.append(CompetencyBriefResponse(
                    id=ac.competency.id,
                    code=ac.competency.code,
                    name=ac.competency.name,
                ))

        return AssessmentDetailResponse(
            id=assessment.id,
            title=assessment.title,
            description=assessment.description,
            assessment_type=assessment.assessment_type,
            status=assessment.status,
            duration_minutes=assessment.duration_minutes,
            question_count=assessment.question_count,
            created_at=assessment.created_at,
            updated_at=assessment.updated_at,
            competencies=comps,
        )

    @staticmethod
    async def start_attempt(
        assessment_id: uuid.UUID,
        employee_id: uuid.UUID,
        db: AsyncSession,
    ) -> AttemptResponse:
        # Validate assessment
        assessment = await AssessmentRepository.get_assessment_by_id(assessment_id, db)
        if not assessment:
            raise PragyaException(
                message=f"Assessment '{assessment_id}' not found",
                status_code=status.HTTP_404_NOT_FOUND,
                code="ASSESSMENT_NOT_FOUND",
            )

        # Validate employee
        emp = await db.get(Employee, employee_id)
        if not emp:
            raise PragyaException(
                message=f"Employee '{employee_id}' not found",
                status_code=status.HTTP_404_NOT_FOUND,
                code="EMPLOYEE_NOT_FOUND",
            )

        attempt = await AssessmentRepository.create_attempt(assessment_id, employee_id, db)
        return AttemptResponse.model_validate(attempt)

    @staticmethod
    async def get_attempt(attempt_id: uuid.UUID, db: AsyncSession) -> AttemptDetailResponse:
        attempt = await AssessmentRepository.get_attempt_by_id(attempt_id, db)
        if not attempt:
            raise PragyaException(
                message=f"Attempt '{attempt_id}' not found",
                status_code=status.HTTP_404_NOT_FOUND,
                code="ATTEMPT_NOT_FOUND",
            )

        public_questions = [
            QuestionPublicResponse(
                id=q.id,
                assessment_id=q.assessment_id,
                competency_id=q.competency_id,
                question_text=q.question_text,
                options=q.options,
                difficulty=q.difficulty,
                points=q.points,
                order_index=q.order_index,
            )
            for q in attempt.assessment.questions
        ]

        answered_ids = [r.question_id for r in attempt.responses]

        return AttemptDetailResponse(
            id=attempt.id,
            assessment_id=attempt.assessment_id,
            employee_id=attempt.employee_id,
            started_at=attempt.started_at,
            completed_at=attempt.completed_at,
            raw_score=attempt.raw_score,
            percentage=attempt.percentage,
            status=attempt.status,
            assessment_title=attempt.assessment.title,
            duration_minutes=attempt.assessment.duration_minutes,
            questions=public_questions,
            answered_question_ids=answered_ids,
        )

    @staticmethod
    async def record_response(
        attempt_id: uuid.UUID,
        question_id: uuid.UUID,
        selected_option: int,
        employee_id: uuid.UUID,
        db: AsyncSession,
    ) -> RecordResponseResult:
        attempt = await AssessmentRepository.get_attempt_by_id(attempt_id, db)
        if not attempt:
            raise PragyaException(
                message=f"Attempt '{attempt_id}' not found",
                status_code=status.HTTP_404_NOT_FOUND,
                code="ATTEMPT_NOT_FOUND",
            )

        if attempt.employee_id != employee_id:
            raise PragyaException(
                message="Unauthorized: this attempt belongs to another employee",
                status_code=status.HTTP_403_FORBIDDEN,
                code="FORBIDDEN_ATTEMPT",
            )

        if attempt.status != AttemptStatus.IN_PROGRESS.value:
            raise PragyaException(
                message=f"Cannot submit answers to an attempt that is '{attempt.status}'",
                status_code=status.HTTP_400_BAD_REQUEST,
                code="ATTEMPT_NOT_ACTIVE",
            )

        question = await AssessmentRepository.get_question_by_id(question_id, db)
        if not question or question.assessment_id != attempt.assessment_id:
            raise PragyaException(
                message=f"Question '{question_id}' does not belong to this assessment",
                status_code=status.HTTP_400_BAD_REQUEST,
                code="INVALID_QUESTION",
            )

        is_correct = (question.correct_option == selected_option)
        points_earned = float(question.points) if is_correct else 0.0

        resp = await AssessmentRepository.record_response(
            attempt_id=attempt_id,
            question_id=question_id,
            selected_option=selected_option,
            is_correct=is_correct,
            points_earned=points_earned,
            db=db,
        )

        return RecordResponseResult(
            attempt_id=resp.attempt_id,
            question_id=resp.question_id,
            selected_option=resp.selected_option,
            responded_at=resp.responded_at,
        )

    @staticmethod
    async def complete_attempt(
        attempt_id: uuid.UUID,
        employee_id: uuid.UUID,
        db: AsyncSession,
    ) -> CompleteAttemptResponse:
        attempt = await AssessmentRepository.get_attempt_by_id(attempt_id, db)
        if not attempt:
            raise PragyaException(
                message=f"Attempt '{attempt_id}' not found",
                status_code=status.HTTP_404_NOT_FOUND,
                code="ATTEMPT_NOT_FOUND",
            )

        if attempt.employee_id != employee_id:
            raise PragyaException(
                message="Unauthorized: this attempt belongs to another employee",
                status_code=status.HTTP_403_FORBIDDEN,
                code="FORBIDDEN_ATTEMPT",
            )

        if attempt.status == AttemptStatus.COMPLETED.value:
            raise PragyaException(
                message="Attempt has already been completed",
                status_code=status.HTTP_400_BAD_REQUEST,
                code="ATTEMPT_ALREADY_COMPLETED",
            )

        questions = attempt.assessment.questions
        responses_map = {r.question_id: r for r in attempt.responses}

        total_points_earned = 0.0
        max_points = 0.0
        competency_stats: dict[uuid.UUID, dict[str, Any]] = {}

        for q in questions:
            max_points += q.points
            if q.competency_id not in competency_stats:
                competency_stats[q.competency_id] = {
                    "competency": q.competency,
                    "tested": 0,
                    "correct": 0,
                    "earned": 0.0,
                    "max": 0.0,
                }
            competency_stats[q.competency_id]["tested"] += 1
            competency_stats[q.competency_id]["max"] += q.points

            resp = responses_map.get(q.id)
            if resp:
                total_points_earned += resp.points_earned
                competency_stats[q.competency_id]["earned"] += resp.points_earned
                if resp.is_correct:
                    competency_stats[q.competency_id]["correct"] += 1

        pct = round((total_points_earned / max_points * 100.0) if max_points > 0 else 0.0, 1)

        # Mark attempt completed
        await AssessmentRepository.update_attempt_completion(
            attempt_id=attempt_id,
            raw_score=total_points_earned,
            percentage=pct,
            db=db,
        )

        # Generate competency breakdown & create evidence records
        breakdown: list[CompetencyBreakdownItem] = []
        for comp_id, stats in competency_stats.items():
            comp_obj = stats["competency"]
            comp_pct = round((stats["earned"] / stats["max"] * 100.0) if stats["max"] > 0 else 0.0, 1)
            breakdown.append(
                CompetencyBreakdownItem(
                    competency_id=comp_id,
                    competency_name=comp_obj.name if comp_obj else "Competency",
                    competency_code=comp_obj.code if comp_obj else "CODE",
                    questions_tested=stats["tested"],
                    correct_count=stats["correct"],
                    score_percentage=comp_pct,
                )
            )

            # Persist DIAGNOSTIC evidence
            evidence = await AssessmentRepository.create_evidence(
                employee_id=employee_id,
                competency_id=comp_id,
                evidence_type=EvidenceType.DIAGNOSTIC.value,
                source_id=str(attempt_id),
                raw_value=comp_pct,
                normalized_score=comp_pct,
                weight_used=0.50,
                contribution=0.0,
                confidence=0.85,
                metadata_dict={
                    "attempt_id": str(attempt_id),
                    "questions_tested": stats["tested"],
                    "correct_count": stats["correct"],
                    "earned_points": stats["earned"],
                    "max_points": stats["max"],
                },
                db=db,
            )

            # Recalibrate employee competency
            await CompetencyScoringService.calculate_competency(
                employee_id=employee_id,
                competency_id=comp_id,
                db=db,
                change_reason=f"Completed Diagnostic Assessment: {attempt.assessment.title} ({comp_pct}%)",
                trigger_evidence_id=evidence.id,
            )

        return CompleteAttemptResponse(
            attempt_id=attempt.id,
            assessment_id=attempt.assessment_id,
            employee_id=attempt.employee_id,
            status=AttemptStatus.COMPLETED.value,
            completed_at=datetime.now(UTC),
            raw_score=total_points_earned,
            max_score=max_points,
            percentage=pct,
            total_questions=len(questions),
            answered_questions=len(attempt.responses),
            competency_breakdown=breakdown,
        )
