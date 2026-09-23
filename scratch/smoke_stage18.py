import asyncio
import io
import sys
sys.path.insert(0, ".")
import zipfile
import pymupdf
from httpx import ASGITransport, AsyncClient

from app.main import app

ADMIN_HEADERS = {"X-User-Role": "ADMIN"}
EMPLOYEE_HEADERS = {"X-User-Role": "EMPLOYEE"}


async def smoke_test_all_reports():
    print("=" * 70)
    print("STAGE 18: SMOKE VERIFICATION OF ALL REPORT ENDPOINTS")
    print("=" * 70)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Authorization check
        r_unauth = await client.get("/api/v1/admin/reports/executive-summary.pdf")
        assert r_unauth.status_code == 403, f"Expected 403, got {r_unauth.status_code}"
        r_emp = await client.get("/api/v1/admin/reports/executive-summary.pdf", headers=EMPLOYEE_HEADERS)
        assert r_emp.status_code == 403, f"Expected 403, got {r_emp.status_code}"
        print("[PASS] Security check: Unauthenticated and EMPLOYEE rejected with 403 Forbidden")

        endpoints = [
            ("Executive Summary (PDF)", "/api/v1/admin/reports/executive-summary.pdf", "pdf"),
            ("Executive Summary (Excel)", "/api/v1/admin/reports/executive-summary.xlsx", "xlsx"),
            ("Workforce Competency (PDF)", "/api/v1/admin/reports/workforce.pdf", "pdf"),
            ("Workforce Competency (Excel)", "/api/v1/admin/reports/workforce.xlsx", "xlsx"),
            ("Skill Gaps (PDF)", "/api/v1/admin/reports/skill-gaps.pdf", "pdf"),
            ("Skill Gaps (Excel)", "/api/v1/admin/reports/skill-gaps.xlsx", "xlsx"),
            ("Training Effectiveness (PDF)", "/api/v1/admin/reports/training-effectiveness.pdf", "pdf"),
            ("Training Effectiveness (Excel)", "/api/v1/admin/reports/training-effectiveness.xlsx", "xlsx"),
            ("Emerging Skills (PDF)", "/api/v1/admin/reports/emerging-skills.pdf", "pdf"),
            ("Emerging Skills (Excel)", "/api/v1/admin/reports/emerging-skills.xlsx", "xlsx"),
            ("Workforce Planning (PDF)", "/api/v1/admin/reports/planning.pdf", "pdf"),
            ("Workforce Planning (Excel)", "/api/v1/admin/reports/planning.xlsx", "xlsx"),
        ]

        for name, url, filetype in endpoints:
            resp = await client.get(url, headers=ADMIN_HEADERS)
            assert resp.status_code == 200, f"{name} failed with {resp.status_code}"
            raw = resp.content
            size_kb = len(raw) / 1024.0

            if filetype == "pdf":
                assert raw.startswith(b"%PDF-"), f"{name} invalid PDF header"
                doc = pymupdf.open(stream=raw, filetype="pdf")
                pages = doc.page_count
                doc.close()
                print(f"[PASS] {name:<32} | Status: 200 | Size: {size_kb:6.1f} KB | Pages: {pages}")
            else:
                assert raw.startswith(b"PK\x03\x04"), f"{name} invalid Excel header"
                zf = zipfile.ZipFile(io.BytesIO(raw))
                sheets = [s for s in zf.namelist() if s.startswith("xl/worksheets/sheet")]
                zf.close()
                print(f"[PASS] {name:<32} | Status: 200 | Size: {size_kb:6.1f} KB | Sheets: {len(sheets)}")

        # Individual Officer Report
        from sqlalchemy import select
        from app.db.session import AsyncSessionLocal
        from app.modules.employees.models import Employee

        async with AsyncSessionLocal() as db:
            emp = (await db.execute(select(Employee).limit(1))).scalar_one()

        emp_pdf = await client.get(f"/api/v1/admin/reports/employee/{emp.id}.pdf", headers=ADMIN_HEADERS)
        assert emp_pdf.status_code == 200
        print(f"[PASS] Officer Report (PDF)           | Status: 200 | Size: {len(emp_pdf.content)/1024:.1f} KB | Officer: {emp.full_name}")

        emp_xlsx = await client.get(f"/api/v1/admin/reports/employee/{emp.id}.xlsx", headers=ADMIN_HEADERS)
        assert emp_xlsx.status_code == 200
        print(f"[PASS] Officer Report (Excel)         | Status: 200 | Size: {len(emp_xlsx.content)/1024:.1f} KB | Officer: {emp.full_name}")

    print("=" * 70)
    print("STAGE 18 SMOKE VERIFICATION COMPLETE: ALL 14 REPORT ENDPOINTS VERIFIED")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(smoke_test_all_reports())
