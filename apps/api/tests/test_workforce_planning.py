import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select

from app.db.session import AsyncSessionLocal
from app.main import app
from app.modules.analytics.admin_service import WorkforceAnalysisService
from app.modules.analytics.emerging_skills_service import EmergingSkillsService
from app.modules.analytics.training_effectiveness_service import TrainingEffectivenessService
from app.modules.analytics.workforce_planning_service import WorkforcePlanningService
from app.modules.employees.models import Employee

ADMIN_HEADERS = {"X-User-Role": "ADMIN"}
SUPER_ADMIN_HEADERS = {"X-User-Role": "SUPER_ADMIN"}
EMPLOYEE_HEADERS = {"X-User-Role": "EMPLOYEE"}
TRAINER_HEADERS = {"X-User-Role": "TRAINER"}


@pytest.mark.asyncio
async def test_1_admin_authorization():
    """Verify ADMIN and SUPER_ADMIN have full access to workforce planning endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for headers in [ADMIN_HEADERS, SUPER_ADMIN_HEADERS]:
            resp = await client.get("/api/v1/admin/workforce/planning/overview", headers=headers)
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "OK"
            assert "population" in data
            assert "capacity" in data


@pytest.mark.asyncio
async def test_2_employee_authorization_rejection():
    """Verify non-admin roles (EMPLOYEE, TRAINER) and unauthenticated users receive 403 Forbidden."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Unauthenticated
        resp_unauth = await client.get("/api/v1/admin/workforce/planning/overview")
        assert resp_unauth.status_code == 403

        # EMPLOYEE
        resp_emp = await client.get("/api/v1/admin/workforce/planning/overview", headers=EMPLOYEE_HEADERS)
        assert resp_emp.status_code == 403

        # TRAINER
        resp_tr = await client.get("/api/v1/admin/workforce/planning/forecast", headers=TRAINER_HEADERS)
        assert resp_tr.status_code == 403


@pytest.mark.asyncio
async def test_3_workforce_overview():
    """Verify GET /api/v1/admin/workforce/planning/overview returns authentic database aggregates."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/workforce/planning/overview", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        data = resp.json()

        pop = data["population"]
        cap = data["capacity"]
        dq = data["data_quality"]

        assert pop["total_employees"] >= 1
        assert pop["departments_count"] >= 1
        assert pop["roles_count"] >= 1
        assert pop["competencies_tracked"] >= 1

        assert cap["employees_with_gaps"] >= 0
        assert cap["employees_learning"] >= 0
        assert 0.0 <= cap["average_role_readiness"] <= 100.0
        assert 0.0 <= cap["overall_planning_pressure"] <= 100.0

        assert dq["status"] in ["SUFFICIENT", "INSUFFICIENT_DATA"]
        assert dq["quality_grade"] in ["HIGH", "MEDIUM", "LOW"]


@pytest.mark.asyncio
async def test_4_historical_trends():
    """Verify GET /api/v1/admin/workforce/planning/trends returns valid trend periods or honest INSUFFICIENT_DATA."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/workforce/planning/trends", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        data = resp.json()

        assert data["status"] in ["OK", "INSUFFICIENT_DATA"]
        assert isinstance(data["trends"], list)
        if data["status"] == "OK":
            assert len(data["trends"]) == data["periods_count"]
            for trend in data["trends"]:
                assert "period" in trend
                assert "average_competency_score" in trend
                assert trend["average_competency_score"] >= 0.0


@pytest.mark.asyncio
async def test_5_insufficient_historical_data_handling():
    """Verify service handles edge cases where no historical records exist cleanly."""
    async with AsyncSessionLocal() as session:
        service = WorkforcePlanningService(session)
        res = await service.get_workforce_planning_trends()
        assert res.status in ["OK", "INSUFFICIENT_DATA"]
        if res.status == "INSUFFICIENT_DATA":
            assert res.message is not None
            assert res.data_quality.quality_grade == "LOW"


@pytest.mark.asyncio
async def test_6_forecast_calculation():
    """Verify deterministic capacity forecast synthesizes capacity, requirements, and projected gaps."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/workforce/planning/forecast", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        fc = resp.json()

        assert fc["total_workforce"] >= 1
        assert fc["current_capacity"] >= 0
        assert fc["estimated_capacity_requirement"] >= fc["current_capacity"]
        assert fc["capacity_gap"] == fc["estimated_capacity_requirement"] - fc["current_capacity"]
        assert fc["projected_gap"] >= 0
        assert 0.0 <= fc["overall_pressure_index"] <= 100.0
        assert isinstance(fc["priority_competencies"], list)
        assert isinstance(fc["priority_roles"], list)
        assert isinstance(fc["priority_departments"], list)


@pytest.mark.asyncio
async def test_7_no_nan_in_forecast_responses():
    """Verify no NaN or Infinite values occur in any float metrics across all planning endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for ep in [
            "/api/v1/admin/workforce/planning/overview",
            "/api/v1/admin/workforce/planning/trends",
            "/api/v1/admin/workforce/planning/forecast",
            "/api/v1/admin/workforce/planning/competencies",
            "/api/v1/admin/workforce/planning/roles",
            "/api/v1/admin/workforce/planning/departments",
            "/api/v1/admin/workforce/planning/recommendations",
        ]:
            resp = await client.get(ep, headers=ADMIN_HEADERS)
            assert resp.status_code == 200
            raw_text = resp.text
            assert "NaN" not in raw_text
            assert "Infinity" not in raw_text
            assert "-Infinity" not in raw_text


@pytest.mark.asyncio
async def test_8_competency_forecast():
    """Verify GET /api/v1/admin/workforce/planning/competencies returns pressure rankings."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/workforce/planning/competencies", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        data = resp.json()

        assert data["total_competencies"] >= 1
        comps = data["competencies"]
        assert len(comps) == data["total_competencies"]

        # Validate sorting descending by planning_pressure
        for i in range(len(comps) - 1):
            assert comps[i]["planning_pressure"] >= comps[i + 1]["planning_pressure"]

        top = comps[0]
        assert "name" in top
        assert "domain" in top
        assert 0.0 <= top["current_coverage"] <= 100.0
        assert top["gap_population"] >= 0
        assert top["status"] in ["HIGH_DEFICIT", "MODERATE_DEFICIT", "BALANCED", "INSUFFICIENT_DATA"]
        assert len(top["rationale"]) >= 1


@pytest.mark.asyncio
async def test_9_role_forecast():
    """Verify GET /api/v1/admin/workforce/planning/roles evaluates cadre level requirements."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/workforce/planning/roles", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        data = resp.json()

        assert data["total_roles"] >= 1
        for role in data["roles"]:
            assert "role_name" in role
            assert role["employee_count"] >= 0
            assert role["employees_meeting_target"] + role["employees_below_target"] == role["employee_count"]
            assert 0.0 <= role["projected_capacity_pressure"] <= 100.0
            assert role["status"] in ["HIGH_PRESSURE", "MODERATE_PRESSURE", "ADEQUATE"]


@pytest.mark.asyncio
async def test_10_department_forecast():
    """Verify GET /api/v1/admin/workforce/planning/departments evaluates departmental capacity."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/workforce/planning/departments", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        data = resp.json()

        assert data["total_departments"] >= 1
        for dept in data["departments"]:
            assert "department_name" in dept
            assert dept["workforce_size"] >= 0
            assert 0.0 <= dept["competency_coverage"] <= 100.0
            assert 0.0 <= dept["projected_capacity_pressure"] <= 100.0
            assert dept["status"] in ["HIGH_PRESSURE", "MODERATE_PRESSURE", "BALANCED"]


@pytest.mark.asyncio
async def test_11_planning_recommendations():
    """Verify GET /api/v1/admin/workforce/planning/recommendations returns actionable signals."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/workforce/planning/recommendations", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        data = resp.json()

        assert data["total_recommendations"] >= 1
        for rec in data["recommendations"]:
            assert rec["type"] in [
                "COMPETENCY_TRAINING",
                "ROLE_CAPACITY",
                "DEPARTMENT_FOCUS",
                "HORIZON_MONITORING",
                "REASSESSMENT",
            ]
            assert rec["priority"] in ["HIGH", "MEDIUM", "LOW"]
            assert len(rec["title"]) > 0
            assert len(rec["rationale"]) > 0
            assert len(rec["suggested_action"]) > 0


@pytest.mark.asyncio
async def test_12_employee_drilldown():
    """Verify GET /api/v1/admin/workforce/planning/employees/{id} returns single officer planning state."""
    async with AsyncSessionLocal() as session:
        emp_res = await session.execute(select(Employee.id).where(Employee.is_active.is_(True)).limit(1))
        emp_id = emp_res.scalar_one_or_none()

    assert emp_id is not None

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(f"/api/v1/admin/workforce/planning/employees/{emp_id}", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        emp_data = resp.json()

        assert emp_data["employee_id"] == str(emp_id)
        assert "full_name" in emp_data
        assert 0.0 <= emp_data["current_average_score"] <= 100.0
        assert 0.0 <= emp_data["role_readiness_percentage"] <= 100.0
        assert emp_data["readiness_indicator"] in ["READY", "DEVELOPING", "AT_RISK"]
        assert isinstance(emp_data["historical_trajectory"], list)
        assert isinstance(emp_data["planning_signals"], list)


@pytest.mark.asyncio
async def test_13_employee_drilldown_not_found():
    """Verify employee drilldown returns 404 for nonexistent employee UUID."""
    random_id = uuid.uuid4()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(f"/api/v1/admin/workforce/planning/employees/{random_id}", headers=ADMIN_HEADERS)
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_14_employee_isolation_on_drilldown():
    """Verify non-admin users cannot access the employee planning drilldown endpoint."""
    async with AsyncSessionLocal() as session:
        emp_res = await session.execute(select(Employee.id).where(Employee.is_active.is_(True)).limit(1))
        emp_id = emp_res.scalar_one_or_none()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(f"/api/v1/admin/workforce/planning/employees/{emp_id}", headers=EMPLOYEE_HEADERS)
        assert resp.status_code == 403


@pytest.mark.asyncio
async def test_15_deterministic_output():
    """Verify executing planning forecasts twice produces identical results."""
    async with AsyncSessionLocal() as session:
        service = WorkforcePlanningService(session)
        fc1 = await service.get_capacity_forecast()
        fc2 = await service.get_capacity_forecast()

        assert fc1.current_capacity == fc2.current_capacity
        assert fc1.capacity_gap == fc2.capacity_gap
        assert fc1.projected_gap == fc2.projected_gap
        assert fc1.overall_pressure_index == fc2.overall_pressure_index
        assert fc1.priority_competencies == fc2.priority_competencies


@pytest.mark.asyncio
async def test_16_methodology_metadata():
    """Verify forecast responses include full transparent methodology and limitations."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/workforce/planning/forecast", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        fc = resp.json()

        m = fc["methodology"]
        assert m["type"] == "deterministic_workforce_projection"
        assert len(m["signals"]) >= 3
        assert len(m["assumptions"]) >= 1
        assert len(m["limitations"]) >= 1


@pytest.mark.asyncio
async def test_17_data_quality_metadata():
    """Verify data quality metadata exists and adheres to schema across endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/workforce/planning/overview", headers=ADMIN_HEADERS)
        data = resp.json()
        dq = data["data_quality"]

        assert "historical_periods" in dq
        assert "records_used" in dq
        assert dq["status"] in ["SUFFICIENT", "INSUFFICIENT_DATA"]
        assert dq["quality_grade"] in ["HIGH", "MEDIUM", "LOW"]


@pytest.mark.asyncio
async def test_18_stage_14_regression():
    """Verify Stage 14 workforce analytics remain completely intact and functional."""
    async with AsyncSessionLocal() as session:
        service = WorkforceAnalysisService(session)
        overview = await service.get_workforce_overview()
        assert overview.total_employees >= 1
        assert overview.active_employees >= 1

        dept_analytics = await service.get_department_analytics()
        assert len(dept_analytics.departments) >= 1


@pytest.mark.asyncio
async def test_19_stage_15_regression():
    """Verify Stage 15 training effectiveness remains completely functional."""
    async with AsyncSessionLocal() as session:
        service = TrainingEffectivenessService(session)
        eff = await service.get_overall_effectiveness()
        assert eff.total_learners >= 0
        assert eff.total_enrollments >= 0


@pytest.mark.asyncio
async def test_20_stage_16_regression():
    """Verify Stage 16 emerging skills intelligence remains completely functional."""
    async with AsyncSessionLocal() as session:
        service = EmergingSkillsService(session)
        signals = await service.get_emerging_skills_signals()
        assert signals.total_analyzed >= 1
        assert len(signals.skills) == signals.total_analyzed
