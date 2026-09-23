import uuid

import pytest
from app.main import app
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_get_departments():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/departments")
    assert response.status_code == 200
    departments = response.json()
    assert isinstance(departments, list)
    assert len(departments) >= 5
    codes = [d["code"] for d in departments]
    assert "DES" in codes
    assert "NAD" in codes


@pytest.mark.asyncio
async def test_get_job_roles():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/job-roles")
    assert response.status_code == 200
    roles = response.json()
    assert isinstance(roles, list)
    assert len(roles) >= 5
    codes = [r["code"] for r in roles]
    assert "SO" in codes
    assert "SSO" in codes


@pytest.mark.asyncio
async def test_get_current_employee_me():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/employees/me")
    assert response.status_code == 200
    data = response.json()
    assert data["employee_code"] == "EMP-0001"
    assert data["full_name"] == "Ananya Sharma"
    assert data["designation"] == "Statistical Officer"
    assert data["department_name"] == "Department of Economics and Statistics"
    assert data["job_role_name"] == "Statistical Officer"
    assert data["experience_years"] == 5
    assert data["preferred_language"] == "English"
    assert data["target_role_name"] == "Senior Statistical Officer"
    assert data["training_count"] >= 4


@pytest.mark.asyncio
async def test_get_employee_by_id():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # First fetch me to get real UUID
        me_resp = await ac.get("/api/v1/employees/me")
        emp_id = me_resp.json()["id"]

        response = await ac.get(f"/api/v1/employees/{emp_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == emp_id
    assert data["employee_code"] == "EMP-0001"


@pytest.mark.asyncio
async def test_get_employee_not_found():
    non_existent_id = str(uuid.uuid4())
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(f"/api/v1/employees/{non_existent_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "EMPLOYEE_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_employee_training_history():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        me_resp = await ac.get("/api/v1/employees/me")
        emp_id = me_resp.json()["id"]

        response = await ac.get(f"/api/v1/employees/{emp_id}/training-history")
    assert response.status_code == 200
    records = response.json()
    assert isinstance(records, list)
    assert len(records) >= 4
    providers = [r["provider_type"] for r in records]
    assert "IGOT" in providers
    assert "NSSTA_TPAC" in providers


@pytest.mark.asyncio
async def test_update_employee_success():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        me_resp = await ac.get("/api/v1/employees/me")
        emp_id = me_resp.json()["id"]

        # Update assignment and preferred language
        update_payload = {
            "current_assignment": "National Sampling Frame Revision 2026",
            "preferred_language": "Hindi",
            "experience_years": 6,
        }
        patch_resp = await ac.patch(f"/api/v1/employees/{emp_id}", json=update_payload)
        assert patch_resp.status_code == 200
        updated = patch_resp.json()
        assert updated["current_assignment"] == "National Sampling Frame Revision 2026"
        assert updated["preferred_language"] == "Hindi"
        assert updated["experience_years"] == 6

        # Restore back to original demonstration data
        restore_payload = {
            "current_assignment": "Survey Data Analysis",
            "preferred_language": "English",
            "experience_years": 5,
        }
        restore_resp = await ac.patch(
            f"/api/v1/employees/{emp_id}", json=restore_payload
        )
        assert restore_resp.status_code == 200


@pytest.mark.asyncio
async def test_update_employee_invalid_experience():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        me_resp = await ac.get("/api/v1/employees/me")
        emp_id = me_resp.json()["id"]

        # Negative experience
        resp_neg = await ac.patch(
            f"/api/v1/employees/{emp_id}", json={"experience_years": -5}
        )
        # Pydantic or service validation rejects
        assert resp_neg.status_code in [400, 422]

        # Over 50 experience
        resp_over = await ac.patch(
            f"/api/v1/employees/{emp_id}", json={"experience_years": 65}
        )
        assert resp_over.status_code in [400, 422]


@pytest.mark.asyncio
async def test_update_employee_invalid_target_role():
    fake_role_id = str(uuid.uuid4())
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        me_resp = await ac.get("/api/v1/employees/me")
        emp_id = me_resp.json()["id"]

        response = await ac.patch(
            f"/api/v1/employees/{emp_id}",
            json={"target_role_id": fake_role_id},
        )
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "JOB_ROLE_NOT_FOUND"


@pytest.mark.asyncio
async def test_update_employee_not_found():
    non_existent_id = str(uuid.uuid4())
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.patch(
            f"/api/v1/employees/{non_existent_id}",
            json={"current_assignment": "New Assignment"},
        )
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "EMPLOYEE_NOT_FOUND"
