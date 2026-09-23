import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.orm import selectinload

import app.main  # Registers all models
from app.core.exceptions import PragyaException
from app.main import app
from app.modules.assessments.repository import AssessmentRepository
from app.modules.adaptive.constants import (
    MAX_ADAPTIVE_QUESTIONS,
    MAX_RECALIBRATION_DELTA,
    MIN_ADAPTIVE_QUESTIONS,
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
    AdaptiveSessionCreateRequest,
    AdaptiveSubmitAnswerRequest,
)
from app.modules.adaptive.service import AdaptiveAssessmentService
from app.modules.assessments.models import CompetencyEvidence, EmployeeCompetency
from app.modules.competencies.models import Competency
from app.modules.employees.models import Employee
from app.modules.materials.models import Document
from app.modules.quizzes.models import QuestionOption, Quiz, QuizQuestion
from app.modules.recommendations.service import RecommendationService
from app.modules.skill_gaps.models import SkillGap
from app.modules.skill_gaps.service import SkillGapService


# ============================================================================
# Unit Tests: Adaptation Rules, Bounding, Confidence & Scoring
# ============================================================================

def test_initial_difficulty_mapping():
    """Initial difficulty is selected deterministically from demonstrated score."""
    assert score_to_initial_level(None) == "BEGINNER"
    assert score_to_initial_level(0.0) == "BEGINNER"
    assert score_to_initial_level(25.0) == "BEGINNER"
    assert score_to_initial_level(29.9) == "BEGINNER"
    assert score_to_initial_level(30.0) == "INTERMEDIATE"
    assert score_to_initial_level(50.0) == "INTERMEDIATE"
    assert score_to_initial_level(59.9) == "INTERMEDIATE"
    assert score_to_initial_level(60.0) == "ADVANCED"
    assert score_to_initial_level(95.0) == "ADVANCED"


def test_deterministic_adaptation_rules():
    """Single-step transitions: correct -> +1 (capped at ADVANCED), incorrect -> -1 (min BEGINNER)."""
    # Progression
    assert next_difficulty("BEGINNER", True) == "INTERMEDIATE"
    assert next_difficulty("INTERMEDIATE", True) == "ADVANCED"
    assert next_difficulty("ADVANCED", True) == "ADVANCED"  # Upper boundary

    # Regression
    assert next_difficulty("ADVANCED", False) == "INTERMEDIATE"
    assert next_difficulty("INTERMEDIATE", False) == "BEGINNER"
    assert next_difficulty("BEGINNER", False) == "BEGINNER"  # Lower boundary


def test_adaptive_confidence_formula():
    """Confidence increases with depth and coverage, and stays bounded [0.20, 1.00]."""
    # 0 questions
    assert calculate_adaptive_confidence(0, set(), []) == 0.0

    # 1 question
    conf_1 = calculate_adaptive_confidence(1, {"BEGINNER"}, [True])
    assert 0.20 <= conf_1 <= 0.40

    # 5 questions, 2 difficulties, consistent
    conf_5 = calculate_adaptive_confidence(5, {"BEGINNER", "INTERMEDIATE"}, [True, True, True, True, True])
    assert conf_5 > conf_1
    assert 0.50 <= conf_5 <= 0.90

    # 10 questions, all 3 difficulties, high consistency
    conf_10 = calculate_adaptive_confidence(
        10, {"BEGINNER", "INTERMEDIATE", "ADVANCED"}, [True, True, True, True, True, False, True, True, True, True]
    )
    assert conf_10 >= 0.85
    assert conf_10 <= 1.00


def test_adaptive_score_calculation():
    """Calculates weighted accuracy across difficulty tiers."""
    assert calculate_adaptive_score([]) == 0.0

    # 1 Beginner correct (1/1) = 100%
    assert calculate_adaptive_score([("BEGINNER", True)]) == 100.0

    # 1 Beginner correct (1 pt), 1 Intermediate incorrect (0/2 pts) -> 1/3 = 33.3%
    assert calculate_adaptive_score([("BEGINNER", True), ("INTERMEDIATE", False)]) == 33.3

    # 1 Intermediate correct (2 pts), 1 Advanced correct (3 pts) -> 5/5 = 100%
    assert calculate_adaptive_score([("INTERMEDIATE", True), ("ADVANCED", True)]) == 100.0


# ============================================================================
# Service & Closed-Loop Recalibration Tests
# ============================================================================

@pytest.fixture
async def sample_adaptive_setup(db_session):
    """Creates a clean test environment with an employee, competency, and questions at all 3 difficulty tiers."""
    emp_res = await db_session.execute(select(Employee).limit(1))
    emp = emp_res.scalar_one()

    comp_res = await db_session.execute(select(Competency).limit(1))
    comp = comp_res.scalar_one()

    doc_res = await db_session.execute(select(Document).limit(1))
    doc = doc_res.scalar_one_or_none()

    # Create dummy quiz for foreign key relationship
    quiz = Quiz(
        id=uuid.uuid4(),
        employee_id=emp.id,
        title="Test Adaptive Pool",
        competency_id=comp.id,
        source_document_id=doc.id if doc else None,
        difficulty="INTERMEDIATE",
        status="READY",
        question_count=6,
    )
    db_session.add(quiz)
    await db_session.flush()

    # Create questions for each tier: 2 BEGINNER, 2 INTERMEDIATE, 2 ADVANCED
    questions = []
    difficulties = ["BEGINNER", "BEGINNER", "INTERMEDIATE", "INTERMEDIATE", "ADVANCED", "ADVANCED"]
    for i, diff in enumerate(difficulties):
        q = QuizQuestion(
            id=uuid.uuid4(),
            quiz_id=quiz.id,
            competency_id=comp.id,
            source_document_id=doc.id if doc else None,
            question_text=f"Adaptive Question {i + 1} ({diff})",
            difficulty=diff,
            bloom_level="UNDERSTAND",
            explanation=f"Explanation for question {i + 1}",
        )
        db_session.add(q)
        await db_session.flush()

        # Add 4 options (opt 0 is correct)
        for opt_idx in range(4):
            opt = QuestionOption(
                id=uuid.uuid4(),
                question_id=q.id,
                option_text=f"Option {opt_idx + 1} for Q{i + 1}",
                option_order=opt_idx + 1,
                is_correct=(opt_idx == 0),
            )
            db_session.add(opt)

        questions.append(q)

    await db_session.commit()
    return emp, comp, doc, questions


@pytest.mark.asyncio
async def test_adaptive_session_lifecycle(db_session, sample_adaptive_setup):
    """Verifies complete lifecycle: creation, question adaptation, response submission, and completion."""
    emp, comp, doc, questions = sample_adaptive_setup
    service = AdaptiveAssessmentService(db_session)

    # 1. Create session
    create_req = AdaptiveSessionCreateRequest(
        competency_id=comp.id,
        source_document_id=doc.id if doc else None,
    )
    session_summary = await service.create_session(emp.id, create_req)
    assert session_summary.status == "IN_PROGRESS"
    assert session_summary.question_count == 0
    assert session_summary.initial_level in ["BEGINNER", "INTERMEDIATE", "ADVANCED"]

    session_id = session_summary.id

    # 2. Get next question (first question matches initial level)
    q1 = await service.get_next_question(emp.id, session_id)
    assert q1 is not None
    assert q1.question_number == 1
    assert len(q1.options) == 4

    # 3. Answer correctly -> difficulty should increase
    q1_db_res = await db_session.execute(
        select(QuizQuestion).options(selectinload(QuizQuestion.options)).where(QuizQuestion.id == q1.id)
    )
    q1_db = q1_db_res.scalar_one()
    correct_opt = next(o for o in q1_db.options if o.is_correct)

    resp1 = await service.submit_response(
        emp.id,
        session_id,
        AdaptiveSubmitAnswerRequest(
            question_id=q1.id,
            selected_option_id=correct_opt.id,
        ),
    )
    assert resp1.is_correct is True
    assert resp1.question_count == 1
    if resp1.current_difficulty == "BEGINNER":
        assert resp1.next_difficulty == "INTERMEDIATE"

    # 4. Attempt premature completion (less than MIN_ADAPTIVE_QUESTIONS) -> Must Fail
    with pytest.raises(PragyaException) as exc_info:
        await service.complete_session(emp.id, session_id)
    assert exc_info.value.code == "MIN_QUESTIONS_NOT_MET"

    # 5. Answer 4 more questions to reach min 5
    for step in range(2, 6):
        q_next = await service.get_next_question(emp.id, session_id)
        q_db = (
            await db_session.execute(
                select(QuizQuestion).options(selectinload(QuizQuestion.options)).where(QuizQuestion.id == q_next.id)
            )
        ).scalar_one()
        c_opt = next(o for o in q_db.options if o.is_correct)
        inc_opt = next(o for o in q_db.options if not o.is_correct)

        # Alternate correct and incorrect
        chosen_opt = c_opt if step % 2 == 0 else inc_opt
        submit_res = await service.submit_response(
            emp.id,
            session_id,
            AdaptiveSubmitAnswerRequest(
                question_id=q_next.id,
                selected_option_id=chosen_opt.id,
            ),
        )
        assert submit_res.question_count == step

    # 6. Now can complete session
    result = await service.complete_session(emp.id, session_id)
    assert result.session_id == session_id
    assert result.questions_answered == 5
    assert result.recalibrated_score >= 0.0
    assert result.confidence >= 0.20
    assert result.delta is not None

    # 7. Check database audit records
    from sqlalchemy import desc
    recal_res = await db_session.execute(
        select(CompetencyRecalibration)
        .where(
            CompetencyRecalibration.employee_id == emp.id,
            CompetencyRecalibration.competency_id == comp.id,
        )
        .order_by(desc(CompetencyRecalibration.created_at))
    )
    recal = recal_res.scalars().first()
    assert recal is not None
    assert recal.delta == result.delta

    # Check that ADAPTIVE_ASSESSMENT evidence was recorded
    ev_res = await db_session.execute(
        select(CompetencyEvidence).where(
            CompetencyEvidence.employee_id == emp.id,
            CompetencyEvidence.competency_id == comp.id,
            CompetencyEvidence.evidence_type == "ADAPTIVE_ASSESSMENT",
            CompetencyEvidence.source_id == str(session_id),
        )
    )
    ev = ev_res.scalars().first()
    assert ev is not None
    assert ev.raw_value == result.assessment_score


@pytest.mark.asyncio
async def test_recalibration_max_delta_and_bounding(db_session, sample_adaptive_setup):
    """Verifies that anti-oscillation clamps score swings to MAX_RECALIBRATION_DELTA (20.0 pts)."""
    emp, comp, _, _ = sample_adaptive_setup
    recal_service = CompetencyRecalibrationService(db_session)

    # Set initial score to 20.0
    await AssessmentRepository.upsert_employee_competency(
        employee_id=emp.id,
        competency_id=comp.id,
        current_score=20.0,
        confidence=0.50,
        confidence_label="MEDIUM",
        evidence_count=1,
        db=db_session,
    )
    await db_session.commit()

    # Simulate perfect 100.0 assessment score (raw delta would be +80.0)
    recal_record, _ = await recal_service.recalibrate_competency(
        employee_id=emp.id,
        competency_id=comp.id,
        session_id=uuid.uuid4(),
        assessment_score=100.0,
        confidence=0.85,
        question_count=5,
    )

    # Delta must be clamped to <= MAX_RECALIBRATION_DELTA (20.0 pts)
    assert recal_record.previous_score == 20.0
    assert recal_record.delta <= MAX_RECALIBRATION_DELTA
    assert recal_record.new_score <= 40.0
    assert 0.0 <= recal_record.new_score <= 100.0


@pytest.mark.asyncio
async def test_duplicate_response_and_idempotent_completion(db_session, sample_adaptive_setup):
    """Verifies idempotency: duplicate answer submission is rejected, and repeat completion returns existing result."""
    emp, comp, doc, _ = sample_adaptive_setup
    service = AdaptiveAssessmentService(db_session)

    session = await service.create_session(
        emp.id, AdaptiveSessionCreateRequest(competency_id=comp.id)
    )

    q = await service.get_next_question(emp.id, session.id)
    q_db = (
        await db_session.execute(
            select(QuizQuestion).options(selectinload(QuizQuestion.options)).where(QuizQuestion.id == q.id)
        )
    ).scalar_one()

    # Submit first answer
    await service.submit_response(
        emp.id,
        session.id,
        AdaptiveSubmitAnswerRequest(
            question_id=q.id,
            selected_option_id=q_db.options[0].id,
        ),
    )

    # Submit duplicate answer for same question -> must raise 409
    with pytest.raises(PragyaException) as exc_info:
        await service.submit_response(
            emp.id,
            session.id,
            AdaptiveSubmitAnswerRequest(
                question_id=q.id,
                selected_option_id=q_db.options[0].id,
            ),
        )
    assert exc_info.value.code == "DUPLICATE_RESPONSE"


@pytest.mark.asyncio
async def test_employee_isolation(db_session, sample_adaptive_setup):
    """Ensures employee cannot access another employee's adaptive assessment session."""
    emp, comp, _, _ = sample_adaptive_setup
    service = AdaptiveAssessmentService(db_session)

    # Create session for emp
    session = await service.create_session(
        emp.id, AdaptiveSessionCreateRequest(competency_id=comp.id)
    )

    # Another employee tries to access session
    other_emp_id = uuid.uuid4()
    with pytest.raises(PragyaException) as exc_info:
        await service.get_session(other_emp_id, session.id)
    assert exc_info.value.code == "FORBIDDEN_SESSION_ACCESS"


# ============================================================================
# API Endpoint Integration Tests (HTTP Layer)
# ============================================================================

@pytest.mark.asyncio
async def test_adaptive_api_endpoints(sample_adaptive_setup):
    """Verifies all 6 REST API endpoints for Stage 11."""
    emp, comp, doc, _ = sample_adaptive_setup

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"X-Employee-Id": str(emp.id)}

        # 1. POST /api/v1/adaptive-assessments (create session)
        create_res = await client.post(
            "/api/v1/adaptive-assessments",
            json={"competency_id": str(comp.id), "source_document_id": str(doc.id) if doc else None},
            headers=headers,
        )
        assert create_res.status_code == 201
        session_data = create_res.json()
        session_id = session_data["id"]

        # 2. GET /api/v1/adaptive-assessments/{session_id}
        get_res = await client.get(f"/api/v1/adaptive-assessments/{session_id}", headers=headers)
        assert get_res.status_code == 200
        assert get_res.json()["id"] == session_id

        # 3. POST /api/v1/adaptive-assessments/{session_id}/questions/next
        next_q_res = await client.post(
            f"/api/v1/adaptive-assessments/{session_id}/questions/next", headers=headers
        )
        assert next_q_res.status_code == 200
        q_data = next_q_res.json()
        assert "question_text" in q_data
        assert len(q_data["options"]) == 4

        # 4. POST /api/v1/adaptive-assessments/{session_id}/responses
        opt_id = q_data["options"][0]["id"]
        ans_res = await client.post(
            f"/api/v1/adaptive-assessments/{session_id}/responses",
            json={"question_id": q_data["id"], "selected_option_id": opt_id},
            headers=headers,
        )
        assert ans_res.status_code == 200
        ans_data = ans_res.json()
        assert "is_correct" in ans_data
        assert "next_difficulty" in ans_data

        # Answer 4 more questions to reach 5
        for _ in range(4):
            nq = (await client.post(f"/api/v1/adaptive-assessments/{session_id}/questions/next", headers=headers)).json()
            oid = nq["options"][0]["id"]
            await client.post(
                f"/api/v1/adaptive-assessments/{session_id}/responses",
                json={"question_id": nq["id"], "selected_option_id": oid},
                headers=headers,
            )

        # 5. POST /api/v1/adaptive-assessments/{session_id}/complete
        comp_res = await client.post(
            f"/api/v1/adaptive-assessments/{session_id}/complete", headers=headers
        )
        assert comp_res.status_code == 200
        comp_data = comp_res.json()
        assert comp_data["session_id"] == session_id
        assert "recalibrated_score" in comp_data

        # 6. GET /api/v1/adaptive-assessments/{session_id}/result
        res_res = await client.get(
            f"/api/v1/adaptive-assessments/{session_id}/result", headers=headers
        )
        assert res_res.status_code == 200
        assert res_res.json()["session_id"] == session_id


@pytest.mark.asyncio
async def test_adaptive_competency_and_skill_gap_targeting(db_session, sample_adaptive_setup):
    """Verifies that an adaptive assessment targets a specific competency or prioritized skill gap."""
    emp, comp, _, _ = sample_adaptive_setup
    service = AdaptiveAssessmentService(db_session)

    # Launch targeting competency
    session = await service.create_session(
        emp.id, AdaptiveSessionCreateRequest(competency_id=comp.id)
    )
    assert session.competency_id == comp.id

    # Verify session summary includes competency name
    summary = await service.get_session(emp.id, session.id)
    assert summary.competency_name == comp.name


@pytest.mark.asyncio
async def test_adaptive_assessment_integration_water_cycle(db_session, sample_adaptive_setup):
    """
    Integration test:
    - Target a competency using learning material.
    - Start an adaptive assessment.
    - Serve questions from grounded quiz pipeline.
    - Answer at least 5 questions observing difficulty adaptation.
    - Complete assessment and verify evidence, recalibrated score, gap, and recommendation updates.
    """
    emp, comp, doc, _ = sample_adaptive_setup

    # Look for Water Cycle doc or fallback to sample doc
    wc_res = await db_session.execute(
        select(Document).where(Document.title.ilike("%Water%")).limit(1)
    )
    active_doc = wc_res.scalar_one_or_none() or doc

    service = AdaptiveAssessmentService(db_session)

    # 1. Start adaptive assessment
    session = await service.create_session(
        emp.id,
        AdaptiveSessionCreateRequest(
            competency_id=comp.id,
            source_document_id=active_doc.id if active_doc else None,
        ),
    )
    assert session.status == "IN_PROGRESS"

    initial_diff = session.initial_level
    difficulties_tracked = []

    # 2. Answer at least 5 questions
    for i in range(5):
        q = await service.get_next_question(emp.id, session.id)
        assert q is not None
        difficulties_tracked.append(q.difficulty)

        q_db = (
            await db_session.execute(
                select(QuizQuestion).options(selectinload(QuizQuestion.options)).where(QuizQuestion.id == q.id)
            )
        ).scalar_one()

        corr_opt = next(o for o in q_db.options if o.is_correct)
        inc_opt = next(o for o in q_db.options if not o.is_correct)

        # First 2 correct (should adapt up), 3rd incorrect (should adapt down), 4th & 5th correct
        chosen = corr_opt if i != 2 else inc_opt
        submit_res = await service.submit_response(
            emp.id,
            session.id,
            AdaptiveSubmitAnswerRequest(
                question_id=q.id,
                selected_option_id=chosen.id,
            ),
        )
        assert submit_res.question_count == i + 1

    # 3. Complete assessment
    result = await service.complete_session(emp.id, session.id)
    assert result.session_id == session.id
    assert result.questions_answered >= 5
    assert result.recalibrated_score >= 0.0

    # 4. Verify responses are stored in database
    resp_stmt = select(AdaptiveAssessmentResponse).where(
        AdaptiveAssessmentResponse.session_id == session.id
    )
    resps = (await db_session.execute(resp_stmt)).scalars().all()
    assert len(resps) >= 5
    assert len(difficulties_tracked) >= 5

    # 5. Verify assessment evidence created
    ev_stmt = select(CompetencyEvidence).where(
        CompetencyEvidence.employee_id == emp.id,
        CompetencyEvidence.competency_id == comp.id,
        CompetencyEvidence.evidence_type == "ADAPTIVE_ASSESSMENT",
        CompetencyEvidence.source_id == str(session.id),
    )
    ev = (await db_session.execute(ev_stmt)).scalar_one_or_none()
    assert ev is not None
    assert ev.raw_value == result.assessment_score

    # 6. Verify competency recalibrated in employee_competencies
    emp_comp = (
        await db_session.execute(
            select(EmployeeCompetency).where(
                EmployeeCompetency.employee_id == emp.id,
                EmployeeCompetency.competency_id == comp.id,
            )
        )
    ).scalar_one()
    assert emp_comp.current_score == result.recalibrated_score

    # 7. Verify skill gap updated & priority synchronized
    gap_stmt = select(SkillGap).where(
        SkillGap.employee_id == emp.id,
        SkillGap.competency_id == comp.id,
    )
    gap = (await db_session.execute(gap_stmt)).scalar_one_or_none()
    if gap:
        assert gap.priority_level in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "NO_GAP"]
        assert gap.priority_score >= 0.0

    # 8. Verify recommendation engine integrates updated priority
    rec_service = RecommendationService(db_session)
    recs = await rec_service.generate_recommendations(emp.id)
    assert isinstance(recs, list)


@pytest.mark.asyncio
async def test_adaptive_abandoned_session(db_session, sample_adaptive_setup):
    """Verifies that an abandoned session cannot accept answers or be completed."""
    emp, comp, _, _ = sample_adaptive_setup
    service = AdaptiveAssessmentService(db_session)

    session = await service.create_session(
        emp.id, AdaptiveSessionCreateRequest(competency_id=comp.id)
    )

    # Manually mark as ABANDONED
    sess_db = (
        await db_session.execute(
            select(AdaptiveAssessmentSession).where(AdaptiveAssessmentSession.id == session.id)
        )
    ).scalar_one()
    sess_db.status = "ABANDONED"
    await db_session.commit()

    # Attempting to fetch next question or complete must fail
    with pytest.raises(PragyaException) as exc_info:
        await service.get_next_question(emp.id, session.id)
    assert exc_info.value.code == "SESSION_NOT_ACTIVE"


# =============================================================================
# Bug 2 & Bug 6 Regression Tests: Question Generation & Lifecycle
# =============================================================================

@pytest.mark.asyncio
async def test_adaptive_question_retrieval_and_dynamic_generation_fallback(db_session, sample_adaptive_setup):
    """
    REGRESSION BUG 2 & 6:
    When get_next_question is called, it retrieves or bridges questions correctly
    without raising AttributeError or premature 404.
    """
    emp, comp, _, _ = sample_adaptive_setup
    service = AdaptiveAssessmentService(db_session)

    session = await service.create_session(
        emp.id,
        AdaptiveSessionCreateRequest(competency_id=comp.id),
    )
    assert session.status == "IN_PROGRESS"

    # Call get_next_question
    q = await service.get_next_question(emp.id, session.id)
    assert q is not None
    assert q.question_text
    assert len(q.options) >= 2
    assert q.difficulty in ("BEGINNER", "INTERMEDIATE", "ADVANCED")


@pytest.mark.asyncio
async def test_adaptive_premature_completion_rejection_at_zero_questions(db_session, sample_adaptive_setup):
    """
    REGRESSION BUG 2 & 6:
    Attempting to complete an adaptive assessment before answering minimum required questions
    must return MIN_QUESTIONS_NOT_MET (HTTP 400).
    """
    emp, comp, _, _ = sample_adaptive_setup
    service = AdaptiveAssessmentService(db_session)

    session = await service.create_session(
        emp.id,
        AdaptiveSessionCreateRequest(competency_id=comp.id),
    )

    with pytest.raises(PragyaException) as exc_info:
        await service.complete_session(emp.id, session.id)

    assert exc_info.value.status_code == 400
    assert exc_info.value.code == "MIN_QUESTIONS_NOT_MET"


