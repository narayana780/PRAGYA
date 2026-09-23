import uuid

import pytest
from app.main import app
from app.modules.assessments.constants import (
    calculate_confidence_score,
    normalize_experience,
    normalize_self_assessment,
    renormalize_weights,
)
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_get_diagnostic_assessment():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/assessments")
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 1
        diag = next((a for a in data if a["assessment_type"] == "DIAGNOSTIC"), None)
        assert diag is not None
        assert "PRAGYA Core Competency Diagnostic" in diag["title"]
        assert diag["question_count"] == 24


@pytest.mark.asyncio
async def test_assessment_questions_hide_correct_option():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/assessments")
        diag_id = res.json()[0]["id"]

        emp_res = await ac.get("/api/v1/employees/me")
        emp_id = emp_res.json()["id"]

        # Start attempt
        start_res = await ac.post(
            f"/api/v1/assessments/{diag_id}/attempts",
            json={"employee_id": emp_id},
        )
        assert start_res.status_code == 201
        attempt_id = start_res.json()["id"]

        # Fetch attempt details
        attempt_res = await ac.get(f"/api/v1/assessments/attempts/{attempt_id}")
        assert attempt_res.status_code == 200
        attempt_data = attempt_res.json()
        assert len(attempt_data["questions"]) == 24

        for q in attempt_data["questions"]:
            assert "correct_option" not in q
            assert "explanation" not in q
            assert len(q["options"]) == 4


@pytest.mark.asyncio
async def test_start_attempt():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/assessments")
        diag_id = res.json()[0]["id"]
        emp_res = await ac.get("/api/v1/employees/me")
        emp_id = emp_res.json()["id"]

        start_res = await ac.post(
            f"/api/v1/assessments/{diag_id}/attempts",
            json={"employee_id": emp_id},
        )
        assert start_res.status_code == 201
        assert start_res.json()["status"] == "IN_PROGRESS"


@pytest.mark.asyncio
async def test_invalid_employee_attempt():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/assessments")
        diag_id = res.json()[0]["id"]
        fake_emp_id = str(uuid.uuid4())

        start_res = await ac.post(
            f"/api/v1/assessments/{diag_id}/attempts",
            json={"employee_id": fake_emp_id},
        )
        assert start_res.status_code == 404
        assert start_res.json()["error"]["code"] == "EMPLOYEE_NOT_FOUND"


@pytest.mark.asyncio
async def test_record_correct_and_incorrect_answers():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/assessments")
        diag_id = res.json()[0]["id"]
        emp_res = await ac.get("/api/v1/employees/me")
        emp_id = emp_res.json()["id"]

        start_res = await ac.post(
            f"/api/v1/assessments/{diag_id}/attempts",
            json={"employee_id": emp_id},
        )
        attempt_id = start_res.json()["id"]
        attempt_data = (await ac.get(f"/api/v1/assessments/attempts/{attempt_id}")).json()

        q1 = attempt_data["questions"][0]
        q2 = attempt_data["questions"][1]

        # Record option 0 (which is correct for seeded questions)
        r1 = await ac.post(
            f"/api/v1/assessments/attempts/{attempt_id}/responses",
            json={"question_id": q1["id"], "selected_option": 0},
            headers={"X-Employee-Id": emp_id},
        )
        assert r1.status_code == 200

        # Record option 3 (which is incorrect for seeded questions)
        r2 = await ac.post(
            f"/api/v1/assessments/attempts/{attempt_id}/responses",
            json={"question_id": q2["id"], "selected_option": 3},
            headers={"X-Employee-Id": emp_id},
        )
        assert r2.status_code == 200


@pytest.mark.asyncio
async def test_prevent_duplicate_response():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/assessments")
        diag_id = res.json()[0]["id"]
        emp_res = await ac.get("/api/v1/employees/me")
        emp_id = emp_res.json()["id"]

        start_res = await ac.post(
            f"/api/v1/assessments/{diag_id}/attempts",
            json={"employee_id": emp_id},
        )
        attempt_id = start_res.json()["id"]
        attempt_data = (await ac.get(f"/api/v1/assessments/attempts/{attempt_id}")).json()
        q1 = attempt_data["questions"][0]

        # Answer option 1 first
        await ac.post(
            f"/api/v1/assessments/attempts/{attempt_id}/responses",
            json={"question_id": q1["id"], "selected_option": 1},
            headers={"X-Employee-Id": emp_id},
        )

        # Update to option 0
        r_update = await ac.post(
            f"/api/v1/assessments/attempts/{attempt_id}/responses",
            json={"question_id": q1["id"], "selected_option": 0},
            headers={"X-Employee-Id": emp_id},
        )
        assert r_update.status_code == 200
        assert r_update.json()["selected_option"] == 0


@pytest.mark.asyncio
async def test_complete_attempt_and_competency_breakdown():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/assessments")
        diag_id = res.json()[0]["id"]
        emp_res = await ac.get("/api/v1/employees/me")
        emp_id = emp_res.json()["id"]

        start_res = await ac.post(
            f"/api/v1/assessments/{diag_id}/attempts",
            json={"employee_id": emp_id},
        )
        attempt_id = start_res.json()["id"]
        attempt_data = (await ac.get(f"/api/v1/assessments/attempts/{attempt_id}")).json()

        # Answer all 24 questions with correct answer (0)
        for q in attempt_data["questions"]:
            await ac.post(
                f"/api/v1/assessments/attempts/{attempt_id}/responses",
                json={"question_id": q["id"], "selected_option": 0},
                headers={"X-Employee-Id": emp_id},
            )

        # Complete attempt
        comp_res = await ac.post(
            f"/api/v1/assessments/attempts/{attempt_id}/complete",
            headers={"X-Employee-Id": emp_id},
        )
        assert comp_res.status_code == 200
        data = comp_res.json()
        assert data["status"] == "COMPLETED"
        assert data["percentage"] == 100.0
        assert len(data["competency_breakdown"]) == 8

        for item in data["competency_breakdown"]:
            assert item["questions_tested"] == 3
            assert item["correct_count"] == 3
            assert item["score_percentage"] == 100.0


@pytest.mark.asyncio
async def test_attempt_cannot_be_completed_twice():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/assessments")
        diag_id = res.json()[0]["id"]
        emp_res = await ac.get("/api/v1/employees/me")
        emp_id = emp_res.json()["id"]

        start_res = await ac.post(
            f"/api/v1/assessments/{diag_id}/attempts",
            json={"employee_id": emp_id},
        )
        attempt_id = start_res.json()["id"]

        await ac.post(
            f"/api/v1/assessments/attempts/{attempt_id}/complete",
            headers={"X-Employee-Id": emp_id},
        )

        second_res = await ac.post(
            f"/api/v1/assessments/attempts/{attempt_id}/complete",
            headers={"X-Employee-Id": emp_id},
        )
        assert second_res.status_code == 400
        assert second_res.json()["error"]["code"] == "ATTEMPT_ALREADY_COMPLETED"


@pytest.mark.asyncio
async def test_unauthorized_employee_attempt():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/assessments")
        diag_id = res.json()[0]["id"]
        emp_res = await ac.get("/api/v1/employees/me")
        emp_id = emp_res.json()["id"]

        start_res = await ac.post(
            f"/api/v1/assessments/{diag_id}/attempts",
            json={"employee_id": emp_id},
        )
        attempt_id = start_res.json()["id"]
        other_emp_id = str(uuid.uuid4())

        resp = await ac.post(
            f"/api/v1/assessments/attempts/{attempt_id}/complete",
            headers={"X-Employee-Id": other_emp_id},
        )
        assert resp.status_code == 403
        assert resp.json()["error"]["code"] == "FORBIDDEN_ATTEMPT"


@pytest.mark.asyncio
async def test_invalid_question_and_assessment():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        fake_id = str(uuid.uuid4())
        a_res = await ac.get(f"/api/v1/assessments/{fake_id}")
        assert a_res.status_code == 404

        emp_res = await ac.get("/api/v1/employees/me")
        emp_id = emp_res.json()["id"]

        real_diag = (await ac.get("/api/v1/assessments")).json()[0]["id"]
        attempt = (await ac.post(
            f"/api/v1/assessments/{real_diag}/attempts",
            json={"employee_id": emp_id},
        )).json()

        # Submit invalid question ID
        q_res = await ac.post(
            f"/api/v1/assessments/attempts/{attempt['id']}/responses",
            json={"question_id": fake_id, "selected_option": 0},
            headers={"X-Employee-Id": emp_id},
        )
        assert q_res.status_code == 400
        assert q_res.json()["error"]["code"] == "INVALID_QUESTION"


@pytest.mark.asyncio
async def test_employee_competencies_persistence_and_evidence():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        emp_res = await ac.get("/api/v1/employees/me")
        emp_id = emp_res.json()["id"]

        comp_res = await ac.get(f"/api/v1/employees/{emp_id}/competencies")
        assert comp_res.status_code == 200
        comps = comp_res.json()
        assert len(comps) >= 2  # Has seeded Python & Sampling

        py_comp = next(c for c in comps if c["competency_code"] == "TECH_PYTHON")
        assert py_comp["current_score"] > 0.0
        assert py_comp["evidence_count"] >= 2
        assert py_comp["confidence_label"] in ["MEDIUM", "HIGH", "VERY_HIGH"]

        # Check evidence drawer endpoint
        ev_res = await ac.get(f"/api/v1/employees/{emp_id}/competencies/{py_comp['competency_id']}/evidence")
        assert ev_res.status_code == 200
        evidence_items = ev_res.json()
        assert len(evidence_items) >= 2

        types = {e["evidence_type"] for e in evidence_items}
        assert "EXPERIENCE" in types or "TRAINING" in types

        # Check score history
        hist_res = await ac.get(f"/api/v1/employees/{emp_id}/competencies/{py_comp['competency_id']}/history")
        assert hist_res.status_code == 200
        assert len(hist_res.json()) >= 1


@pytest.mark.asyncio
async def test_self_assessment_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        emp_res = await ac.get("/api/v1/employees/me")
        emp_id = emp_res.json()["id"]

        # Get Python competency ID
        comps = (await ac.get("/api/v1/competencies")).json()["items"]
        py_comp = next(c for c in comps if c["code"] == "TECH_PYTHON")

        # Submit self-assessment: Level 4 (Proficient -> 80.0)
        sa_res = await ac.post(
            f"/api/v1/employees/{emp_id}/self-assessment",
            json={"competency_id": py_comp["id"], "level": 4},
        )
        assert sa_res.status_code == 201
        data = sa_res.json()
        assert data["level"] == 4
        assert data["normalized_score"] == 80.0
        assert data["new_competency_score"] > 0.0

        # Verify evidence was added
        ev_list = (await ac.get(f"/api/v1/employees/{emp_id}/competencies/{py_comp['id']}/evidence")).json()
        sa_ev = next(e for e in ev_list if e["evidence_type"] == "SELF_ASSESSMENT")
        assert sa_ev["normalized_score"] == 80.0


def test_experience_normalization_curve():
    assert normalize_experience(0) == 0.0
    assert normalize_experience(1) == 20.0
    assert normalize_experience(2) == 35.0
    assert normalize_experience(3) == 45.0
    assert normalize_experience(4) == 55.0
    assert normalize_experience(5) == 65.0
    assert normalize_experience(6) == 70.0
    assert normalize_experience(8) == 75.0
    assert normalize_experience(12) == 85.0
    assert normalize_experience(20) == 90.0


def test_self_assessment_conversion():
    assert normalize_self_assessment(1) == 20.0
    assert normalize_self_assessment(2) == 40.0
    assert normalize_self_assessment(3) == 60.0
    assert normalize_self_assessment(4) == 80.0
    assert normalize_self_assessment(5) == 100.0
    with pytest.raises(ValueError):
        normalize_self_assessment(6)


def test_weight_renormalization_missing_sources():
    # Only Diagnostic (0.50), Training (0.15), Experience (0.10) available -> sum = 0.75
    available = ["DIAGNOSTIC", "TRAINING", "EXPERIENCE"]
    reweighted = renormalize_weights(available)

    assert round(sum(reweighted.values()), 5) == 1.0
    assert round(reweighted["DIAGNOSTIC"], 3) == round(0.50 / 0.75, 3)
    assert round(reweighted["TRAINING"], 3) == round(0.15 / 0.75, 3)
    assert round(reweighted["EXPERIENCE"], 3) == round(0.10 / 0.75, 3)

    # Empty
    assert renormalize_weights([]) == {}


def test_confidence_calculation_and_labels():
    conf1, label1 = calculate_confidence_score(1, ["EXPERIENCE"])
    assert label1.value == "LOW"
    assert conf1 < 0.40

    conf3, label3 = calculate_confidence_score(3, ["DIAGNOSTIC", "TRAINING", "EXPERIENCE"], [80.0, 85.0, 82.0])
    assert label3.value in ["HIGH", "VERY_HIGH"]
    assert conf3 >= 0.70
