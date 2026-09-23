import asyncio
import httpx
from app.main import app

COMPETENCY_ID = "7e21882d-ace2-439d-ae56-5a51a2025ca6"

async def run_tests():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. Exact combination
        url_exact = f"/api/v1/learning-items?provider=IGOT&competency_id={COMPETENCY_ID}&difficulty=BEGINNER&format=SELF_PACED"
        resp_exact = await client.get(url_exact)
        data_exact = resp_exact.json()
        print("=== 1. EXACT COMBINATION ===")
        print("URL:", url_exact)
        print("HTTP Status:", resp_exact.status_code)
        print("Total:", data_exact.get("total"))
        print("Returned item count:", len(data_exact.get("items", [])))

        # 2. Incremental tests
        print("\n=== 2. INCREMENTAL FILTER TESTS ===")
        # A: provider=IGOT
        url_a = "/api/v1/learning-items?provider=IGOT"
        resp_a = await client.get(url_a)
        data_a = resp_a.json()
        print(f"A: provider=IGOT -> Status: {resp_a.status_code}, Total: {data_a.get('total')}, Count: {len(data_a.get('items', []))}")

        # B: provider=IGOT & competency=Labour Statistics
        url_b = f"/api/v1/learning-items?provider=IGOT&competency_id={COMPETENCY_ID}"
        resp_b = await client.get(url_b)
        data_b = resp_b.json()
        print(f"B: provider=IGOT & competency=Labour Statistics -> Status: {resp_b.status_code}, Total: {data_b.get('total')}, Count: {len(data_b.get('items', []))}")
        if data_b.get("items"):
            for it in data_b["items"]:
                print(f"   Item: '{it['title']}' | Provider: {it['provider']} | Difficulty: {it['difficulty']} | Format: {it['format']}")

        # C: provider=IGOT & competency=Labour Statistics & difficulty=BEGINNER
        url_c = f"/api/v1/learning-items?provider=IGOT&competency_id={COMPETENCY_ID}&difficulty=BEGINNER"
        resp_c = await client.get(url_c)
        data_c = resp_c.json()
        print(f"C: provider=IGOT & competency=Labour Statistics & difficulty=BEGINNER -> Status: {resp_c.status_code}, Total: {data_c.get('total')}, Count: {len(data_c.get('items', []))}")

        # D: provider=IGOT & competency=Labour Statistics & difficulty=BEGINNER & format=SELF_PACED
        url_d = f"/api/v1/learning-items?provider=IGOT&competency_id={COMPETENCY_ID}&difficulty=BEGINNER&format=SELF_PACED"
        resp_d = await client.get(url_d)
        data_d = resp_d.json()
        print(f"D: All 4 filters -> Status: {resp_d.status_code}, Total: {data_d.get('total')}, Count: {len(data_d.get('items', []))}")

        # E: Test what happens with INTERMEDIATE
        url_e = f"/api/v1/learning-items?provider=IGOT&competency_id={COMPETENCY_ID}&difficulty=INTERMEDIATE&format=SELF_PACED"
        resp_e = await client.get(url_e)
        data_e = resp_e.json()
        print(f"\nE: With correct difficulty=INTERMEDIATE -> Status: {resp_e.status_code}, Total: {data_e.get('total')}, Count: {len(data_e.get('items', []))}")

if __name__ == "__main__":
    asyncio.run(run_tests())
