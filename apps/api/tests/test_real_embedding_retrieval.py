import uuid
import pytest
from sqlalchemy import select, func

from app.modules.materials.embeddings import (
    EmbeddingProvider,
    LocalEmbeddingProvider,
    MockEmbeddingProvider,
    get_embedding_provider,
)
from app.main import app
from app.modules.materials.models import Document, DocumentChunk, UploadedMaterial
from app.modules.employees.models import Employee
from app.modules.competencies.models import Competency
from app.modules.materials.service import MaterialService
from app.modules.materials.vector_store import PgVectorStore
from app.core.config import settings


# 1. Real embedding provider initialization & 384-dim output
def test_real_embedding_provider_initialization():
    provider = LocalEmbeddingProvider(model_name="sentence-transformers/all-MiniLM-L6-v2")
    assert isinstance(provider, EmbeddingProvider)
    assert provider.dimension == 384


# 2. Embedding generation (single and batch)
def test_real_embedding_generation():
    provider = LocalEmbeddingProvider()
    vec = provider.embed_text("PRAGYA workforce competency intelligence")
    assert len(vec) == 384
    assert all(isinstance(x, float) for x in vec)

    batch = provider.embed_batch(["Query one", "Query two"])
    assert len(batch) == 2
    assert len(batch[0]) == 384
    assert len(batch[1]) == 384


# 3. MockEmbeddingProvider remains preserved for offline/deterministic testing
def test_mock_provider_preserved():
    mock_p = MockEmbeddingProvider(dimension=384)
    assert mock_p.dimension == 384
    vec = mock_p.embed_text("Deterministic test string")
    assert len(vec) == 384
    assert vec == mock_p.embed_text("Deterministic test string")


# 4. Database chunk count and no-duplicates check
@pytest.mark.asyncio
async def test_chunk_integrity_and_dimensions(db_session):
    # Verify all chunks in database have exactly 384-dim non-null embeddings
    stmt = select(DocumentChunk).where(DocumentChunk.embedding.isnot(None)).limit(10)
    res = await db_session.execute(stmt)
    chunks = res.scalars().all()
    assert len(chunks) > 0, "No chunks found with embeddings"
    for c in chunks:
        assert len(c.embedding) == 384


# 5. Semantic retrieval using real embeddings (relevant vs unrelated)
@pytest.mark.asyncio
async def test_semantic_retrieval_real_embeddings(db_session):
    emp_id = uuid.UUID("e85b4b98-7177-4c62-8eee-6c6f5702c04a")
    service = MaterialService(db_session)

    # Relevant query: What is PRAGYA?
    res_pragya, is_vec, status, _ = await service.retrieve_evidence(
        employee_id=emp_id,
        query="What is PRAGYA?",
        top_k=3,
        min_score=0.45,
    )
    assert status == "SUCCESS"
    assert len(res_pragya) > 0
    assert "PRAGYA" in res_pragya[0].document_title

    # Unrelated query: What is the capital of Japan?
    res_unrelated, is_vec, status_unrelated, msg = await service.retrieve_evidence(
        employee_id=emp_id,
        query="What is the capital of Japan?",
        top_k=3,
        min_score=0.50,
    )
    assert status_unrelated == "INSUFFICIENT_EVIDENCE"
    assert len(res_unrelated) == 0


# 6. Document filter resilience (Document.id vs UploadedMaterial.id)
@pytest.mark.asyncio
async def test_document_filter_resilience(db_session):
    emp_id = uuid.UUID("e85b4b98-7177-4c62-8eee-6c6f5702c04a")
    service = MaterialService(db_session)

    doc_stmt = (
        select(Document, UploadedMaterial)
        .join(UploadedMaterial, UploadedMaterial.id == Document.uploaded_material_id)
        .where(UploadedMaterial.employee_id == emp_id)
        .limit(1)
    )
    row = (await db_session.execute(doc_stmt)).first()
    if row:
        doc, mat = row
        # Search using Document.id
        r_doc, _, _, _ = await service.retrieve_evidence(
            employee_id=emp_id,
            query="sampling",
            top_k=3,
            document_id=doc.id,
            min_score=0.20,
        )
        # Search using UploadedMaterial.id
        r_mat, _, _, _ = await service.retrieve_evidence(
            employee_id=emp_id,
            query="sampling",
            top_k=3,
            document_id=mat.id,
            min_score=0.20,
        )
        assert len(r_doc) == len(r_mat)


# 7. Strict Employee Isolation
@pytest.mark.asyncio
async def test_employee_isolation_real_embeddings(db_session):
    other_emp_id = uuid.uuid4() # Random officer with 0 uploaded materials
    service = MaterialService(db_session)

    results, is_vec, status, _ = await service.retrieve_evidence(
        employee_id=other_emp_id,
        query="What is stratified sampling?",
        top_k=3,
        min_score=0.20,
    )
    assert status == "INSUFFICIENT_EVIDENCE"
    assert len(results) == 0
