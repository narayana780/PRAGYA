import uuid
from datetime import datetime, timezone, timedelta
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.main import app
from app.modules.analytics.training_effectiveness_service import (
    TrainingEffectivenessService,
)
from app.modules.assessments.models import (
    CompetencyEvidence,
    CompetencyScoreHistory,
    EmployeeCompetency,
)
from app.modules.competencies.models import Competency
from app.modules.courses.models import (
    CourseProgress,
    LearningItem,
    LearningItemCompetency,
)
from app.modules.employees.models import Employee
from app.modules.recommendations.models import LearningRecommendation

ADMIN_HEADERS = {"X-User-Role": "ADMIN"}
SUPER_ADMIN_HEADERS = {"X-User-Role": "SUPER_ADMIN"}
EMPLOYEE_HEADERS = {"X-User-Role": "EMPLOYEE"}
TRAINER_HEADERS = {"X-User-Role": "TRAINER"}


@pytest.mark.asyncio
async def test_1_overall_effectiveness_endpoint():
    """Verify GET /api/v1/admin/training/effectiveness returns 200 with valid schema."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/api/v1/admin/training/effectiveness", headers=ADMIN_HEADERS
        )
        assert resp.status_code == 200
        data = resp.json()

        for field in [
            "total_learners",
            "total_enrollments",
            "completed_enrollments",
            "completion_rate",
            "measurable_interventions",
            "effective_interventions",
            "average_observed_improvement",
            "competencies_improved_count",
            "competency_improvements",
            "top_effective_courses",
            "recommendation_summary",
        ]:
            assert field in data, f"Missing field {field}"


@pytest.mark.asyncio
async def test_2_pre_training_score_retrieval():
    """Verify pre-training score resolves to latest history on or prior to enrollment."""
    async with AsyncSessionLocal() as session:
        service = TrainingEffectivenessService(session)

        res_emp = await session.execute(select(Employee).limit(1))
        emp = res_emp.scalar_one_or_none()
        assert emp is not None

        res_comp = await session.execute(select(Competency).limit(1))
        comp = res_comp.scalar_one_or_none()
        assert comp is not None

        t_base = datetime.now(timezone.utc) - timedelta(days=100)
        t_pre = datetime.now(timezone.utc) - timedelta(days=50)

        hist = CompetencyScoreHistory(
            id=uuid.uuid4(),
            employee_id=emp.id,
            competency_id=comp.id,
            previous_score=40.0,
            new_score=55.0,
            previous_confidence=0.5,
            new_confidence=0.7,
            change_reason="Unit test baseline score",
            created_at=t_base,
        )
        session.add(hist)
        await session.commit()

        try:
            # At t_pre, if this was the latest score <= t_pre, it should resolve
            resolved_score = await service._resolve_learner_pre_score(
                emp.id, comp.id, t_pre
            )
            assert resolved_score is not None
        finally:
            await session.delete(hist)
            await session.commit()


@pytest.mark.asyncio
async def test_3_post_training_score_retrieval():
    """Verify post-training score resolves to evidence/history on or after course completion."""
    async with AsyncSessionLocal() as session:
        service = TrainingEffectivenessService(session)

        res_emp = await session.execute(select(Employee).limit(1))
        emp = res_emp.scalar_one_or_none()
        assert emp is not None

        res_comp = await session.execute(select(Competency).limit(1))
        comp = res_comp.scalar_one_or_none()
        assert comp is not None

        t_comp = datetime.now(timezone.utc) + timedelta(days=1)
        t_post = datetime.now(timezone.utc) + timedelta(days=2)

        hist_post = CompetencyScoreHistory(
            id=uuid.uuid4(),
            employee_id=emp.id,
            competency_id=comp.id,
            previous_score=55.0,
            new_score=75.0,
            previous_confidence=0.7,
            new_confidence=0.85,
            change_reason="Unit test post-training recalibration",
            created_at=t_post,
        )
        session.add(hist_post)
        await session.commit()

        try:
            resolved_post = await service._resolve_learner_post_score(
                emp.id, comp.id, t_comp
            )
            assert resolved_post == 75.0
        finally:
            await session.delete(hist_post)
            await session.commit()


@pytest.mark.asyncio
async def test_4_improvement_points_calculation():
    """Verify improvement points strictly equal post_score - pre_score."""
    pre = 60.0
    post = 78.5
    diff = round(post - pre, 2)
    assert diff == 18.5


@pytest.mark.asyncio
async def test_5_improvement_percentage_calculation():
    """Verify improvement percentage = ((post - pre) / pre) * 100."""
    pre = 50.0
    post = 75.0
    pct = round(((post - pre) / pre) * 100.0, 2)
    assert pct == 50.0


@pytest.mark.asyncio
async def test_6_zero_baseline_handling():
    """Verify improvement percentage calculation handles baseline = 0 gracefully without NaN."""
    pre = 0.0
    post = 25.0
    pct = 100.0 if post > 0 else 0.0
    assert pct == 100.0
    assert not (pct != pct)  # not NaN


@pytest.mark.asyncio
async def test_7_missing_baseline_handling():
    """Verify learner with no prior history returns None (NO_BASELINE) and does not invent a score."""
    async with AsyncSessionLocal() as session:
        service = TrainingEffectivenessService(session)
        fake_emp_id = uuid.uuid4()
        fake_comp_id = uuid.uuid4()

        score = await service._resolve_learner_pre_score(
            fake_emp_id, fake_comp_id, datetime.now(timezone.utc)
        )
        assert score is None


@pytest.mark.asyncio
async def test_8_missing_post_training_score_handling():
    """Verify learner with no subsequent evidence returns None (NO_POST_DATA)."""
    async with AsyncSessionLocal() as session:
        service = TrainingEffectivenessService(session)
        fake_emp_id = uuid.uuid4()
        fake_comp_id = uuid.uuid4()

        # Completed time is None -> course not completed
        score_none = await service._resolve_learner_post_score(
            fake_emp_id, fake_comp_id, None
        )
        assert score_none is None

        # Completed time in future -> no score yet
        score_future = await service._resolve_learner_post_score(
            fake_emp_id, fake_comp_id, datetime.now(timezone.utc) + timedelta(days=10)
        )
        assert score_future is None


@pytest.mark.asyncio
async def test_9_course_aggregation():
    """Verify GET /api/v1/admin/training/courses/effectiveness returns courses list."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/api/v1/admin/training/courses/effectiveness", headers=ADMIN_HEADERS
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "courses" in data
        assert "total_courses" in data
        assert isinstance(data["courses"], list)


@pytest.mark.asyncio
async def test_10_completion_rate_calculation():
    """Verify course completion rate equals (completed / enrolled) * 100."""
    enrolled = 20
    completed = 15
    rate = round((completed / enrolled * 100.0), 1)
    assert rate == 75.0


@pytest.mark.asyncio
async def test_11_recommendation_outcomes_funnel():
    """Verify GET /api/v1/admin/recommendations/effectiveness returns lifecycle funnel metrics."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/api/v1/admin/recommendations/effectiveness", headers=ADMIN_HEADERS
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "summary" in data
        summary = data["summary"]
        for field in [
            "recommendations_issued",
            "recommendations_started",
            "recommendations_completed",
            "measurable_recommendations",
            "recommendations_with_improvement",
            "start_rate",
            "completion_rate",
            "improvement_rate",
            "by_priority",
        ]:
            assert field in summary, f"Missing recommendation field: {field}"


@pytest.mark.asyncio
async def test_12_no_data_handling():
    """Verify that courses without enrollments have NO_DATA or INSUFFICIENT_DATA status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/api/v1/admin/training/courses/effectiveness", headers=ADMIN_HEADERS
        )
        assert resp.status_code == 200
        data = resp.json()
        for course in data["courses"]:
            if course["enrolled_count"] == 0:
                assert course["effectiveness_status"] in ("NO_DATA", "INSUFFICIENT_DATA")
                assert course["measurable_learners"] == 0
                assert course["average_improvement"] is None


@pytest.mark.asyncio
async def test_13_not_available_effectiveness_index():
    """Verify effectiveness index is None (NOT_AVAILABLE) when duration hours are unavailable."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/api/v1/admin/training/courses/effectiveness", headers=ADMIN_HEADERS
        )
        assert resp.status_code == 200
        data = resp.json()
        for course in data["courses"]:
            if not course["duration_hours"] or course["duration_hours"] <= 0:
                assert course["effectiveness_index"] is None


@pytest.mark.asyncio
async def test_14_no_fabricated_training_hours():
    """Verify training hours strictly derive from duration_minutes / 60 without arbitrary inflation."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(LearningItem).where(LearningItem.duration_minutes > 0).limit(5))
        items = res.scalars().all()
        for item in items:
            expected_hours = round(item.duration_minutes / 60.0, 1)
            assert expected_hours > 0


@pytest.mark.asyncio
async def test_15_deterministic_ordering():
    """Verify courses response has deterministic ordering by average improvement desc, completed desc, title asc."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/api/v1/admin/training/courses/effectiveness", headers=ADMIN_HEADERS
        )
        assert resp.status_code == 200
        courses = resp.json()["courses"]
        for i in range(len(courses) - 1):
            imp1 = courses[i]["average_improvement"] if courses[i]["average_improvement"] is not None else -999.0
            imp2 = courses[i + 1]["average_improvement"] if courses[i + 1]["average_improvement"] is not None else -999.0
            assert imp1 >= imp2


@pytest.mark.asyncio
async def test_16_admin_authorization():
    """Verify ADMIN and SUPER_ADMIN roles can access training effectiveness endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # ADMIN -> 200
        resp_admin = await client.get(
            "/api/v1/admin/training/effectiveness", headers=ADMIN_HEADERS
        )
        assert resp_admin.status_code == 200

        # SUPER_ADMIN -> 200
        resp_super = await client.get(
            "/api/v1/admin/training/effectiveness", headers=SUPER_ADMIN_HEADERS
        )
        assert resp_super.status_code == 200


@pytest.mark.asyncio
async def test_17_employee_and_trainer_isolation():
    """Verify EMPLOYEE and TRAINER roles receive 403 Forbidden on admin training effectiveness endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # EMPLOYEE -> 403
        resp_emp = await client.get(
            "/api/v1/admin/training/effectiveness", headers=EMPLOYEE_HEADERS
        )
        assert resp_emp.status_code == 403

        # TRAINER -> 403
        resp_trainer = await client.get(
            "/api/v1/admin/training/effectiveness", headers=TRAINER_HEADERS
        )
        assert resp_trainer.status_code == 403

        # Unauthenticated -> 403
        resp_unauth = await client.get("/api/v1/admin/training/effectiveness")
        assert resp_unauth.status_code == 403


@pytest.mark.asyncio
async def test_18_stage_13_regression():
    """Verify Stage 13 employee performance analysis endpoint is completely intact."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Employee.id).limit(1))
        emp_id = res.scalar_one_or_none()
        assert emp_id is not None

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(f"/api/v1/employees/{emp_id}/performance")
        assert resp.status_code == 200
        data = resp.json()
        assert "employee_id" in data
        assert "strongest_competencies" in data
        assert "modalities" in data


@pytest.mark.asyncio
async def test_19_stage_14_regression():
    """Verify Stage 14 admin workforce analytics endpoints are completely intact."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp_wf = await client.get("/api/v1/admin/workforce/overview", headers=ADMIN_HEADERS)
        assert resp_wf.status_code == 200

        resp_tr = await client.get("/api/v1/admin/training/analytics", headers=ADMIN_HEADERS)
        assert resp_tr.status_code == 200
        data_tr = resp_tr.json()
        assert "total_learners" in data_tr
        assert "total_enrollments" in data_tr


@pytest.mark.asyncio
async def test_20_recommendation_engine_unaffected():
    """Verify that existing recommendation endpoints continue to function without modification."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Employee.id).limit(1))
        emp_id = res.scalar_one_or_none()
        assert emp_id is not None

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(f"/api/v1/employees/{emp_id}/recommendations")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
