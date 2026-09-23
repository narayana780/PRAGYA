import uuid
import pytest
from sqlalchemy import select

import app.main  # Registers all SQLAlchemy ORM models

from app.core.exceptions import PragyaException
from app.modules.assessments.models import CompetencyEvidence
from app.modules.employees.models import Employee
from app.modules.materials.models import Document
from app.modules.quizzes.generation_service import QuizGenerationService
from app.modules.quizzes.schemas import QuizGenerateRequest, SubmitAnswerRequest
from app.modules.quizzes.service import QuizService


@pytest.mark.asyncio
async def test_quiz_attempt_lifecycle_and_scoring(db_session):
    emp_res = await db_session.execute(select(Employee).limit(1))
    emp = emp_res.scalar_one()

    doc_res = await db_session.execute(select(Document).limit(1))
    doc = doc_res.scalar_one_or_none()

    if not doc:
        pytest.skip("No document found in DB")

    gen_service = QuizGenerationService(db_session)
    quiz = await gen_service.generate_quiz(
        emp.id,
        QuizGenerateRequest(
            document_id=doc.id,
            difficulty="BEGINNER",
            question_count=3,
        ),
    )

    quiz_service = QuizService(db_session)
    
    # 1. Start Attempt
    attempt = await quiz_service.create_attempt(emp.id, quiz.id)
    assert attempt is not None
    assert attempt.status == "IN_PROGRESS"

    # 2. Get Quiz for attempt (sanitized, is_correct hidden)
    student_quiz = await quiz_service.get_quiz(emp.id, quiz.id, include_correctness=False)
    for q in student_quiz.questions:
        for opt in q.options:
            assert opt.is_correct is None

    # 3. Submit Answers
    quiz_detail_admin = await quiz_service.get_quiz(emp.id, quiz.id, include_correctness=True)
    
    for i, q in enumerate(quiz_detail_admin.questions):
        correct_opt = next(o for o in q.options if o.is_correct)
        incorrect_opt = next(o for o in q.options if not o.is_correct)
        
        # Pick correct for 1st question, incorrect for others
        selected_id = correct_opt.id if i == 0 else incorrect_opt.id
        
        ans_resp = await quiz_service.submit_answer(
            emp.id,
            attempt.id,
            SubmitAnswerRequest(question_id=q.id, selected_option_id=selected_id),
        )
        assert ans_resp.question_id == q.id
        assert ans_resp.explanation is not None

    # 4. Complete Attempt
    result = await quiz_service.complete_attempt(emp.id, attempt.id)
    assert result.total_questions == len(quiz_detail_admin.questions)
    assert result.score == 1.0
    assert result.percentage == round(1.0 / len(quiz_detail_admin.questions) * 100.0, 2)

    # 5. Get Review
    review = await quiz_service.get_review(emp.id, attempt.id)
    assert len(review.items) == len(quiz_detail_admin.questions)
    assert review.items[0].is_correct is True


@pytest.mark.asyncio
async def test_assessment_evidence_creation(db_session):
    emp_res = await db_session.execute(select(Employee).limit(1))
    emp = emp_res.scalar_one()

    doc_res = await db_session.execute(select(Document).limit(1))
    doc = doc_res.scalar_one_or_none()

    if not doc:
        pytest.skip("No document found in DB")

    gen_service = QuizGenerationService(db_session)
    quiz = await gen_service.generate_quiz(
        emp.id,
        QuizGenerateRequest(
            document_id=doc.id,
            difficulty="BEGINNER",
            question_count=2,
        ),
    )

    quiz_service = QuizService(db_session)
    attempt = await quiz_service.create_attempt(emp.id, quiz.id)
    
    quiz_detail = await quiz_service.get_quiz(emp.id, quiz.id, include_correctness=True)
    for q in quiz_detail.questions:
        opt = q.options[0]
        await quiz_service.submit_answer(
            emp.id, attempt.id, SubmitAnswerRequest(question_id=q.id, selected_option_id=opt.id)
        )

    await quiz_service.complete_attempt(emp.id, attempt.id)

    # Verify CompetencyEvidence logged in DB if quiz was mapped to competency
    if quiz.competency_id:
        ev_stmt = select(CompetencyEvidence).where(
            CompetencyEvidence.employee_id == emp.id,
            CompetencyEvidence.evidence_type == "AI_GENERATED_QUIZ",
            CompetencyEvidence.source_id == str(attempt.id),
        )
        ev_res = await db_session.execute(ev_stmt)
        ev = ev_res.scalar_one_or_none()
        assert ev is not None
        assert ev.evidence_type == "AI_GENERATED_QUIZ"


@pytest.mark.asyncio
async def test_employee_isolation_and_security(db_session):
    emps_res = await db_session.execute(select(Employee).limit(2))
    emps = emps_res.scalars().all()
    if len(emps) < 2:
        pytest.skip("Need at least 2 employees in DB for security isolation test")

    emp1, emp2 = emps[0], emps[1]

    doc_res = await db_session.execute(select(Document).limit(1))
    doc = doc_res.scalar_one_or_none()

    if not doc:
        pytest.skip("No document found in DB")

    gen_service = QuizGenerationService(db_session)
    quiz = await gen_service.generate_quiz(
        emp1.id,
        QuizGenerateRequest(document_id=doc.id, question_count=2),
    )

    quiz_service = QuizService(db_session)

    # Emp2 attempts to access Emp1's private quiz -> 403 Forbidden
    with pytest.raises(PragyaException) as exc_info:
        await quiz_service.get_quiz(emp2.id, quiz.id)
    assert exc_info.value.status_code == 403

    # Emp2 attempts to start attempt on Emp1's quiz -> 403 Forbidden
    with pytest.raises(PragyaException) as exc_info2:
        await quiz_service.create_attempt(emp2.id, quiz.id)
    assert exc_info2.value.status_code == 403
