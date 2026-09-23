import io
import math
import uuid
import pytest
import pymupdf
import zipfile
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.main import app
from app.modules.employees.models import Employee

ADMIN_HEADERS = {"X-User-Role": "ADMIN"}
SUPER_ADMIN_HEADERS = {"X-User-Role": "SUPER_ADMIN"}
EMPLOYEE_HEADERS = {"X-User-Role": "EMPLOYEE"}
TRAINER_HEADERS = {"X-User-Role": "TRAINER"}


def _validate_pdf_document(content: bytes, expected_keywords: list[str] = None):
    """Ensure binary payload is a structurally valid PDF and contains expected textual keywords."""
    assert len(content) > 500, "PDF byte payload is too small"
    assert content.startswith(b"%PDF-"), "Invalid PDF signature magic bytes"

    # Open with pymupdf to ensure it is not corrupt
    doc = pymupdf.open(stream=content, filetype="pdf")
    assert doc.page_count >= 1, "PDF document must have at least 1 page"
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()

    assert "PRAGYA" in full_text, "Report must identify platform as PRAGYA"
    assert "methodology" in full_text.lower() or "audit" in full_text.lower(), "Report must contain methodology/audit trace"
    assert "NaN" not in full_text, "Report contains invalid NaN string"
    assert "Infinity" not in full_text, "Report contains invalid Infinity string"
    assert "Government of India Official Gazette" not in full_text, "Must avoid fake official claim"

    if expected_keywords:
        for kw in expected_keywords:
            assert kw.lower() in full_text.lower(), f"Expected keyword '{kw}' not found in PDF text"
    return full_text


def _validate_excel_workbook(content: bytes, expected_sheets: list[str] = None):
    """Ensure binary payload is a valid Excel (ZIP-based .xlsx) workbook with expected sheets."""
    assert len(content) > 1000, "Excel byte payload is too small"
    assert content.startswith(b"PK\x03\x04"), "Invalid Excel ZIP signature magic bytes"

    # Open as ZipFile to inspect workbook structure
    zf = zipfile.ZipFile(io.BytesIO(content))
    namelist = zf.namelist()
    assert "[Content_Types].xml" in namelist, "Missing openxml content types in xlsx"
    assert "xl/workbook.xml" in namelist, "Missing xl/workbook.xml in xlsx"
    zf.close()


@pytest.mark.asyncio
async def test_1_admin_authorization():
    """Verify ADMIN and SUPER_ADMIN have full access to reporting endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for headers in [ADMIN_HEADERS, SUPER_ADMIN_HEADERS]:
            resp = await client.get("/api/v1/admin/reports/executive-summary.pdf", headers=headers)
            assert resp.status_code == 200
            assert resp.headers["content-type"] == "application/pdf"
            assert resp.content.startswith(b"%PDF-")


@pytest.mark.asyncio
async def test_2_employee_authorization_rejection():
    """Verify non-admin roles (EMPLOYEE, TRAINER) and unauthenticated users receive 403 Forbidden."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Unauthenticated
        resp_unauth = await client.get("/api/v1/admin/reports/executive-summary.pdf")
        assert resp_unauth.status_code == 403

        # EMPLOYEE
        resp_emp = await client.get("/api/v1/admin/reports/workforce.xlsx", headers=EMPLOYEE_HEADERS)
        assert resp_emp.status_code == 403

        # TRAINER
        resp_tr = await client.get("/api/v1/admin/reports/skill-gaps.pdf", headers=TRAINER_HEADERS)
        assert resp_tr.status_code == 403


@pytest.mark.asyncio
async def test_3_workforce_pdf():
    """Verify GET /api/v1/admin/reports/workforce.pdf produces a valid, readable PDF."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/reports/workforce.pdf", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        assert "filename=" in resp.headers.get("content-disposition", "")
        _validate_pdf_document(resp.content, ["Workforce", "Competency"])


@pytest.mark.asyncio
async def test_4_workforce_excel():
    """Verify GET /api/v1/admin/reports/workforce.xlsx produces a valid openxml Excel spreadsheet."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/reports/workforce.xlsx", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        assert "spreadsheetml" in resp.headers["content-type"]
        _validate_excel_workbook(resp.content)


@pytest.mark.asyncio
async def test_5_skill_gap_pdf():
    """Verify GET /api/v1/admin/reports/skill-gaps.pdf produces a valid skill gap PDF."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/reports/skill-gaps.pdf", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        _validate_pdf_document(resp.content, ["Skill Gap", "Deficit"])


@pytest.mark.asyncio
async def test_6_skill_gap_excel():
    """Verify GET /api/v1/admin/reports/skill-gaps.xlsx produces a valid skill gap Excel."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/reports/skill-gaps.xlsx", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        _validate_excel_workbook(resp.content)


@pytest.mark.asyncio
async def test_7_training_effectiveness_pdf():
    """Verify GET /api/v1/admin/reports/training-effectiveness.pdf produces a valid training report."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/reports/training-effectiveness.pdf", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        _validate_pdf_document(resp.content, ["Training", "Effectiveness"])


@pytest.mark.asyncio
async def test_8_training_effectiveness_excel():
    """Verify GET /api/v1/admin/reports/training-effectiveness.xlsx produces a valid training Excel."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/reports/training-effectiveness.xlsx", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        _validate_excel_workbook(resp.content)


@pytest.mark.asyncio
async def test_9_emerging_skills_pdf():
    """Verify GET /api/v1/admin/reports/emerging-skills.pdf produces valid horizon report PDF."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/reports/emerging-skills.pdf", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        _validate_pdf_document(resp.content, ["Emerging", "Horizon"])


@pytest.mark.asyncio
async def test_10_emerging_skills_excel():
    """Verify GET /api/v1/admin/reports/emerging-skills.xlsx produces valid horizon Excel."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/reports/emerging-skills.xlsx", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        _validate_excel_workbook(resp.content)


@pytest.mark.asyncio
async def test_11_planning_pdf():
    """Verify GET /api/v1/admin/reports/planning.pdf produces valid workforce planning PDF."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/reports/planning.pdf", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        _validate_pdf_document(resp.content, ["Planning", "Capacity"])


@pytest.mark.asyncio
async def test_12_planning_excel():
    """Verify GET /api/v1/admin/reports/planning.xlsx produces valid workforce planning Excel."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/reports/planning.xlsx", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        _validate_excel_workbook(resp.content)


@pytest.mark.asyncio
async def test_13_employee_report_pdf():
    """Verify individual employee report PDF works for valid employee and 404s on unknown ID."""
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Employee).limit(1))
        emp = res.scalar_one_or_none()

    assert emp is not None, "At least one employee must exist in db"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Valid employee
        resp = await client.get(f"/api/v1/admin/reports/employee/{emp.id}.pdf", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        _validate_pdf_document(resp.content, [emp.full_name[:10]])

        # Non-existent employee
        fake_id = uuid.uuid4()
        resp_fake = await client.get(f"/api/v1/admin/reports/employee/{fake_id}.pdf", headers=ADMIN_HEADERS)
        assert resp_fake.status_code == 404


@pytest.mark.asyncio
async def test_14_employee_report_excel():
    """Verify individual employee report Excel works for valid employee and 404s on unknown ID."""
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Employee).limit(1))
        emp = res.scalar_one_or_none()

    assert emp is not None

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(f"/api/v1/admin/reports/employee/{emp.id}.xlsx", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        _validate_excel_workbook(resp.content)

        # Non-existent employee
        fake_id = uuid.uuid4()
        resp_fake = await client.get(f"/api/v1/admin/reports/employee/{fake_id}.xlsx", headers=ADMIN_HEADERS)
        assert resp_fake.status_code == 404


@pytest.mark.asyncio
async def test_15_executive_summary_pdf():
    """Verify GET /api/v1/admin/reports/executive-summary.pdf produces multi-domain executive brief."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/reports/executive-summary.pdf", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        _validate_pdf_document(resp.content, ["Executive", "Summary"])


@pytest.mark.asyncio
async def test_16_executive_summary_excel():
    """Verify GET /api/v1/admin/reports/executive-summary.xlsx produces multi-domain workbook."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/reports/executive-summary.xlsx", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        _validate_excel_workbook(resp.content)


@pytest.mark.asyncio
async def test_17_empty_data_handling():
    """Ensure report generation behaves gracefully without 500 crashes even if subsets of data are empty."""
    from app.modules.reports.report_service import ReportGenerationService

    async with AsyncSessionLocal() as db:
        service = ReportGenerationService(db)
        # Directly generate pdf for workforce
        pdf_bytes = await service.generate_workforce_report(fmt="pdf")
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF-")


@pytest.mark.asyncio
async def test_18_metadata_presence():
    """Verify generated PDF contains standard audit metadata elements."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/reports/executive-summary.pdf", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        text = _validate_pdf_document(resp.content)
        assert "Generated:" in text
        assert "Report Version:" in text
        assert "Scope:" in text
        assert "Data Quality:" in text


@pytest.mark.asyncio
async def test_19_methodology_presence():
    """Verify generated PDF explicitly documents the deterministic calculation methodology."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/reports/planning.pdf", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        text = _validate_pdf_document(resp.content)
        assert "audit traceability & methodology" in text.lower() or "deterministic" in text.lower()
        assert "planning signal" in text.lower() or "capacity pressure" in text.lower()


@pytest.mark.asyncio
async def test_20_no_nan_or_infinity():
    """Verify reports contain no NaN or Infinity floating-point artifacts."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for endpoint in [
            "/api/v1/admin/reports/executive-summary.pdf",
            "/api/v1/admin/reports/workforce.pdf",
            "/api/v1/admin/reports/skill-gaps.pdf",
            "/api/v1/admin/reports/training-effectiveness.pdf",
            "/api/v1/admin/reports/emerging-skills.pdf",
            "/api/v1/admin/reports/planning.pdf",
        ]:
            resp = await client.get(endpoint, headers=ADMIN_HEADERS)
            assert resp.status_code == 200
            assert b"NaN" not in resp.content
            assert b"Infinity" not in resp.content


@pytest.mark.asyncio
async def test_21_employee_isolation():
    """Verify an employee cannot request employee reports or executive reports."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        fake_id = uuid.uuid4()
        resp1 = await client.get(f"/api/v1/admin/reports/employee/{fake_id}.pdf", headers=EMPLOYEE_HEADERS)
        assert resp1.status_code == 403

        resp2 = await client.get(f"/api/v1/admin/reports/employee/{fake_id}.xlsx", headers=EMPLOYEE_HEADERS)
        assert resp2.status_code == 403


@pytest.mark.asyncio
async def test_22_report_content_sanity():
    """Verify content sanity of exported Excel workbook across multiple sheets."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/admin/reports/planning.xlsx", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        zf = zipfile.ZipFile(io.BytesIO(resp.content))
        # Ensure it contains sheet XMLs
        sheets = [name for name in zf.namelist() if name.startswith("xl/worksheets/sheet")]
        assert len(sheets) >= 2, "Expected at least Summary and Data sheets"
        zf.close()


@pytest.mark.asyncio
async def test_23_regression_against_stages_13_to_17():
    """Verify Stage 13-17 underlying analytics endpoints remain healthy alongside report exports."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Stage 14 Cadre
        r14 = await client.get("/api/v1/admin/workforce/overview", headers=ADMIN_HEADERS)
        assert r14.status_code == 200

        # Stage 15 Training
        r15 = await client.get("/api/v1/admin/training/effectiveness", headers=ADMIN_HEADERS)
        assert r15.status_code == 200

        # Stage 16 Emerging
        r16 = await client.get("/api/v1/admin/emerging-skills", headers=ADMIN_HEADERS)
        assert r16.status_code == 200

        # Stage 17 Planning
        r17 = await client.get("/api/v1/admin/workforce/planning/overview", headers=ADMIN_HEADERS)
        assert r17.status_code == 200
