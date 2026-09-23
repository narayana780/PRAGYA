import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select

from app.db.session import AsyncSessionLocal
from app.main import app
from app.modules.assessments.models import EmployeeCompetency
from app.modules.departments.models import Department
from app.modules.employees.models import Employee
from app.modules.job_roles.models import JobRole
from app.modules.skill_gaps.models import SkillGap


ADMIN_HEADERS = {"X-User-Role": "ADMIN"}
SUPER_ADMIN_HEADERS = {"X-User-Role": "SUPER_ADMIN"}
EMPLOYEE_HEADERS = {"X-User-Role": "EMPLOYEE"}


@pytest.mark.asyncio
async def test_1_admin_workforce_overview():
    """Verify admin overview endpoint returns 200 with complete, valid schema."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/workforce/overview", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        data = resp.json()

        for field in [
            "total_employees",
            "active_employees",
            "departments_count",
            "roles_count",
            "competencies_tracked",
            "employees_assessed",
            "employees_with_competencies",
            "average_competency_score",
            "average_role_readiness",
            "employees_needing_attention",
        ]:
            assert field in data, f"Missing field: {field}"

        assert data["total_employees"] >= 1
        assert data["active_employees"] >= 1
        assert data["departments_count"] >= 1
        assert data["roles_count"] >= 1
        assert data["competencies_tracked"] >= 1


@pytest.mark.asyncio
async def test_2_total_employee_count():
    """Verify total employee count strictly matches real PostgreSQL record count."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(func.count(Employee.id)))
        expected_total = res.scalar() or 0

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/workforce/overview", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        assert resp.json()["total_employees"] == expected_total


@pytest.mark.asyncio
async def test_3_active_employee_count():
    """Verify active employee count strictly matches real PostgreSQL active records."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(func.count(Employee.id)).where(Employee.is_active.is_(True))
        )
        expected_active = res.scalar() or 0

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/workforce/overview", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        assert resp.json()["active_employees"] == expected_active


@pytest.mark.asyncio
async def test_4_workforce_competency_averages():
    """Verify workforce competency average reflects actual EmployeeCompetency records."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(func.avg(EmployeeCompetency.current_score)))
        val = res.scalar()
        expected_avg = round(float(val), 2) if val is not None else None

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/workforce/overview", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        actual_avg = resp.json()["average_competency_score"]
        if expected_avg is not None:
            assert actual_avg == expected_avg
        else:
            assert actual_avg is None


@pytest.mark.asyncio
async def test_5_competency_gap_counts():
    """Verify total skill gaps count matches real SkillGap table count."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(func.count(SkillGap.id)))
        expected_gaps = res.scalar() or 0

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/workforce/gaps", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        assert resp.json()["total_gaps"] == expected_gaps


@pytest.mark.asyncio
async def test_6_critical_gap_aggregation():
    """Verify critical gaps aggregation strictly matches database records."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(func.count(SkillGap.id)).where(SkillGap.priority_level == "CRITICAL")
        )
        expected_critical = res.scalar() or 0

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/workforce/gaps", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        assert resp.json()["critical_gaps"] == expected_critical


@pytest.mark.asyncio
async def test_7_department_analytics():
    """Verify department analytics lists real departments with accurate metric structure."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/departments/analytics", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "departments" in data
        assert len(data["departments"]) >= 1

        for dept in data["departments"]:
            assert "department_id" in dept
            assert "department_name" in dept
            assert "department_code" in dept
            assert "employee_count" in dept
            assert "critical_gap_count" in dept
            assert "high_gap_count" in dept
            assert isinstance(dept["top_competency_strengths"], list)
            assert isinstance(dept["top_competency_gaps"], list)


@pytest.mark.asyncio
async def test_8_department_heatmap():
    """Verify department heatmap matrix structure and gap level resolutions."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/departments/heatmap", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "departments" in data
        assert "competencies_reference" in data
        assert len(data["departments"]) >= 1

        for dept in data["departments"]:
            assert "department_name" in dept
            assert "competencies" in dept
            for comp in dept["competencies"]:
                assert "competency_name" in comp
                assert comp["gap_level"] in [
                    "CRITICAL",
                    "HIGH",
                    "MEDIUM",
                    "LOW",
                    "NO_GAP",
                    "NO_DATA",
                ]
                if comp["average_score"] is not None:
                    assert 0.0 <= comp["average_score"] <= 100.0


@pytest.mark.asyncio
async def test_9_role_cadre_analytics():
    """Verify role & cadre analytics returns valid readiness and requirement counts."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/roles/analytics", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "roles" in data
        assert len(data["roles"]) >= 1

        for role in data["roles"]:
            assert "role_id" in role
            assert "role_name" in role
            assert "role_code" in role
            assert "career_level" in role
            assert "employee_count" in role
            assert "competency_requirements_count" in role
            assert "employees_below_target" in role
            assert isinstance(role["major_skill_gaps"], list)


@pytest.mark.asyncio
async def test_10_workforce_gap_ranking():
    """Verify top workforce gaps are sorted deterministically: CRITICAL -> HIGH -> MEDIUM -> LOW."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/workforce/gaps", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        top_gaps = resp.json()["top_workforce_gaps"]

        priority_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "NO_GAP": 0}
        prev_weight = 5
        for gap in top_gaps:
            weight = priority_order.get(gap["highest_priority_level"], 0)
            assert weight <= prev_weight, "Gaps not ordered by priority level"
            prev_weight = weight


@pytest.mark.asyncio
async def test_11_empty_department():
    """Verify an empty department returns honest null/empty metrics and not fake 0%."""
    dept_code = f"TEST_DEPT_{uuid.uuid4().hex[:6]}"
    async with AsyncSessionLocal() as session:
        empty_dept = Department(
            id=uuid.uuid4(),
            name=f"Empty Test Division {uuid.uuid4().hex[:6]}",
            code=dept_code,
            is_active=True,
        )
        session.add(empty_dept)
        await session.commit()
        dept_id = empty_dept.id

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/departments/analytics", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        depts = resp.json()["departments"]
        target = next((d for d in depts if d["department_id"] == str(dept_id)), None)
        assert target is not None
        assert target["employee_count"] == 0
        assert target["average_competency_score"] is None
        assert target["average_role_readiness"] is None
        assert target["average_skill_gap_score"] is None
        assert target["critical_gap_count"] == 0

    # Cleanup
    async with AsyncSessionLocal() as session:
        await session.delete(await session.get(Department, dept_id))
        await session.commit()


@pytest.mark.asyncio
async def test_12_employee_with_no_competency_data():
    """Verify employee with no competency data is handled gracefully in admin roster."""
    async with AsyncSessionLocal() as session:
        dept = (await session.execute(select(Department).limit(1))).scalar_one()
        role = (await session.execute(select(JobRole).limit(1))).scalar_one()
        emp_code = f"TEMP_{uuid.uuid4().hex[:6]}"
        test_emp = Employee(
            id=uuid.uuid4(),
            employee_code=emp_code,
            full_name="Unassessed Test Officer",
            designation="Statistical Trainee",
            department_id=dept.id,
            job_role_id=role.id,
            is_active=True,
        )
        session.add(test_emp)
        await session.commit()
        emp_id = test_emp.id

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/workforce/employees", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        emps = resp.json()["employees"]
        target = next((e for e in emps if e["id"] == str(emp_id)), None)
        assert target is not None
        assert target["average_competency"] is None

    # Cleanup
    async with AsyncSessionLocal() as session:
        await session.delete(await session.get(Employee, emp_id))
        await session.commit()


@pytest.mark.asyncio
async def test_13_deterministic_ordering():
    """Verify deterministic ordering across repeated calls."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp1 = await client.get("/api/v1/admin/workforce/competencies", headers=ADMIN_HEADERS)
        resp2 = await client.get("/api/v1/admin/workforce/competencies", headers=ADMIN_HEADERS)
        assert resp1.status_code == 200
        assert resp2.status_code == 200

        comps1 = [c["competency_id"] for c in resp1.json()["competencies"]]
        comps2 = [c["competency_id"] for c in resp2.json()["competencies"]]
        assert comps1 == comps2


@pytest.mark.asyncio
async def test_14_no_fake_data():
    """Verify department names and role names strictly match existing DB records."""
    async with AsyncSessionLocal() as session:
        db_dept_names = set((await session.execute(select(Department.name))).scalars().all())
        db_role_names = set((await session.execute(select(JobRole.name))).scalars().all())

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp_dept = await client.get("/api/v1/admin/departments/analytics", headers=ADMIN_HEADERS)
        for dept in resp_dept.json()["departments"]:
            assert dept["department_name"] in db_dept_names

        resp_role = await client.get("/api/v1/admin/roles/analytics", headers=ADMIN_HEADERS)
        for role in resp_role.json()["roles"]:
            assert role["role_name"] in db_role_names


@pytest.mark.asyncio
async def test_15_admin_authorization():
    """Verify admin endpoints permit valid ADMIN and SUPER_ADMIN roles."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp1 = await client.get("/api/v1/admin/workforce/overview", headers=ADMIN_HEADERS)
        assert resp1.status_code == 200

        resp2 = await client.get("/api/v1/admin/workforce/overview", headers=SUPER_ADMIN_HEADERS)
        assert resp2.status_code == 200


@pytest.mark.asyncio
async def test_16_employee_cannot_access_admin_analytics():
    """Verify requests with EMPLOYEE role receive HTTP 403 Forbidden."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/workforce/overview", headers=EMPLOYEE_HEADERS)
        assert resp.status_code == 403
        data = resp.json()
        assert data.get("error", {}).get("code") == "UNAUTHORIZED_ACCESS"


@pytest.mark.asyncio
async def test_17_employee_isolation():
    """Verify unauthenticated requests without role header are blocked with 403 Forbidden."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/workforce/overview")
        assert resp.status_code == 403


@pytest.mark.asyncio
async def test_18_existing_stage13_performance_remains_unaffected():
    """Verify Stage 13 employee performance endpoint remains 100% operational."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        me_resp = await client.get("/api/v1/employees/me")
        assert me_resp.status_code == 200
        emp_id = me_resp.json()["id"]

        perf_resp = await client.get(f"/api/v1/employees/{emp_id}/performance")
        assert perf_resp.status_code == 200
        perf_data = perf_resp.json()
        assert perf_data["employee_id"] == emp_id
        assert "overall" in perf_data
        assert "competencies" in perf_data

        timeline_resp = await client.get(f"/api/v1/employees/{emp_id}/history/timeline")
        assert timeline_resp.status_code == 200
        assert "events" in timeline_resp.json()


@pytest.mark.asyncio
async def test_19_existing_skill_gap_calculations_unaffected():
    """Verify existing skill gap endpoints continue functioning normally."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        me_resp = await client.get("/api/v1/employees/me")
        assert me_resp.status_code == 200
        emp_id = me_resp.json()["id"]

        resp = await client.get(f"/api/v1/employees/{emp_id}/skill-gaps")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_20_existing_recommendations_and_courses_unaffected():
    """Verify recommendation and catalogue APIs remain unaffected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        me_resp = await client.get("/api/v1/employees/me")
        assert me_resp.status_code == 200
        emp_id = me_resp.json()["id"]

        recom_resp = await client.get(f"/api/v1/employees/{emp_id}/recommendations")
        assert recom_resp.status_code == 200

        items_resp = await client.get("/api/v1/learning-items")
        assert items_resp.status_code == 200
        assert "items" in items_resp.json()


@pytest.mark.asyncio
async def test_21_workforce_training_overview():
    """Verify training participation overview returns valid aggregate structure."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/training/analytics", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        data = resp.json()

        for field in [
            "total_learners",
            "total_enrollments",
            "completed_courses_count",
            "average_learning_progress",
            "total_learning_activities",
            "top_courses",
            "employees_with_competency_growth",
        ]:
            assert field in data


@pytest.mark.asyncio
async def test_22_admin_employee_drilldown_list():
    """Verify admin employee roster for executive drill-down."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/workforce/employees", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "employees" in data
        assert "total" in data
        assert len(data["employees"]) >= 1
        emp = data["employees"][0]
        assert "employee_code" in emp
        assert "full_name" in emp
        assert "department_name" in emp
        assert "needs_attention" in emp
