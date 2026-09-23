import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin_role
from app.modules.reports.report_service import ReportGenerationService

router = APIRouter(
    prefix="/admin/reports",
    tags=["Official Reporting & Audit Compliance Export"],
    dependencies=[Depends(require_admin_role)],
)

DbSession = Annotated[AsyncSession, Depends(get_db)]

PDF_MEDIA_TYPE = "application/pdf"
EXCEL_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.get("/executive-summary.pdf", summary="Export Executive Workforce Summary (PDF)")
async def export_executive_summary_pdf(db: DbSession):
    service = ReportGenerationService(db)
    pdf_bytes = await service.generate_executive_summary_report(fmt="pdf")
    return Response(
        content=pdf_bytes,
        media_type=PDF_MEDIA_TYPE,
        headers={"Content-Disposition": 'attachment; filename="PRAGYA_Executive_Summary.pdf"'},
    )


@router.get("/executive-summary.xlsx", summary="Export Executive Workforce Summary (Excel)")
async def export_executive_summary_excel(db: DbSession):
    service = ReportGenerationService(db)
    excel_bytes = await service.generate_executive_summary_report(fmt="excel")
    return Response(
        content=excel_bytes,
        media_type=EXCEL_MEDIA_TYPE,
        headers={"Content-Disposition": 'attachment; filename="PRAGYA_Executive_Summary.xlsx"'},
    )


@router.get("/workforce.pdf", summary="Export Workforce Competency Report (PDF)")
async def export_workforce_pdf(db: DbSession):
    service = ReportGenerationService(db)
    pdf_bytes = await service.generate_workforce_report(fmt="pdf")
    return Response(
        content=pdf_bytes,
        media_type=PDF_MEDIA_TYPE,
        headers={"Content-Disposition": 'attachment; filename="PRAGYA_Workforce_Competency_Report.pdf"'},
    )


@router.get("/workforce.xlsx", summary="Export Workforce Competency Report (Excel)")
async def export_workforce_excel(db: DbSession):
    service = ReportGenerationService(db)
    excel_bytes = await service.generate_workforce_report(fmt="excel")
    return Response(
        content=excel_bytes,
        media_type=EXCEL_MEDIA_TYPE,
        headers={"Content-Disposition": 'attachment; filename="PRAGYA_Workforce_Competency_Report.xlsx"'},
    )


@router.get("/skill-gaps.pdf", summary="Export Skill Gap Analysis Report (PDF)")
async def export_skill_gaps_pdf(db: DbSession):
    service = ReportGenerationService(db)
    pdf_bytes = await service.generate_skill_gaps_report(fmt="pdf")
    return Response(
        content=pdf_bytes,
        media_type=PDF_MEDIA_TYPE,
        headers={"Content-Disposition": 'attachment; filename="PRAGYA_Skill_Gaps_Report.pdf"'},
    )


@router.get("/skill-gaps.xlsx", summary="Export Skill Gap Analysis Report (Excel)")
async def export_skill_gaps_excel(db: DbSession):
    service = ReportGenerationService(db)
    excel_bytes = await service.generate_skill_gaps_report(fmt="excel")
    return Response(
        content=excel_bytes,
        media_type=EXCEL_MEDIA_TYPE,
        headers={"Content-Disposition": 'attachment; filename="PRAGYA_Skill_Gaps_Report.xlsx"'},
    )


@router.get("/training-effectiveness.pdf", summary="Export Training Effectiveness Report (PDF)")
async def export_training_effectiveness_pdf(db: DbSession):
    service = ReportGenerationService(db)
    pdf_bytes = await service.generate_training_effectiveness_report(fmt="pdf")
    return Response(
        content=pdf_bytes,
        media_type=PDF_MEDIA_TYPE,
        headers={"Content-Disposition": 'attachment; filename="PRAGYA_Training_Effectiveness_Report.pdf"'},
    )


@router.get("/training-effectiveness.xlsx", summary="Export Training Effectiveness Report (Excel)")
async def export_training_effectiveness_excel(db: DbSession):
    service = ReportGenerationService(db)
    excel_bytes = await service.generate_training_effectiveness_report(fmt="excel")
    return Response(
        content=excel_bytes,
        media_type=EXCEL_MEDIA_TYPE,
        headers={"Content-Disposition": 'attachment; filename="PRAGYA_Training_Effectiveness_Report.xlsx"'},
    )


@router.get("/emerging-skills.pdf", summary="Export Emerging Skills Horizon Report (PDF)")
async def export_emerging_skills_pdf(db: DbSession):
    service = ReportGenerationService(db)
    pdf_bytes = await service.generate_emerging_skills_report(fmt="pdf")
    return Response(
        content=pdf_bytes,
        media_type=PDF_MEDIA_TYPE,
        headers={"Content-Disposition": 'attachment; filename="PRAGYA_Emerging_Skills_Report.pdf"'},
    )


@router.get("/emerging-skills.xlsx", summary="Export Emerging Skills Horizon Report (Excel)")
async def export_emerging_skills_excel(db: DbSession):
    service = ReportGenerationService(db)
    excel_bytes = await service.generate_emerging_skills_report(fmt="excel")
    return Response(
        content=excel_bytes,
        media_type=EXCEL_MEDIA_TYPE,
        headers={"Content-Disposition": 'attachment; filename="PRAGYA_Emerging_Skills_Report.xlsx"'},
    )


@router.get("/planning.pdf", summary="Export Workforce Planning Report (PDF)")
async def export_planning_pdf(db: DbSession):
    service = ReportGenerationService(db)
    pdf_bytes = await service.generate_planning_report(fmt="pdf")
    return Response(
        content=pdf_bytes,
        media_type=PDF_MEDIA_TYPE,
        headers={"Content-Disposition": 'attachment; filename="PRAGYA_Workforce_Planning_Report.pdf"'},
    )


@router.get("/planning.xlsx", summary="Export Workforce Planning Report (Excel)")
async def export_planning_excel(db: DbSession):
    service = ReportGenerationService(db)
    excel_bytes = await service.generate_planning_report(fmt="excel")
    return Response(
        content=excel_bytes,
        media_type=EXCEL_MEDIA_TYPE,
        headers={"Content-Disposition": 'attachment; filename="PRAGYA_Workforce_Planning_Report.xlsx"'},
    )


@router.get("/employee/{employee_id}.pdf", summary="Export Individual Employee Competency Report (PDF)")
async def export_employee_pdf(employee_id: uuid.UUID, db: DbSession):
    service = ReportGenerationService(db)
    try:
        pdf_bytes = await service.generate_employee_report(employee_id, fmt="pdf")
        return Response(
            content=pdf_bytes,
            media_type=PDF_MEDIA_TYPE,
            headers={"Content-Disposition": f'attachment; filename="PRAGYA_Officer_Report_{str(employee_id)[:8]}.pdf"'},
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/employee/{employee_id}.xlsx", summary="Export Individual Employee Competency Report (Excel)")
async def export_employee_excel(employee_id: uuid.UUID, db: DbSession):
    service = ReportGenerationService(db)
    try:
        excel_bytes = await service.generate_employee_report(employee_id, fmt="excel")
        return Response(
            content=excel_bytes,
            media_type=EXCEL_MEDIA_TYPE,
            headers={"Content-Disposition": f'attachment; filename="PRAGYA_Officer_Report_{str(employee_id)[:8]}.xlsx"'},
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
