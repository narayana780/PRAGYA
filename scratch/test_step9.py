import asyncio
import httpx
from app.main import app

LABOUR_COMPETENCY_ID = "7e21882d-ace2-439d-ae56-5a51a2025ca6"
SAMPLING_COMPETENCY_ID = "20c255da-21f0-4c40-a84e-315e172ef110"

async def test_all_scenarios():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        print("==================================================")
        print("STEP 9 VERIFICATION SUITE")
        print("==================================================")

        # 1. Initial page -> all items (no filters sent / empty)
        r_init = await client.get("/api/v1/learning-items?limit=100")
        d_init = r_init.json()
        print(f"1. Initial page (no filters): Status={r_init.status_code}, Total={d_init.get('total')}, Count={len(d_init.get('items', []))}")
        assert d_init.get('total') == 40, f"Expected 40 items, got {d_init.get('total')}"

        # 2. Provider only -> results
        r_prov = await client.get("/api/v1/learning-items?provider=IGOT")
        d_prov = r_prov.json()
        print(f"2. Provider only (IGOT): Status={r_prov.status_code}, Total={d_prov.get('total')}, Count={len(d_prov.get('items', []))}")
        assert d_prov.get('total') == 22, f"Expected 22 items for IGOT, got {d_prov.get('total')}"

        r_nssta = await client.get("/api/v1/learning-items?provider=NSSTA_TPAC")
        d_nssta = r_nssta.json()
        print(f"   Provider only (NSSTA_TPAC): Status={r_nssta.status_code}, Total={d_nssta.get('total')}")
        assert d_nssta.get('total') == 11

        r_pragya = await client.get("/api/v1/learning-items?provider=PRAGYA")
        d_pragya = r_pragya.json()
        print(f"   Provider only (PRAGYA): Status={r_pragya.status_code}, Total={d_pragya.get('total')}")
        assert d_pragya.get('total') == 7

        # 3. Competency only -> results
        r_comp = await client.get(f"/api/v1/learning-items?competency_id={LABOUR_COMPETENCY_ID}")
        d_comp = r_comp.json()
        print(f"3. Competency only (Labour Statistics): Status={r_comp.status_code}, Total={d_comp.get('total')}, Count={len(d_comp.get('items', []))}")
        assert d_comp.get('total') == 1

        r_comp2 = await client.get(f"/api/v1/learning-items?competency_id={SAMPLING_COMPETENCY_ID}")
        d_comp2 = r_comp2.json()
        print(f"   Competency only (Sampling): Status={r_comp2.status_code}, Total={d_comp2.get('total')}")
        assert d_comp2.get('total') == 7

        # 4. Difficulty only -> results
        r_diff_beg = await client.get("/api/v1/learning-items?difficulty=BEGINNER")
        d_diff_beg = r_diff_beg.json()
        print(f"4. Difficulty only (BEGINNER): Status={r_diff_beg.status_code}, Total={d_diff_beg.get('total')}")
        assert d_diff_beg.get('total') == 13

        r_diff_int = await client.get("/api/v1/learning-items?difficulty=INTERMEDIATE")
        d_diff_int = r_diff_int.json()
        print(f"   Difficulty only (INTERMEDIATE): Status={r_diff_int.status_code}, Total={d_diff_int.get('total')}")
        assert d_diff_int.get('total') == 21

        r_diff_adv = await client.get("/api/v1/learning-items?difficulty=ADVANCED")
        d_diff_adv = r_diff_adv.json()
        print(f"   Difficulty only (ADVANCED): Status={r_diff_adv.status_code}, Total={d_diff_adv.get('total')}")
        assert d_diff_adv.get('total') == 6

        # 5. Format only -> results
        r_fmt_sp = await client.get("/api/v1/learning-items?format=SELF_PACED")
        d_fmt_sp = r_fmt_sp.json()
        print(f"5. Format only (SELF_PACED): Status={r_fmt_sp.status_code}, Total={d_fmt_sp.get('total')}")
        assert d_fmt_sp.get('total') == 22

        r_fmt_il = await client.get("/api/v1/learning-items?format=INSTRUCTOR_LED")
        d_fmt_il = r_fmt_il.json()
        print(f"   Format only (INSTRUCTOR_LED): Status={r_fmt_il.status_code}, Total={d_fmt_il.get('total')}")
        assert d_fmt_il.get('total') == 9

        # 6. Combined filters -> correct result
        r_comb = await client.get(f"/api/v1/learning-items?provider=IGOT&competency_id={LABOUR_COMPETENCY_ID}&difficulty=INTERMEDIATE&format=SELF_PACED")
        d_comb = r_comb.json()
        print(f"6. Combined filters (IGOT + Labour Statistics + INTERMEDIATE + SELF_PACED): Status={r_comb.status_code}, Total={d_comb.get('total')}")
        assert d_comb.get('total') == 1
        print(f"   Found item: '{d_comb['items'][0]['title']}'")

        # 7. Zero-match combination -> correct zero state
        r_zero = await client.get(f"/api/v1/learning-items?provider=IGOT&competency_id={LABOUR_COMPETENCY_ID}&difficulty=BEGINNER&format=SELF_PACED")
        d_zero = r_zero.json()
        print(f"7. Zero-match combination (IGOT + Labour Statistics + BEGINNER + SELF_PACED): Status={r_zero.status_code}, Total={d_zero.get('total')}, Count={len(d_zero.get('items', []))}")
        assert d_zero.get('total') == 0
        assert len(d_zero.get('items', [])) == 0

        # 8. "ALL" string handling (should behave as NO filter)
        r_all = await client.get("/api/v1/learning-items?provider=ALL&difficulty=ALL&format=ALL&competency_id=ALL")
        d_all = r_all.json()
        print(f"8. 'ALL' filter values: Status={r_all.status_code}, Total={d_all.get('total')}")
        assert d_all.get('total') == 40

        # 9. "null" string handling (should behave as NO filter)
        r_null = await client.get("/api/v1/learning-items?provider=null&difficulty=null&format=null&competency_id=null")
        d_null = r_null.json()
        print(f"9. 'null' filter values: Status={r_null.status_code}, Total={d_null.get('total')}")
        assert d_null.get('total') == 40

        # 10. Reset -> all items
        r_reset = await client.get("/api/v1/learning-items?limit=100")
        d_reset = r_reset.json()
        print(f"10. Reset (all items): Status={r_reset.status_code}, Total={d_reset.get('total')}")
        assert d_reset.get('total') == 40

        print("\nALL STEP 9 TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(test_all_scenarios())
