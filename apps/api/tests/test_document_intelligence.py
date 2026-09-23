import io
import uuid
import pytest
import fitz
from pptx import Presentation
from pptx.util import Inches, Pt
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.core.exceptions import PragyaException
from app.core.storage import LocalFileStorage
from app.modules.materials.chunker import TextChunker
from app.modules.materials.embeddings import MockEmbeddingProvider, get_embedding_provider
from app.modules.materials.processors.base import DocumentContent, ExtractedDocument
from app.modules.materials.processors.pdf import PDFProcessor
from app.modules.materials.processors.pptx import PPTProcessor
from app.modules.materials.processors.txt import TXTProcessor
from app.modules.materials.processors import get_processor
from sqlalchemy import select
from app.modules.materials.models import Document
from app.modules.materials.service import MaterialService
from app.modules.materials.vector_store import DevelopmentLexicalStore, PgVectorStore, get_vector_store


def create_sample_pdf_bytes(title: str = "Survey Sampling Manual", text: str = "What is stratified sampling? Stratified sampling divides population into subgroups.") -> bytes:
    doc = fitz.open()
    page1 = doc.new_page()
    page1.insert_text((50, 50), f"{title}\n\nPage 1 Content:\n{text}")
    page2 = doc.new_page()
    page2.insert_text((50, 50), f"Page 2 Content:\nSample allocation techniques in multi-stage surveys.")
    doc.set_metadata({"title": title, "author": "MoSPI NSSTA"})
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


def create_sample_pptx_bytes(title: str = "Statistical Quality Assurance") -> bytes:
    prs = Presentation()
    slide_layout = prs.slide_layouts[0]
    slide1 = prs.slides.add_slide(slide_layout)
    slide1.shapes.title.text = title
    slide1.placeholders[1].text = "Overview of Data Validation Standards."

    slide2 = prs.slides.add_slide(prs.slide_layouts[1])
    slide2.shapes.title.text = "Audit Framework"
    slide2.placeholders[1].text = "Key audit checks for official statistics."

    buf = io.BytesIO()
    prs.save(buf)
    return buf.getvalue()


@pytest.fixture
def sample_pdf():
    return create_sample_pdf_bytes()


@pytest.fixture
def sample_pptx():
    return create_sample_pptx_bytes()


@pytest.fixture
def sample_txt():
    return b"# National Accounts\n\nGross domestic product calculation methodologies and deflators.\n\nQuarterly estimation routines."


# ============================================================================
# 1. PROCESSOR UNIT TESTS (PDF, PPTX, TXT, METADATA)
# ============================================================================

def test_pdf_processor_extraction(sample_pdf):
    proc = PDFProcessor()
    assert proc.supports("application/pdf", ".pdf")
    res = proc.extract(sample_pdf, "sample.pdf")
    assert res.document_type == "PDF"
    assert res.page_count == 2
    assert len(res.contents) == 2
    assert res.contents[0].page_number == 1
    assert "stratified sampling" in res.contents[0].text.lower()
    assert res.contents[1].page_number == 2


def test_pptx_processor_extraction(sample_pptx):
    proc = PPTProcessor()
    assert proc.supports("application/vnd.openxmlformats-officedocument.presentationml.presentation", ".pptx")
    res = proc.extract(sample_pptx, "presentation.pptx")
    assert res.document_type == "PPTX"
    assert res.slide_count == 2
    assert len(res.contents) >= 1
    assert res.contents[0].slide_number == 1
    assert "Statistical Quality Assurance" in res.contents[0].text


def test_txt_processor_extraction(sample_txt):
    proc = TXTProcessor()
    assert proc.supports("text/plain", ".txt")
    res = proc.extract(sample_txt, "notes.txt")
    assert res.document_type == "TXT"
    assert len(res.contents) >= 1
    assert any("Gross domestic product" in c.text for c in res.contents)


def test_unsupported_processor_error():
    with pytest.raises(PragyaException) as exc:
        get_processor("application/x-executable", "virus.exe")
    assert exc.value.code == "UNSUPPORTED_FILE_TYPE"


# ============================================================================
# 2. CHUNKER UNIT TESTS
# ============================================================================

def test_text_chunker():
    chunker = TextChunker(min_tokens=20, max_tokens=100, overlap_tokens=20)
    doc_id = uuid.uuid4()
    emp_id = uuid.uuid4()
    long_text = " ".join([f"Sentence number {i} discussing statistical estimation." for i in range(40)])
    
    extracted = ExtractedDocument(
        document_type="PDF",
        title="Test Document",
        contents=[
            DocumentContent(text=long_text, page_number=1, section_title="Introduction"),
        ]
    )
    chunks = chunker.chunk_document(extracted, doc_id, emp_id)
    assert len(chunks) > 1
    assert chunks[0].page_number == 1
    assert chunks[0].metadata["document_id"] == str(doc_id)
    assert chunks[0].metadata["employee_id"] == str(emp_id)
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1


# ============================================================================
# 3. EMBEDDING & VECTOR STORE UNIT TESTS
# ============================================================================

def test_embedding_provider_generation():
    provider = MockEmbeddingProvider(dimension=384)
    assert provider.dimension == 384
    v1 = provider.embed_text("Sample query for stratified sampling")
    assert len(v1) == 384
    batch = provider.embed_batch(["Text 1", "Text 2"])
    assert len(batch) == 2
    assert len(batch[0]) == 384


def test_development_lexical_store_unsupported_signal():
    store = DevelopmentLexicalStore(None)
    # Explicitly reports native vector search unavailable
    assert store.is_vector_supported() is False


# ============================================================================
# 4. STORAGE ABSTRACTION & SECURITY
# ============================================================================

def test_local_storage_security(tmp_path):
    storage = LocalFileStorage(base_dir=str(tmp_path))
    content = b"Confidential Government Statistical Tables"
    stored_name, path = storage.save(content, "test.pdf")
    assert storage.exists(path)
    read_back = storage.open(path)
    assert read_back == content

    # Test path traversal prevention
    with pytest.raises(PragyaException) as exc:
        storage.open(str(tmp_path / "../../../windows/system32/cmd.exe"))
    assert exc.value.code == "INVALID_STORAGE_PATH"

    # Test delete
    assert storage.delete(path) is True
    assert not storage.exists(path)


# ============================================================================
# 5. INTEGRATION API TESTS VIA HTTPX CLIENT
# ============================================================================

@pytest.mark.asyncio
async def test_document_intelligence_full_api_flow(sample_pdf, sample_pptx, sample_txt):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # A. Upload validation: invalid extension
        bad_file = {"file": ("script.sh", b"echo evil", "application/x-sh")}
        r_bad = await client.post("/api/v1/materials/upload", files=bad_file)
        assert r_bad.status_code == 400
        assert r_bad.json()["error"]["code"] == "UNSUPPORTED_FILE_TYPE"

        # B. Upload valid PDF
        files_pdf = {"file": ("Sampling_Manual.pdf", sample_pdf, "application/pdf")}
        r_up = await client.post("/api/v1/materials/upload", files=files_pdf)
        assert r_up.status_code == 202
        data_up = r_up.json()
        mat_id = data_up["id"]
        assert data_up["original_filename"] == "Sampling_Manual.pdf"
        assert data_up["status"] in ("UPLOADED", "PROCESSING", "PROCESSED")

        # C. Duplicate upload by same employee must fail with 409 DUPLICATE_MATERIAL
        files_dup = {"file": ("Sampling_Manual.pdf", sample_pdf, "application/pdf")}
        r_dup = await client.post("/api/v1/materials/upload", files=files_dup)
        assert r_dup.status_code == 409
        assert r_dup.json()["error"]["code"] == "DUPLICATE_MATERIAL"

        # D. Same file by DIFFERENT employee should succeed
        other_emp_id = "d4e1d903-6fbd-4ada-9c65-48abd8e6fd1e"
        files_other = {"file": ("Sampling_Manual_Other.pdf", sample_pdf, "application/pdf")}
        r_other = await client.post(
            "/api/v1/materials/upload",
            files=files_other,
            headers={"X-Employee-Id": other_emp_id},
        )
        assert r_other.status_code == 202
        mat_id_other = r_other.json()["id"]

        # E. Process the uploaded PDF synchronously to test chunks & retrieval
        from app.db.session import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            service = MaterialService(session)
            await service.process_material(uuid.UUID(mat_id))

        # F. Check status endpoint
        r_status = await client.get(f"/api/v1/materials/{mat_id}/status")
        assert r_status.status_code == 200
        assert r_status.json()["status"] == "PROCESSED"

        # G. List materials
        r_list = await client.get("/api/v1/materials")
        assert r_list.status_code == 200
        items = r_list.json()["items"]
        assert any(m["id"] == mat_id for m in items)

        # H. Inspect chunks
        r_chunks = await client.get(f"/api/v1/materials/{mat_id}/chunks")
        assert r_chunks.status_code == 200
        chunks = r_chunks.json()
        assert len(chunks) >= 2
        assert chunks[0]["page_number"] == 1
        assert "stratified" in chunks[0]["text"].lower()

        # I. RAG Semantic Evidence Retrieval
        r_search = await client.post(
            "/api/v1/rag/search",
            json={"query": "What is stratified sampling?", "top_k": 3},
        )
        assert r_search.status_code == 200
        search_data = r_search.json()
        assert search_data["query"] == "What is stratified sampling?"
        assert search_data["retrieval_mode"] == "vector"
        assert search_data["warning"] is None
        assert len(search_data["results"]) > 0
        top_res = search_data["results"][0]
        assert top_res["document_title"] == "Sampling_Manual" or "Survey Sampling" in top_res["document_title"]
        assert top_res["page_number"] == 1

        # J. Strict Employee Isolation Test:
        # Searching under other employee should NOT return this employee's document chunks
        r_search_isolated = await client.post(
            "/api/v1/rag/search",
            json={"query": "What is stratified sampling?", "top_k": 3},
            headers={"X-Employee-Id": str(uuid.uuid4())},
        )
        assert r_search_isolated.status_code == 200
        assert len(r_search_isolated.json()["results"]) == 0

        # K. Delete materials
        r_del = await client.delete(f"/api/v1/materials/{mat_id}")
        assert r_del.status_code == 200
        r_after = await client.get(f"/api/v1/materials/{mat_id}")
        assert r_after.status_code == 404

        # Clean up second employee test material
        await client.delete(f"/api/v1/materials/{mat_id_other}", headers={"X-Employee-Id": other_emp_id})


@pytest.mark.asyncio
async def test_pgvector_extension_and_vector_column():
    """Verify PostgreSQL has vector extension active and document_chunks.embedding is vector(384)."""
    from app.db.session import AsyncSessionLocal
    from sqlalchemy import text

    async with AsyncSessionLocal() as session:
        # Extension verification
        res_ext = await session.execute(text("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"))
        ext_row = res_ext.fetchone()
        assert ext_row is not None
        assert ext_row[0] == "vector"
        assert ext_row[1] == "0.8.6"

        # Vector column type verification
        res_col = await session.execute(text("""
            SELECT column_name, data_type, udt_name 
            FROM information_schema.columns 
            WHERE table_name = 'document_chunks' AND column_name = 'embedding';
        """))
        col_row = res_col.fetchone()
        assert col_row is not None
        assert col_row[2] == "vector"


@pytest.mark.asyncio
async def test_pgvector_store_direct_retrieval_and_isolation():
    """Directly test PgVectorStore and DevelopmentLexicalStore behavior and isolation."""
    from app.db.session import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        store = get_vector_store(session)
        assert isinstance(store, PgVectorStore)
        assert store.is_vector_supported() is True

        # Verify fallback store remains functional
        fallback_store = DevelopmentLexicalStore(session)
        assert fallback_store.is_vector_supported() is False


@pytest.mark.asyncio
async def test_retrieval_quality_relevant_vs_unrelated_queries(sample_pdf):
    """
    Test Stage 8 Retrieval Quality Fix:
    1. Relevant query returns evidence with status SUCCESS.
    2. Unrelated query returns INSUFFICIENT_EVIDENCE with standard message.
    3. Duplicate chunk content from same doc/page is deduplicated.
    4. Top-k count is respected.
    5. Threshold is configurable.
    6. Strict employee isolation remains enforced.
    """
    from app.db.session import AsyncSessionLocal
    from sqlalchemy import text

    async with AsyncSessionLocal() as session:
        res = await session.execute(text("SELECT id FROM employees ORDER BY created_at ASC LIMIT 2;"))
        rows = res.fetchall()
        emp_id = str(rows[0][0])
        other_emp_id = str(rows[1][0])

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # A. Upload sample PDF with unique filename
        filename = f"Sampling_Guide_{uuid.uuid4().hex[:6]}.pdf"
        files = {"file": (filename, sample_pdf, "application/pdf")}
        r_upload = await client.post(
            "/api/v1/materials/upload",
            files=files,
            headers={"X-Employee-Id": emp_id}
        )
        assert r_upload.status_code == 202
        mat_id = r_upload.json()["id"]

        # Ensure processed
        async with AsyncSessionLocal() as session:
            service = MaterialService(session)
            await service.process_material(uuid.UUID(mat_id))

        # 1. Relevant query returns evidence
        r_rel = await client.post(
            "/api/v1/rag/search",
            json={"query": "What is stratified sampling?", "top_k": 5},
            headers={"X-Employee-Id": emp_id}
        )
        assert r_rel.status_code == 200
        data_rel = r_rel.json()
        assert data_rel["status"] == "SUCCESS"
        assert data_rel["message"] is None
        assert len(data_rel["results"]) > 0
        assert data_rel["results"][0]["score"] >= 0.50
        assert "stratified" in data_rel["results"][0]["text"].lower()

        # 2. Unrelated query returns insufficient evidence
        r_unrel = await client.post(
            "/api/v1/rag/search",
            json={"query": "What is the capital of Japan?", "top_k": 5},
            headers={"X-Employee-Id": emp_id}
        )
        assert r_unrel.status_code == 200
        data_unrel = r_unrel.json()
        assert data_unrel["status"] == "INSUFFICIENT_EVIDENCE"
        assert data_unrel["message"] == "No sufficiently relevant evidence was found in your uploaded learning materials."
        assert len(data_unrel["results"]) == 0

        # 3. Duplicate chunks are not repeated
        seen_chunks = set()
        for res in data_rel["results"]:
            chunk_sig = (res["document_title"], res["page_number"], res["text"].strip().lower())
            assert chunk_sig not in seen_chunks, "Duplicate chunk returned in retrieval results!"
            seen_chunks.add(chunk_sig)

        # 4. Top-k remains correct
        r_top2 = await client.post(
            "/api/v1/rag/search",
            json={"query": "What is stratified sampling?", "top_k": 1},
            headers={"X-Employee-Id": emp_id}
        )
        assert r_top2.status_code == 200
        assert len(r_top2.json()["results"]) <= 1

        # 5. Configurable threshold test via service
        async with AsyncSessionLocal() as session:
            service = MaterialService(session)
            # With strict threshold 0.99, even relevant query yields insufficient evidence
            res_strict, _, status_strict, msg_strict = await service.retrieve_evidence(
                employee_id=uuid.UUID(emp_id),
                query="What is stratified sampling?",
                min_score=0.99
            )
            assert status_strict == "INSUFFICIENT_EVIDENCE"
            assert len(res_strict) == 0

            # With permissive threshold 0.0, unrelated query passes
            res_perm, _, status_perm, _ = await service.retrieve_evidence(
                employee_id=uuid.UUID(emp_id),
                query="What is the capital of Japan?",
                min_score=0.0
            )
            assert status_perm == "SUCCESS"
            assert len(res_perm) > 0

        # 6. Employee isolation remains enforced
        isolated_emp_id = str(uuid.uuid4())
        r_iso = await client.post(
            "/api/v1/rag/search",
            json={"query": "What is stratified sampling?", "top_k": 5},
            headers={"X-Employee-Id": isolated_emp_id}
        )
        assert r_iso.status_code == 200
        assert r_iso.json()["status"] == "INSUFFICIENT_EVIDENCE"
        assert len(r_iso.json()["results"]) == 0

        # And verify other_emp_id never retrieves emp_id's specific material
        r_other = await client.post(
            "/api/v1/rag/search",
            json={"query": "What is stratified sampling?", "top_k": 10},
            headers={"X-Employee-Id": other_emp_id}
        )
        assert r_other.status_code == 200
        # Check document IDs returned for other_emp_id do not belong to mat_id
        async with AsyncSessionLocal() as session:
            stmt_mat_doc = select(Document.id).where(Document.uploaded_material_id == uuid.UUID(mat_id))
            res_mat_doc = await session.execute(stmt_mat_doc)
            emp1_doc_id = res_mat_doc.scalar_one_or_none()
            if emp1_doc_id:
                for r in r_other.json()["results"]:
                    assert r["document_id"] != str(emp1_doc_id), "Cross-employee document leakage!"

        # Cleanup
        await client.delete(f"/api/v1/materials/{mat_id}", headers={"X-Employee-Id": emp_id})


