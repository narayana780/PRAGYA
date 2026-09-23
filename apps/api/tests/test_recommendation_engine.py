import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.main import app
from app.modules.competencies.models import Competency
from app.modules.courses.models import LearningItem, LearningItemCompetency
from app.modules.employees.models import Employee
from app.modules.recommendations.constants import (
    DEFAULT_RECOMMENDATION_CONFIG,
    calculate_duration_fit,
    calculate_level_fit,
    calculate_novelty_score,
    calculate_outcome_coverage,
    calculate_prerequisite_fit,
    calculate_recommendation_score,
    generate_recommendation_reason,
)
from app.modules.recommendations.matcher.keyword import KeywordSemanticMatcher
from app.modules.recommendations.models import LearningPath, LearningRecommendation
from app.modules.recommendations.providers.registry import ProviderRegistry
from app.modules.recommendations.service import LearningPathService, RecommendationService
from app.modules.skill_gaps.models import SkillGap


# =========================================================================
# 1. COURSE CATALOGUE RETRIEVAL
# =========================================================================
@pytest.mark.asyncio
async def test_course_catalogue_retrieval():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/learning-items?limit=20")
        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 35
        assert len(data["items"]) <= 20
        item = data["items"][0]
        assert "id" in item
        assert "title" in item
        assert "provider" in item
        assert "source_mode" in item
        assert item["source_mode"] == "MOCK"


# =========================================================================
# 2. PROVIDER FILTERING
# =========================================================================
@pytest.mark.asyncio
async def test_provider_filtering():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # iGOT filter
        res_igot = await ac.get("/api/v1/learning-items?provider=IGOT")
        assert res_igot.status_code == 200
        items_igot = res_igot.json()["items"]
        assert len(items_igot) >= 20
        assert all(i["provider"] == "IGOT" for i in items_igot)

        # NSSTA filter
        res_nssta = await ac.get("/api/v1/learning-items?provider=NSSTA_TPAC")
        assert res_nssta.status_code == 200
        items_nssta = res_nssta.json()["items"]
        assert len(items_nssta) >= 10
        assert all(i["provider"] == "NSSTA_TPAC" for i in items_nssta)

        # PRAGYA filter
        res_pragya = await ac.get("/api/v1/learning-items?provider=PRAGYA")
        assert res_pragya.status_code == 200
        items_pragya = res_pragya.json()["items"]
        assert len(items_pragya) >= 5
        assert all(i["provider"] == "PRAGYA" for i in items_pragya)


# =========================================================================
# 3. COMPETENCY FILTERING
# =========================================================================
@pytest.mark.asyncio
async def test_competency_filtering():
    async with AsyncSessionLocal() as session:
        comp = (await session.execute(select(Competency).where(Competency.code == "STAT_SURVEY_DESIGN"))).scalar_one()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(f"/api/v1/learning-items?competency_id={comp.id}")
        assert res.status_code == 200
        items = res.json()["items"]
        assert len(items) >= 1
        for it in items:
            comp_ids = [c["competency_id"] for c in it["competencies"]]
            assert str(comp.id) in comp_ids


# =========================================================================
# 4. CANDIDATE GENERATION
# =========================================================================
@pytest.mark.asyncio
async def test_candidate_generation():
    async with AsyncSessionLocal() as session:
        emp = (await session.execute(select(Employee).where(Employee.employee_code == "EMP-0001"))).scalar_one()
        service = RecommendationService(session)
        recs = await service.generate_recommendations(emp.id)
        assert len(recs) > 0
        assert all(r.score > 0 for r in recs)


# =========================================================================
# 5. NO-GAP EMPLOYEE
# =========================================================================
@pytest.mark.asyncio
async def test_no_gap_employee():
    from app.modules.departments.models import Department
    from app.modules.job_roles.models import JobRole

    async with AsyncSessionLocal() as session:
        dept = (await session.execute(select(Department).limit(1))).scalar_one()
        role = (await session.execute(select(JobRole).limit(1))).scalar_one()

        # Create temporary dummy employee with no gaps
        dummy_id = uuid.uuid4()
        emp = Employee(
            id=dummy_id,
            employee_code=f"EMP-NOGAP-{str(dummy_id)[:6]}",
            full_name="No Gap Officer",
            department_id=dept.id,
            job_role_id=role.id,
            designation="Junior Analyst",
            experience_years=2,
            is_active=True,
        )
        session.add(emp)
        await session.flush()

        service = RecommendationService(session)
        recs = await service.generate_recommendations(emp.id)
        # Because dummy officer has no skill gaps, candidate pool is empty
        assert len(recs) == 0

        # Rollback temporary employee
        await session.rollback()


# =========================================================================
# 6. CRITICAL GAP PRIORITIZATION
# =========================================================================
@pytest.mark.asyncio
async def test_critical_gap_prioritization():
    async with AsyncSessionLocal() as session:
        emp = (await session.execute(select(Employee).where(Employee.employee_code == "EMP-0001"))).scalar_one()
        service = RecommendationService(session)
        recs = await service.get_employee_recommendations(emp.id)

        # Top ranked item should target a CRITICAL or HIGH priority gap
        top_rec = recs[0]
        assert top_rec.priority_level in ["CRITICAL", "HIGH"]
        assert top_rec.priority_breakdown.gap_priority_component > 20.0


# =========================================================================
# 7. SEMANTIC MATCHING FALLBACK
# =========================================================================
def test_semantic_matching_fallback():
    matcher = KeywordSemanticMatcher()

    # Exact overlap
    score_exact = matcher.match_competency(
        item_title="Survey Questionnaire Design",
        item_description="Designing standardized survey questionnaires",
        competency_name="Survey Design",
        competency_description="Methodology and questionnaire design",
    )
    assert score_exact > 0.60

    # Unrelated
    score_unrelated = matcher.match_competency(
        item_title="Cloud Security Fundamentals",
        item_description="AWS VPC and IAM security policies",
        competency_name="Sampling Methods",
        competency_description="Probability sampling and survey frame construction",
    )
    assert score_unrelated < 0.20


# =========================================================================
# 8. LEVEL FIT CALCULATION
# =========================================================================
def test_level_fit_calculation():
    # 1. Perfect foundation step (level 2 course for level 1 learner targeting level 3)
    fit_ideal = calculate_level_fit(item_level=2, emp_level=1, required_level=3)
    assert fit_ideal == 100.0

    # 2. Direct match to target required level
    fit_target = calculate_level_fit(item_level=3, emp_level=1, required_level=3)
    assert fit_target == 75.0

    # 3. Same as current level (reinforcement)
    fit_reinforce = calculate_level_fit(item_level=2, emp_level=2, required_level=4)
    assert fit_reinforce == 85.0

    # 4. Excessive jump (level 5 course for level 1 learner)
    fit_too_high = calculate_level_fit(item_level=5, emp_level=1, required_level=3)
    assert fit_too_high < 50.0

    # 5. Over-qualified (level 1 course for level 4 learner)
    fit_too_low = calculate_level_fit(item_level=1, emp_level=4, required_level=4)
    assert fit_too_low == 25.0


# =========================================================================
# 9. PREREQUISITE FIT
# =========================================================================
def test_prerequisite_fit():
    # No prerequisites -> 100.0
    assert calculate_prerequisite_fit([], {}) == 100.0

    # Satisfied prerequisite
    prereqs = [{"competency_code": "STAT_SAMPLING", "min_score": 50.0}]
    scores_met = {"STAT_SAMPLING": 75.0}
    assert calculate_prerequisite_fit(prereqs, scores_met) == 100.0

    # Unmet prerequisite (returns employee's current score 25.0)
    scores_unmet = {"STAT_SAMPLING": 25.0}
    assert calculate_prerequisite_fit(prereqs, scores_unmet) == 25.0


# =========================================================================
# 10. DURATION FIT
# =========================================================================
def test_duration_fit():
    # Short micro-learning (2 hours)
    assert calculate_duration_fit(120) == 100.0
    # Standard module (5 hours)
    assert calculate_duration_fit(300) == 90.0
    # Multi-day programme (24 hours)
    assert calculate_duration_fit(1440) == 80.0
    # Very long bootcamp (> 40 hours)
    assert calculate_duration_fit(3000) == 65.0


# =========================================================================
# 11. NOVELTY
# =========================================================================
def test_novelty_calculation():
    # Completely new item
    assert calculate_novelty_score(is_completed=False, is_in_progress=False) == 100.0

    # Already completed
    assert calculate_novelty_score(is_completed=True) == 0.0

    # In progress
    assert calculate_novelty_score(is_completed=False, is_in_progress=True) == 40.0


# =========================================================================
# 12. RECOMMENDATION SCORE WEIGHTS
# =========================================================================
def test_recommendation_score_weights():
    # Test theoretical maximum score (all 100s)
    total, breakdown = calculate_recommendation_score(
        gap_priority_score=100.0,
        semantic_match_score=100.0,
        level_fit_score=100.0,
        outcome_coverage_score=100.0,
        prerequisite_fit_score=100.0,
        duration_fit_score=100.0,
        novelty_score=100.0,
    )
    assert total == 100.0
    assert breakdown["gap_priority_component"] == 35.0
    assert breakdown["semantic_match_component"] == 25.0
    assert breakdown["level_fit_component"] == 15.0
    assert breakdown["outcome_coverage_component"] == 10.0
    assert breakdown["prerequisite_fit_component"] == 5.0
    assert breakdown["duration_fit_component"] == 5.0
    assert breakdown["novelty_component"] == 5.0


# =========================================================================
# 13. DETERMINISTIC RANKING
# =========================================================================
@pytest.mark.asyncio
async def test_deterministic_ranking():
    async with AsyncSessionLocal() as session:
        emp = (await session.execute(select(Employee).where(Employee.employee_code == "EMP-0001"))).scalar_one()
        service = RecommendationService(session)

        # Run 1
        recs1 = await service.generate_recommendations(emp.id)
        # Run 2
        recs2 = await service.generate_recommendations(emp.id)

        assert len(recs1) == len(recs2)
        for r1, r2 in zip(recs1, recs2, strict=False):
            assert r1.learning_item_id == r2.learning_item_id
            assert r1.score == r2.score
            assert r1.rank == r2.rank


# =========================================================================
# 14. EXPLANATION GENERATION
# =========================================================================
def test_explanation_generation():
    reason = generate_recommendation_reason(
        competency_name="Survey Design",
        priority_level="CRITICAL",
        gap_score=64.2,
        current_score=25.8,
        required_score=90.0,
        role_name="Statistical Officer",
        item_title="Survey Questionnaire Design",
        item_provider="iGOT",
        coverage_level="WORKING",
        level_fit_score=100.0,
        is_completed=False,
    )
    assert "Survey Design is a CRITICAL role requirement" in reason["summary"]
    assert "64.2-pt deficit" in reason["summary"]
    assert "Survey Design" in reason["gap_reason"]
    assert "25.8" in reason["gap_reason"]
    assert "Survey Design" in reason["competency_reason"]
    assert "iGOT" in reason["novelty_reason"]
    assert "not been completed previously" in reason["novelty_reason"]


# =========================================================================
# 15. LEARNING PATH GENERATION
# =========================================================================
@pytest.mark.asyncio
async def test_learning_path_generation():
    async with AsyncSessionLocal() as session:
        emp = (await session.execute(select(Employee).where(Employee.employee_code == "EMP-0001"))).scalar_one()
        service = LearningPathService(session)
        path = await service.generate_learning_path(emp.id)

        assert path is not None
        assert "Cadre Advancement Pathway" in path.title
        assert len(path.items) >= 3
        # Check sequence order is sequential
        for idx, item in enumerate(path.items, 1):
            assert item.sequence_order == idx


# =========================================================================
# 16. PROVIDER MIXING IN LEARNING PATH
# =========================================================================
@pytest.mark.asyncio
async def test_provider_mixing():
    async with AsyncSessionLocal() as session:
        emp = (await session.execute(select(Employee).where(Employee.employee_code == "EMP-0001"))).scalar_one()
        service = LearningPathService(session)
        path = await service.get_learning_path(emp.id)
        assert path is not None

        providers = {item.learning_item.provider for item in path.items}
        # Path should feature mixed providers (e.g. IGOT, PRAGYA, and NSSTA_TPAC)
        assert len(providers) >= 2


# =========================================================================
# 17. COMPLETED COURSE EXCLUSION
# =========================================================================
@pytest.mark.asyncio
async def test_completed_course_exclusion():
    async with AsyncSessionLocal() as session:
        emp = (await session.execute(select(Employee).where(Employee.employee_code == "EMP-0001"))).scalar_one()
        service = RecommendationService(session)
        recs = await service.get_employee_recommendations(emp.id)

        # Ananya completed Python and Sampling trainings in Stage 5/6 training history
        # She should not have completed items as her top #1 recommendation
        top_rec = recs[0]
        assert top_rec.priority_breakdown.novelty_component == 5.0  # Full novelty


# =========================================================================
# 18. DISMISSED RECOMMENDATION
# =========================================================================
@pytest.mark.asyncio
async def test_dismissed_recommendation():
    async with AsyncSessionLocal() as session:
        emp = (await session.execute(select(Employee).where(Employee.employee_code == "EMP-0001"))).scalar_one()
        rec = (
            await session.execute(
                select(LearningRecommendation)
                .where(LearningRecommendation.employee_id == emp.id)
                .order_by(LearningRecommendation.rank.desc())
            )
        ).scalars().first()

    assert rec is not None
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(f"/api/v1/employees/{emp.id}/recommendations/{rec.id}/dismiss")
        assert res.status_code == 200
        assert res.json()["status"] == "DISMISSED"


# =========================================================================
# 19. RECOMMENDATION REGENERATION
# =========================================================================
@pytest.mark.asyncio
async def test_recommendation_regeneration():
    async with AsyncSessionLocal() as session:
        emp = (await session.execute(select(Employee).where(Employee.employee_code == "EMP-0001"))).scalar_one()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(f"/api/v1/employees/{emp.id}/recommendations/generate")
        assert res.status_code == 200
        recs = res.json()
        assert len(recs) > 0


# =========================================================================
# 20. ROLE-AWARE RECOMMENDATIONS
# =========================================================================
@pytest.mark.asyncio
async def test_role_aware_recommendations():
    async with AsyncSessionLocal() as session:
        emp = (await session.execute(select(Employee).where(Employee.employee_code == "EMP-0001"))).scalar_one()
        service = LearningPathService(session)
        path = await service.get_learning_path(emp.id)
        assert path is not None
        # Ananya is Statistical Officer targeting Senior Statistical Officer
        assert "Senior Statistical Officer" in path.title or "Cadre Advancement" in path.title


# =========================================================================
# 21. INVALID EMPLOYEE
# =========================================================================
@pytest.mark.asyncio
async def test_invalid_employee():
    fake_id = uuid.uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(f"/api/v1/employees/{fake_id}/recommendations")
        assert res.status_code == 404
        data = res.json()
        assert data.get("error", {}).get("code") == "EMPLOYEE_NOT_FOUND" or data.get("code") == "EMPLOYEE_NOT_FOUND"


# =========================================================================
# 22. INVALID LEARNING ITEM
# =========================================================================
@pytest.mark.asyncio
async def test_invalid_learning_item():
    fake_id = uuid.uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(f"/api/v1/learning-items/{fake_id}")
        assert res.status_code == 404
        data = res.json()
        assert data.get("error", {}).get("code") == "LEARNING_ITEM_NOT_FOUND" or data.get("code") == "LEARNING_ITEM_NOT_FOUND"


# =========================================================================
# 23. RECOMMENDATION PERSISTENCE
# =========================================================================
@pytest.mark.asyncio
async def test_recommendation_persistence():
    async with AsyncSessionLocal() as session:
        emp = (await session.execute(select(Employee).where(Employee.employee_code == "EMP-0001"))).scalar_one()
        recs = (
            await session.execute(
                select(LearningRecommendation).where(LearningRecommendation.employee_id == emp.id)
            )
        ).scalars().all()
        assert len(recs) > 0
        rec = recs[0]
        assert rec.score > 0
        assert rec.rank >= 1
        assert "structured_reason" in rec.recommendation_metadata


# =========================================================================
# 24. CATALOGUE DIAGNOSTIC & FILTER REGRESSION TESTS
# =========================================================================
@pytest.mark.asyncio
async def test_unfiltered_catalogue():
    """Confirms unfiltered catalogue returns exactly 40 items and total = 40."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/learning-items?limit=100")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 40
        assert len(data["items"]) == 40


@pytest.mark.asyncio
async def test_provider_filter_exact_counts():
    """Confirms exact provider breakdown and verifies provider=ALL returns all 40."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # IGOT -> 22
        res = await ac.get("/api/v1/learning-items?provider=IGOT&limit=100")
        assert res.status_code == 200
        assert res.json()["total"] == 22

        # NSSTA_TPAC -> 11
        res = await ac.get("/api/v1/learning-items?provider=NSSTA_TPAC&limit=100")
        assert res.status_code == 200
        assert res.json()["total"] == 11

        # PRAGYA -> 7
        res = await ac.get("/api/v1/learning-items?provider=PRAGYA&limit=100")
        assert res.status_code == 200
        assert res.json()["total"] == 7

        # ALL -> 40
        res = await ac.get("/api/v1/learning-items?provider=ALL&limit=100")
        assert res.status_code == 200
        assert res.json()["total"] == 40


@pytest.mark.asyncio
async def test_competency_filter_labour_statistics():
    """Confirms Labour Statistics filter returns mapped items and competency_id=ALL returns 40."""
    async with AsyncSessionLocal() as session:
        comp = (await session.execute(select(Competency).where(Competency.code == "STAT_LABOUR_STATISTICS"))).scalar_one()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(f"/api/v1/learning-items?competency_id={comp.id}")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] >= 1
        assert any("STAT_LABOUR_STATISTICS" in [c["competency_code"] for c in it["competencies"]] for it in data["items"])

        # ALL competency string
        res_all = await ac.get("/api/v1/learning-items?competency_id=ALL&limit=100")
        assert res_all.status_code == 200
        assert res_all.json()["total"] == 40


@pytest.mark.asyncio
async def test_difficulty_filter():
    """Confirms BEGINNER, INTERMEDIATE, ADVANCED, and ALL filters."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res_b = await ac.get("/api/v1/learning-items?difficulty=BEGINNER&limit=100")
        assert res_b.status_code == 200
        assert res_b.json()["total"] == 13

        res_i = await ac.get("/api/v1/learning-items?difficulty=INTERMEDIATE&limit=100")
        assert res_i.status_code == 200
        assert res_i.json()["total"] == 21

        res_a = await ac.get("/api/v1/learning-items?difficulty=ADVANCED&limit=100")
        assert res_a.status_code == 200
        assert res_a.json()["total"] == 6

        res_all = await ac.get("/api/v1/learning-items?difficulty=ALL&limit=100")
        assert res_all.status_code == 200
        assert res_all.json()["total"] == 40


@pytest.mark.asyncio
async def test_format_filter_aliases():
    """Confirms format_type, format alias, and format=ALL."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res_ft = await ac.get("/api/v1/learning-items?format_type=SELF_PACED&limit=100")
        assert res_ft.status_code == 200
        assert res_ft.json()["total"] == 22

        res_f = await ac.get("/api/v1/learning-items?format=SELF_PACED&limit=100")
        assert res_f.status_code == 200
        assert res_f.json()["total"] == 22

        res_all = await ac.get("/api/v1/learning-items?format=ALL&limit=100")
        assert res_all.status_code == 200
        assert res_all.json()["total"] == 40


@pytest.mark.asyncio
async def test_combined_filters():
    """Confirms multiple filters narrow down results accurately."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/learning-items?provider=IGOT&difficulty=INTERMEDIATE&format=SELF_PACED&limit=100")
        assert res.status_code == 200
        assert res.json()["total"] == 11
        for it in res.json()["items"]:
            assert it["provider"] == "IGOT"
            assert it["difficulty"] == "INTERMEDIATE"
            assert it["format"] == "SELF_PACED"


@pytest.mark.asyncio
async def test_no_matching_filter():
    """Confirms impossible search term returns 0 items and total = 0 without error."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/learning-items?search=NONEXISTENT_QUERY_XYZ_12345")
        assert res.status_code == 200
        assert res.json()["total"] == 0
        assert res.json()["items"] == []


@pytest.mark.asyncio
async def test_reset_filters_and_pagination():
    """Confirms empty/reset query returns all 40, and pagination works."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Reset / empty params
        res_reset = await ac.get("/api/v1/learning-items?provider=&difficulty=&search=&limit=100")
        assert res_reset.status_code == 200
        assert res_reset.json()["total"] == 40

        # Pagination: Page 1 (limit 15, offset 0)
        p1 = await ac.get("/api/v1/learning-items?limit=15&offset=0")
        assert p1.status_code == 200
        data1 = p1.json()
        assert len(data1["items"]) == 15
        assert data1["total"] == 40

        # Pagination: Page 2 (limit 15, offset 15)
        p2 = await ac.get("/api/v1/learning-items?limit=15&offset=15")
        assert p2.status_code == 200
        data2 = p2.json()
        assert len(data2["items"]) == 15
        assert data2["total"] == 40

        # Disjoint item IDs
        ids1 = {it["id"] for it in data1["items"]}
        ids2 = {it["id"] for it in data2["items"]}
        assert len(ids1.intersection(ids2)) == 0

