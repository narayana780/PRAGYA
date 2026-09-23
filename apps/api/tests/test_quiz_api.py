import uuid
import pytest
from httpx import ASGITransport, AsyncClient

import app.main
from app.main import app


@pytest.mark.asyncio
async def test_quiz_api_full_flow():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # 1. Generate Quiz
        gen_res = await ac.post(
            "/api/v1/quizzes/generate",
            json={
                "difficulty": "BEGINNER",
                "question_count": 3,
            },
        )
        assert gen_res.status_code == 201
        quiz_data = gen_res.json()
        assert "id" in quiz_data
        quiz_id = quiz_data["id"]
        assert len(quiz_data["questions"]) == 3

        # 2. List Quizzes
        list_res = await ac.get("/api/v1/quizzes")
        assert list_res.status_code == 200
        quizzes = list_res.json()
        assert any(q["id"] == quiz_id for q in quizzes)

        # 3. Get Specific Quiz (Student View: is_correct hidden)
        get_res = await ac.get(f"/api/v1/quizzes/{quiz_id}")
        assert get_res.status_code == 200
        q_detail = get_res.json()
        assert q_detail["id"] == quiz_id
        for q in q_detail["questions"]:
            for opt in q["options"]:
                assert opt.get("is_correct") is None

        # 4. Start Attempt
        att_res = await ac.post(f"/api/v1/quizzes/{quiz_id}/attempts")
        assert att_res.status_code == 201
        attempt_data = att_res.json()
        attempt_id = attempt_data["id"]

        # 5. Submit Answers to questions
        for q in q_detail["questions"]:
            selected_opt_id = q["options"][0]["id"]
            ans_res = await ac.post(
                f"/api/v1/quiz-attempts/{attempt_id}/answers",
                json={
                    "question_id": q["id"],
                    "selected_option_id": selected_opt_id,
                },
            )
            assert ans_res.status_code == 200
            ans_data = ans_res.json()
            assert "is_correct" in ans_data
            assert "explanation" in ans_data

        # 6. Complete Attempt
        comp_res = await ac.post(f"/api/v1/quiz-attempts/{attempt_id}/complete")
        assert comp_res.status_code == 200
        res_data = comp_res.json()
        assert res_data["total_questions"] == 3
        assert "percentage" in res_data

        # 7. Get Result Analytics
        res_summary = await ac.get(f"/api/v1/quiz-attempts/{attempt_id}/result")
        assert res_summary.status_code == 200

        # 8. Get Question Review with Citations
        rev_res = await ac.get(f"/api/v1/quiz-attempts/{attempt_id}/review")
        assert rev_res.status_code == 200
        rev_data = rev_res.json()
        assert len(rev_data["items"]) == 3
        assert "explanation" in rev_data["items"][0]


@pytest.mark.asyncio
async def test_quiz_api_security_isolation():
    other_emp_id = str(uuid.uuid4())
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Create quiz as owner
        gen_res = await ac.post(
            "/api/v1/quizzes/generate",
            json={"question_count": 2},
        )
        quiz_id = gen_res.json()["id"]

        # Attempt start attempt as unauthorized employee -> 403 Forbidden
        unauth_start = await ac.post(
            f"/api/v1/quizzes/{quiz_id}/attempts",
            headers={"x-employee-id": other_emp_id},
        )
        assert unauth_start.status_code in (403, 404)
