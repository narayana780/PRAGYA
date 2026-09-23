import asyncio
import sys
import uuid

sys.path.insert(0, r"D:\PRAGYA\apps\api")
from httpx import ASGITransport, AsyncClient
from app.main import app


async def smoke():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Fetch current employee
        r_me = await client.get("/api/v1/employees/me")
        assert r_me.status_code == 200, f"GET /me failed: {r_me.text}"
        emp = r_me.json()
        emp_id = emp["id"]
        print(f"Employee verified: {emp['full_name']} (ID: {emp_id})")

        # 2. Test Performance Endpoint
        r_perf = await client.get(f"/api/v1/employees/{emp_id}/performance")
        assert r_perf.status_code == 200, f"GET /performance failed: {r_perf.text}"
        perf = r_perf.json()
        print("=== PERFORMANCE ENDPOINT SMOKE TEST ===")
        print(f"Overall Baseline: {perf['overall']['baseline_score']}")
        print(f"Overall Current: {perf['overall']['current_score']}")
        print(
            f"Overall Improvement: {perf['overall']['improvement_points']} pts ({perf['overall']['improvement_percentage']}%)"
        )
        print(f"Target Readiness: {perf['overall']['target_readiness_percentage']}%")
        print(f"Evaluated Competencies: {len(perf['competencies'])}")
        print(f"Top Strengths: {[s['competency_name'] for s in perf['strongest_competencies']]}")
        print(f"Priority Focus Areas: {[f['competency_name'] for f in perf['focus_competencies']]}")
        print(f"Modalities: {list(perf['modalities'].keys())}")
        for mod, val in perf['modalities'].items():
            print(f"  - {mod}: status={val['status']}")

        # 3. Test Timeline Endpoint
        r_time = await client.get(f"/api/v1/employees/{emp_id}/history/timeline")
        assert r_time.status_code == 200, f"GET /history/timeline failed: {r_time.text}"
        timeline = r_time.json()
        print("=== TIMELINE ENDPOINT SMOKE TEST ===")
        print(f"Total Timeline Events: {timeline['total_events']}")
        for ev in timeline["events"][:5]:
            print(f"  - [{ev['type']}] {ev['timestamp']}: {ev['title']} (Score: {ev['score']})")

        # 4. Unknown Employee Test
        fake_id = str(uuid.uuid4())
        r_fake = await client.get(f"/api/v1/employees/{fake_id}/performance")
        assert r_fake.status_code == 404, "Unknown employee should 404"
        print("Unknown employee isolation verified (404 Not Found)")
        print("ALL SMOKE TESTS PASSED!")


if __name__ == "__main__":
    asyncio.run(smoke())
