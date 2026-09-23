import random
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import PragyaException
from app.modules.adaptive.constants import (
    MAX_ADAPTIVE_QUESTIONS,
    MIN_ADAPTIVE_QUESTIONS,
    TARGET_CONFIDENCE,
    calculate_adaptive_confidence,
    calculate_adaptive_score,
    next_difficulty,
    score_to_initial_level,
)
from app.modules.adaptive.models import (
    AdaptiveAssessmentResponse,
    AdaptiveAssessmentSession,
    CompetencyRecalibration,
)
from app.modules.adaptive.recalibration_service import CompetencyRecalibrationService
from app.modules.adaptive.schemas import (
    AdaptiveQuestionOption,
    AdaptiveQuestionPresentation,
    AdaptiveSessionCreateRequest,
    AdaptiveSessionSummary,
    AdaptiveSubmitAnswerRequest,
    AdaptiveSubmitAnswerResponse,
    RecalibrationResultResponse,
)
from app.modules.assessments.models import AssessmentQuestion, EmployeeCompetency
from app.modules.competencies.models import Competency
from app.modules.materials.models import Document
from app.modules.quizzes.generation_service import QuizGenerationService
from app.modules.quizzes.models import QuestionOption, Quiz, QuizQuestion
from app.modules.quizzes.schemas import QuizGenerateRequest
from app.modules.quizzes.service import QuizService
from app.modules.skill_gaps.models import SkillGap


class AdaptiveAssessmentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(
        self, employee_id: uuid.UUID, req: AdaptiveSessionCreateRequest
    ) -> AdaptiveSessionSummary:
        # Validate competency
        comp_res = await self.db.execute(
            select(Competency).where(Competency.id == req.competency_id)
        )
        comp = comp_res.scalar_one_or_none()
        if not comp:
            raise PragyaException(
                code="COMPETENCY_NOT_FOUND",
                message=f"Competency {req.competency_id} not found.",
                status_code=404,
            )

        # Validate source document if provided
        doc_title = None
        if req.source_document_id:
            doc_res = await self.db.execute(
                select(Document).where(Document.id == req.source_document_id)
            )
            doc = doc_res.scalar_one_or_none()
            if doc:
                doc_title = doc.title

        # Determine starting level from previous demonstrated score
        emp_comp_res = await self.db.execute(
            select(EmployeeCompetency).where(
                EmployeeCompetency.employee_id == employee_id,
                EmployeeCompetency.competency_id == req.competency_id,
            )
        )
        emp_comp = emp_comp_res.scalar_one_or_none()
        current_score = emp_comp.current_score if emp_comp else None
        initial_lvl = score_to_initial_level(current_score)

        session = AdaptiveAssessmentSession(
            id=uuid.uuid4(),
            employee_id=employee_id,
            competency_id=req.competency_id,
            source_document_id=req.source_document_id,
            initial_level=initial_lvl,
            current_level=initial_lvl,
            question_count=0,
            correct_count=0,
            incorrect_count=0,
            status="IN_PROGRESS",
            confidence=0.20,
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        return AdaptiveSessionSummary(
            id=session.id,
            employee_id=session.employee_id,
            competency_id=session.competency_id,
            competency_name=comp.name,
            source_document_id=session.source_document_id,
            source_document_title=doc_title,
            initial_level=session.initial_level,
            current_level=session.current_level,
            question_count=session.question_count,
            correct_count=session.correct_count,
            incorrect_count=session.incorrect_count,
            status=session.status,
            confidence=session.confidence,
            started_at=session.started_at,
            completed_at=session.completed_at,
        )

    async def get_session(
        self, employee_id: uuid.UUID, session_id: uuid.UUID
    ) -> AdaptiveSessionSummary:
        session = await self._get_verified_session(employee_id, session_id)

        comp_name = None
        if session.competency:
            comp_name = session.competency.name

        doc_title = None
        if session.source_document:
            doc_title = session.source_document.title

        return AdaptiveSessionSummary(
            id=session.id,
            employee_id=session.employee_id,
            competency_id=session.competency_id,
            competency_name=comp_name,
            source_document_id=session.source_document_id,
            source_document_title=doc_title,
            initial_level=session.initial_level,
            current_level=session.current_level,
            question_count=session.question_count,
            correct_count=session.correct_count,
            incorrect_count=session.incorrect_count,
            status=session.status,
            confidence=session.confidence,
            started_at=session.started_at,
            completed_at=session.completed_at,
        )

    async def get_next_question(
        self, employee_id: uuid.UUID, session_id: uuid.UUID
    ) -> AdaptiveQuestionPresentation:
        session = await self._get_verified_session(employee_id, session_id)

        if session.status != "IN_PROGRESS":
            raise PragyaException(
                code="SESSION_NOT_ACTIVE",
                message=f"Adaptive assessment session is {session.status}.",
                status_code=400,
            )

        if session.question_count >= MAX_ADAPTIVE_QUESTIONS:
            raise PragyaException(
                code="MAX_QUESTIONS_REACHED",
                message=f"Session reached maximum limit of {MAX_ADAPTIVE_QUESTIONS} questions.",
                status_code=400,
            )

        # IDs of questions already answered in this session
        answered_stmt = select(AdaptiveAssessmentResponse.question_id).where(
            AdaptiveAssessmentResponse.session_id == session.id
        )
        answered_res = await self.db.execute(answered_stmt)
        answered_q_ids = set(answered_res.scalars().all())

        target_diff = session.current_level.upper()

        # Try to find an existing unused question matching competency and difficulty
        q_stmt = (
            select(QuizQuestion)
            .options(
                selectinload(QuizQuestion.options),
            )
            .where(
                QuizQuestion.competency_id == session.competency_id,
                func.upper(QuizQuestion.difficulty) == target_diff,
            )
        )
        if session.source_document_id:
            q_stmt = q_stmt.where(QuizQuestion.source_document_id == session.source_document_id)
        if answered_q_ids:
            q_stmt = q_stmt.where(QuizQuestion.id.not_in(answered_q_ids))

        res = await self.db.execute(q_stmt)
        candidates = res.scalars().all()

        question: QuizQuestion | None = None
        if candidates:
            question = random.choice(candidates)
        else:
            # Generate a new question for this competency & difficulty via QuizGenerationService
            quiz_gen_service = QuizGenerationService(self.db)
            try:
                gen_req = QuizGenerateRequest(
                    competency_id=session.competency_id,
                    document_id=session.source_document_id,
                    difficulty=target_diff,
                    question_count=1,
                )
                generated_quiz = await quiz_gen_service.generate_quiz(employee_id, gen_req)
                if generated_quiz.questions:
                    available_q = [q for q in generated_quiz.questions if q.id not in answered_q_ids]
                    if available_q:
                        diff_match = [q for q in available_q if q.difficulty and q.difficulty.upper() == target_diff]
                        chosen_q = diff_match[0] if diff_match else available_q[0]
                        q_fresh = await self.db.execute(
                            select(QuizQuestion)
                            .options(
                                selectinload(QuizQuestion.options),
                            )
                            .where(QuizQuestion.id == chosen_q.id)
                        )
                        question = q_fresh.scalar_one_or_none()
            except Exception as e:
                logger.warning(f"Failed to dynamically generate question for competency {session.competency_id}: {e}")
                question = None

            if not question:
                # If generation or difficulty-matched retrieval fails, try any unused question for this competency
                fallback_stmt = (
                    select(QuizQuestion)
                    .options(
                        selectinload(QuizQuestion.options),
                    )
                    .where(QuizQuestion.competency_id == session.competency_id)
                )
                if answered_q_ids:
                    fallback_stmt = fallback_stmt.where(QuizQuestion.id.not_in(answered_q_ids))
                f_res = await self.db.execute(fallback_stmt)
                fallback_candidates = f_res.scalars().all()
                if fallback_candidates:
                    question = random.choice(fallback_candidates)

            if not question:
                # Check for seeded AssessmentQuestion for this competency and bridge to QuizQuestion
                aq_stmt = select(AssessmentQuestion).where(
                    AssessmentQuestion.competency_id == session.competency_id
                )
                aq_res = await self.db.execute(aq_stmt)
                aq_candidates = aq_res.scalars().all()
                if aq_candidates:
                    for candidate_aq in aq_candidates:
                        # Check if a QuizQuestion matching this question_text exists
                        match_stmt = (
                            select(QuizQuestion)
                            .options(selectinload(QuizQuestion.options))
                            .where(QuizQuestion.question_text == candidate_aq.question_text)
                        )
                        match_q = (await self.db.execute(match_stmt)).scalar_one_or_none()
                        if match_q:
                            if answered_q_ids and match_q.id in answered_q_ids:
                                continue
                            question = match_q
                            break
                        else:
                            # Materialize QuizQuestion from AssessmentQuestion
                            q_id = uuid.uuid4()
                            question_obj = QuizQuestion(
                                id=q_id,
                                quiz_id=None,
                                question_text=candidate_aq.question_text,
                                question_type="MCQ_SINGLE",
                                difficulty=target_diff,
                                bloom_level="APPLY",
                                competency_id=session.competency_id,
                                source_document_id=session.source_document_id or uuid.uuid4(),
                                explanation=candidate_aq.explanation or "Official MoSPI assessment benchmark item.",
                            )
                            self.db.add(question_obj)
                            for idx, opt_text in enumerate(candidate_aq.options):
                                opt = QuestionOption(
                                    id=uuid.uuid4(),
                                    question_id=q_id,
                                    option_text=opt_text,
                                    option_order=idx + 1,
                                    is_correct=(idx == candidate_aq.correct_option),
                                )
                                self.db.add(opt)
                            await self.db.commit()

                            q_fresh = await self.db.execute(
                                select(QuizQuestion)
                                .options(selectinload(QuizQuestion.options))
                                .where(QuizQuestion.id == q_id)
                            )
                            question = q_fresh.scalar_one_or_none()
                            break

            if not question:
                raise PragyaException(
                    code="NO_QUESTIONS_AVAILABLE",
                    message="No more questions available for this competency. Please complete the assessment.",
                    status_code=404,
                )

        # Shuffle options for presentation
        options = list(question.options)
        random.shuffle(options)

        doc_title = None
        if question.source_document_id:
            d_res = await self.db.execute(
                select(Document.title).where(Document.id == question.source_document_id)
            )
            doc_title = d_res.scalar_one_or_none()

        return AdaptiveQuestionPresentation(
            id=question.id,
            session_id=session.id,
            question_text=question.question_text,
            difficulty=question.difficulty,
            bloom_level=question.bloom_level,
            question_number=session.question_count + 1,
            total_target_questions=MAX_ADAPTIVE_QUESTIONS,
            options=[
                AdaptiveQuestionOption(
                    id=opt.id,
                    option_text=opt.option_text,
                    option_order=idx + 1,
                )
                for idx, opt in enumerate(options)
            ],
            source_document_title=doc_title,
            source_page_number=question.source_page_number,
        )

    async def submit_response(
        self,
        employee_id: uuid.UUID,
        session_id: uuid.UUID,
        req: AdaptiveSubmitAnswerRequest,
    ) -> AdaptiveSubmitAnswerResponse:
        session = await self._get_verified_session(employee_id, session_id)

        if session.status != "IN_PROGRESS":
            raise PragyaException(
                code="SESSION_NOT_ACTIVE",
                message=f"Session is {session.status}. Answers cannot be submitted.",
                status_code=400,
            )

        # Idempotency: Prevent duplicate answer submission for the same question
        existing_res = await self.db.execute(
            select(AdaptiveAssessmentResponse).where(
                AdaptiveAssessmentResponse.session_id == session.id,
                AdaptiveAssessmentResponse.question_id == req.question_id,
            )
        )
        if existing_res.scalar_one_or_none():
            raise PragyaException(
                code="DUPLICATE_RESPONSE",
                message="Response for this question has already been submitted.",
                status_code=409,
            )

        # Fetch question and options
        q_res = await self.db.execute(
            select(QuizQuestion)
            .options(selectinload(QuizQuestion.options))
            .where(QuizQuestion.id == req.question_id)
        )
        question = q_res.scalar_one_or_none()
        if not question:
            raise PragyaException(
                code="QUESTION_NOT_FOUND",
                message="Question not found.",
                status_code=404,
            )

        selected_opt = next((o for o in question.options if o.id == req.selected_option_id), None)
        if not selected_opt:
            raise PragyaException(
                code="OPTION_NOT_FOUND",
                message="Selected option does not belong to this question.",
                status_code=400,
            )

        correct_opt = next((o for o in question.options if o.is_correct), None)
        if not correct_opt:
            raise PragyaException(
                code="CORRECT_OPTION_MISSING",
                message="Question data integrity error: no correct option found.",
                status_code=500,
            )

        is_correct = selected_opt.is_correct

        # 1. Record response
        resp = AdaptiveAssessmentResponse(
            id=uuid.uuid4(),
            session_id=session.id,
            question_id=question.id,
            difficulty=question.difficulty,
            selected_option_id=selected_opt.id,
            is_correct=is_correct,
            response_time_ms=req.response_time_ms,
        )
        self.db.add(resp)
        await self.db.flush()

        # 2. Update session metrics
        session.question_count += 1
        if is_correct:
            session.correct_count += 1
        else:
            session.incorrect_count += 1

        curr_diff = session.current_level
        next_diff = next_difficulty(curr_diff, is_correct)
        session.current_level = next_diff

        # 3. Recalculate confidence
        all_res_stmt = select(AdaptiveAssessmentResponse).where(
            AdaptiveAssessmentResponse.session_id == session.id
        )
        all_res = (await self.db.execute(all_res_stmt)).scalars().all()
        diffs_seen = {r.difficulty.upper() for r in all_res}
        history = [r.is_correct for r in all_res]
        conf = calculate_adaptive_confidence(len(all_res), diffs_seen, history)
        session.confidence = conf

        can_complete = session.question_count >= MIN_ADAPTIVE_QUESTIONS
        should_stop = False
        stop_reason = None

        if session.question_count >= MAX_ADAPTIVE_QUESTIONS:
            should_stop = True
            stop_reason = f"Maximum assessment question limit ({MAX_ADAPTIVE_QUESTIONS}) reached."
        elif can_complete and conf >= TARGET_CONFIDENCE:
            should_stop = True
            stop_reason = f"Target measurement confidence ({conf:.0%}) achieved."

        await self.db.commit()

        return AdaptiveSubmitAnswerResponse(
            response_id=resp.id,
            session_id=session.id,
            question_id=question.id,
            selected_option_id=selected_opt.id,
            is_correct=is_correct,
            correct_option_id=correct_opt.id,
            explanation=question.explanation,
            current_difficulty=curr_diff,
            next_difficulty=next_diff,
            question_count=session.question_count,
            confidence=session.confidence,
            can_complete=can_complete,
            should_stop=should_stop,
            stop_reason=stop_reason,
        )

    async def complete_session(
        self, employee_id: uuid.UUID, session_id: uuid.UUID
    ) -> RecalibrationResultResponse:
        session = await self._get_verified_session(employee_id, session_id)

        # Idempotency: If already completed, return existing result without recalibrating again
        if session.status == "COMPLETED":
            return await self.get_result(employee_id, session_id)

        if session.question_count < MIN_ADAPTIVE_QUESTIONS:
            if session.question_count == 0:
                raise PragyaException(
                    code="MIN_QUESTIONS_NOT_MET",
                    message=f"At least {MIN_ADAPTIVE_QUESTIONS} questions required before completing.",
                    status_code=400,
                )
            # Check if any unused questions remain for this competency
            answered_q_ids = list((
                await self.db.execute(
                    select(AdaptiveAssessmentResponse.question_id).where(
                        AdaptiveAssessmentResponse.session_id == session.id
                    )
                )
            ).scalars().all())
            unused_q_stmt = (
                select(QuizQuestion)
                .where(
                    QuizQuestion.competency_id == session.competency_id,
                    QuizQuestion.id.not_in(answered_q_ids) if answered_q_ids else True,
                )
            )
            has_more = (await self.db.execute(unused_q_stmt)).scalars().first()
            if has_more:
                raise PragyaException(
                    code="MIN_QUESTIONS_NOT_MET",
                    message=f"At least {MIN_ADAPTIVE_QUESTIONS} questions required before completing.",
                    status_code=400,
                )
            logger.info(f"Permitting early completion for session {session_id} due to exhausted question pool.")

        # Calculate assessment score
        all_res_stmt = (
            select(AdaptiveAssessmentResponse)
            .where(AdaptiveAssessmentResponse.session_id == session.id)
            .order_by(AdaptiveAssessmentResponse.created_at)
        )
        responses = (await self.db.execute(all_res_stmt)).scalars().all()
        pair_list = [(r.difficulty, r.is_correct) for r in responses]
        assessment_score = calculate_adaptive_score(pair_list)

        session.status = "COMPLETED"
        session.completed_at = datetime.now()

        # Compute difficulty distribution
        diff_dist: dict[str, int] = {}
        for r in responses:
            diff_dist[r.difficulty] = diff_dist.get(r.difficulty, 0) + 1

        # Closed-loop recalibration
        recal_service = CompetencyRecalibrationService(self.db)
        recal_record, updated_gap = await recal_service.recalibrate_competency(
            employee_id=employee_id,
            competency_id=session.competency_id,
            session_id=session.id,
            assessment_score=assessment_score,
            confidence=session.confidence,
            question_count=session.question_count,
            metadata_dict={"difficulty_distribution": diff_dist},
        )

        await self.db.commit()

        comp_name = session.competency.name if session.competency else "Competency"

        return RecalibrationResultResponse(
            session_id=session.id,
            competency_id=session.competency_id,
            competency_name=comp_name,
            previous_score=recal_record.previous_score,
            assessment_score=assessment_score,
            recalibrated_score=recal_record.new_score,
            delta=recal_record.delta,
            confidence=recal_record.confidence,
            reason=recal_record.reason,
            questions_answered=session.question_count,
            correct_count=session.correct_count,
            incorrect_count=session.incorrect_count,
            difficulty_distribution=diff_dist,
            updated_gap_score=updated_gap.gap_score if updated_gap else None,
            updated_priority_level=updated_gap.priority_level if updated_gap else None,
            updated_priority_score=updated_gap.priority_score if updated_gap else None,
            completed_at=session.completed_at or datetime.now(),
        )

    async def get_result(
        self, employee_id: uuid.UUID, session_id: uuid.UUID
    ) -> RecalibrationResultResponse:
        session = await self._get_verified_session(employee_id, session_id)

        if session.status != "COMPLETED":
            raise PragyaException(
                code="SESSION_NOT_COMPLETED",
                message="Session is still in progress.",
                status_code=400,
            )

        # Fetch recalibration record
        recal_stmt = select(CompetencyRecalibration).where(
            CompetencyRecalibration.employee_id == employee_id,
            CompetencyRecalibration.competency_id == session.competency_id,
        ).order_by(desc(CompetencyRecalibration.created_at))
        recal_res = await self.db.execute(recal_stmt)
        recal = recal_res.scalars().first()

        all_res_stmt = select(AdaptiveAssessmentResponse).where(
            AdaptiveAssessmentResponse.session_id == session.id
        )
        responses = (await self.db.execute(all_res_stmt)).scalars().all()
        diff_dist: dict[str, int] = {}
        for r in responses:
            diff_dist[r.difficulty] = diff_dist.get(r.difficulty, 0) + 1

        assessment_score = calculate_adaptive_score([(r.difficulty, r.is_correct) for r in responses])

        # Fetch latest skill gap
        gap_stmt = select(SkillGap).where(
            SkillGap.employee_id == employee_id,
            SkillGap.competency_id == session.competency_id,
        )
        gap = (await self.db.execute(gap_stmt)).scalar_one_or_none()

        comp_name = session.competency.name if session.competency else "Competency"

        return RecalibrationResultResponse(
            session_id=session.id,
            competency_id=session.competency_id,
            competency_name=comp_name,
            previous_score=recal.previous_score if recal else 0.0,
            assessment_score=assessment_score,
            recalibrated_score=recal.new_score if recal else assessment_score,
            delta=recal.delta if recal else 0.0,
            confidence=session.confidence,
            reason=recal.reason if recal else "Completed assessment",
            questions_answered=session.question_count,
            correct_count=session.correct_count,
            incorrect_count=session.incorrect_count,
            difficulty_distribution=diff_dist,
            updated_gap_score=gap.gap_score if gap else None,
            updated_priority_level=gap.priority_level if gap else None,
            updated_priority_score=gap.priority_score if gap else None,
            completed_at=session.completed_at or datetime.now(),
        )

    async def _get_verified_session(
        self, employee_id: uuid.UUID, session_id: uuid.UUID
    ) -> AdaptiveAssessmentSession:
        stmt = (
            select(AdaptiveAssessmentSession)
            .options(
                selectinload(AdaptiveAssessmentSession.competency),
                selectinload(AdaptiveAssessmentSession.source_document),
            )
            .where(AdaptiveAssessmentSession.id == session_id)
        )
        res = await self.db.execute(stmt)
        session = res.scalar_one_or_none()

        if not session:
            raise PragyaException(
                code="SESSION_NOT_FOUND",
                message="Adaptive assessment session not found.",
                status_code=404,
            )

        if session.employee_id != employee_id:
            raise PragyaException(
                code="FORBIDDEN_SESSION_ACCESS",
                message="Access denied to this assessment session.",
                status_code=403,
            )

        return session
