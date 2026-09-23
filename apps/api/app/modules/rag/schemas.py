import uuid

from pydantic import BaseModel, Field


class RAGSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Query string to search in materials")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of results to retrieve")
    document_id: uuid.UUID | None = Field(default=None, description="Optional document filter")
    competency_id: uuid.UUID | None = Field(default=None, description="Optional competency filter")


class RAGSearchResultItem(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    text: str
    score: float
    page_number: int | None = None
    slide_number: int | None = None
    section_title: str | None = None
    document_title: str


class RAGSearchResponse(BaseModel):
    query: str
    results: list[RAGSearchResultItem]
    retrieval_mode: str  # "vector" | "development_lexical_fallback"
    status: str = "SUCCESS"  # "SUCCESS" | "INSUFFICIENT_EVIDENCE"
    message: str | None = None
    warning: str | None = None
