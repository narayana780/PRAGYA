import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import PragyaException
from app.modules.assessments.models import CompetencyEvidence
from app.modules.competencies.models import Competency
from app.modules.materials.models import Document
from app.modules.quizzes.models import (
    QuestionOption,
    Quiz,
    QuizAttempt,
    QuizQuestion,
    QuizResponse,
)
from app.modules.quizzes.schemas import (
    AnswerResponse,
    CitationDetail,
    QuestionOptionSchema,
    QuizAttemptItem,
    QuizDetail,
    QuizItem,
    QuizQuestionItem,
    QuizResultResponse,
    QuizReviewItem,
    QuizReviewResponse,
    SubmitAnswerRequest,
)


class QuizService:
    """
    Quiz lifecycle, attempt execution, server-side scoring, instant feedback,
    and competency evidence integration.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_quizzes(self, employee_id: uuid.UUID, limit: int = 50) -> list[QuizItem]:
        stmt = (
            select(Quiz)
            .where(
                (Quiz.employee_id == employee_id) | (Quiz.employee_id.is_(None))
            )
            .where(Quiz.status.in_(["READY", "IN_PROGRESS", "COMPLETED"]))
            .order_by(desc(Quiz.created_at))
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        quizzes = res.scalars().all()

        seen_keys = set()
        items = []
        for q in quizzes:
            # Filter internal test harness quizzes
            if q.title and q.title.startswith("Test Adaptive Pool"):
                continue

            # Deduplicate quizzes so duplicate generations appear as single unique cards
            key = (q.title, str(q.difficulty).upper())
            if key in seen_keys:
                continue
            seen_keys.add(key)

            doc_title = None
            if q.source_document_id:
                d_res = await self.db.execute(select(Document.title).where(Document.id == q.source_document_id))
                doc_title = d_res.scalar_one_or_none()

            comp_name = None
            if q.competency_id:
                c_res = await self.db.execute(select(Competency.name).where(Competency.id == q.competency_id))
                comp_name = c_res.scalar_one_or_none()

            items.append(
                QuizItem(
                    id=q.id,
                    employee_id=q.employee_id,
                    title=q.title,
                    description=q.description,
                    source_document_id=q.source_document_id,
                    competency_id=q.competency_id,
                    question_count=q.question_count,
                    difficulty=q.difficulty,
                    status=q.status,
                    created_at=q.created_at,
                    updated_at=q.updated_at,
                    document_title=doc_title,
                    competency_name=comp_name,
                )
            )
        return items

    async def get_quiz(
        self, employee_id: uuid.UUID, quiz_id: uuid.UUID, include_correctness: bool = False
    ) -> QuizDetail:
        stmt = (
            select(Quiz)
            .options(
                selectinload(Quiz.questions).selectinload(QuizQuestion.options)
            )
            .where(Quiz.id == quiz_id)
        )
        res = await self.db.execute(stmt)
        q = res.scalar_one_or_none()

        if not q:
            raise PragyaException(
                code="QUIZ_NOT_FOUND",
                message="Quiz not found.",
                status_code=404,
            )

        if q.employee_id and q.employee_id != employee_id:
            raise PragyaException(
                code="UNAUTHORIZED_QUIZ_ACCESS",
                message="You do not have permission to access this quiz.",
                status_code=403,
            )

        doc_title = None
        if q.source_document_id:
            d_res = await self.db.execute(select(Document.title).where(Document.id == q.source_document_id))
            doc_title = d_res.scalar_one_or_none()

        comp_name = None
        if q.competency_id:
            c_res = await self.db.execute(select(Competency.name).where(Competency.id == q.competency_id))
            comp_name = c_res.scalar_one_or_none()

        question_items = []
        for question in q.questions:
            options = []
            for opt in question.options:
                options.append(
                    QuestionOptionSchema(
                        id=opt.id,
                        question_id=opt.question_id,
                        option_text=opt.option_text,
                        option_order=opt.option_order,
                        is_correct=opt.is_correct if include_correctness else None,
                    )
                )

            question_items.append(
                QuizQuestionItem(
                    id=question.id,
                    quiz_id=question.quiz_id,
                    question_text=question.question_text,
                    question_type=question.question_type,
                    difficulty=question.difficulty,
                    bloom_level=question.bloom_level,
                    competency_id=question.competency_id,
                    source_document_id=question.source_document_id,
                    source_chunk_id=question.source_chunk_id,
                    source_page_number=question.source_page_number,
                    explanation=question.explanation if include_correctness else "",
                    options=options,
                    document_title=doc_title,
                    competency_name=comp_name,
                )
            )

        return QuizDetail(
            id=q.id,
            employee_id=q.employee_id,
            title=q.title,
            description=q.description,
            source_document_id=q.source_document_id,
            competency_id=q.competency_id,
            question_count=q.question_count,
            difficulty=q.difficulty,
            status=q.status,
            created_at=q.created_at,
            updated_at=q.updated_at,
            document_title=doc_title,
            competency_name=comp_name,
            questions=question_items,
        )

    async def create_attempt(
        self, employee_id: uuid.UUID, quiz_id: uuid.UUID
    ) -> QuizAttemptItem:
        quiz_detail = await self.get_quiz(employee_id, quiz_id)

        # Create Attempt
        attempt = QuizAttempt(
            id=uuid.uuid4(),
            quiz_id=quiz_id,
            employee_id=employee_id,
            started_at=datetime.now(),
            status="IN_PROGRESS",
        )
        self.db.add(attempt)
        await self.db.commit()
        await self.db.refresh(attempt)

        return QuizAttemptItem(
            id=attempt.id,
            quiz_id=attempt.quiz_id,
            employee_id=attempt.employee_id,
            started_at=attempt.started_at,
            status=attempt.status,
            quiz_title=quiz_detail.title,
        )

    async def list_attempts(
        self, employee_id: uuid.UUID, quiz_id: uuid.UUID | None = None
    ) -> list[QuizAttemptItem]:
        stmt = (
            select(QuizAttempt)
            .options(selectinload(QuizAttempt.quiz))
            .where(QuizAttempt.employee_id == employee_id)
        )
        if quiz_id:
            stmt = stmt.where(QuizAttempt.quiz_id == quiz_id)
        stmt = stmt.order_by(desc(QuizAttempt.started_at))

        res = await self.db.execute(stmt)
        attempts = res.scalars().all()

        return [
            QuizAttemptItem(
                id=a.id,
                quiz_id=a.quiz_id,
                employee_id=a.employee_id,
                started_at=a.started_at,
                completed_at=a.completed_at,
                score=a.score,
                percentage=a.percentage,
                status=a.status,
                quiz_title=a.quiz.title if a.quiz else "Practice Quiz",
            )
            for a in attempts
        ]

    async def submit_answer(
        self, employee_id: uuid.UUID, attempt_id: uuid.UUID, req: SubmitAnswerRequest
    ) -> AnswerResponse:
        stmt = (
            select(QuizAttempt)
            .where(QuizAttempt.id == attempt_id, QuizAttempt.employee_id == employee_id)
        )
        res = await self.db.execute(stmt)
        attempt = res.scalar_one_or_none()

        if not attempt:
            raise PragyaException(
                code="ATTEMPT_NOT_FOUND",
                message="Quiz attempt not found or access denied.",
                status_code=404,
            )

        if attempt.status != "IN_PROGRESS":
            raise PragyaException(
                code="ATTEMPT_ALREADY_COMPLETED",
                message="This quiz attempt has already been completed.",
                status_code=400,
            )

        # Get Question & Options
        q_stmt = (
            select(QuizQuestion)
            .options(selectinload(QuizQuestion.options))
            .where(QuizQuestion.id == req.question_id)
        )
        q_res = await self.db.execute(q_stmt)
        question = q_res.scalar_one_or_none()

        if not question or question.quiz_id != attempt.quiz_id:
            raise PragyaException(
                code="QUESTION_NOT_FOUND",
                message="Question does not belong to this quiz attempt.",
                status_code=404,
            )

        # Check existing response for double submit prevention
        r_stmt = select(QuizResponse).where(
            QuizResponse.attempt_id == attempt_id, QuizResponse.question_id == req.question_id
        )
        r_res = await self.db.execute(r_stmt)
        existing = r_res.scalar_one_or_none()

        selected_opt = next((o for o in question.options if o.id == req.selected_option_id), None)
        correct_opt = next((o for o in question.options if o.is_correct), None)

        if not selected_opt or not correct_opt:
            raise PragyaException(
                code="INVALID_OPTION",
                message="Selected option is invalid for this question.",
                status_code=400,
            )

        is_correct = selected_opt.is_correct

        if existing:
            # Update existing submission
            existing.selected_option_id = req.selected_option_id
            existing.is_correct = is_correct
            existing.answered_at = datetime.now()
            resp_obj = existing
        else:
            resp_obj = QuizResponse(
                id=uuid.uuid4(),
                attempt_id=attempt_id,
                question_id=req.question_id,
                selected_option_id=req.selected_option_id,
                is_correct=is_correct,
                answered_at=datetime.now(),
            )
            self.db.add(resp_obj)

        await self.db.commit()

        # Fetch Citation
        doc_title = None
        if question.source_document_id:
            d_res = await self.db.execute(select(Document.title).where(Document.id == question.source_document_id))
            doc_title = d_res.scalar_one_or_none()

        return AnswerResponse(
            response_id=resp_obj.id,
            question_id=question.id,
            selected_option_id=req.selected_option_id,
            is_correct=is_correct,
            correct_option_id=correct_opt.id,
            explanation=question.explanation,
            citation=CitationDetail(
                document_title=doc_title,
                page_number=question.source_page_number,
            ),
        )

    async def complete_attempt(
        self, employee_id: uuid.UUID, attempt_id: uuid.UUID
    ) -> QuizResultResponse:
        stmt = (
            select(QuizAttempt)
            .options(
                selectinload(QuizAttempt.quiz).selectinload(Quiz.questions),
                selectinload(QuizAttempt.responses),
            )
            .where(QuizAttempt.id == attempt_id, QuizAttempt.employee_id == employee_id)
        )
        res = await self.db.execute(stmt)
        attempt = res.scalar_one_or_none()

        if not attempt:
            raise PragyaException(
                code="ATTEMPT_NOT_FOUND",
                message="Quiz attempt not found or access denied.",
                status_code=404,
            )

        total_questions = len(attempt.quiz.questions)
        correct_count = sum(1 for r in attempt.responses if r.is_correct)
        percentage = round((correct_count / total_questions * 100.0) if total_questions > 0 else 0.0, 2)

        attempt.score = float(correct_count)
        attempt.percentage = percentage
        attempt.completed_at = datetime.now()
        attempt.status = "COMPLETED"

        # Log Competency Evidence
        await self._record_assessment_evidence(attempt, total_questions, percentage)

        await self.db.commit()

        # Build analytics
        competencies_tested = set()
        diff_dist: dict[str, int] = {}
        for q in attempt.quiz.questions:
            diff_dist[q.difficulty] = diff_dist.get(q.difficulty, 0) + 1
            if q.competency_id:
                c_res = await self.db.execute(select(Competency.name).where(Competency.id == q.competency_id))
                c_name = c_res.scalar_one_or_none()
                if c_name:
                    competencies_tested.add(c_name)

        return QuizResultResponse(
            attempt_id=attempt.id,
            quiz_id=attempt.quiz_id,
            score=float(correct_count),
            total_questions=total_questions,
            percentage=percentage,
            completed_at=attempt.completed_at or datetime.now(),
            competencies_tested=list(competencies_tested),
            difficulty_distribution=diff_dist,
        )

    async def get_result(
        self, employee_id: uuid.UUID, attempt_id: uuid.UUID
    ) -> QuizResultResponse:
        stmt = (
            select(QuizAttempt)
            .options(
                selectinload(QuizAttempt.quiz).selectinload(Quiz.questions),
                selectinload(QuizAttempt.responses),
            )
            .where(QuizAttempt.id == attempt_id, QuizAttempt.employee_id == employee_id)
        )
        res = await self.db.execute(stmt)
        attempt = res.scalar_one_or_none()

        if not attempt:
            raise PragyaException(
                code="ATTEMPT_NOT_FOUND",
                message="Quiz attempt not found or access denied.",
                status_code=404,
            )

        total_questions = len(attempt.quiz.questions)
        correct_count = sum(1 for r in attempt.responses if r.is_correct)
        percentage = attempt.percentage or (round(correct_count / total_questions * 100.0, 2) if total_questions > 0 else 0.0)

        competencies_tested = set()
        diff_dist: dict[str, int] = {}
        for q in attempt.quiz.questions:
            diff_dist[q.difficulty] = diff_dist.get(q.difficulty, 0) + 1
            if q.competency_id:
                c_res = await self.db.execute(select(Competency.name).where(Competency.id == q.competency_id))
                c_name = c_res.scalar_one_or_none()
                if c_name:
                    competencies_tested.add(c_name)

        return QuizResultResponse(
            attempt_id=attempt.id,
            quiz_id=attempt.quiz_id,
            score=float(correct_count),
            total_questions=total_questions,
            percentage=percentage,
            completed_at=attempt.completed_at or datetime.now(),
            competencies_tested=list(competencies_tested),
            difficulty_distribution=diff_dist,
        )

    async def get_review(
        self, employee_id: uuid.UUID, attempt_id: uuid.UUID
    ) -> QuizReviewResponse:
        stmt = (
            select(QuizAttempt)
            .options(
                selectinload(QuizAttempt.quiz)
                .selectinload(Quiz.questions)
                .selectinload(QuizQuestion.options),
                selectinload(QuizAttempt.responses),
            )
            .where(QuizAttempt.id == attempt_id, QuizAttempt.employee_id == employee_id)
        )
        res = await self.db.execute(stmt)
        attempt = res.scalar_one_or_none()

        if not attempt:
            raise PragyaException(
                code="ATTEMPT_NOT_FOUND",
                message="Quiz attempt not found or access denied.",
                status_code=404,
            )

        resp_map = {r.question_id: r for r in attempt.responses}

        review_items = []
        for q in attempt.quiz.questions:
            resp = resp_map.get(q.id)
            selected_opt_id = resp.selected_option_id if resp else uuid.UUID("00000000-0000-0000-0000-000000000000")
            correct_opt = next((o for o in q.options if o.is_correct), q.options[0] if q.options else None)
            correct_opt_id = correct_opt.id if correct_opt else uuid.UUID("00000000-0000-0000-0000-000000000000")
            is_correct = resp.is_correct if resp else False

            doc_title = None
            if q.source_document_id:
                d_res = await self.db.execute(select(Document.title).where(Document.id == q.source_document_id))
                doc_title = d_res.scalar_one_or_none()

            options = [
                QuestionOptionSchema(
                    id=o.id,
                    question_id=o.question_id,
                    option_text=o.option_text,
                    option_order=o.option_order,
                    is_correct=o.is_correct,
                )
                for o in q.options
            ]

            review_items.append(
                QuizReviewItem(
                    question_id=q.id,
                    question_text=q.question_text,
                    selected_option_id=selected_opt_id,
                    correct_option_id=correct_opt_id,
                    is_correct=is_correct,
                    options=options,
                    explanation=q.explanation,
                    source_document_title=doc_title,
                    source_page_number=q.source_page_number,
                )
            )

        return QuizReviewResponse(
            attempt_id=attempt.id,
            quiz_id=attempt.quiz_id,
            score=attempt.score or 0.0,
            percentage=attempt.percentage or 0.0,
            items=review_items,
        )

    async def _record_assessment_evidence(
        self, attempt: QuizAttempt, total_questions: int, percentage: float
    ) -> None:
        """
        Logs Stage 5 CompetencyEvidence for mapped competencies without directly overwriting score.
        Confidence policy: 5 questions -> 0.70 confidence; 10+ questions -> 0.85 confidence.
        """
        quiz = attempt.quiz
        if not quiz:
            return

        competency_ids = set()
        if quiz.competency_id:
            competency_ids.add(quiz.competency_id)
        for q in quiz.questions:
            if q.competency_id:
                competency_ids.add(q.competency_id)

        confidence = 0.70 if total_questions < 8 else 0.85
        normalized_score = percentage / 100.0  # Scale 0.0 to 1.0

        for comp_id in competency_ids:
            evidence = CompetencyEvidence(
                id=uuid.uuid4(),
                employee_id=attempt.employee_id,
                competency_id=comp_id,
                evidence_type="AI_GENERATED_QUIZ",
                source_id=str(attempt.id),
                raw_value=percentage,
                normalized_score=normalized_score,
                weight_used=1.0,
                contribution=normalized_score * confidence,
                confidence=confidence,
                metadata_json={
                    "quiz_id": str(quiz.id),
                    "attempt_id": str(attempt.id),
                    "quiz_title": quiz.title,
                    "total_questions": total_questions,
                    "difficulty": quiz.difficulty,
                },
            )
            self.db.add(evidence)
