import uuid
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Header,
    Query,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.employees.service import EmployeeService
from app.modules.materials.models import Document, DocumentChunk
from app.modules.materials.schemas import (
    DocumentChunkResponse,
    MaterialStatusResponse,
    PaginatedMaterialsResponse,
    UploadedMaterialResponse,
)
from app.modules.materials.service import MaterialService

router = APIRouter(prefix="/materials", tags=["Learning Materials"])
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
    "/upload",
    response_model=UploadedMaterialResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload learning material for background document intelligence processing",
)
async def upload_material(
    background_tasks: BackgroundTasks,
    db: DbSession,
    file: Annotated[UploadFile, File(...)],
    employee_id: CurrentEmployeeId,
) -> UploadedMaterialResponse:
    service = MaterialService(db)
    material = await service.create_upload(employee_id, file)

    # Queue background processing
    async def run_pipeline(mat_id: uuid.UUID):
        from app.db.session import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            bg_service = MaterialService(session)
            await bg_service.process_material(mat_id)

    background_tasks.add_task(run_pipeline, material.id)
    return UploadedMaterialResponse.model_validate(material)


@router.get(
    "",
    response_model=PaginatedMaterialsResponse,
    summary="List uploaded learning materials for current employee",
)
async def list_materials(
    db: DbSession,
    employee_id: CurrentEmployeeId,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> PaginatedMaterialsResponse:
    service = MaterialService(db)
    items, total = await service.list_materials(employee_id, skip=skip, limit=limit)
    return PaginatedMaterialsResponse(
        items=[UploadedMaterialResponse.model_validate(m) for m in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{material_id}",
    response_model=UploadedMaterialResponse,
    summary="Get detailed information for a specific uploaded material",
)
async def get_material(
    material_id: uuid.UUID,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> UploadedMaterialResponse:
    service = MaterialService(db)
    material = await service.get_material(employee_id, material_id)
    return UploadedMaterialResponse.model_validate(material)


@router.get(
    "/{material_id}/status",
    response_model=MaterialStatusResponse,
    summary="Poll processing status for a specific material",
)
async def get_material_status(
    material_id: uuid.UUID,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> MaterialStatusResponse:
    service = MaterialService(db)
    material = await service.get_material(employee_id, material_id)
    return MaterialStatusResponse(
        material_id=material.id,
        status=material.status.value,
        error_code=material.error_code,
        updated_at=material.updated_at,
    )


@router.delete(
    "/{material_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete uploaded learning material",
)
async def delete_material(
    material_id: uuid.UUID,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> dict:
    service = MaterialService(db)
    await service.delete_material(employee_id, material_id)
    return {"status": "success", "message": "Material deleted successfully."}


@router.get(
    "/{material_id}/chunks",
    response_model=list[DocumentChunkResponse],
    summary="Get extracted and indexed chunks for an uploaded material",
)
async def get_material_chunks(
    material_id: uuid.UUID,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> list[DocumentChunkResponse]:
    service = MaterialService(db)
    # Enforce ownership
    await service.get_material(employee_id, material_id)

    stmt = (
        select(DocumentChunk)
        .join(Document, Document.id == DocumentChunk.document_id)
        .where(Document.uploaded_material_id == material_id)
        .order_by(DocumentChunk.chunk_index)
    )
    res = await db.execute(stmt)
    chunks = res.scalars().all()
    return [DocumentChunkResponse.model_validate(c) for c in chunks]
