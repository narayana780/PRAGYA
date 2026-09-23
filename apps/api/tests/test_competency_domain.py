import uuid

import pytest
from app.main import app
from app.modules.competencies.constants import (
    level_to_score_range,
    score_to_proficiency_level,
)
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_list_domains():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/domains")
    assert response.status_code == 200
    domains = response.json()
    assert isinstance(domains, list)
    assert len(domains) == 4
    codes = [d["code"] for d in domains]
    assert "STATISTICAL" in codes
    assert "TECHNICAL" in codes
    assert "DIGITAL_GOVERNANCE" in codes
    assert "BEHAVIOURAL_MANAGERIAL" in codes
    # Check that counts add up to 33
    total_count = sum(d["competency_count"] for d in domains)
    assert total_count == 33


@pytest.mark.asyncio
async def test_list_competencies():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/competencies")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 33
    assert len(data["items"]) == 33


@pytest.mark.asyncio
async def test_filter_by_domain():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp_stat = await ac.get("/api/v1/competencies?domain=STATISTICAL")
        assert resp_stat.status_code == 200
        assert resp_stat.json()["total"] == 10

        resp_tech = await ac.get("/api/v1/competencies?domain=TECHNICAL")
        assert resp_tech.status_code == 200
        assert resp_tech.json()["total"] == 12

        resp_dig = await ac.get("/api/v1/competencies?domain=DIGITAL_GOVERNANCE")
        assert resp_dig.status_code == 200
        assert resp_dig.json()["total"] == 5

        resp_behav = await ac.get("/api/v1/competencies?domain=BEHAVIOURAL_MANAGERIAL")
        assert resp_behav.status_code == 200
        assert resp_behav.json()["total"] == 6


@pytest.mark.asyncio
async def test_search_competency():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Search Python
        resp_py = await ac.get("/api/v1/competencies?search=Python")
        assert resp_py.status_code == 200
        items = resp_py.json()["items"]
        assert len(items) >= 1
        assert any(i["code"] == "TECH_PYTHON" for i in items)

        # Search Survey
        resp_surv = await ac.get("/api/v1/competencies?search=Survey")
        assert resp_surv.status_code == 200
        assert resp_surv.json()["total"] >= 1


@pytest.mark.asyncio
async def test_get_competency_by_id():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Get list to pick Python ID
        list_resp = await ac.get("/api/v1/competencies?search=Python")
        py_id = list_resp.json()["items"][0]["id"]

        detail_resp = await ac.get(f"/api/v1/competencies/{py_id}")
        assert detail_resp.status_code == 200
        comp = detail_resp.json()
        assert comp["code"] == "TECH_PYTHON"
        assert comp["name"] == "Python"
        assert comp["domain_code"] == "TECHNICAL"
        assert "description" in comp
        assert "learning_objectives" in comp
        assert "requiring_roles" in comp
        assert len(comp["requiring_roles"]) >= 1


@pytest.mark.asyncio
async def test_competency_not_found():
    fake_id = str(uuid.uuid4())
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(f"/api/v1/competencies/{fake_id}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "COMPETENCY_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_proficiency_levels():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/proficiency-levels")
    assert response.status_code == 200
    levels = response.json()
    assert len(levels) == 5
    assert levels[0]["level_number"] == 1
    assert levels[0]["name"] == "Awareness"
    assert levels[0]["minimum_score"] == 0
    assert levels[0]["maximum_score"] == 20
    assert levels[4]["level_number"] == 5
    assert levels[4]["name"] == "Advanced"
    assert levels[4]["maximum_score"] == 100


@pytest.mark.asyncio
async def test_get_role_competencies():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Find Statistical Officer role ID
        roles_resp = await ac.get("/api/v1/job-roles")
        so_role = next(r for r in roles_resp.json() if r["code"] == "SO")

        reqs_resp = await ac.get(f"/api/v1/job-roles/{so_role['id']}/competencies")
        assert reqs_resp.status_code == 200
        reqs = reqs_resp.json()
        assert len(reqs) >= 8
        comp_codes = [r["competency_code"] for r in reqs]
        assert "STAT_SURVEY_DESIGN" in comp_codes
        assert "STAT_SAMPLING" in comp_codes
        assert "TECH_PYTHON" in comp_codes


@pytest.mark.asyncio
async def test_unknown_role():
    fake_id = str(uuid.uuid4())
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(f"/api/v1/job-roles/{fake_id}/competencies")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "JOB_ROLE_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_roles_requiring_competency():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Find Sampling ID
        list_resp = await ac.get("/api/v1/competencies?search=Sampling")
        comp_id = list_resp.json()["items"][0]["id"]

        resp = await ac.get(f"/api/v1/competencies/{comp_id}/roles")
        assert resp.status_code == 200
        roles = resp.json()
        assert len(roles) >= 2
        role_codes = [r["job_role_code"] for r in roles]
        assert "SO" in role_codes
        assert "SSO" in role_codes


def test_score_conversion_utilities():
    lvl, name = score_to_proficiency_level(15)
    assert lvl == 1 and name == "Awareness"

    lvl, name = score_to_proficiency_level(35)
    assert lvl == 2 and name == "Foundation"

    lvl, name = score_to_proficiency_level(50)
    assert lvl == 3 and name == "Working"

    lvl, name = score_to_proficiency_level(75)
    assert lvl == 4 and name == "Proficient"

    lvl, name = score_to_proficiency_level(95)
    assert lvl == 5 and name == "Advanced"

    min_s, max_s = level_to_score_range(4)
    assert min_s == 61 and max_s == 80
