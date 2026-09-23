import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    document_id: uuid.UUID
    chunk_index: int
    text: str
    page_number: int | None = None
    slide_number: int | None = None
    section_title: str | None = None
    token_count: int | None = None
    competency_id: uuid.UUID | None = None
    metadata: dict = Field(default_factory=dict, validation_alias="chunk_metadata")


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    uploaded_material_id: uuid.UUID
    document_type: str
    title: str
    page_count: int | None = None
    slide_count: int | None = None
    language: str
    processing_version: str
    created_at: datetime


class UploadedMaterialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID
    original_filename: str
    mime_type: str
    file_size: int
    checksum_sha256: str
    status: str
    error_code: str | None = None
    created_at: datetime
    updated_at: datetime
    documents: list[DocumentResponse] = []


class PaginatedMaterialsResponse(BaseModel):
    items: list[UploadedMaterialResponse]
    total: int
    skip: int
    limit: int


class MaterialStatusResponse(BaseModel):
    material_id: uuid.UUID
    status: str
    error_code: str | None = None
    updated_at: datetime
