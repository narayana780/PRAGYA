import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.main import app
from app.modules.assessments.models import EmployeeCompetency
from app.modules.competencies.models import Competency, CompetencyRequirement
from app.modules.employees.models import Employee
from app.modules.job_roles.models import JobRole
from app.modules.skill_gaps.constants import (
    DEFAULT_GAP_PRIORITY_CONFIG,
    calculate_priority_score,
    generate_gap_explanation,
    get_confidence_flag,
)
from app.modules.skill_gaps.models import SkillGap
from app.modules.skill_gaps.service import SkillGapService


@pytest.mark.asyncio
async def test_gap_calculation_positive_and_no_gap():
    """Test quantitative gap = max(required - current, 0)."""
    # Positive gap
    req = 80.0
    curr = 58.0
    gap = max(req - curr, 0.0)
    assert gap == 22.0

    # Current equals required -> no gap
    curr_eq = 80.0
    assert max(req - curr_eq, 0.0) == 0.0

    # Current exceeds required -> no negative gap
    curr_exceed = 95.0
    assert max(req - curr_exceed, 0.0) == 0.0


@pytest.mark.asyncio
async def test_priority_score_and_weights():
    """Verify priority score multi-factor weighting formula."""
    gap = 35.0
    crit = "HIGH"  # 75
    task = "HIGH"  # 100
    urg = "MEDIUM"  # 60
    conf = 0.80  # 80

    score, level, breakdown = calculate_priority_score(
        gap_score=gap,
        criticality=crit,
        task_relevance=task,
        mission_urgency=urg,
        confidence=conf,
    )

    # 35 * 0.40 = 14.0
    # 75 * 0.25 = 18.75
    # 100 * 0.15 = 15.0
    # 60 * 0.10 = 6.0
    # 80 * 0.10 = 8.0
    # Total = 61.75
    assert breakdown["gap_component"] == 14.0
    assert breakdown["criticality_component"] == 18.75
    assert breakdown["task_relevance_component"] == 15.0
    assert breakdown["mission_urgency_component"] == 6.0
    assert breakdown["confidence_component"] == 8.0
    assert score == 61.75
    assert level == "HIGH"


@pytest.mark.asyncio
async def test_criticality_weighting_variation():
    """Changing role criticality alone strictly shifts priority score by expected delta."""
    gap = 40.0
    task = "MEDIUM"
    urg = "MEDIUM"
    conf = 0.50

    score_crit, _, _ = calculate_priority_score(gap, "CRITICAL", task, urg, conf)
    score_low, _, _ = calculate_priority_score(gap, "LOW", task, urg, conf)

    # CRITICAL (100 * 0.25 = 25) vs LOW (25 * 0.25 = 6.25) -> Delta: 18.75 pts
    assert round(score_crit - score_low, 2) == 18.75


@pytest.mark.asyncio
async def test_task_relevance_and_mission_urgency_weighting():
    """Verify task relevance (15%) and mission urgency (10%) components."""
    gap = 50.0
    crit = "HIGH"
    conf = 0.60

    score_high_task, _, _ = calculate_priority_score(gap, crit, "HIGH", "LOW", conf)
    score_low_task, _, _ = calculate_priority_score(gap, crit, "LOW", "LOW", conf)
    # (100 - 30) * 0.15 = 70 * 0.15 = 10.5
    assert round(score_high_task - score_low_task, 2) == 10.5

    score_high_urg, _, _ = calculate_priority_score(gap, crit, "LOW", "HIGH", conf)
    score_low_urg, _, _ = calculate_priority_score(gap, crit, "LOW", "LOW", conf)
    # (100 - 30) * 0.10 = 70 * 0.10 = 7.0
    assert round(score_high_urg - score_low_urg, 2) == 7.0


@pytest.mark.asyncio
async def test_confidence_weighting_and_flags():
    """Verify confidence mapping, weighting, and confidence status flags."""
    assert get_confidence_flag(0.25) == "LOW_CONFIDENCE"
    assert get_confidence_flag(0.55) == "MEDIUM_CONFIDENCE"
    assert get_confidence_flag(0.75) == "HIGH_CONFIDENCE"
    assert get_confidence_flag(0.90) == "VERY_HIGH_CONFIDENCE"

    gap = 30.0
    crit = "MEDIUM"
    task = "MEDIUM"
    urg = "MEDIUM"

    score_high_conf, _, b_high = calculate_priority_score(gap, crit, task, urg, 1.0)
    score_zero_conf, _, b_zero = calculate_priority_score(gap, crit, task, urg, 0.0)

    # 1.0 * 100 * 0.10 = 10.0 vs 0.0 -> Delta: 10.0
    assert b_high["confidence_component"] == 10.0
    assert b_zero["confidence_component"] == 0.0
    assert round(score_high_conf - score_zero_conf, 2) == 10.0


@pytest.mark.asyncio
async def test_priority_threshold_levels():
    """Verify classification into NO_GAP, LOW, MEDIUM, HIGH, CRITICAL."""
    # NO GAP
    s0, l0, _ = calculate_priority_score(0.0, "CRITICAL", "HIGH", "HIGH", 1.0)
    assert s0 == 0.0
    assert l0 == "NO_GAP"

    # LOW (< 25)
    s_low, l_low, _ = calculate_priority_score(5.0, "LOW", "LOW", "LOW", 0.1)
    assert l_low == "LOW"

    # MEDIUM (25 - 49.99)
    s_med, l_med, _ = calculate_priority_score(25.0, "MEDIUM", "MEDIUM", "MEDIUM", 0.5)
    assert l_med == "MEDIUM"

    # HIGH (50 - 74.99)
    s_high, l_high, _ = calculate_priority_score(50.0, "HIGH", "HIGH", "HIGH", 0.7)
    assert l_high == "HIGH"

    # CRITICAL (>= 75)
    s_crit, l_crit, _ = calculate_priority_score(90.0, "CRITICAL", "HIGH", "HIGH", 0.9)
    assert l_crit == "CRITICAL"


@pytest.mark.asyncio
async def test_low_confidence_explanation_flag():
    """Verify explainability template contains warning when confidence is LOW."""
    exp_low = generate_gap_explanation(
        competency_name="GIS",
        role_name="Statistical Officer",
        current_score=25.0,
        required_score=60.0,
        gap_score=35.0,
        priority_level="HIGH",
        criticality="HIGH",
        task_relevance="MEDIUM",
        mission_urgency="HIGH",
        confidence=0.25,
    )
    assert "potential gap" in exp_low
    assert "evidence confidence is low" in exp_low

    exp_high = generate_gap_explanation(
        competency_name="Sampling",
        role_name="Statistical Officer",
        current_score=50.0,
        required_score=70.0,
        gap_score=20.0,
        priority_level="HIGH",
        criticality="HIGH",
        task_relevance="HIGH",
        mission_urgency="HIGH",
        confidence=0.80,
    )
    assert "potential gap" not in exp_high
    assert "HIGH priority for capacity building" in exp_high


@pytest.mark.asyncio
async def test_get_employee_skill_gaps_api():
    """Verify GET /api/v1/employees/{id}/skill-gaps endpoint returns computed gaps."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Fetch current demo employee
        emp_resp = await client.get("/api/v1/employees/me")
        assert emp_resp.status_code == 200
        emp_id = emp_resp.json()["id"]

        # Fetch skill gaps
        resp = await client.get(f"/api/v1/employees/{emp_id}/skill-gaps")
        assert resp.status_code == 200
        gaps = resp.json()
        assert isinstance(gaps, list)
        assert len(gaps) > 0

        # Verify attributes on first gap
        first = gaps[0]
        assert "competency_code" in first
        assert "gap_score" in first
        assert "priority_score" in first
        assert "priority_level" in first
        assert "priority_breakdown" in first
        assert "explanation" in first


@pytest.mark.asyncio
async def test_skill_gaps_summary_api():
    """Verify GET /api/v1/employees/{id}/skill-gaps/summary endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        emp_resp = await client.get("/api/v1/employees/me")
        emp_id = emp_resp.json()["id"]

        resp = await client.get(f"/api/v1/employees/{emp_id}/skill-gaps/summary")
        assert resp.status_code == 200
        summary = resp.json()

        assert "total_competencies" in summary
        assert "gaps_count" in summary
        assert "critical_count" in summary
        assert "high_count" in summary
        assert "medium_count" in summary
        assert "low_count" in summary
        assert "no_gap_count" in summary
        assert "average_gap" in summary

        # Total equals sum of priority counts
        sum_counts = (
            summary["critical_count"]
            + summary["high_count"]
            + summary["medium_count"]
            + summary["low_count"]
            + summary["no_gap_count"]
        )
        assert summary["total_competencies"] == sum_counts


@pytest.mark.asyncio
async def test_filter_gaps_by_priority_and_domain():
    """Verify query filtering by priority level and competency domain."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        emp_resp = await client.get("/api/v1/employees/me")
        emp_id = emp_resp.json()["id"]

        # Filter by priority=NO_GAP
        resp_prio = await client.get(
            f"/api/v1/employees/{emp_id}/skill-gaps?priority=NO_GAP"
        )
        assert resp_prio.status_code == 200
        for g in resp_prio.json():
            assert g["priority_level"] == "NO_GAP"
            assert g["gap_score"] == 0.0

        # Filter by domain=STATISTICAL
        resp_dom = await client.get(
            f"/api/v1/employees/{emp_id}/skill-gaps?domain=STATISTICAL"
        )
        assert resp_dom.status_code == 200
        for g in resp_dom.json():
            assert g["domain_code"] == "STATISTICAL"


@pytest.mark.asyncio
async def test_get_single_gap_detail_and_not_found():
    """Verify single gap detail endpoint and error handling for unknown competency."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        emp_resp = await client.get("/api/v1/employees/me")
        emp_id = emp_resp.json()["id"]

        gaps_resp = await client.get(f"/api/v1/employees/{emp_id}/skill-gaps")
        first_comp_id = gaps_resp.json()[0]["competency_id"]

        # Get detail
        detail_resp = await client.get(
            f"/api/v1/employees/{emp_id}/skill-gaps/{first_comp_id}"
        )
        assert detail_resp.status_code == 200
        assert detail_resp.json()["competency_id"] == first_comp_id

        # Unknown competency
        random_comp = str(uuid.uuid4())
        nf_resp = await client.get(
            f"/api/v1/employees/{emp_id}/skill-gaps/{random_comp}"
        )
        assert nf_resp.status_code == 404


@pytest.mark.asyncio
async def test_recalculate_skill_gaps_endpoint():
    """Verify POST /api/v1/employees/{id}/skill-gaps/recalculate forces recalculation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        emp_resp = await client.get("/api/v1/employees/me")
        emp_id = emp_resp.json()["id"]

        recalc_resp = await client.post(
            f"/api/v1/employees/{emp_id}/skill-gaps/recalculate"
        )
        assert recalc_resp.status_code == 200
        gaps = recalc_resp.json()
        assert isinstance(gaps, list)
        assert len(gaps) > 0


@pytest.mark.asyncio
async def test_unknown_employee_skill_gaps():
    """Verify 404 response for non-existent employee ID."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        fake_id = str(uuid.uuid4())
        resp = await client.post(
            f"/api/v1/employees/{fake_id}/skill-gaps/recalculate"
        )
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_competency_update_triggers_gap_recalculation():
    """Verify Stage 5 self-assessment submission seamlessly recalculates downstream skill gap."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        emp_resp = await client.get("/api/v1/employees/me")
        emp_id = emp_resp.json()["id"]

        # Find Python competency
        gaps_resp = await client.get(
            f"/api/v1/employees/{emp_id}/skill-gaps?competency=Python"
        )
        assert gaps_resp.status_code == 200
        py_gap = gaps_resp.json()[0]
        py_comp_id = py_gap["competency_id"]

        # Submit self-assessment for Python at Level 3 (Working -> score 60)
        sa_resp = await client.post(
            f"/api/v1/employees/{emp_id}/self-assessment",
            json={"competency_id": py_comp_id, "level": 3},
        )
        assert sa_resp.status_code == 201

        # Fetch refreshed skill gap for Python
        refreshed_gap_resp = await client.get(
            f"/api/v1/employees/{emp_id}/skill-gaps/{py_comp_id}"
        )
        assert refreshed_gap_resp.status_code == 200
        refreshed_gap = refreshed_gap_resp.json()
        assert refreshed_gap["current_score"] > 0


@pytest.mark.asyncio
async def test_duplicate_gap_prevention():
    """Verify recalculation updates existing records in place and never duplicates."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        emp_resp = await client.get("/api/v1/employees/me")
        emp_id = emp_resp.json()["id"]

        r1 = await client.post(f"/api/v1/employees/{emp_id}/skill-gaps/recalculate")
        assert r1.status_code == 200
        count1 = len(r1.json())

        r2 = await client.post(f"/api/v1/employees/{emp_id}/skill-gaps/recalculate")
        assert r2.status_code == 200
        count2 = len(r2.json())

        assert count1 == count2


@pytest.mark.asyncio
async def test_role_change_recalculation():
    """Verify changing an employee's role recalculates skill gaps against the new role profile."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Fetch available job roles
        roles_resp = await client.get("/api/v1/job-roles")
        assert roles_resp.status_code == 200
        roles = roles_resp.json()
        sso_role = next((r for r in roles if r["code"] == "SSO"), None)
        so_role = next((r for r in roles if r["code"] == "SO"), None)
        assert sso_role is not None and so_role is not None

        emp_resp = await client.get("/api/v1/employees/me")
        emp_id = emp_resp.json()["id"]

        # Recalculate against SSO role
        from app.db.session import AsyncSessionLocal
        from app.modules.skill_gaps.service import SkillGapService

        async with AsyncSessionLocal() as session:
            stmt = select(Employee).where(Employee.id == uuid.UUID(emp_id))
            res = await session.execute(stmt)
            emp = res.scalar_one()

            service = SkillGapService(session)
            try:
                # Change role to SSO
                emp.job_role_id = uuid.UUID(sso_role["id"])
                await session.commit()
                sso_gaps = await service.recalculate_employee_gaps(emp.id)
                assert len(sso_gaps) == 11  # SSO role has 11 competency requirements
            finally:
                # Reliably restore original role to Statistical Officer (SO)
                emp.job_role_id = uuid.UUID(so_role["id"])
                await session.commit()
                restored_gaps = await service.recalculate_employee_gaps(emp.id)
                assert len(restored_gaps) == 9  # SO role has 9 competency requirements


@pytest.mark.asyncio
async def test_filter_by_competency_and_unknown_competency():
    """Verify filtering by competency code/name and 404 for unknown competency."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        emp_resp = await client.get("/api/v1/employees/me")
        emp_id = emp_resp.json()["id"]

        # Filter by competency name
        resp = await client.get(f"/api/v1/employees/{emp_id}/skill-gaps?competency=Python")
        assert resp.status_code == 200
        gaps = resp.json()
        assert len(gaps) == 1
        assert "Python" in gaps[0]["competency_name"]

        # Detail for random unknown competency UUID returns 404
        random_comp_id = str(uuid.uuid4())
        resp_404 = await client.get(f"/api/v1/employees/{emp_id}/skill-gaps/{random_comp_id}")
        assert resp_404.status_code == 404
        assert resp_404.json()["error"]["code"] == "SKILL_GAP_NOT_FOUND"


@pytest.mark.asyncio
async def test_unknown_role_requirement_recalculate():
    """Verify recalculating a competency that is not in the employee's role requirements returns 404."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        emp_resp = await client.get("/api/v1/employees/me")
        emp_id = emp_resp.json()["id"]

        # Try to recalculate a non-existent requirement
        random_comp_id = str(uuid.uuid4())
        from app.db.session import AsyncSessionLocal
        from app.modules.skill_gaps.service import SkillGapService

        async with AsyncSessionLocal() as session:
            service = SkillGapService(session)
            gap = await service.recalculate_gap(uuid.UUID(emp_id), uuid.UUID(random_comp_id))
            assert gap is None


@pytest.mark.asyncio
async def test_employee_with_no_gaps_all_satisfied():
    """Verify gap math and summary when all requirements are met (gap = 0)."""
    # Unit level test of summary logic when all gaps are 0
    from app.modules.skill_gaps.constants import calculate_priority_score

    # Competency requirements met
    gap_score = max(round(70.0 - 85.0, 2), 0.0)
    assert gap_score == 0.0

    priority_score, priority_level, breakdown = calculate_priority_score(
        gap_score=gap_score,
        criticality="CRITICAL",
        task_relevance="HIGH",
        mission_urgency="HIGH",
        confidence=1.0,
    )
    assert priority_score == 0.0
    assert priority_level == "NO_GAP"
    assert breakdown["gap_component"] == 0.0
    assert breakdown["criticality_component"] == 0.0


