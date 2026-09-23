# PRAGYA Document Intelligence Foundation

## 1. Architecture Overview
The PRAGYA Document Intelligence Foundation establishes a secure, isolated, and traceable pipeline for ingesting official statistical learning materials, extracting text across heterogeneous formats, segmenting content along semantic boundaries, generating multilingual vector embeddings, and executing precision retrieval for evidence grounding.

```
[ Upload File (PDF/PPT/TXT) ]
              │
              ▼
[ Upload Security Validation ] (MIME, Extension, Size, SHA-256 Checksum)
              │
              ▼
[ LocalFileStorage ] ──► Stores encrypted/isolated binary on disk
              │
              ▼
[ Background Ingestion Pipeline ]
  ├─ 1. Format-Specific Processor (PyMuPDF, python-pptx, TXT)
  ├─ 2. Document Normalization (DocumentContent with page/slide bounds)
  ├─ 3. Semantic Text Chunker (400–700 tokens, 50–100 token overlap)
  ├─ 4. Batch Embedder (SentenceTransformer / Multilingual 384-dim)
  └─ 5. Vector Store & Indexing (PgVectorStore / DevelopmentLexicalStore)
              │
              ▼
[ POST /api/v1/rag/search ] ──► Cosine Similarity Retrieval with Strict Employee Isolation
```

---

## 2. Supported Formats
The system supports four official enterprise document formats:
- **PDF (`.pdf`)**: Statistical survey manuals, methodological notes, official gazettes, and administrative training circulars.
- **PPTX (`.pptx`)**: Modern training slide presentations from NSSTA, TPAC, and administrative academies.
- **PPT (`.ppt`)**: Legacy slide presentations.
- **TXT / Markdown (`.txt`, `.md`, `.csv`)**: Plain text notes, curriculum guidelines, and syllabus documents.

---

## 3. File Storage Abstraction
The binary payload is stored completely outside PostgreSQL to prevent database bloat:
- **Interface**: `FileStorage` Protocol with `save()`, `open()`, `delete()`, `exists()`.
- **Implementation**: `LocalFileStorage` writing to `storage/uploads`.
- **Naming**: Files are stored with cryptographically secure random UUIDs (`uuid4().hex + sanitized_extension`).
- **Path Traversal Protection**: All paths are resolved against the canonical storage root using `Path.relative_to()`. Attempted path traversals immediately abort with error code `INVALID_STORAGE_PATH`.

---

## 4. Extraction Engines
- **PDF Extraction**: Implemented via **PyMuPDF (`fitz`)**. Extracts text page-by-page, retaining 1-indexed `page_number` and total document page counts.
- **Presentation Extraction**: Implemented via **`python-pptx`**. Extracts text slide-by-slide, extracting slide titles and body shapes while preserving 1-indexed `slide_number`.
- **Text Extraction**: Implemented with explicit multi-encoding safe decoding (`utf-8`, `utf-8-sig`, `cp1252`, `latin-1`).

---

## 5. Document Normalization
All extractors return a unified `DocumentContent` and `ExtractedDocument` schema:
- `document_type`: `PDF`, `PPT`, `PPTX`, `TXT`
- `page_number`: 1-indexed page (or `None`)
- `slide_number`: 1-indexed slide (or `None`)
- `section_title`: Extracted header or slide title
- `text`: Cleaned content string
- `metadata`: Source structural markers

The downstream chunker, embedder, and vector retriever operate uniformly regardless of whether the source was a 50-page PDF manual or a 20-slide presentation.

---

## 6. Chunking Strategy
Implemented in `TextChunker`:
- **Token Target**: 400–700 tokens per chunk (~1600–2800 characters).
- **Token Overlap**: 50–100 tokens (~200–400 characters) across consecutive chunk splits.
- **Boundary Preservation**: Splits occur on paragraph breaks (`\n\n`) and sentence boundaries (`[.!?]`).
- **Integrity Guarantee**: Chunks smaller than 15 tokens or empty fragments are automatically suppressed.
- **Page/Slide Isolation**: Chunk boundaries never bleed across physical document pages or presentation slides.

---

## 7. Embedding Architecture
- **Interface**: `EmbeddingProvider` declaring `embed_text(text)`, `embed_batch(texts)`, and `dimension`.
- **Batch Processing**: Chunks are embedded in batches of 32 (`embed_chunks(chunks)`) in strict deterministic order.
- **Dimension Validation**: Dimension size is verified dynamically during provider initialization.

---

## 8. Model Configuration
Configured via `settings.EMBEDDING_MODEL`:
- Default: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions).
- Multilingual Target: `paraphrase-multilingual-MiniLM-L12-v2` (384 dimensions), providing native support for English, Hindi, and Telugu.
- Mock/Offline Mode: `MockEmbeddingProvider` generates deterministic 384-dimensional unit vectors for fast testing.

---

## 9. Native pgvector Setup on Windows (PostgreSQL 18.6)
- **Status**: **ACTIVE & VERIFIED**. Native `pgvector` v0.8.6 compiled via MSVC / NMAKE from official source (`https://github.com/pgvector/pgvector.git`) and installed into PostgreSQL 18.6 on Windows.
- **Binaries Installed**:
  - `C:\Program Files\PostgreSQL\18\lib\vector.dll` (280 KB)
  - `C:\Program Files\PostgreSQL\18\share\extension\vector.control`
  - Extension upgrade scripts: `sql\vector--0.8.6.sql`
- **Database Extension**: Enabled via `CREATE EXTENSION IF NOT EXISTS vector;`.
  - Extension version: `0.8.6`
  - Verified via: `SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';`
- **Database Schema**: Column `document_chunks.embedding` is migrated to native `vector(384)` via Alembic revision `e2a1b9d4c7f0`.
  - Type: `USER-DEFINED (vector)`
  - Dimensions: 384
  - All existing document chunks and metadata preserved.
- **Native Windows Build Procedure**:
  1. Open Visual Studio 2022 Build Tools x64 Native Tools Environment (`vcvars64.bat`).
  2. Set `PGROOT=C:\Program Files\PostgreSQL\18`.
  3. Compile source: `nmake /F Makefile.win`.
  4. Copy generated `vector.dll`, `vector.control`, and SQL scripts to PostgreSQL 18 lib and share directories.

---

## 10. Vector Store Selection & Retrieval
- **Interface**: `VectorStore` declaring `add_chunks()`, `search()`, `delete_document()`, and `is_vector_supported()`.
- **Active Store**: `PgVectorStore` (selected via `settings.VECTOR_BACKEND = "pgvector"`).
  - Distance Metric: Native PostgreSQL pgvector cosine distance operator (`<=>`).
  - Scoring Convention: Cosine Distance $d \in [0, 2]$; Cosine Similarity $s = 1.0 - d \in [-1.0, 1.0]$ rounded to 4 decimal places.
  - Returns `RetrievalResult` with `chunk_id`, `document_id`, `text`, `score`, `page_number`, `slide_number`, `section_title`, `document_title`, `metadata`.
  - Returns `is_vector_supported() = True`.
- **Controlled Fallback**: `DevelopmentLexicalStore`
  - Retained for offline environments or environments where `pgvector` is uncompiled (`VECTOR_BACKEND=lexical`).
  - Computes exact vector cosine similarity in Python over stored chunk embeddings with lexical boosting.
  - Returns `is_vector_supported() = False`, triggering the transparent UI fallback banner.

---

## 11. Chunk Metadata
Every stored `DocumentChunk` preserves a complete provenance dictionary in `metadata`:
```json
{
  "document_id": "87f0b8d5-...",
  "employee_id": "d4e1d903-...",
  "chunk_index": 0,
  "page": 1,
  "slide": null,
  "section": "Section 1: Foundations of Survey Sampling",
  "document_type": "PDF",
  "language": "en",
  "total_pages": 12
}
```

---

## 12. Source Traceability
Every retrieval result (`RAGSearchResultItem`) guarantees source attribution:
- `document_title`: Human-readable document name (e.g. *"Survey Sampling Manual"*).
- `page_number`: Exact physical page number in PDF/TXT.
- `slide_number`: Exact slide number in PPT/PPTX.
- `section_title`: Specific chapter or slide heading.
- `score`: Cosine similarity coefficient (0.0 to 1.0).

Future AI assistant answers in Stage 9 will cite these specific page and slide coordinates.

---

## 13. Employee Document Isolation
**Strict multi-tenant employee isolation is enforced at the database query level.**
When an employee executes a search:
```sql
SELECT document_chunks.*
FROM document_chunks
JOIN documents ON documents.id = document_chunks.document_id
JOIN uploaded_materials ON uploaded_materials.id = documents.uploaded_material_id
WHERE uploaded_materials.employee_id = :authenticated_employee_id
  AND uploaded_materials.status = 'PROCESSED'
```
An employee can never retrieve, preview, or view chunks belonging to materials uploaded by another officer.

---

## 14. Upload Security Controls
1. **MIME Whitelisting**: Strict verification of incoming content-type against supported document formats.
2. **File Extension Sanitization**: Rejection of executables (`.exe`, `.sh`, `.bat`, `.py`, `.dll`).
3. **Payload Limit**: Enforced `MAX_UPLOAD_SIZE_MB` (default: 25MB) checked prior to disk storage.
4. **Server-Generated Filenames**: Random UUIDs prevent collision and execution vulnerabilities.
5. **Path Traversal Prevention**: Storage paths are validated to remain subpaths of `settings.STORAGE_UPLOAD_DIR`.
6. **Integrity Checksums**: SHA-256 digests verify payload authenticity.

---

## 15. Duplicate Handling
Duplicate detection operates on a per-employee basis:
- If Employee A uploads file X with checksum $C$, and re-uploads file X, the API returns `409 Conflict` (`DUPLICATE_MATERIAL`).
- If Employee B uploads identical file X, the upload succeeds independently, preserving strict employee ownership and isolation.

---

## 16. Processing Pipeline States
```
UPLOADED  ──►  PROCESSING  ──►  PROCESSED
                     │
                     └──►  FAILED
```
- `UPLOADED`: File received, validated, and saved to disk.
- `PROCESSING`: Background task active (extracting text, chunking, and embedding).
- `PROCESSED`: Document and chunks committed, indexed, and ready for retrieval.
- `FAILED`: Ingestion encountered an extraction or format error; safe `error_code` recorded.
- `DELETED`: Soft-deleted; physical storage file safely removed from disk.

---

## 17. Failure Handling & Transactions
Ingestion runs in isolated transactional units:
- If extraction fails (e.g., corrupted PDF), the material status transitions to `FAILED` with `error_code = 'PROCESSING_FAILED'`.
- Chunks and documents are rolled back so no half-indexed state is left.
- Stack traces are logged server-side and never leaked in API responses.

---

## 18. Fallback Behavior
When running in an environment without native `pgvector`:
- The system gracefully uses `DevelopmentLexicalStore`.
- The RAG API returns:
  ```json
  {
    "retrieval_mode": "development_lexical_fallback",
    "warning": "Vector search unavailable in current environment."
  }
  ```
- Retrieval results remain fully functional for local demonstration and automated testing.

---

## 19. Known Limitations
1. **Windows PostgreSQL 18 pgvector**: Awaiting compiled pgvector DLL release for PostgreSQL 18 on Windows x86_64.
2. **Scanned Images**: Optical Character Recognition (OCR) for scanned image-only PDFs is not active; documents must contain digital text layers.
3. **Password Protected Files**: Encrypted or DRM-locked PDFs are rejected at upload.

---

## 20. Future RAG Integration (Stage 9)
This stage establishes the data foundation:
$$\text{Document} \longrightarrow \text{Chunking} \longrightarrow \text{Embedding} \longrightarrow \text{Vector Retrieval}$$
In Stage 9, the AI Learning Assistant will ingest these retrieved evidence chunks and construct source-grounded answers citing the document name, page, and section title without hallucinations.
