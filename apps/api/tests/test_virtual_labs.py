"""
PRAGYA Virtual Lab Test Suite (Stage 12)
Validates all 29 verification requirements:
- Scenario catalogue, filters & synthetic dataset enforcement
- Session lifecycle & employee isolation
- Step actions for Data Quality Audit, Survey Sampling, Descriptive Statistics, Missing Data Analysis
- Scoring accuracy, confidence calculation, deterministic hints
- Idempotency for actions and completion
- CompetencyEvidence creation (evidence_type = "VIRTUAL_LAB")
- Security sandboxing (rejection of arbitrary Python, SQL, shell code)
- Integration with Skill Gaps, Quizzes, and Adaptive Assessment
"""
import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.exceptions import PragyaException
from app.main import app
from app.modules.assessments.constants import EvidenceType
from app.modules.assessments.models import CompetencyEvidence, EmployeeCompetency
from app.modules.competencies.models import Competency
from app.modules.employees.models import Employee
from app.modules.labs.engine import LabEngine
from app.modules.labs.models import LabAction, LabDataset, LabResult, LabScenario, LabSession
from app.modules.labs.schemas import (
    LabActionSubmitRequest,
    LabHintRequest,
)
from app.modules.labs.seed_scenarios import (
    DATASET_DQ_ID,
    SCENARIO_DESC_ID,
    SCENARIO_DQ_ID,
    SCENARIO_MISSING_ID,
    SCENARIO_SAMPLING_ID,
    seed_virtual_labs,
)
from app.modules.labs.service import LabService


@pytest.fixture(autouse=True)
async def seed_labs_fixture(db_session):
    """Ensures the 4 canonical synthetic scenarios and datasets are seeded."""
    await seed_virtual_labs(db_session)


@pytest.fixture
async def test_officer(db_session):
    """Retrieves an employee for testing."""
    emp_res = await db_session.execute(select(Employee).limit(1))
    return emp_res.scalar_one()


@pytest.fixture
async def second_officer(db_session):
    """Retrieves a second employee for employee isolation testing."""
    emp_res = await db_session.execute(select(Employee).offset(1).limit(1))
    emp = emp_res.scalar_one_or_none()
    if not emp:
        # Create a second employee if only 1 exists
        emp = Employee(
            id=uuid.uuid4(),
            employee_code="EMP-TEST-02",
            full_name="Test Officer Isolation",
            designation="Statistical Officer",
            experience_years=3,
        )
        db_session.add(emp)
        await db_session.commit()
    return emp


# =============================================================================
# 1-4. Scenario Listing, Retrieval & Synthetic Enforcement
# =============================================================================

@pytest.mark.asyncio
async def test_list_labs_and_filters(db_session, test_officer):
    """1. List labs with status and competency filters."""
    service = LabService(db_session)
    labs = await service.list_scenarios()
    assert len(labs) >= 4

    # Verify scenario types
    types = {lab.scenario_type for lab in labs}
    assert "DATA_QUALITY_AUDIT" in types
    assert "SURVEY_SAMPLING" in types
    assert "DESCRIPTIVE_STATISTICS" in types
    assert "MISSING_DATA_ANALYSIS" in types

    # Filter by difficulty
    intermediate_labs = await service.list_scenarios(difficulty="INTERMEDIATE")
    assert all(l.difficulty == "INTERMEDIATE" for l in intermediate_labs)


@pytest.mark.asyncio
async def test_get_scenario_detail_and_synthetic_enforcement(db_session):
    """2 & 21. Get scenario detail and enforce synthetic dataset status."""
    service = LabService(db_session)
    scenario = await service.get_scenario_detail(SCENARIO_DQ_ID)
    assert scenario.id == SCENARIO_DQ_ID
    assert scenario.is_synthetic is True
    assert scenario.dataset.is_synthetic is True
    assert scenario.dataset.row_count > 0
    assert len(scenario.dataset.dataset_json) == scenario.dataset.row_count
    assert "record_id" in scenario.dataset.schema_definition


@pytest.mark.asyncio
async def test_start_session_lifecycle(db_session, test_officer):
    """3. Start a new virtual lab session."""
    service = LabService(db_session)
    session = await service.start_session(test_officer.id, SCENARIO_DQ_ID)
    assert session.status == "IN_PROGRESS"
    assert session.employee_id == test_officer.id
    assert session.scenario_id == SCENARIO_DQ_ID
    assert session.current_step == 1
    assert session.score == 0.0


# =============================================================================
# 5. Data Quality Audit Step Actions & Scoring
# =============================================================================

@pytest.mark.asyncio
async def test_data_quality_audit_flow(db_session, test_officer):
    """5, 9, 10, 11. Data Quality actions, correct scoring, and feedback."""
    service = LabService(db_session)
    session = await service.start_session(test_officer.id, SCENARIO_DQ_ID)

    # Step 1: Identify anomalies
    res1 = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(
            step_number=1,
            action_type="IDENTIFY_ISSUES",
            action_payload={"identified_issues": ["DUPLICATE_ROWS", "OUT_OF_RANGE", "INVALID_CODE", "INCONSISTENT_CATEGORY"]},
        ),
    )
    assert res1.is_correct is True
    assert res1.score_awarded == 25.0
    assert "duplicate" in res1.feedback.lower()
    assert res1.next_step == 2

    # Step 2: Select validation rule
    res2 = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(
            step_number=2,
            action_type="SELECT_VALIDATION_RULE",
            action_payload={"selected_rules": ["NQAF_UNIQUE_KEY", "NQAF_RANGE_CHECK"]},
        ),
    )
    assert res2.is_correct is True
    assert res2.score_awarded == 25.0

    # Step 3: Apply correction
    res3 = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(
            step_number=3,
            action_type="APPLY_CORRECTION",
            action_payload={"correction_strategy": "DEDUPLICATE_AND_CLEAN", "apply_all": True},
        ),
    )
    assert res3.is_correct is True
    assert res3.score_awarded == 25.0
    assert res3.metrics["duplicates_removed"] >= 1

    # Step 4: Submit Quality Report
    res4 = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(
            step_number=4,
            action_type="SUBMIT_QUALITY_REPORT",
            action_payload={"report_notes": "All NQAF validation protocols satisfied."},
        ),
    )
    assert res4.is_correct is True
    assert res4.score_awarded == 25.0
    assert res4.is_completed is True


# =============================================================================
# 6. Survey Sampling Flow & Deterministic Simulation
# =============================================================================

@pytest.mark.asyncio
async def test_survey_sampling_flow(db_session, test_officer):
    """6. Survey sampling actions: method, sample size, strata, and deterministic sample draw."""
    service = LabService(db_session)
    session = await service.start_session(test_officer.id, SCENARIO_SAMPLING_ID)

    # Step 1: Method
    res1 = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(
            step_number=1,
            action_type="SELECT_SAMPLING_METHOD",
            action_payload={"sampling_method": "STRATIFIED"},
        ),
    )
    assert res1.is_correct is True
    assert res1.score_awarded == 25.0
    assert "stratified" in res1.feedback.lower()

    # Step 2: Sample size
    res2 = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(
            step_number=2,
            action_type="SET_SAMPLE_SIZE",
            action_payload={"sample_size": 30},
        ),
    )
    assert res2.is_correct is True
    assert res2.score_awarded == 25.0

    # Step 3: Configure strata
    res3 = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(
            step_number=3,
            action_type="CONFIGURE_STRATA",
            action_payload={"strata_fields": ["region", "sector"], "allocation_method": "PROPORTIONAL"},
        ),
    )
    assert res3.is_correct is True

    # Step 4: Execute deterministic simulation
    res4 = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(
            step_number=4,
            action_type="EXECUTE_SIMULATION",
            action_payload={"sample_size": 30},
        ),
    )
    assert res4.is_correct is True
    assert res4.metrics["total_sampled"] > 0
    assert len(res4.data_preview) > 0


# =============================================================================
# 7. Descriptive Statistics (Authoritative Backend Computation)
# =============================================================================

@pytest.mark.asyncio
async def test_descriptive_statistics_backend_authority(db_session, test_officer):
    """7. Backend calculates authoritative mean, median, min, max, stdev."""
    service = LabService(db_session)
    session = await service.start_session(test_officer.id, SCENARIO_DESC_ID)

    # Step 1: Central Tendency
    res1 = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(
            step_number=1,
            action_type="CALCULATE_CENTRAL_TENDENCY",
            action_payload={"metrics": ["MEAN", "MEDIAN"]},
        ),
    )
    assert res1.is_correct is True
    assert res1.metrics["mean"] > 0
    assert res1.metrics["median"] > 0

    # Step 2: Dispersion
    res2 = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(
            step_number=2,
            action_type="CALCULATE_DISPERSION",
            action_payload={"metrics": ["MIN", "MAX", "STD_DEV"]},
        ),
    )
    assert res2.is_correct is True
    assert res2.metrics["std_dev"] > 0

    # Step 3: Interpretation
    res3 = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(
            step_number=3,
            action_type="INTERPRET_DISTRIBUTION",
            action_payload={"skewness_diagnosis": "RIGHT_SKEWED", "recommended_central_measure": "MEDIAN"},
        ),
    )
    assert res3.is_correct is True
    assert res3.score_awarded == 30.0


# =============================================================================
# 8. Missing Data Analysis Flow
# =============================================================================

@pytest.mark.asyncio
async def test_missing_data_analysis_flow(db_session, test_officer):
    """8. Missing data rate detection, MAR mechanism diagnosis, and imputation."""
    service = LabService(db_session)
    session = await service.start_session(test_officer.id, SCENARIO_MISSING_ID)

    # Step 1: Detect Rates
    res1 = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(step_number=1, action_type="IDENTIFY_MISSING_RATES"),
    )
    assert res1.is_correct is True
    assert "annual_turnover_lakhs" in res1.metrics["missing_percentages"]

    # Step 2: Diagnose Mechanism
    res2 = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(step_number=2, action_type="DIAGNOSE_PATTERN", action_payload={"mechanism": "MAR"}),
    )
    assert res2.is_correct is True

    # Step 3: Strategy
    res3 = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(step_number=3, action_type="SELECT_STRATEGY", action_payload={"handling_strategy": "MEDIAN_IMPUTATION"}),
    )
    assert res3.is_correct is True

    # Step 4: Evaluate Impact
    res4 = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(step_number=4, action_type="EVALUATE_IMPUTATION_IMPACT"),
    )
    assert res4.is_correct is True
    assert res4.metrics["imputed_value"] > 0


# =============================================================================
# 12-16. Hints, Completion, Results, Evidence Creation & Confidence
# =============================================================================

@pytest.mark.asyncio
async def test_hints_and_completion_and_evidence(db_session, test_officer):
    """12, 13, 14, 15, 16. Test hint, session completion, score, confidence, and CompetencyEvidence."""
    service = LabService(db_session)
    session = await service.start_session(test_officer.id, SCENARIO_DQ_ID)

    # 12. Request hint
    hint = await service.get_hint(test_officer.id, session.id, step_number=1)
    assert hint.step_number == 1
    assert len(hint.hint) > 10

    # Perform all 4 steps
    for step in range(1, 5):
        action_type = ["IDENTIFY_ISSUES", "SELECT_VALIDATION_RULE", "APPLY_CORRECTION", "SUBMIT_QUALITY_REPORT"][step - 1]
        payload = {
            1: {"identified_issues": ["DUPLICATE_ROWS", "OUT_OF_RANGE", "INVALID_CODE"]},
            2: {"selected_rules": ["NQAF_UNIQUE_KEY", "NQAF_RANGE_CHECK"]},
            3: {"correction_strategy": "DEDUPLICATE_AND_CLEAN", "apply_all": True},
            4: {"report_notes": "Validated"},
        }[step]
        await service.submit_action(
            test_officer.id,
            session.id,
            LabActionSubmitRequest(step_number=step, action_type=action_type, action_payload=payload),
        )

    # 13 & 14. Complete session & get result
    complete_res = await service.complete_session(test_officer.id, session.id)
    assert complete_res.total_score == 100.0
    assert complete_res.percentage == 100.0
    assert complete_res.passed is True
    assert 0.70 <= complete_res.confidence <= 0.95
    assert complete_res.evidence_id is not None

    # 15. Verify CompetencyEvidence in assessment evidence table
    ev = await db_session.get(CompetencyEvidence, complete_res.evidence_id)
    assert ev is not None
    assert ev.employee_id == test_officer.id
    assert ev.evidence_type == EvidenceType.VIRTUAL_LAB.value
    assert ev.raw_value == 100.0

    # 16. Verify result report
    result_detail = await service.get_result(test_officer.id, session.id)
    assert result_detail.total_score == 100.0
    assert result_detail.actions_completed == 4
    assert result_detail.correct_actions == 4
    assert len(result_detail.learning_feedback) == 4


# =============================================================================
# 17-18. Idempotency (Duplicate Action & Duplicate Completion)
# =============================================================================

@pytest.mark.asyncio
async def test_idempotency_duplicate_action_and_completion(db_session, test_officer):
    """17 & 18. Submitting same action twice does not double-count; duplicate completion returns existing result."""
    service = LabService(db_session)
    session = await service.start_session(test_officer.id, SCENARIO_SAMPLING_ID)

    # Submit step 1
    req1 = LabActionSubmitRequest(
        step_number=1,
        action_type="SELECT_SAMPLING_METHOD",
        action_payload={"sampling_method": "STRATIFIED"},
    )
    first_res = await service.submit_action(test_officer.id, session.id, req1)
    assert first_res.score_awarded == 25.0

    # Resubmit same step 1 (Idempotent)
    second_res = await service.submit_action(test_officer.id, session.id, req1)
    assert second_res.action_id == first_res.action_id
    assert second_res.current_score == 25.0  # NOT 50.0

    # Complete remaining steps to complete
    await service.submit_action(test_officer.id, session.id, LabActionSubmitRequest(step_number=2, action_type="SET_SAMPLE_SIZE", action_payload={"sample_size": 30}))
    await service.submit_action(test_officer.id, session.id, LabActionSubmitRequest(step_number=3, action_type="CONFIGURE_STRATA", action_payload={"strata_fields": ["region", "sector"]}))
    await service.submit_action(test_officer.id, session.id, LabActionSubmitRequest(step_number=4, action_type="EXECUTE_SIMULATION", action_payload={"sample_size": 30}))

    comp1 = await service.complete_session(test_officer.id, session.id)
    comp2 = await service.complete_session(test_officer.id, session.id)

    # Same evidence_id returned, no duplicate records created
    assert comp1.evidence_id == comp2.evidence_id
    assert comp1.total_score == comp2.total_score


# =============================================================================
# 19-20. Employee Isolation & Unauthorized Access
# =============================================================================

@pytest.mark.asyncio
async def test_employee_isolation(db_session, test_officer, second_officer):
    """19 & 20. Employee B cannot access or submit actions to Employee A's lab session."""
    service = LabService(db_session)
    session_a = await service.start_session(test_officer.id, SCENARIO_DQ_ID)

    # Officer B tries to view session A -> 403
    with pytest.raises(PragyaException) as exc_get:
        await service.get_session(second_officer.id, session_a.id)
    assert exc_get.value.status_code == 403

    # Officer B tries to submit action to session A -> 403
    with pytest.raises(PragyaException) as exc_action:
        await service.submit_action(
            second_officer.id,
            session_a.id,
            LabActionSubmitRequest(step_number=1, action_type="IDENTIFY_ISSUES"),
        )
    assert exc_action.value.status_code == 403

    # Officer B tries to complete session A -> 403
    with pytest.raises(PragyaException) as exc_comp:
        await service.complete_session(second_officer.id, session_a.id)
    assert exc_comp.value.status_code == 403


# =============================================================================
# 22. Security Sandbox: Reject Arbitrary Code Execution
# =============================================================================

@pytest.mark.asyncio
async def test_security_sandbox_rejects_arbitrary_code(db_session, test_officer):
    """22. Injections like eval, exec, DROP TABLE, or import are rejected by sandbox."""
    service = LabService(db_session)
    session = await service.start_session(test_officer.id, SCENARIO_DQ_ID)

    # Python exec injection attempt
    with pytest.raises(PragyaException) as exc_py:
        await service.submit_action(
            test_officer.id,
            session.id,
            LabActionSubmitRequest(
                step_number=1,
                action_type="IDENTIFY_ISSUES",
                action_payload={"code": "import os; os.system('whoami')"},
            ),
        )
    assert exc_py.value.code == "SECURITY_SANDBOX_VIOLATION"

    # SQL injection attempt
    with pytest.raises(PragyaException) as exc_sql:
        await service.submit_action(
            test_officer.id,
            session.id,
            LabActionSubmitRequest(
                step_number=1,
                action_type="IDENTIFY_ISSUES",
                action_payload={"query": "SELECT * FROM employees; DROP TABLE lab_actions;"},
            ),
        )
    assert exc_sql.value.code == "SECURITY_SANDBOX_VIOLATION"


# =============================================================================
# 23-25. Skill-Gap Targeting, Competency Linking & Abandonment
# =============================================================================

@pytest.mark.asyncio
async def test_skill_gap_targeting_and_abandonment(db_session, test_officer):
    """23, 24, 25. Skill gap competency targeting and abandoned session behavior."""
    service = LabService(db_session)

    # Target specific competency
    scenario = await service.get_scenario_detail(SCENARIO_SAMPLING_ID)
    comp_id = scenario.competency_id

    targeted_labs = await service.list_scenarios(competency_id=comp_id)
    assert any(l.id == SCENARIO_SAMPLING_ID for l in targeted_labs)

    # 25. Abandoned session
    session = await service.start_session(test_officer.id, SCENARIO_SAMPLING_ID)
    abandoned = await service.abandon_session(test_officer.id, session.id)
    assert abandoned.status == "ABANDONED"

    # Actions and completion rejected on abandoned session
    with pytest.raises(PragyaException) as exc_act:
        await service.submit_action(
            test_officer.id,
            session.id,
            LabActionSubmitRequest(step_number=1, action_type="SELECT_SAMPLING_METHOD"),
        )
    assert exc_act.value.code == "SESSION_NOT_IN_PROGRESS"

    with pytest.raises(PragyaException) as exc_comp:
        await service.complete_session(test_officer.id, session.id)
    assert exc_comp.value.code == "SESSION_ABANDONED"


# =============================================================================
# 28-29. HTTP API Integration (Quiz & Adaptive Assessment linkable)
# =============================================================================

@pytest.mark.asyncio
async def test_http_api_endpoints_full_lifecycle(test_officer):
    """28 & 29. Test HTTP API routes via FastAPI AsyncClient."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        headers = {"X-Employee-Id": str(test_officer.id)}

        # 1. GET /api/v1/labs
        res_list = await ac.get("/api/v1/labs", headers=headers)
        assert res_list.status_code == 200
        labs_data = res_list.json()
        assert len(labs_data) >= 4

        # 2. GET /api/v1/labs/{scenario_id}
        res_sc = await ac.get(f"/api/v1/labs/{SCENARIO_DQ_ID}", headers=headers)
        assert res_sc.status_code == 200
        sc_data = res_sc.json()
        assert sc_data["id"] == str(SCENARIO_DQ_ID)
        assert len(sc_data["dataset"]["dataset_json"]) > 0

        # 3. POST /api/v1/labs/{scenario_id}/sessions
        res_start = await ac.post(f"/api/v1/labs/{SCENARIO_DQ_ID}/sessions", json={}, headers=headers)
        assert res_start.status_code == 201
        session_data = res_start.json()
        session_id = session_data["id"]

        # 4. POST /api/v1/lab-sessions/{session_id}/actions (Step 1)
        res_act = await ac.post(
            f"/api/v1/lab-sessions/{session_id}/actions",
            json={
                "step_number": 1,
                "action_type": "IDENTIFY_ISSUES",
                "action_payload": {"identified_issues": ["DUPLICATE_ROWS", "OUT_OF_RANGE", "INVALID_CODE"]},
            },
            headers=headers,
        )
        assert res_act.status_code == 200
        act_data = res_act.json()
        assert act_data["is_correct"] is True

        # 5. POST /api/v1/lab-sessions/{session_id}/hint
        res_hint = await ac.post(
            f"/api/v1/lab-sessions/{session_id}/hint",
            json={"step_number": 2},
            headers=headers,
        )
        assert res_hint.status_code == 200
        assert "hint" in res_hint.json()

        # 6. Complete remaining steps and complete lab
        for s in [2, 3, 4]:
            await ac.post(
                f"/api/v1/lab-sessions/{session_id}/actions",
                json={
                    "step_number": s,
                    "action_type": ["SELECT_VALIDATION_RULE", "APPLY_CORRECTION", "SUBMIT_QUALITY_REPORT"][s - 2],
                    "action_payload": {"apply_all": True, "selected_rules": ["NQAF_UNIQUE_KEY", "NQAF_RANGE_CHECK"]},
                },
                headers=headers,
            )

        res_complete = await ac.post(f"/api/v1/lab-sessions/{session_id}/complete", headers=headers)
        assert res_complete.status_code == 200
        comp_data = res_complete.json()
        assert comp_data["passed"] is True

        # 7. GET /api/v1/lab-sessions/{session_id}/result
        res_res = await ac.get(f"/api/v1/lab-sessions/{session_id}/result", headers=headers)
        assert res_res.status_code == 200
        result_data = res_res.json()
        assert result_data["percentage"] >= 60.0
        assert len(result_data["actions_history"]) == 4


# =============================================================================
# Additional Edge Cases: Status, Invalid Actions, Partial/Incorrect Scoring
# =============================================================================

@pytest.mark.asyncio
async def test_scenario_status_draft_cannot_start(db_session, test_officer):
    """27. Scenarios in DRAFT or ARCHIVED status cannot be started."""
    scenario = await db_session.get(LabScenario, SCENARIO_DQ_ID)
    scenario.status = "DRAFT"
    await db_session.commit()

    service = LabService(db_session)
    with pytest.raises(PragyaException) as exc:
        await service.start_session(test_officer.id, SCENARIO_DQ_ID)
    assert exc.value.code == "SCENARIO_INACTIVE"

    # Restore
    scenario.status = "READY"
    await db_session.commit()


@pytest.mark.asyncio
async def test_invalid_action_sequence(db_session, test_officer):
    """26. Submitting out-of-order step number (e.g. step 3 when on step 1) is rejected."""
    service = LabService(db_session)
    session = await service.start_session(test_officer.id, SCENARIO_DQ_ID)

    with pytest.raises(PragyaException) as exc:
        await service.submit_action(
            test_officer.id,
            session.id,
            LabActionSubmitRequest(step_number=3, action_type="APPLY_CORRECTION"),
        )
    assert exc.value.code == "INVALID_STEP_SEQUENCE"


@pytest.mark.asyncio
async def test_partial_and_incorrect_scoring(db_session, test_officer):
    """10 & 11. Incorrect action yields 0 pts; partially correct action yields partial pts."""
    service = LabService(db_session)
    session = await service.start_session(test_officer.id, SCENARIO_DQ_ID)

    # Completely incorrect issues -> 0 pts
    res_inc = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(
            step_number=1,
            action_type="IDENTIFY_ISSUES",
            action_payload={"identified_issues": ["NOT_AN_ISSUE", "RANDOM_FLAG"]},
        ),
    )
    assert res_inc.is_correct is False
    assert res_inc.score_awarded == 0.0

    # Start sampling session to test partial scoring
    samp_session = await service.start_session(test_officer.id, SCENARIO_SAMPLING_ID)
    # SIMPLE_RANDOM is partially valid (12 pts awarded instead of 25)
    res_part = await service.submit_action(
        test_officer.id,
        samp_session.id,
        LabActionSubmitRequest(
            step_number=1,
            action_type="SELECT_SAMPLING_METHOD",
            action_payload={"sampling_method": "SIMPLE_RANDOM"},
        ),
    )
    assert res_part.is_correct is False
    assert 0.0 < res_part.score_awarded < 25.0


@pytest.mark.asyncio
async def test_quiz_and_adaptive_assessment_integration_links(db_session, test_officer):
    """28 & 29. Virtual lab links to existing Quiz and Adaptive Assessment engines via competency."""
    service = LabService(db_session)
    scenario = await service.get_scenario_detail(SCENARIO_SAMPLING_ID)
    comp_id = scenario.competency_id

    # Verify that competency exists and can be targeted by quiz or adaptive assessment
    comp = await db_session.get(Competency, comp_id)
    assert comp is not None
    assert comp.code == "STAT_SAMPLING"


# =============================================================================
# Bug 5 Regression Tests: Premature Completion Rejection & My Sessions
# =============================================================================

@pytest.mark.asyncio
async def test_lab_premature_completion_rejected_until_all_steps_completed(db_session, test_officer):
    """
    REGRESSION BUG 5:
    Executing only 1 step ('Run Analysis') must NOT allow lab completion.
    Must reject premature completion with INCOMPLETE_LAB_STEPS (HTTP 400).
    Only completing all simulation steps allows completion and evidence recording.
    """
    service = LabService(db_session)
    session = await service.start_session(test_officer.id, SCENARIO_DQ_ID)

    # Execute only step 1 (Analysis)
    await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(
            step_number=1,
            action_type="IDENTIFY_ISSUES",
            action_payload={"identified_issues": ["DUPLICATE_ROWS", "OUT_OF_RANGE", "INVALID_CODE"]},
        ),
    )

    # Attempt premature completion -> MUST FAIL with 400
    with pytest.raises(PragyaException) as exc_info:
        await service.complete_session(test_officer.id, session.id)

    assert exc_info.value.status_code == 400
    assert exc_info.value.code == "INCOMPLETE_LAB_STEPS"
    assert "steps must be completed" in exc_info.value.message.lower()

    # Session status must remain IN_PROGRESS
    reloaded_session = await service.get_session(test_officer.id, session.id)
    assert reloaded_session.status == "IN_PROGRESS"

    # Now execute remaining steps: 2, 3, 4
    for step in range(2, 5):
        action_type = ["SELECT_VALIDATION_RULE", "APPLY_CORRECTION", "SUBMIT_QUALITY_REPORT"][step - 2]
        payload = {
            2: {"selected_rules": ["NQAF_UNIQUE_KEY", "NQAF_RANGE_CHECK"]},
            3: {"correction_strategy": "DEDUPLICATE_AND_CLEAN", "apply_all": True},
            4: {"report_notes": "Validated microdata report"},
        }[step]
        await service.submit_action(
            test_officer.id,
            session.id,
            LabActionSubmitRequest(step_number=step, action_type=action_type, action_payload=payload),
        )

    # Completion now succeeds
    complete_res = await service.complete_session(test_officer.id, session.id)
    assert complete_res.total_score == 100.0
    assert complete_res.passed is True
    assert complete_res.evidence_id is not None


@pytest.mark.asyncio
async def test_lab_get_my_sessions_endpoint(db_session, test_officer):
    """
    REGRESSION BUG 5:
    Endpoint GET /api/v1/labs/sessions/my returns real lab sessions for current employee.
    """
    service = LabService(db_session)
    session = await service.start_session(test_officer.id, SCENARIO_SAMPLING_ID)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(
            "/api/v1/labs/sessions/my",
            headers={"X-Employee-Id": str(test_officer.id)},
        )
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        found = next((s for s in data if s["id"] == str(session.id)), None)
        assert found is not None
        assert found["scenario_id"] == str(SCENARIO_SAMPLING_ID)
        assert found["status"] in ("IN_PROGRESS", "COMPLETED")


# =============================================================================
# REGRESSION SUITE: SPECIFIC TESTS A - J
# =============================================================================

@pytest.mark.asyncio
async def test_regression_a_valid_step_3_analysis_completes(db_session, test_officer):
    """A. Valid Step 3 configuration successfully completes analysis and returns strata metrics."""
    service = LabService(db_session)
    session = await service.start_session(test_officer.id, SCENARIO_SAMPLING_ID)

    # Execute step 1 and 2
    await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(step_number=1, action_type="SELECT_SAMPLING_METHOD", action_payload={"sampling_method": "STRATIFIED"}),
    )
    await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(step_number=2, action_type="SET_SAMPLE_SIZE", action_payload={"sample_size": 30}),
    )

    # Valid Step 3
    res3 = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(
            step_number=3,
            action_type="CONFIGURE_STRATA",
            action_payload={"strata_fields": ["region", "sector"], "allocation_method": "PROPORTIONAL"},
        ),
    )
    assert res3.is_correct is True
    assert res3.score_awarded == 25.0
    assert "strata_partitions" in res3.metrics
    assert res3.is_completed is False


@pytest.mark.asyncio
async def test_regression_b_invalid_step_3_rejected(db_session, test_officer):
    """B. Invalid Step 3 configuration is rejected with partial/low score and not awarded full points."""
    service = LabService(db_session)
    session = await service.start_session(test_officer.id, SCENARIO_SAMPLING_ID)

    await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(step_number=1, action_type="SELECT_SAMPLING_METHOD", action_payload={"sampling_method": "STRATIFIED"}),
    )
    await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(step_number=2, action_type="SET_SAMPLE_SIZE", action_payload={"sample_size": 30}),
    )

    # Invalid Step 3: invalid strata field and invalid allocation method
    res3 = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(
            step_number=3,
            action_type="CONFIGURE_STRATA",
            action_payload={"strata_fields": ["invalid_col"], "allocation_method": "RANDOM_GUESS"},
        ),
    )
    assert res3.is_correct is False
    assert res3.score_awarded <= 10.0


@pytest.mark.asyncio
async def test_regression_d_step3_analysis_does_not_complete_lab(db_session, test_officer):
    """D. Step 3 analysis does NOT complete the entire lab."""
    service = LabService(db_session)
    session = await service.start_session(test_officer.id, SCENARIO_SAMPLING_ID)

    for step, p, at in [
        (1, {"sampling_method": "STRATIFIED"}, "SELECT_SAMPLING_METHOD"),
        (2, {"sample_size": 30}, "SET_SAMPLE_SIZE"),
        (3, {"strata_fields": ["region", "sector"], "allocation_method": "PROPORTIONAL"}, "CONFIGURE_STRATA"),
    ]:
        res = await service.submit_action(
            test_officer.id,
            session.id,
            LabActionSubmitRequest(step_number=step, action_type=at, action_payload=p),
        )
        assert res.is_completed is False

    reloaded = await service.get_session(test_officer.id, session.id)
    assert reloaded.status == "IN_PROGRESS"
    assert len(reloaded.actions) == 3


@pytest.mark.asyncio
async def test_regression_e_f_step4_required_before_final_completion(db_session, test_officer):
    """E & F. Step 4 is required before final lab completion; premature completion is rejected."""
    service = LabService(db_session)
    session = await service.start_session(test_officer.id, SCENARIO_SAMPLING_ID)

    # Steps 1 to 3
    for step, p, at in [
        (1, {"sampling_method": "STRATIFIED"}, "SELECT_SAMPLING_METHOD"),
        (2, {"sample_size": 30}, "SET_SAMPLE_SIZE"),
        (3, {"strata_fields": ["region", "sector"], "allocation_method": "PROPORTIONAL"}, "CONFIGURE_STRATA"),
    ]:
        await service.submit_action(
            test_officer.id,
            session.id,
            LabActionSubmitRequest(step_number=step, action_type=at, action_payload=p),
        )

    # Attempt completion before step 4 -> Rejected!
    with pytest.raises(PragyaException) as exc_info:
        await service.complete_session(test_officer.id, session.id)
    assert exc_info.value.status_code == 400
    assert exc_info.value.code == "INCOMPLETE_LAB_STEPS"


@pytest.mark.asyncio
async def test_regression_g_h_i_realistic_scoring_from_validated_actions(db_session, test_officer):
    """
    G, H, I:
    - Score is calculated from validated actions.
    - Suboptimal choices (e.g. SRS in Step 1) produce realistic score (~87%, not 100%).
    - A single Run Analysis action cannot produce a completed 100% lab.
    """
    service = LabService(db_session)
    session = await service.start_session(test_officer.id, SCENARIO_SAMPLING_ID)

    # Step 1: Suboptimal method (SIMPLE_RANDOM awards 12.0 instead of 25.0)
    res1 = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(step_number=1, action_type="SELECT_SAMPLING_METHOD", action_payload={"sampling_method": "SIMPLE_RANDOM"}),
    )
    assert res1.is_correct is False
    assert res1.score_awarded == 12.0

    # Step 2: Optimal
    await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(step_number=2, action_type="SET_SAMPLE_SIZE", action_payload={"sample_size": 30}),
    )
    # Step 3: Optimal
    await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(step_number=3, action_type="CONFIGURE_STRATA", action_payload={"strata_fields": ["region", "sector"], "allocation_method": "PROPORTIONAL"}),
    )
    # Step 4: Optimal
    res4 = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(step_number=4, action_type="EXECUTE_SIMULATION", action_payload={"sample_size": 30}),
    )
    assert res4.is_completed is True

    # Complete session
    complete_res = await service.complete_session(test_officer.id, session.id)

    # Realistic score validation:
    # 12.0 + 25.0 + 25.0 + 25.0 = 87.0
    assert complete_res.total_score == 87.0
    assert complete_res.percentage == 87.0
    assert complete_res.correct_actions == 3
@pytest.mark.asyncio
async def test_regression_unselected_inputs_rejected(db_session, test_officer):
    """
    Learner input requirement:
    - Empty sampling_method in Step 1 receives 0 points and is rejected.
    - Missing sample_size in Step 2 receives 0 points and is rejected.
    - Missing strata/allocation in Step 3 receives 0 points and is rejected.
    - Untouched/default submissions cannot earn points or pass steps.
    """
    service = LabService(db_session)
    session = await service.start_session(test_officer.id, SCENARIO_SAMPLING_ID)

    # Step 1 with empty selection
    res1_empty = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(step_number=1, action_type="SELECT_SAMPLING_METHOD", action_payload={"sampling_method": ""}),
    )
    assert res1_empty.is_correct is False
    assert res1_empty.score_awarded == 0.0

    # Step 1 corrected with real learner selection
    res1_correct = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(step_number=1, action_type="SELECT_SAMPLING_METHOD", action_payload={"sampling_method": "STRATIFIED"}),
    )
    assert res1_correct.is_correct is True
    assert res1_correct.score_awarded == 25.0

    # Step 2 with missing/empty sample size
    res2_empty = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(step_number=2, action_type="SET_SAMPLE_SIZE", action_payload={"sample_size": None}),
    )
    assert res2_empty.is_correct is False
    assert res2_empty.score_awarded == 0.0

    # Step 2 corrected with real learner input
    res2_correct = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(step_number=2, action_type="SET_SAMPLE_SIZE", action_payload={"sample_size": 35}),
    )
    assert res2_correct.is_correct is True
    assert res2_correct.score_awarded == 25.0

    # Step 3 with empty strata list
    res3_empty = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(step_number=3, action_type="CONFIGURE_STRATA", action_payload={"strata_fields": [], "allocation_method": ""}),
    )
    assert res3_empty.is_correct is False
    assert res3_empty.score_awarded == 0.0

    # Step 3 corrected with real learner selection
    res3_correct = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(step_number=3, action_type="CONFIGURE_STRATA", action_payload={"strata_fields": ["region", "sector"], "allocation_method": "PROPORTIONAL"}),
    )
    assert res3_correct.is_correct is True
    assert res3_correct.score_awarded == 25.0

    # Step 4 execution
    res4 = await service.submit_action(
        test_officer.id,
        session.id,
        LabActionSubmitRequest(step_number=4, action_type="EXECUTE_SIMULATION", action_payload={"sample_size": 35}),
    )
    assert res4.is_correct is True
    assert res4.score_awarded == 25.0

    # Completion succeeds with 100% only because all steps were actively corrected and submitted
    comp = await service.complete_session(test_officer.id, session.id)
    assert comp.total_score == 100.0
    assert comp.passed is True


@pytest.mark.asyncio
async def test_step_4_and_completion_locking(db_session, test_officer):
    """Verifies that Step 4 is locked until Steps 1-3 succeed, and completion is locked until Step 4 succeeds."""
    service = LabService(db_session)
    session = await service.start_session(test_officer.id, SCENARIO_SAMPLING_ID)

    # 1. Attempting Step 4 right away fails
    with pytest.raises(PragyaException) as exc1:
        await service.submit_action(
            test_officer.id,
            session.id,
            LabActionSubmitRequest(step_number=4, action_type="EXECUTE_SIMULATION", action_payload={"sample_size": 30}),
        )
    assert exc1.value.code in ["INVALID_STEP_SEQUENCE", "STEP_LOCKED"]

    # 2. Attempting completion right away fails
    with pytest.raises(PragyaException) as exc2:
        await service.complete_session(test_officer.id, session.id)
    assert exc2.value.code == "INCOMPLETE_LAB_STEPS"




