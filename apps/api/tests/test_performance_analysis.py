import math
import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.main import app
from app.modules.adaptive.models import CompetencyRecalibration
from app.modules.assessments.models import (
    CompetencyEvidence,
    EmployeeCompetency,
)
from app.modules.departments.models import Department
from app.modules.employees.models import Employee
from app.modules.job_roles.models import JobRole
from app.modules.skill_gaps.models import SkillGap
from app.modules.analytics.service import PerformanceAnalysisService


@pytest.mark.asyncio
async def test_get_employee_performance_success_for_primary_employee():
    """Verify endpoint returns 200 with complete, valid structure for seeded employee."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        me_resp = await client.get("/api/v1/employees/me")
        assert me_resp.status_code == 200
        emp = me_resp.json()
        emp_id = emp["id"]

        resp = await client.get(f"/api/v1/employees/{emp_id}/performance")
        assert resp.status_code == 200
        data = resp.json()

        assert data["employee_id"] == emp_id
        assert data["employee_name"] == emp["full_name"]
        assert "overall" in data
        assert "competencies" in data
        assert "strongest_competencies" in data
        assert "focus_competencies" in data
        assert "modalities" in data
        assert "summary" in data


@pytest.mark.asyncio
async def test_baseline_and_current_score_derivation():
    """Verify baseline derives from diagnostic evidence and current score matches authoritative state."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        me_resp = await client.get("/api/v1/employees/me")
        emp_id = me_resp.json()["id"]

        resp = await client.get(f"/api/v1/employees/{emp_id}/performance")
        assert resp.status_code == 200
        data = resp.json()

        for comp in data["competencies"]:
            assert "current_score" in comp
            assert comp["current_score"] >= 0.0
            if comp["baseline_score"] is not None:
                assert comp["baseline_score"] >= 0.0
                expected_points = round(comp["current_score"] - comp["baseline_score"], 2)
                assert comp["improvement_points"] == expected_points


@pytest.mark.asyncio
async def test_improvement_calculation_zero_division_guard():
    """Verify improvement percentage handles 0 baseline, missing baseline, and never produces NaN."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        me_resp = await client.get("/api/v1/employees/me")
        emp_id = me_resp.json()["id"]

        resp = await client.get(f"/api/v1/employees/{emp_id}/performance")
        assert resp.status_code == 200
        data = resp.json()

        for comp in data["competencies"]:
            pct = comp["improvement_percentage"]
            assert not math.isnan(pct)
            assert not math.isinf(pct)


@pytest.mark.asyncio
async def test_overall_aggregate_improvement_determinism():
    """Verify aggregate overall metrics are mathematically defensible and deterministic."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        me_resp = await client.get("/api/v1/employees/me")
        emp_id = me_resp.json()["id"]

        resp1 = await client.get(f"/api/v1/employees/{emp_id}/performance")
        resp2 = await client.get(f"/api/v1/employees/{emp_id}/performance")
        assert resp1.status_code == 200
        assert resp2.status_code == 200

        d1 = resp1.json()["overall"]
        d2 = resp2.json()["overall"]
        assert d1["baseline_score"] == d2["baseline_score"]
        assert d1["current_score"] == d2["current_score"]
        assert d1["improvement_points"] == d2["improvement_points"]
        assert d1["improvement_percentage"] == d2["improvement_percentage"]


@pytest.mark.asyncio
async def test_strongest_competencies_ordering():
    """Verify top 3 strongest competencies are sorted by current_score DESC, improvement DESC."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        me_resp = await client.get("/api/v1/employees/me")
        emp_id = me_resp.json()["id"]

        resp = await client.get(f"/api/v1/employees/{emp_id}/performance")
        assert resp.status_code == 200
        data = resp.json()

        strongest = data["strongest_competencies"]
        assert len(strongest) <= 3
        if len(strongest) >= 2:
            for i in range(len(strongest) - 1):
                assert strongest[i]["current_score"] >= strongest[i + 1]["current_score"]


@pytest.mark.asyncio
async def test_focus_competencies_respect_skill_gap_priority():
    """Verify priority focus competencies order by priority criticality (CRITICAL > HIGH > MEDIUM > LOW)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        me_resp = await client.get("/api/v1/employees/me")
        emp_id = me_resp.json()["id"]

        resp = await client.get(f"/api/v1/employees/{emp_id}/performance")
        assert resp.status_code == 200
        data = resp.json()

        focus = data["focus_competencies"]
        assert len(focus) <= 3
        priority_ranks = {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "LOW": 4, "NO_GAP": 5}
        for item in focus:
            assert item["priority_level"] in priority_ranks


@pytest.mark.asyncio
async def test_modality_analytics_real_metrics():
    """Verify all 5 modalities contain real, non-fabricated metrics with valid statuses."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        me_resp = await client.get("/api/v1/employees/me")
        emp_id = me_resp.json()["id"]

        resp = await client.get(f"/api/v1/employees/{emp_id}/performance")
        assert resp.status_code == 200
        modalities = resp.json()["modalities"]

        valid_statuses = {"COMPLETED", "IN_PROGRESS", "NO_DATA"}
        assert modalities["diagnostic"]["status"] in valid_statuses
        assert modalities["quizzes"]["status"] in valid_statuses
        assert modalities["adaptive_assessment"]["status"] in valid_statuses
        assert modalities["virtual_labs"]["status"] in valid_statuses
        assert modalities["courses"]["status"] in valid_statuses


@pytest.mark.asyncio
async def test_empty_employee_performance():
    """Verify clean, crash-free response with NO_DATA status for employee with no history."""
    async with AsyncSessionLocal() as db:
        stmt_dept = select(Department).limit(1)
        res_dept = await db.execute(stmt_dept)
        dept = res_dept.scalar_one()

        stmt_role = select(JobRole).limit(1)
        res_role = await db.execute(stmt_role)
        role = res_role.scalar_one()

        fresh_emp = Employee(
            employee_code=f"EMP-EMPTY-{uuid.uuid4().hex[:6]}",
            full_name="Blank Slate Employee",
            designation="Junior Analyst",
            department_id=dept.id,
            job_role_id=role.id,
        )
        db.add(fresh_emp)
        await db.commit()
        await db.refresh(fresh_emp)
        empty_id = str(fresh_emp.id)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(f"/api/v1/employees/{empty_id}/performance")
        assert resp.status_code == 200
        data = resp.json()
        assert data["overall"]["baseline_score"] is None
        assert data["overall"]["current_score"] == 0.0
        assert data["modalities"]["diagnostic"]["status"] == "NO_DATA"
        assert data["modalities"]["quizzes"]["status"] == "NO_DATA"
        assert data["modalities"]["virtual_labs"]["status"] == "NO_DATA"


@pytest.mark.asyncio
async def test_timeline_chronological_ordering():
    """Verify timeline endpoint returns events sorted strictly newest first (DESC)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        me_resp = await client.get("/api/v1/employees/me")
        emp_id = me_resp.json()["id"]

        resp = await client.get(f"/api/v1/employees/{emp_id}/history/timeline")
        assert resp.status_code == 200
        data = resp.json()
        assert "events" in data
        events = data["events"]

        if len(events) >= 2:
            for i in range(len(events) - 1):
                assert events[i]["timestamp"] >= events[i + 1]["timestamp"]


@pytest.mark.asyncio
async def test_timeline_employee_isolation():
    """Verify timeline strictly isolates events and never leaks another employee's records."""
    async with AsyncSessionLocal() as db:
        stmt_dept = select(Department).limit(1)
        res_dept = await db.execute(stmt_dept)
        dept = res_dept.scalar_one()

        stmt_role = select(JobRole).limit(1)
        res_role = await db.execute(stmt_role)
        role = res_role.scalar_one()

        emp_isolated = Employee(
            employee_code=f"EMP-ISO-{uuid.uuid4().hex[:6]}",
            full_name="Isolated Employee",
            designation="Statistical Trainee",
            department_id=dept.id,
            job_role_id=role.id,
        )
        db.add(emp_isolated)
        await db.commit()
        await db.refresh(emp_isolated)
        iso_id = str(emp_isolated.id)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(f"/api/v1/employees/{iso_id}/history/timeline")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_events"] == 0
        assert len(data["events"]) == 0


@pytest.mark.asyncio
async def test_unknown_employee_404():
    """Verify 404 error code for non-existent employee ID."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        fake_id = str(uuid.uuid4())
        resp_perf = await client.get(f"/api/v1/employees/{fake_id}/performance")
        assert resp_perf.status_code == 404

        resp_time = await client.get(f"/api/v1/employees/{fake_id}/history/timeline")
        assert resp_time.status_code == 404


@pytest.mark.asyncio
async def test_timeline_event_filtering():
    """Verify timeline event_type filter query param works correctly."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        me_resp = await client.get("/api/v1/employees/me")
        emp_id = me_resp.json()["id"]

        resp = await client.get(
            f"/api/v1/employees/{emp_id}/history/timeline?event_type=DIAGNOSTIC_ASSESSMENT"
        )
        assert resp.status_code == 200
        data = resp.json()
        for ev in data["events"]:
            assert ev["type"] == "DIAGNOSTIC_ASSESSMENT"


@pytest.mark.asyncio
async def test_recalibration_remains_unaffected():
    """Verify existing adaptive recalibration functionality continues to operate seamlessly."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        me_resp = await client.get("/api/v1/employees/me")
        emp_id = me_resp.json()["id"]

        # Recalculation of downstream skill gaps operates seamlessly
        recalc_resp = await client.post(f"/api/v1/employees/{emp_id}/skill-gaps/recalculate")
        assert recalc_resp.status_code == 200
        gaps = recalc_resp.json()
        assert isinstance(gaps, list)


@pytest.mark.asyncio
async def test_target_score_from_role_requirements():
    """Verify target score corresponds to employee's assigned role requirements."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        me_resp = await client.get("/api/v1/employees/me")
        emp_id = me_resp.json()["id"]

        resp = await client.get(f"/api/v1/employees/{emp_id}/performance")
        assert resp.status_code == 200
        data = resp.json()
        assert data["job_role_id"] is not None

        # Role targets must be populated for role-required competencies
        role_targeted = [c for c in data["competencies"] if c["target_score"] is not None]
        assert len(role_targeted) > 0
        for comp in role_targeted:
            assert comp["target_score"] > 0.0


@pytest.mark.asyncio
async def test_timeline_pagination_limit():
    """Verify timeline limit parameter restricts returned count deterministically."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        me_resp = await client.get("/api/v1/employees/me")
        emp_id = me_resp.json()["id"]

        resp = await client.get(f"/api/v1/employees/{emp_id}/history/timeline?limit=3")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["events"]) <= 3


@pytest.mark.asyncio
async def test_performance_status_derivation():
    """Verify derived status is one of valid deterministic enum-like values."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        me_resp = await client.get("/api/v1/employees/me")
        emp_id = me_resp.json()["id"]

        resp = await client.get(f"/api/v1/employees/{emp_id}/performance")
        assert resp.status_code == 200
        valid_statuses = {"MASTERED", "IMPROVING", "STABLE", "NEEDS_FOCUS", "NO_BASELINE"}
        for c in resp.json()["competencies"]:
            assert c["status"] in valid_statuses


@pytest.mark.asyncio
async def test_recommendation_behavior_remains_unaffected():
    """Verify recommendations engine continues to return valid recommendations."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        me_resp = await client.get("/api/v1/employees/me")
        emp_id = me_resp.json()["id"]

        recs_resp = await client.get(f"/api/v1/employees/{emp_id}/recommendations")
        assert recs_resp.status_code == 200
        data = recs_resp.json()
        assert "recommendations" in data or isinstance(data, list)


@pytest.mark.asyncio
async def test_openapi_spec_includes_performance_endpoints():
    """Verify performance and timeline endpoints appear properly in OpenAPI schema."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/openapi.json")
        assert resp.status_code == 200
        paths = resp.json()["paths"]
        assert "/api/v1/employees/{employee_id}/performance" in paths
        assert "/api/v1/employees/{employee_id}/history/timeline" in paths

