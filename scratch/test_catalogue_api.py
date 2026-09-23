import asyncio
import httpx
from app.main import app

async def main():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. Providers endpoint
        r0 = await client.get("/api/v1/providers")
        print("=== 1. Providers ===")
        print(f"Status: {r0.status_code}")
        for p in r0.json():
            print(f" - {p['provider']}: {p['name']} (Mode: {p['mode']}, Status: {p['status']}, Count: {p.get('catalogue_count')})")

        # 2. All learning items
        r = await client.get("/api/v1/learning-items?limit=5")
        print("\n=== 2. Learning Items (Base) ===")
        print(f"Status: {r.status_code}")
        data = r.json()
        print(f"Total: {data.get('total')}, Limit: {data.get('limit')}, Offset: {data.get('offset')}")
        print(f"Returned items count: {len(data.get('items', []))}")

        # 3. Filter by provider: NSSTA_TPAC
        r1 = await client.get("/api/v1/learning-items?provider=NSSTA_TPAC")
        print("\n=== 3. Filter: provider=NSSTA_TPAC ===")
        print(f"Status: {r1.status_code}, Total: {r1.json().get('total')}")

        # 4. Filter by difficulty: ADVANCED
        r2 = await client.get("/api/v1/learning-items?difficulty=ADVANCED")
        print("\n=== 4. Filter: difficulty=ADVANCED ===")
        print(f"Status: {r2.status_code}, Total: {r2.json().get('total')}")

        # 5b. Filter by competency_id: 87ca43ef-d9e4-4cd7-a1e0-7750aaf8b83f (Data Quality Frameworks)
        r_comp = await client.get("/api/v1/learning-items?competency_id=87ca43ef-d9e4-4cd7-a1e0-7750aaf8b83f")
        print("\n=== 5b. Filter: competency_id='87ca43ef-d9e4-4cd7-a1e0-7750aaf8b83f' ===")
        print(f"Status: {r_comp.status_code}, Total: {r_comp.json().get('total')}")
        for it in r_comp.json().get("items", [])[:3]:
            print(f" - [{it['provider']}] {it['title']}")

        # 6. Keyword search: Sampling
        r4 = await client.get("/api/v1/learning-items?search=Sampling")
        data4 = r4.json()
        print("\n=== 6. Filter: search='Sampling' ===")
        print(f"Status: {r4.status_code}, Total: {data4.get('total')}")
        for it in data4.get("items", [])[:3]:
            print(f" - [{it['provider']}] {it['title']} ({it['difficulty']}, {it['format']}, {it['duration_minutes']} min)")

        # 7. Single item detail
        sample_item = data.get("items", [])[0]
        item_id = sample_item["id"]
        r5 = await client.get(f"/api/v1/learning-items/{item_id}")
        print(f"\n=== 7. Single Item Detail ({item_id}) ===")
        print(f"Status: {r5.status_code}")
        det = r5.json()
        print(f"Title: {det['title']}")
        print(f"Provider: {det['provider']}")
        print(f"Type: {det['type']}, Format: {det['format']}, Difficulty: {det['difficulty']}, Level: {det['level']}")
        print(f"Competencies mapped: {len(det.get('competencies', []))}")
        for c in det.get("competencies", []):
            print(f"   * Competency ID: {c.get('competency_id')}, Relevance: {c.get('relevance_score')}, Target Level: {c.get('target_proficiency_level')}")

if __name__ == "__main__":
    asyncio.run(main())
