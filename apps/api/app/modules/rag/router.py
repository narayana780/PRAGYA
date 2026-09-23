import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.employees.service import EmployeeService
from app.modules.materials.service import MaterialService
from app.modules.rag.schemas import (
    RAGSearchRequest,
    RAGSearchResponse,
    RAGSearchResultItem,
)

router = APIRouter(prefix="/rag", tags=["Retrieval-Augmented Generation (RAG)"])
DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_employee_id(
    db: DbSession,
    x_employee_id: Annotated[str | None, Header()] = None,
) -> uuid.UUID:
    """Resolve current authenticated employee context with X-Employee-Id override for tests."""
    if x_employee_id:
        try:
            return uuid.UUID(x_employee_id.strip())
        except ValueError:
            pass
    service = EmployeeService(db)
    me = await service.get_me()
    return me.id


CurrentEmployeeId = Annotated[uuid.UUID, Depends(get_current_employee_id)]


@router.post(
    "/search",
    response_model=RAGSearchResponse,
    summary="Semantic retrieval of relevant evidence chunks from employee learning materials",
)
async def search_evidence(
    req: RAGSearchRequest,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> RAGSearchResponse:
    service = MaterialService(db)
    results, is_vector, status, message = await service.retrieve_evidence(
        employee_id=employee_id,
        query=req.query,
        top_k=req.top_k,
        document_id=req.document_id,
        competency_id=req.competency_id,
    )

    items = [
        RAGSearchResultItem(
            chunk_id=r.chunk_id,
            document_id=r.document_id,
            text=r.text,
            score=r.score,
            page_number=r.page_number,
            slide_number=r.slide_number,
            section_title=r.section_title,
            document_title=r.document_title,
        )
        for r in results
    ]

    retrieval_mode = "vector" if is_vector else "development_lexical_fallback"
    warning = None if is_vector else "Vector search unavailable in current environment."

    return RAGSearchResponse(
        query=req.query,
        results=items,
        retrieval_mode=retrieval_mode,
        status=status,
        message=message,
        warning=warning,
    )
