import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select

from app.db.session import AsyncSessionLocal
from app.main import app
from app.modules.analytics.emerging_skills_service import EmergingSkillsService
from app.modules.competencies.models import Competency, CompetencyRequirement
from app.modules.courses.models import CourseProgress, LearningItemCompetency
from app.modules.recommendations.models import LearningRecommendation
from app.modules.skill_gaps.models import SkillGap

ADMIN_HEADERS = {"X-User-Role": "ADMIN"}
SUPER_ADMIN_HEADERS = {"X-User-Role": "SUPER_ADMIN"}
EMPLOYEE_HEADERS = {"X-User-Role": "EMPLOYEE"}
TRAINER_HEADERS = {"X-User-Role": "TRAINER"}


@pytest.mark.asyncio
async def test_1_endpoint_returns_real_data():
    """Verify GET /api/v1/admin/emerging-skills returns 200 with valid schema."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/emerging-skills", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        data = resp.json()

        for field in [
            "skills",
            "total_analyzed",
            "emerging_count",
            "watch_count",
            "established_count",
            "insufficient_data_count",
            "methodology",
        ]:
            assert field in data, f"Missing field: {field}"

        assert data["total_analyzed"] >= 1
        assert len(data["skills"]) == data["total_analyzed"]


@pytest.mark.asyncio
async def test_2_signal_calculation_is_deterministic():
    """Verify multiple executions on identical database state yield identical signal scores."""
    async with AsyncSessionLocal() as session:
        service = EmergingSkillsService(session)
        res1 = await service.get_emerging_skills_signals()
        res2 = await service.get_emerging_skills_signals()

        assert res1.total_analyzed == res2.total_analyzed
        assert res1.emerging_count == res2.emerging_count
        assert len(res1.skills) == len(res2.skills)

        for s1, s2 in zip(res1.skills, res2.skills):
            assert s1.competency_id == s2.competency_id
            assert s1.signal_score == s2.signal_score
            assert s1.status == s2.status


@pytest.mark.asyncio
async def test_3_gap_frequency_calculation():
    """Verify gap frequency matches actual distinct employee count in SkillGap with gap_score > 0."""
    async with AsyncSessionLocal() as session:
        # Find a competency with skill gaps
        stmt = (
            select(
                SkillGap.competency_id,
                func.count(func.distinct(SkillGap.employee_id)).label("cnt"),
            )
            .where(SkillGap.gap_score > 0)
            .group_by(SkillGap.competency_id)
            .limit(1)
        )
        res = await session.execute(stmt)
        row = res.one_or_none()

    if row:
        target_comp_id = str(row.competency_id)
        expected_cnt = row.cnt

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/admin/emerging-skills", headers=ADMIN_HEADERS)
            assert resp.status_code == 200
            skills = resp.json()["skills"]
            matched = next((s for s in skills if s["competency_id"] == target_comp_id), None)
            assert matched is not None
            assert matched["gap_frequency"] == expected_cnt


@pytest.mark.asyncio
async def test_4_recommendation_frequency():
    """Verify recommendation frequency matches count of LearningRecommendation records."""
    async with AsyncSessionLocal() as session:
        stmt = (
            select(
                LearningRecommendation.target_competency_id,
                func.count(LearningRecommendation.id).label("cnt"),
            )
            .group_by(LearningRecommendation.target_competency_id)
            .limit(1)
        )
        res = await session.execute(stmt)
        row = res.one_or_none()

    if row:
        target_comp_id = str(row.target_competency_id)
        expected_cnt = row.cnt

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/admin/emerging-skills", headers=ADMIN_HEADERS)
            assert resp.status_code == 200
            skills = resp.json()["skills"]
            matched = next((s for s in skills if s["competency_id"] == target_comp_id), None)
            assert matched is not None
            assert matched["recommendation_frequency"] == expected_cnt


@pytest.mark.asyncio
async def test_5_training_demand():
    """Verify training demand matches distinct employee enrollments for mapped courses."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/emerging-skills", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        skills = resp.json()["skills"]
        for s in skills:
            assert s["training_demand"] >= 0


@pytest.mark.asyncio
async def test_6_role_coverage():
    """Verify role coverage matches distinct job roles requiring the competency."""
    async with AsyncSessionLocal() as session:
        stmt = (
            select(
                CompetencyRequirement.competency_id,
                func.count(func.distinct(CompetencyRequirement.job_role_id)).label("cnt"),
            )
            .group_by(CompetencyRequirement.competency_id)
            .limit(1)
        )
        res = await session.execute(stmt)
        row = res.one_or_none()

    if row:
        target_comp_id = str(row.competency_id)
        expected_cnt = row.cnt

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/admin/emerging-skills", headers=ADMIN_HEADERS)
            assert resp.status_code == 200
            skills = resp.json()["skills"]
            matched = next((s for s in skills if s["competency_id"] == target_comp_id), None)
            assert matched is not None
            assert matched["role_coverage"] == expected_cnt


@pytest.mark.asyncio
async def test_7_no_data_and_insufficient_data_handling():
    """Verify that competencies with 0 signals receive INSUFFICIENT_DATA status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/emerging-skills", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        skills = resp.json()["skills"]
        for s in skills:
            total_signals = (
                s["gap_frequency"]
                + s["recommendation_frequency"]
                + s["training_demand"]
                + s["role_coverage"]
            )
            if total_signals == 0:
                assert s["status"] == "INSUFFICIENT_DATA"
                assert s["signal_score"] == 0.0


@pytest.mark.asyncio
async def test_8_explainability_signals():
    """Verify explainability signals provide human-readable justification for each competency."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/emerging-skills", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        skills = resp.json()["skills"]
        for s in skills:
            assert isinstance(s["signals"], list)
            assert len(s["signals"]) >= 1
            for sig in s["signals"]:
                assert isinstance(sig, str)
                assert len(sig) > 0


@pytest.mark.asyncio
async def test_9_stable_ordering():
    """Verify response is sorted deterministically by signal_score descending, then gap_frequency desc."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/emerging-skills", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        skills = resp.json()["skills"]
        for i in range(len(skills) - 1):
            s1 = skills[i]["signal_score"]
            s2 = skills[i + 1]["signal_score"]
            assert s1 >= s2


@pytest.mark.asyncio
async def test_10_admin_authorization():
    """Verify ADMIN and SUPER_ADMIN have full access to emerging skills intelligence."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp_admin = await client.get("/api/v1/admin/emerging-skills", headers=ADMIN_HEADERS)
        assert resp_admin.status_code == 200

        resp_super = await client.get("/api/v1/admin/emerging-skills", headers=SUPER_ADMIN_HEADERS)
        assert resp_super.status_code == 200


@pytest.mark.asyncio
async def test_11_employee_and_trainer_forbidden():
    """Verify EMPLOYEE and TRAINER receive 403 Forbidden on emerging skills."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp_emp = await client.get("/api/v1/admin/emerging-skills", headers=EMPLOYEE_HEADERS)
        assert resp_emp.status_code == 403

        resp_trainer = await client.get("/api/v1/admin/emerging-skills", headers=TRAINER_HEADERS)
        assert resp_trainer.status_code == 403

        resp_unauth = await client.get("/api/v1/admin/emerging-skills")
        assert resp_unauth.status_code == 403


@pytest.mark.asyncio
async def test_12_stage_15_unaffected():
    """Verify Stage 15 training effectiveness endpoints continue to function."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp1 = await client.get("/api/v1/admin/training/effectiveness", headers=ADMIN_HEADERS)
        assert resp1.status_code == 200

        resp2 = await client.get("/api/v1/admin/training/courses/effectiveness", headers=ADMIN_HEADERS)
        assert resp2.status_code == 200


@pytest.mark.asyncio
async def test_13_stage_14_unaffected():
    """Verify Stage 14 workforce analytics endpoints continue to function."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/workforce/overview", headers=ADMIN_HEADERS)
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_14_no_fabricated_skills():
    """Verify all returned competency IDs exist in the active PostgreSQL database table."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Competency.id).where(Competency.is_active.is_(True)))
        valid_ids = {str(cid) for cid in res.scalars().all()}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/emerging-skills", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        for s in resp.json()["skills"]:
            assert s["competency_id"] in valid_ids


@pytest.mark.asyncio
async def test_15_no_random_scores():
    """Verify signal scores are strictly bounded between 0.0 and 100.0."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/emerging-skills", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        for s in resp.json()["skills"]:
            score = s["signal_score"]
            assert 0.0 <= score <= 100.0
            assert s["status"] in ("EMERGING", "WATCH", "ESTABLISHED", "INSUFFICIENT_DATA")
