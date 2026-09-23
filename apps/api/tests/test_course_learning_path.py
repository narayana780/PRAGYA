"""
PRAGYA Course Learning Path & Progression Test Suite
Validates all 28+ requirements for the structured learning path:
1. Curriculum catalogue loading and module hierarchy
2. Module 1 Foundations (videos, readings, knowledge check)
3. Module 2 Methodology & Practical Assignment + Knowledge Check
4. Module 3 Official Standards & Assessment
5. Module 4 PRAGYA Virtual Lab integration & verification
6. Authoritative completion rules (no automatic complete on open)
7. Video completion threshold (>= 90%)
8. Reading completion verification
9. Knowledge check scoring and retry logic
10. Assignment rubric evaluation and CompetencyEvidence generation
11. Sequential module locking and unlocking
12. Virtual Lab requirement (lab alone cannot complete course)
13. Final assessment gatekeeper
14. Authoritative course completion (100% only on genuine completion)
15. Elimination of bypass shortcuts
16. Competency recalibration post-course
"""
import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, delete

from app.main import app
from app.modules.assessments.models import CompetencyEvidence, EmployeeCompetency
from app.modules.courses.models import CourseProgress, CourseResourceProgress, ModuleActivityAttempt
from app.modules.employees.models import Employee
from app.modules.labs.models import LabScenario, LabSession
from app.modules.labs.seed_scenarios import seed_virtual_labs
from app.modules.recommendations.models import LearningItem


@pytest.fixture(autouse=True)
async def seed_fixtures(db_session):
    """Seed virtual labs."""
    await seed_virtual_labs(db_session)


@pytest.fixture
async def sample_course(db_session):
    """Retrieves the flagship Survey Methodology course (IGOT-STAT-004)."""
    res = await db_session.execute(
        select(LearningItem).where(LearningItem.provider_item_id == "IGOT-STAT-004")
    )
    item = res.scalar_one_or_none()
    if not item:
        res = await db_session.execute(select(LearningItem).limit(1))
        item = res.scalar_one()
    return item


@pytest.fixture
async def test_employee(db_session, sample_course):
    """Retrieves an employee and resets their course progress for isolation."""
    res = await db_session.execute(select(Employee).limit(1))
    emp = res.scalar_one()
    await db_session.execute(
        delete(CourseProgress).where(
            CourseProgress.employee_id == emp.id,
            CourseProgress.learning_item_id == sample_course.id,
        )
    )
    await db_session.execute(
        delete(CourseResourceProgress).where(
            CourseResourceProgress.employee_id == emp.id,
            CourseResourceProgress.learning_item_id == sample_course.id,
        )
    )
    await db_session.execute(
        delete(ModuleActivityAttempt).where(
            ModuleActivityAttempt.employee_id == emp.id,
            ModuleActivityAttempt.learning_item_id == sample_course.id,
        )
    )
    await db_session.execute(
        delete(LabSession).where(
            LabSession.employee_id == emp.id,
        )
    )
    await db_session.commit()
    return emp


@pytest.mark.asyncio
async def test_curriculum_structure_loads(sample_course):
    """1. Curriculum structure loads correctly with 4 modules and final assessment."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/courses/{str(sample_course.id)}/curriculum")
        assert response.status_code == 200
        data = response.json()
        assert data["learning_item_id"] == str(sample_course.id)
        assert "modules" in data
        assert len(data["modules"]) == 4
        assert "final_assessment" in data


@pytest.mark.asyncio
async def test_module_1_content_and_kc(sample_course):
    """2 & 3. Module 1 contains learning resources and knowledge check."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/courses/{str(sample_course.id)}/curriculum")
        data = response.json()
        mod1 = data["modules"][0]
        assert mod1["id"] == 1
        assert len(mod1["resources"]) >= 2
        types = [r["type"] for r in mod1["resources"]]
        assert "VIDEO" in types
        assert "READING" in types
        assert mod1["knowledge_check"] is not None
        assert len(mod1["knowledge_check"]["questions"]) >= 3
        assert mod1["knowledge_check"]["pass_threshold_percentage"] == 75.0


@pytest.mark.asyncio
async def test_module_2_assignment_and_kc(sample_course):
    """4 & 5. Module 2 contains assignment and knowledge check."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/courses/{str(sample_course.id)}/curriculum")
        data = response.json()
        mod2 = data["modules"][1]
        assert mod2["id"] == 2
        assert mod2["assignment"] is not None
        assert "scenario" in mod2["assignment"]
        assert mod2["knowledge_check"] is not None
        assert mod2["knowledge_check"]["pass_threshold_percentage"] == 75.0


@pytest.mark.asyncio
async def test_module_3_standards_and_module_4_virtual_lab(sample_course):
    """6 & 7. Module 3 contains standards and Module 4 contains Virtual Lab."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/courses/{str(sample_course.id)}/curriculum")
        data = response.json()
        mod3 = data["modules"][2]
        assert mod3["id"] == 3
        assert len(mod3["resources"]) >= 2
        assert mod3["knowledge_check"] is not None

        mod4 = data["modules"][3]
        assert mod4["id"] == 4
        assert mod4["is_lab"] is True
        assert "lab_scenario_id" in mod4


@pytest.mark.asyncio
async def test_initial_progress_starts_at_module_1(sample_course, test_employee):
    """8. Progress starts at 0% with only Module 1 unlocked."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers = {"X-Employee-Id": str(test_employee.id)}
        response = await client.get(
            f"/api/v1/courses/{str(sample_course.id)}/progress",
            headers=headers,
        )
        assert response.status_code == 200
        prog = response.json()
        assert prog["progress_percentage"] == 0.0
        assert prog["completed_modules"] == []
        assert prog["unlocked_modules"] == [1]
        assert prog["course_completed"] is False


@pytest.mark.asyncio
async def test_video_completion_threshold_enforced(sample_course, test_employee):
    """9 & 10. Video below 90% is not completed; >= 90% marks completed."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers = {"X-Employee-Id": str(test_employee.id)}
        payload_low = {
            "module_id": 1,
            "resource_type": "VIDEO",
            "progress_seconds": 50,
            "duration_seconds": 200,
            "progress_percentage": 25.0,
            "is_completed": False,
        }
        res_low = await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/resources/mod1-video-1/progress",
            json=payload_low,
            headers=headers,
        )
        assert res_low.status_code == 200
        data_low = res_low.json()
        assert data_low["is_completed"] is False

        payload_high = {
            "module_id": 1,
            "resource_type": "VIDEO",
            "progress_seconds": 185,
            "duration_seconds": 200,
            "progress_percentage": 92.5,
            "is_completed": True,
        }
        res_high = await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/resources/mod1-video-1/progress",
            json=payload_high,
            headers=headers,
        )
        assert res_high.status_code == 200
        data_high = res_high.json()
        assert data_high["is_completed"] is True


@pytest.mark.asyncio
async def test_video_cannot_be_manually_completed_without_watch_threshold(sample_course, test_employee):
    """Bypass prevention: sending is_completed: true with low watch progress does not complete video."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers = {"X-Employee-Id": str(test_employee.id)}
        # Attempt to exploit manual complete flag with only 10 seconds of 200 seconds watched (5%)
        bypass_payload = {
            "module_id": 1,
            "resource_type": "VIDEO",
            "progress_seconds": 10,
            "duration_seconds": 200,
            "progress_percentage": 5.0,
            "is_completed": True,
        }
        res = await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/resources/mod1-video-2/progress",
            json=bypass_payload,
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()
        # Authoritative backend rejection: must be False
        assert data["is_completed"] is False


@pytest.mark.asyncio
async def test_reading_resource_completion(sample_course, test_employee):
    """11. Reading resource marked completed updates progress."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers = {"X-Employee-Id": str(test_employee.id)}
        payload = {
            "module_id": 1,
            "resource_type": "READING",
            "progress_seconds": 600,
            "duration_seconds": 600,
            "progress_percentage": 100.0,
            "is_completed": True,
        }
        res = await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/resources/mod1-read-1/progress",
            json=payload,
            headers=headers,
        )
        assert res.status_code == 200
        assert res.json()["is_completed"] is True


@pytest.mark.asyncio
async def test_module_1_kc_failure_does_not_complete_module(sample_course, test_employee):
    """12, 13 & 14. Submitting failing answers does not mark Module 1 complete."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers = {"X-Employee-Id": str(test_employee.id)}
        wrong_answers = {
            "m1-q1": 0,
            "m1-q2": 0,
            "m1-q3": 0,
            "m1-q4": 0,
        }
        res = await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/modules/1/knowledge-check",
            json={"answers": wrong_answers},
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["passed"] is False
        assert data["module_completed"] is False

        prog_res = await client.get(
            f"/api/v1/courses/{str(sample_course.id)}/progress",
            headers=headers,
        )
        prog = prog_res.json()
        assert 1 not in prog["completed_modules"]
        assert 2 not in prog["unlocked_modules"]


@pytest.mark.asyncio
async def test_module_1_passing_kc_completes_module_and_unlocks_module_2(sample_course, test_employee):
    """15. Submitting correct answers passes KC and unlocks Module 2."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers = {"X-Employee-Id": str(test_employee.id)}
        for res_id in ["mod1-video-1", "mod1-video-2", "mod1-read-1", "mod1-read-2"]:
            await client.post(
                f"/api/v1/courses/{str(sample_course.id)}/resources/{res_id}/progress",
                json={
                    "module_id": 1,
                    "resource_type": "VIDEO" if "video" in res_id else "READING",
                    "progress_seconds": 600,
                    "duration_seconds": 600,
                    "progress_percentage": 100.0,
                    "is_completed": True,
                },
                headers=headers,
            )

        correct_answers = {
            "m1-q1": 1,
            "m1-q2": 1,
            "m1-q3": 1,
            "m1-q4": 2,
        }
        res = await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/modules/1/knowledge-check",
            json={"answers": correct_answers},
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["passed"] is True
        assert data["module_completed"] is True

        prog_res = await client.get(
            f"/api/v1/courses/{str(sample_course.id)}/progress",
            headers=headers,
        )
        prog = prog_res.json()
        assert 1 in prog["completed_modules"]
        assert 2 in prog["unlocked_modules"]
        assert prog["progress_percentage"] >= 20.0


@pytest.mark.asyncio
async def test_module_2_assignment_evaluation_and_evidence(sample_course, test_employee, db_session):
    """17, 18 & 19. Module 2 assignment rubric grading & CompetencyEvidence creation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers = {"X-Employee-Id": str(test_employee.id)}

        flawed_payload = {
            "sampling_method": "SIMPLE_RANDOM",
            "allocation_strategy": "EQUAL",
            "non_response_buffer": "ZERO",
            "justification_code": "CONVENIENCE",
        }
        flawed_res = await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/modules/2/assignment",
            json=flawed_payload,
            headers=headers,
        )
        assert flawed_res.status_code == 200
        flawed_data = flawed_res.json()
        assert flawed_data["passed"] is False
        assert flawed_data["percentage"] < 75.0

        optimal_payload = {
            "sampling_method": "STRATIFIED_TWO_STAGE",
            "allocation_strategy": "NEYMAN_OPTIMAL",
            "non_response_buffer": "12_PERCENT",
            "justification_code": "VARIANCE_MINIMIZATION",
        }
        opt_res = await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/modules/2/assignment",
            json=optimal_payload,
            headers=headers,
        )
        assert opt_res.status_code == 200
        opt_data = opt_res.json()
        assert opt_data["passed"] is True
        assert opt_data["percentage"] >= 90.0
        assert opt_data["evidence_id"] is not None

        ev_id = uuid.UUID(opt_data["evidence_id"])
        ev_res = await db_session.execute(
            select(CompetencyEvidence).where(CompetencyEvidence.id == ev_id)
        )
        ev = ev_res.scalar_one_or_none()
        assert ev is not None
        assert ev.employee_id == test_employee.id


@pytest.mark.asyncio
async def test_virtual_lab_alone_cannot_complete_course(sample_course, test_employee):
    """16 & 17. Virtual Lab cannot complete the course without coursework and assessment."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers = {"X-Employee-Id": str(test_employee.id)}
        complete_res = await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/complete",
            headers=headers,
        )
        assert complete_res.status_code == 400
        assert "Cannot complete course" in complete_res.text


@pytest.mark.asyncio
async def test_course_completion_gatekeeper_and_recalibration(sample_course, test_employee, db_session):
    """20 to 28. Full authentic learning journey through to final completion and recalibration."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers = {"X-Employee-Id": str(test_employee.id)}

        # Step 1: Complete Module 1
        for res_id in ["mod1-video-1", "mod1-video-2", "mod1-read-1", "mod1-read-2"]:
            await client.post(
                f"/api/v1/courses/{str(sample_course.id)}/resources/{res_id}/progress",
                json={
                    "module_id": 1,
                    "resource_type": "VIDEO" if "video" in res_id else "READING",
                    "progress_seconds": 600,
                    "duration_seconds": 600,
                    "progress_percentage": 100.0,
                    "is_completed": True,
                },
                headers=headers,
            )
        await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/modules/1/knowledge-check",
            json={"answers": {"m1-q1": 1, "m1-q2": 1, "m1-q3": 1, "m1-q4": 2}},
            headers=headers,
        )

        # Step 2: Complete Module 2
        for res_id in ["mod2-video-1", "mod2-read-1"]:
            await client.post(
                f"/api/v1/courses/{str(sample_course.id)}/resources/{res_id}/progress",
                json={
                    "module_id": 2,
                    "resource_type": "VIDEO" if "video" in res_id else "READING",
                    "progress_seconds": 600,
                    "duration_seconds": 600,
                    "progress_percentage": 100.0,
                    "is_completed": True,
                },
                headers=headers,
            )
        await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/modules/2/assignment",
            json={
                "sampling_method": "STRATIFIED_TWO_STAGE",
                "allocation_strategy": "NEYMAN_OPTIMAL",
                "non_response_buffer": "12_PERCENT",
                "justification_code": "VARIANCE_MINIMIZATION",
            },
            headers=headers,
        )
        await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/modules/2/knowledge-check",
            json={"answers": {"m2-q1": 2, "m2-q2": 0, "m2-q3": 1}},
            headers=headers,
        )

        # Step 3: Complete Module 3
        for res_id in ["mod3-read-1", "mod3-read-2"]:
            await client.post(
                f"/api/v1/courses/{str(sample_course.id)}/resources/{res_id}/progress",
                json={
                    "module_id": 3,
                    "resource_type": "READING",
                    "progress_seconds": 600,
                    "duration_seconds": 600,
                    "progress_percentage": 100.0,
                    "is_completed": True,
                },
                headers=headers,
            )
        await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/modules/3/knowledge-check",
            json={"answers": {"m3-q1": 1, "m3-q2": 1, "m3-q3": 0}},
            headers=headers,
        )

        # Verify Modules 1, 2, 3 completed
        prog_res = await client.get(
            f"/api/v1/courses/{str(sample_course.id)}/progress",
            headers=headers,
        )
        prog = prog_res.json()
        assert 1 in prog["completed_modules"]
        assert 2 in prog["completed_modules"]
        assert 3 in prog["completed_modules"]
        assert 4 in prog["unlocked_modules"]
        assert 5 in prog["unlocked_modules"]

        # Step 4: Create a verified Virtual Lab session in DB
        lab_session = LabSession(
            id=uuid.uuid4(),
            employee_id=test_employee.id,
            scenario_id=uuid.UUID("22222222-3333-4444-5555-666666666602"),
            status="COMPLETED",
            score=88.0,
            percentage=88.0,
            confidence=0.92,
        )
        db_session.add(lab_session)
        await db_session.commit()

        # Step 5: Submit Final Assessment
        final_answers = {
            "fa-q1": 1,  # Stratified Sampling with disproportionate allocation
            "fa-q2": 0,  # Non-response bias distorts aggregates
            "fa-q3": 1,  # Weight 200
            "fa-q4": 1,  # Collection of Statistics Act, 2008
            "fa-q5": 1,  # Minimizes variance
            "fa-q6": 1,  # SDMX DSDs
        }
        fa_res = await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/final-assessment",
            json={"answers": final_answers},
            headers=headers,
        )
        assert fa_res.status_code == 200
        fa_data = fa_res.json()
        assert fa_data["passed"] is True
        assert fa_data["score"] == 6.0
        assert fa_data["percentage"] == 100.0

        # Step 6: Complete Course
        comp_res = await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/complete",
            headers=headers,
        )
        assert comp_res.status_code == 200
        comp_data = comp_res.json()
        assert comp_data["success"] is True
        assert comp_data["progress_percentage"] == 100.0

        # Step 7: Recalibrate Competencies
        recal_res = await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/recalibrate",
            headers=headers,
        )
        assert recal_res.status_code == 200
        recal_data = recal_res.json()
        assert recal_data["recalibrated"] is True
        assert len(recal_data["recalibrated_competencies"]) > 0

        # Step 8: Persistence survives fresh DB query
        fresh_prog = await client.get(
            f"/api/v1/courses/{str(sample_course.id)}/progress",
            headers=headers,
        )
        assert fresh_prog.status_code == 200
        fp = fresh_prog.json()
        assert fp["course_completed"] is True
        assert fp["progress_percentage"] == 100.0
        assert 1 in fp["completed_modules"]
        assert 2 in fp["completed_modules"]
        assert 3 in fp["completed_modules"]
        assert 4 in fp["completed_modules"]


@pytest.mark.asyncio
async def test_final_assessment_locked_until_modules_complete(sample_course, test_employee):
    """Prerequisite enforcement: Final assessment cannot be taken before Modules 1-3."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers = {"X-Employee-Id": str(test_employee.id)}
        res = await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/final-assessment",
            json={"answers": {"fa-q1": 1}},
            headers=headers,
        )
        assert res.status_code == 400
        assert "Complete Modules 1-3 first" in res.text


@pytest.mark.asyncio
async def test_final_assessment_failure_prevents_completion(sample_course, test_employee, db_session):
    """Final assessment failing (< 70%) prevents course completion."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers = {"X-Employee-Id": str(test_employee.id)}

        # Complete Modules 1-3
        for res_id in ["mod1-video-1", "mod1-video-2", "mod1-read-1", "mod1-read-2"]:
            await client.post(
                f"/api/v1/courses/{str(sample_course.id)}/resources/{res_id}/progress",
                json={"module_id": 1, "resource_type": "VIDEO" if "video" in res_id else "READING", "progress_seconds": 600, "duration_seconds": 600, "progress_percentage": 100.0, "is_completed": True},
                headers=headers,
            )
        await client.post(f"/api/v1/courses/{str(sample_course.id)}/modules/1/knowledge-check", json={"answers": {"m1-q1": 1, "m1-q2": 1, "m1-q3": 1, "m1-q4": 2}}, headers=headers)

        for res_id in ["mod2-video-1", "mod2-read-1"]:
            await client.post(
                f"/api/v1/courses/{str(sample_course.id)}/resources/{res_id}/progress",
                json={"module_id": 2, "resource_type": "VIDEO" if "video" in res_id else "READING", "progress_seconds": 600, "duration_seconds": 600, "progress_percentage": 100.0, "is_completed": True},
                headers=headers,
            )
        await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/modules/2/assignment",
            json={"sampling_method": "STRATIFIED_TWO_STAGE", "allocation_strategy": "NEYMAN_OPTIMAL", "non_response_buffer": "12_PERCENT", "justification_code": "VARIANCE_MINIMIZATION"},
            headers=headers,
        )
        await client.post(f"/api/v1/courses/{str(sample_course.id)}/modules/2/knowledge-check", json={"answers": {"m2-q1": 2, "m2-q2": 0, "m2-q3": 1}}, headers=headers)

        for res_id in ["mod3-read-1", "mod3-read-2"]:
            await client.post(
                f"/api/v1/courses/{str(sample_course.id)}/resources/{res_id}/progress",
                json={"module_id": 3, "resource_type": "READING", "progress_seconds": 600, "duration_seconds": 600, "progress_percentage": 100.0, "is_completed": True},
                headers=headers,
            )
        await client.post(f"/api/v1/courses/{str(sample_course.id)}/modules/3/knowledge-check", json={"answers": {"m3-q1": 1, "m3-q2": 1, "m3-q3": 0}}, headers=headers)

        # Add passing lab session
        lab_session = LabSession(
            id=uuid.uuid4(),
            employee_id=test_employee.id,
            scenario_id=uuid.UUID("22222222-3333-4444-5555-666666666602"),
            status="COMPLETED",
            score=88.0,
            percentage=88.0,
            confidence=0.92,
        )
        db_session.add(lab_session)
        await db_session.commit()

        # Submit FAILING answers to final assessment (0% score)
        failing_answers = {"fa-q1": 0, "fa-q2": 2, "fa-q3": 0, "fa-q4": 0, "fa-q5": 0, "fa-q6": 0}
        fa_res = await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/final-assessment",
            json={"answers": failing_answers},
            headers=headers,
        )
        assert fa_res.status_code == 200
        assert fa_res.json()["passed"] is False

        # Completion attempt MUST fail
        comp_res = await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/complete",
            headers=headers,
        )
        assert comp_res.status_code == 400
        assert "Final Course Comprehensive Assessment" in comp_res.text


@pytest.mark.asyncio
async def test_knowledge_check_retry_allows_progression(sample_course, test_employee):
    """Knowledge check supports retrying after failure and updates progress once passed."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers = {"X-Employee-Id": str(test_employee.id)}

        for res_id in ["mod1-video-1", "mod1-video-2", "mod1-read-1", "mod1-read-2"]:
            await client.post(
                f"/api/v1/courses/{str(sample_course.id)}/resources/{res_id}/progress",
                json={"module_id": 1, "resource_type": "VIDEO" if "video" in res_id else "READING", "progress_seconds": 600, "duration_seconds": 600, "progress_percentage": 100.0, "is_completed": True},
                headers=headers,
            )

        # Attempt 1: Failed
        res1 = await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/modules/1/knowledge-check",
            json={"answers": {"m1-q1": 0, "m1-q2": 0, "m1-q3": 0, "m1-q4": 0}},
            headers=headers,
        )
        assert res1.json()["passed"] is False
        assert res1.json()["module_completed"] is False

        # Attempt 2: Passed
        res2 = await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/modules/1/knowledge-check",
            json={"answers": {"m1-q1": 1, "m1-q2": 1, "m1-q3": 1, "m1-q4": 2}},
            headers=headers,
        )
        assert res2.json()["passed"] is True
        assert res2.json()["module_completed"] is True


@pytest.mark.asyncio
async def test_igot_resource_metadata_and_architecture(sample_course, test_employee):
    """iGOT resources have official provider metadata, external IDs, and NO local fake video MP4 URLs."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(f"/api/v1/courses/{str(sample_course.id)}/curriculum")
        assert res.status_code == 200
        data = res.json()

        assert data["provider_label"] == "iGOT & PRAGYA"
        assert data["learning_path_mode"] == "PRAGYA Demonstration Learning Path"

        mod1 = next(m for m in data["modules"] if m["id"] == 1)
        v1 = next(r for r in mod1["resources"] if r["id"] == "mod1-video-1")
        assert v1["provider"] == "iGOT"
        assert v1.get("external_resource_id") is None
        assert v1.get("external_url") is None
        assert v1["completion_required"] is True
        assert "video_url" not in v1 or not v1.get("video_url")

        r1 = next(r for r in mod1["resources"] if r["id"] == "mod1-read-1")
        assert r1["provider"] == "PRAGYA"
        assert r1["completion_required"] is True


@pytest.mark.asyncio
async def test_launch_resource_does_not_fake_completion(sample_course, test_employee):
    """Launching an iGOT resource without URL returns NOT_CONFIGURED and never fakes completion or unlocks modules."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers = {"X-Employee-Id": str(test_employee.id)}

        res = await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/resources/mod1-video-1/launch",
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "NOT_CONFIGURED"
        assert data["verification_status"] == "NOT_VERIFIED"
        assert data["provider"] == "iGOT"
        assert "link not configured" in data["message"]

        # Verify CourseProgress is strictly NOT_CONFIGURED and NOT completed
        prog_res = await client.get(f"/api/v1/courses/{str(sample_course.id)}/progress", headers=headers)
        assert prog_res.status_code == 200
        prog_data = prog_res.json()
        res_item = prog_data["resource_progress"].get("mod1-video-1", {})
        assert res_item.get("is_completed") is False
        assert res_item.get("status") == "NOT_CONFIGURED"
        assert res_item.get("status") != "IN_PROGRESS"
        assert res_item.get("verification_status") == "NOT_VERIFIED"
        assert 1 not in prog_data["completed_modules"]


@pytest.mark.asyncio
async def test_provider_sync_reports_unconfigured_honestly(sample_course, test_employee):
    """Synchronizing provider completion when live iGOT credentials are not configured honestly reports status."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers = {"X-Employee-Id": str(test_employee.id)}

        res = await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/resources/mod1-video-1/sync",
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["verified"] is False
        assert data["reason"] == "IGOT_INTEGRATION_NOT_CONFIGURED"
        assert data["status"] == "NOT_VERIFIED"
        assert "Official iGOT completion verification" in data["message"] or "iGOT completion verification is not configured" in data["message"]


@pytest.mark.asyncio
async def test_igot_state_machine_and_verification_rules(sample_course, test_employee, monkeypatch):
    """Validates truthful iGOT state machine: NOT_CONFIGURED, NOT_STARTED, LAUNCHED, and VERIFIED_COMPLETED."""
    from app.modules.courses import curriculum as curr_module
    from app.modules.training_history.models import TrainingHistory

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers = {"X-Employee-Id": str(test_employee.id)}

        # 1. Unconfigured resource: status MUST be NOT_CONFIGURED, never IN_PROGRESS
        prog_res = await client.get(f"/api/v1/courses/{str(sample_course.id)}/progress", headers=headers)
        data = prog_res.json()
        res_mod1 = data["resource_progress"]["mod1-video-1"]
        assert res_mod1["status"] == "NOT_CONFIGURED"
        assert res_mod1["status"] != "IN_PROGRESS"

        # 2. Mock a configured resource with external URL
        orig_get_curr = curr_module.get_curriculum_for_item
        def mock_get_curr(item_id, provider_id=None, title=None):
            curr = orig_get_curr(item_id, provider_id, title)
            import copy
            curr_copy = copy.deepcopy(curr)
            for m in curr_copy.get("modules", []):
                for r in m.get("resources", []):
                    if r["id"] == "mod1-video-1":
                        r["external_url"] = "https://igotkarmayogi.gov.in/app/toc/do_test_123/overview"
                        r["external_resource_id"] = "do_test_123"
            return curr_copy

        monkeypatch.setattr("app.modules.courses.service.get_curriculum_for_item", mock_get_curr)

        # Before launch: should be NOT_STARTED
        prog_configured = await client.get(f"/api/v1/courses/{str(sample_course.id)}/progress", headers=headers)
        res_cfg = prog_configured.json()["resource_progress"]["mod1-video-1"]
        assert res_cfg["status"] in ["NOT_STARTED", "NOT_CONFIGURED"]

        # Launch configured resource: should transition to LAUNCHED
        launch_res = await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/resources/mod1-video-1/launch",
            headers=headers,
        )
        assert launch_res.status_code == 200
        launch_data = launch_res.json()
        assert launch_data["status"] == "LAUNCHED"
        assert launch_data["external_url"] == "https://igotkarmayogi.gov.in/app/toc/do_test_123/overview"

        # Progress should now be LAUNCHED, but still NOT completed
        prog_after_launch = await client.get(f"/api/v1/courses/{str(sample_course.id)}/progress", headers=headers)
        res_after = prog_after_launch.json()["resource_progress"]["mod1-video-1"]
        assert res_after["status"] == "LAUNCHED"
        assert res_after["is_completed"] is False
        assert 1 not in prog_after_launch.json()["completed_modules"]

        # 3. Simulate verified provider record (e.g. from government batch/sync in TrainingHistory)
        from app.db.session import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            th = TrainingHistory(
                id=uuid.uuid4(),
                employee_id=str(test_employee.id),
                course_id="do_test_123",
                title="Official iGOT Verified Course",
                provider="iGOT",
                provider_type="IGOT",
                status="COMPLETED",
                score=95.0,
            )
            session.add(th)
            await session.commit()

        # Sync provider status now legitimately verifies completion
        sync_res = await client.post(
            f"/api/v1/courses/{str(sample_course.id)}/resources/mod1-video-1/sync",
            headers=headers,
        )
        assert sync_res.status_code == 200
        sync_data = sync_res.json()
        assert sync_data["verified"] is True
        assert sync_data["status"] == "COMPLETED"

        # Progress should now show VERIFIED_COMPLETED
        prog_verified = await client.get(f"/api/v1/courses/{str(sample_course.id)}/progress", headers=headers)
        res_verified = prog_verified.json()["resource_progress"]["mod1-video-1"]
        assert res_verified["status"] == "VERIFIED_COMPLETED"
        assert res_verified["is_completed"] is True
        assert res_verified["verification_status"] == "VERIFIED"




