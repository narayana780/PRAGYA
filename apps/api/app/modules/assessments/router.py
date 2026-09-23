import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PragyaException
from app.db.session import get_db
from app.modules.assessments.constants import normalize_self_assessment
from app.modules.assessments.evidence_service import EvidenceService
from app.modules.assessments.repository import AssessmentRepository
from app.modules.assessments.schemas import (
    AssessmentDetailResponse,
    AssessmentResponse,
    AttemptDetailResponse,
    AttemptResponse,
    AttemptStartRequest,
    CompetencyEvidenceResponse,
    CompetencyScoreHistoryResponse,
    CompleteAttemptResponse,
    EmployeeCompetencyResponse,
    RecordResponseRequest,
    RecordResponseResult,
    SelfAssessmentRequest,
    SelfAssessmentResponse,
)
from app.modules.assessments.service import AssessmentService
from app.modules.competencies.constants import score_to_proficiency_level
from app.modules.employees.models import Employee

router = APIRouter(tags=["Assessments & Evidence"])


# ============================================================================
# Assessment Endpoints (Static/nested attempt paths placed before parameterized {assessment_id})
# ============================================================================


@router.get(
    "/assessments",
    response_model=list[AssessmentResponse],
    summary="List assessments",
)
async def list_assessments(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[AssessmentResponse]:
    return await AssessmentService.get_assessments(db)


@router.get(
    "/assessments/attempts/{attempt_id}",
    response_model=AttemptDetailResponse,
    summary="Get attempt details with questions (answers hidden)",
)
async def get_attempt(
    attempt_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AttemptDetailResponse:
    return await AssessmentService.get_attempt(attempt_id, db)


@router.post(
    "/assessments/attempts/{attempt_id}/responses",
    response_model=RecordResponseResult,
    summary="Record an answer response",
)
async def record_response(
    attempt_id: uuid.UUID,
    payload: RecordResponseRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_employee_id: Annotated[str | None, Header(alias="X-Employee-Id")] = None,
) -> RecordResponseResult:
    # Resolve employee ID: header or attempt's employee
    attempt = await AssessmentRepository.get_attempt_by_id(attempt_id, db)
    if not attempt:
        raise PragyaException(
            code="ATTEMPT_NOT_FOUND",
            message=f"Attempt '{attempt_id}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    emp_id = uuid.UUID(x_employee_id) if x_employee_id else attempt.employee_id
    return await AssessmentService.record_response(
        attempt_id=attempt_id,
        question_id=payload.question_id,
        selected_option=payload.selected_option,
        employee_id=emp_id,
        db=db,
    )


@router.post(
    "/assessments/attempts/{attempt_id}/complete",
    response_model=CompleteAttemptResponse,
    summary="Complete an assessment attempt and calculate score",
)
async def complete_attempt(
    attempt_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_employee_id: Annotated[str | None, Header(alias="X-Employee-Id")] = None,
) -> CompleteAttemptResponse:
    attempt = await AssessmentRepository.get_attempt_by_id(attempt_id, db)
    if not attempt:
        raise PragyaException(
            code="ATTEMPT_NOT_FOUND",
            message=f"Attempt '{attempt_id}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    emp_id = uuid.UUID(x_employee_id) if x_employee_id else attempt.employee_id
    return await AssessmentService.complete_attempt(attempt_id, emp_id, db)


@router.post(
    "/assessments/{assessment_id}/attempts",
    response_model=AttemptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start an assessment attempt",
)
async def start_attempt(
    assessment_id: uuid.UUID,
    payload: AttemptStartRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AttemptResponse:
    return await AssessmentService.start_attempt(assessment_id, payload.employee_id, db)


@router.get(
    "/assessments/{assessment_id}",
    response_model=AssessmentDetailResponse,
    summary="Get assessment detail",
)
async def get_assessment_detail(
    assessment_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AssessmentDetailResponse:
    return await AssessmentService.get_assessment_by_id(assessment_id, db)


# ============================================================================
# Employee Competencies & Evidence Endpoints
# ============================================================================


@router.get(
    "/employees/{employee_id}/competencies",
    response_model=list[EmployeeCompetencyResponse],
    summary="Get employee's current estimated competencies",
)
async def get_employee_competencies(
    employee_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[EmployeeCompetencyResponse]:
    emp = await db.get(Employee, employee_id)
    if not emp:
        raise PragyaException(
            code="EMPLOYEE_NOT_FOUND",
            message=f"Employee '{employee_id}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    records = await AssessmentRepository.get_employee_competencies(employee_id, db)
    results = []
    for r in records:
        lvl_num, lvl_name = score_to_proficiency_level(r.current_score)
        comp = r.competency
        domain_name = comp.domain.name if comp and comp.domain else "General"
        domain_code = comp.domain.code if comp and comp.domain else "GENERAL"

        results.append(
            EmployeeCompetencyResponse(
                id=r.id,
                employee_id=r.employee_id,
                competency_id=r.competency_id,
                competency_name=comp.name if comp else "Competency",
                competency_code=comp.code if comp else "CODE",
                domain_name=domain_name,
                domain_code=domain_code,
                current_score=r.current_score,
                proficiency_level_number=lvl_num,
                proficiency_level_name=lvl_name,
                confidence=r.confidence,
                confidence_label=r.confidence_label,
                last_assessed_at=r.last_assessed_at,
                evidence_count=r.evidence_count,
            )
        )
    return results


@router.get(
    "/employees/{employee_id}/competencies/{competency_id}",
    response_model=EmployeeCompetencyResponse,
    summary="Get single employee competency score",
)
async def get_employee_competency_detail(
    employee_id: uuid.UUID,
    competency_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> EmployeeCompetencyResponse:
    record = await AssessmentRepository.get_employee_competency(employee_id, competency_id, db)
    if not record:
        raise PragyaException(
            code="COMPETENCY_RECORD_NOT_FOUND",
            message=f"No competency record found for employee '{employee_id}' and competency '{competency_id}'",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    lvl_num, lvl_name = score_to_proficiency_level(record.current_score)
    comp = record.competency
    domain_name = comp.domain.name if comp and comp.domain else "General"
    domain_code = comp.domain.code if comp and comp.domain else "GENERAL"

    return EmployeeCompetencyResponse(
        id=record.id,
        employee_id=record.employee_id,
        competency_id=record.competency_id,
        competency_name=comp.name if comp else "Competency",
        competency_code=comp.code if comp else "CODE",
        domain_name=domain_name,
        domain_code=domain_code,
        current_score=record.current_score,
        proficiency_level_number=lvl_num,
        proficiency_level_name=lvl_name,
        confidence=record.confidence,
        confidence_label=record.confidence_label,
        last_assessed_at=record.last_assessed_at,
        evidence_count=record.evidence_count,
    )


@router.get(
    "/employees/{employee_id}/competencies/{competency_id}/evidence",
    response_model=list[CompetencyEvidenceResponse],
    summary="Get all evidence records contributing to a competency",
)
async def get_competency_evidence(
    employee_id: uuid.UUID,
    competency_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[CompetencyEvidenceResponse]:
    evidence_list = await AssessmentRepository.get_employee_competency_evidence(
        employee_id, competency_id, db
    )
    return [CompetencyEvidenceResponse.model_validate(e) for e in evidence_list]


@router.get(
    "/employees/{employee_id}/competencies/{competency_id}/history",
    response_model=list[CompetencyScoreHistoryResponse],
    summary="Get score audit history for a competency",
)
async def get_competency_history(
    employee_id: uuid.UUID,
    competency_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[CompetencyScoreHistoryResponse]:
    history_list = await AssessmentRepository.get_competency_score_history(
        employee_id, competency_id, db
    )
    return [CompetencyScoreHistoryResponse.model_validate(h) for h in history_list]


@router.post(
    "/employees/{employee_id}/self-assessment",
    response_model=SelfAssessmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit employee self-assessment for a competency",
)
async def submit_self_assessment(
    employee_id: uuid.UUID,
    payload: SelfAssessmentRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SelfAssessmentResponse:
    emp = await db.get(Employee, employee_id)
    if not emp:
        raise PragyaException(
            code="EMPLOYEE_NOT_FOUND",
            message=f"Employee '{employee_id}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    _evidence, updated_comp = await EvidenceService.record_self_assessment(
        employee_id=employee_id,
        competency_id=payload.competency_id,
        level=payload.level,
        db=db,
    )

    norm_score = normalize_self_assessment(payload.level)
    return SelfAssessmentResponse(
        competency_id=payload.competency_id,
        level=payload.level,
        normalized_score=norm_score,
        new_competency_score=updated_comp.current_score if updated_comp else norm_score,
        confidence=updated_comp.confidence if updated_comp else 0.6,
        confidence_label=updated_comp.confidence_label if updated_comp else "MEDIUM",
    )
