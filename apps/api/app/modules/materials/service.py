import hashlib
import re
import traceback
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import PragyaException
from app.core.logging import logger
from app.core.storage import FileStorage, default_storage
from app.modules.materials.chunker import TextChunker
from app.modules.materials.embeddings import EmbeddingProvider, get_embedding_provider
from app.modules.materials.models import (
    Document,
    DocumentType,
    MaterialStatus,
    UploadedMaterial,
)
from app.modules.materials.processors import get_processor
from app.modules.materials.vector_store import (
    RetrievalResult,
    VectorStore,
    get_vector_store,
)

ALLOWED_EXTENSIONS = {".pdf", ".ppt", ".pptx", ".txt", ".md"}
ALLOWED_MIMES = {
    "application/pdf",
    "application/x-pdf",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "text/plain",
    "text/markdown",
    "text/x-markdown",
    "application/octet-stream",  # Sometimes reported by browsers for pptx/txt
}


class MaterialService:
    def __init__(
        self,
        db: AsyncSession,
        storage: FileStorage | None = None,
        embedding_provider: EmbeddingProvider | None = None,
        vector_store: VectorStore | None = None,
        chunker: TextChunker | None = None,
    ):
        self.db = db
        self.storage = storage or default_storage
        self.embedding_provider = embedding_provider or get_embedding_provider()
        self.vector_store = vector_store or get_vector_store(db)
        self.chunker = chunker or TextChunker()

    def validate_file(self, filename: str, mime_type: str, file_size: int) -> str:
        """Validate filename extension, MIME type, and file size limits."""
        ext = Path(filename).suffix.lower()
        if not ext or ext not in ALLOWED_EXTENSIONS:
            raise PragyaException(
                message=f"File format '{ext}' is not supported. Allowed formats: PDF, PPT, PPTX, TXT.",
                status_code=400,
                error_code="UNSUPPORTED_FILE_TYPE",
            )

        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if file_size > max_bytes:
            raise PragyaException(
                message=f"File size exceeds maximum limit of {settings.MAX_UPLOAD_SIZE_MB}MB.",
                status_code=400,
                error_code="FILE_TOO_LARGE",
            )

        # Detect canonical document type
        if ext == ".pdf":
            return DocumentType.PDF.value
        elif ext == ".pptx":
            return DocumentType.PPTX.value
        elif ext == ".ppt":
            return DocumentType.PPT.value
        else:
            return DocumentType.TXT.value

    async def calculate_checksum(self, content: bytes) -> str:
        """Compute SHA-256 checksum."""
        return hashlib.sha256(content).hexdigest()

    async def check_duplicate(self, employee_id: uuid.UUID, checksum: str) -> UploadedMaterial | None:
        """Check if identical content was already uploaded by the same employee."""
        stmt = select(UploadedMaterial).where(
            UploadedMaterial.employee_id == employee_id,
            UploadedMaterial.checksum_sha256 == checksum,
            UploadedMaterial.status != MaterialStatus.DELETED,
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def create_upload(
        self,
        employee_id: uuid.UUID,
        file: UploadFile,
    ) -> UploadedMaterial:
        """Save file, check duplicates, create DB record, and queue background extraction."""
        filename = file.filename or "document.txt"
        content = await file.read()
        file_size = len(content)

        # Validate
        self.validate_file(filename, file.content_type or "", file_size)
        checksum = await self.calculate_checksum(content)

        # Enforce duplicate check for same employee
        existing = await self.check_duplicate(employee_id, checksum)
        if existing:
            raise PragyaException(
                message=f"Identical file '{existing.original_filename}' has already been uploaded.",
                status_code=409,
                error_code="DUPLICATE_MATERIAL",
            )

        # Save to file storage
        stored_filename, storage_path = self.storage.save(content, filename)

        # Create database record
        material = UploadedMaterial(
            employee_id=employee_id,
            original_filename=filename,
            stored_filename=stored_filename,
            mime_type=file.content_type or "application/octet-stream",
            file_size=file_size,
            checksum_sha256=checksum,
            status=MaterialStatus.UPLOADED,
            storage_path=storage_path,
        )
        self.db.add(material)
        await self.db.commit()
        await self.db.refresh(material)

        logger.info(f"Material {material.id} uploaded successfully for employee {employee_id}.")
        return material

    async def process_material(self, material_id: uuid.UUID) -> None:
        """
        Background ingestion pipeline:
        Set PROCESSING -> Extract -> Normalize -> Chunk -> Embed -> Store Vectors -> Set PROCESSED.
        """
        logger.info(f"Starting ingestion pipeline for material {material_id}")
        stmt = select(UploadedMaterial).where(UploadedMaterial.id == material_id)
        res = await self.db.execute(stmt)
        material = res.scalar_one_or_none()
        if not material:
            logger.error(f"Material {material_id} not found for processing.")
            return

        # Update status to PROCESSING
        material.status = MaterialStatus.PROCESSING
        material.error_code = None
        await self.db.commit()

        try:
            # 1. Read binary
            content = self.storage.open(material.storage_path)

            # 2. Extract content
            processor = get_processor(material.mime_type, material.original_filename)
            extracted = processor.extract(content, material.original_filename)

            # 3. Create or reuse document record (Idempotent ingestion)
            stmt_doc = select(Document).where(Document.uploaded_material_id == material.id)
            res_doc = await self.db.execute(stmt_doc)
            document = res_doc.scalars().first()
            if document:
                # Clean up previous chunks before re-indexing to guarantee zero duplicate chunks
                await self.vector_store.delete_document(document.id)
                document.document_type = DocumentType(extracted.document_type)
                document.title = extracted.title
                document.page_count = extracted.page_count
                document.slide_count = extracted.slide_count
                document.language = extracted.language or "en"
            else:
                document = Document(
                    uploaded_material_id=material.id,
                    document_type=DocumentType(extracted.document_type),
                    title=extracted.title,
                    page_count=extracted.page_count,
                    slide_count=extracted.slide_count,
                    language=extracted.language or "en",
                    processing_version="v1",
                )
                self.db.add(document)
            await self.db.flush()

            # 4. Chunk document
            chunks = self.chunker.chunk_document(
                extracted=extracted,
                document_id=document.id,
                employee_id=material.employee_id,
            )

            # 5. Generate embeddings in batch
            embeddings = self.embedding_provider.embed_chunks(chunks)

            # 6. Store chunks and vectors
            chunks_data = []
            for chunk, emb in zip(chunks, embeddings):
                chunks_data.append(
                    {
                        "chunk_index": chunk.chunk_index,
                        "text": chunk.text,
                        "page_number": chunk.page_number,
                        "slide_number": chunk.slide_number,
                        "section_title": chunk.section_title,
                        "token_count": chunk.token_count,
                        "competency_id": None,
                        "embedding": emb,
                        "metadata": chunk.metadata,
                    }
                )

            await self.vector_store.add_chunks(document.id, chunks_data)

            # 7. Transition to PROCESSED
            material.status = MaterialStatus.PROCESSED
            material.error_code = None
            await self.db.commit()
            logger.info(
                f"Material {material.id} processed successfully: {len(chunks)} chunks created and indexed."
            )

        except Exception as e:  # noqa: BLE001
            logger.error(f"Processing failed for material {material_id}: {e}\n{traceback.format_exc()}")
            material.status = MaterialStatus.FAILED
            material.error_code = "PROCESSING_FAILED"
            await self.db.commit()

    async def list_materials(
        self,
        employee_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[UploadedMaterial], int]:
        """List active materials for an employee with pagination."""
        base_query = select(UploadedMaterial).where(
            UploadedMaterial.employee_id == employee_id,
            UploadedMaterial.status != MaterialStatus.DELETED,
        )
        count_res = await self.db.execute(select(func.count()).select_from(base_query.subquery()))
        total = count_res.scalar_one() or 0

        stmt = base_query.order_by(UploadedMaterial.created_at.desc()).offset(skip).limit(limit)
        res = await self.db.execute(stmt)
        items = list(res.scalars().all())
        return items, total

    async def get_material(
        self,
        employee_id: uuid.UUID,
        material_id: uuid.UUID,
    ) -> UploadedMaterial:
        """Get material ensuring strict employee ownership."""
        stmt = select(UploadedMaterial).where(
            UploadedMaterial.id == material_id,
            UploadedMaterial.employee_id == employee_id,
            UploadedMaterial.status != MaterialStatus.DELETED,
        )
        res = await self.db.execute(stmt)
        material = res.scalar_one_or_none()
        if not material:
            raise PragyaException(
                message="Material not found or access unauthorized.",
                status_code=404,
                error_code="MATERIAL_NOT_FOUND",
            )
        return material

    async def delete_material(
        self,
        employee_id: uuid.UUID,
        material_id: uuid.UUID,
    ) -> bool:
        """Soft delete material and remove physical file."""
        material = await self.get_material(employee_id, material_id)
        material.status = MaterialStatus.DELETED
        await self.db.commit()

        # Delete physical file
        self.storage.delete(material.storage_path)
        return True

    async def retrieve_evidence(
        self,
        employee_id: uuid.UUID,
        query: str,
        top_k: int = 5,
        document_id: uuid.UUID | None = None,
        competency_id: uuid.UUID | None = None,
        min_score: float | None = None,
    ) -> tuple[list[RetrievalResult], bool, str, str | None]:
        """
        Execute semantic retrieval with strict employee isolation, deduplication,
        and minimum relevance score thresholding.
        Returns (results, is_vector_supported, status, message).
        """
        is_vector = self.vector_store.is_vector_supported()
        if not query.strip():
            return [], is_vector, "INSUFFICIENT_EVIDENCE", "Query string cannot be empty."

        threshold = min_score if min_score is not None else getattr(settings, "MIN_RETRIEVAL_SCORE", 0.50)

        # Generate query embedding vector
        query_embedding = self.embedding_provider.embed_text(query.strip())

        # Retrieve a wider pool of candidate matches to allow post-deduplication and thresholding
        candidate_k = max(top_k * 4, 25)
        raw_results = await self.vector_store.search(
            query_embedding=query_embedding,
            query_text=query.strip(),
            employee_id=employee_id,
            top_k=candidate_k,
            document_id=document_id,
            competency_id=competency_id,
        )

        # Deduplicate identical chunk content from the same document/page while preserving
        # genuinely different nearby chunks
        deduped: list[RetrievalResult] = []
        seen_keys: set[tuple[str, int | None, int | None, str]] = set()

        for r in raw_results:
            norm_text = re.sub(r"\s+", " ", r.text.strip().lower())
            key = (r.document_title.strip().lower(), r.page_number, r.slide_number, norm_text)
            if key in seen_keys:
                continue
            seen_keys.add(key)

            # Filter by relevance threshold
            if r.score >= threshold:
                deduped.append(r)
                if len(deduped) >= top_k:
                    break

        if not deduped:
            return (
                [],
                is_vector,
                "INSUFFICIENT_EVIDENCE",
                "No sufficiently relevant evidence was found in your uploaded learning materials.",
            )

        return deduped, is_vector, "SUCCESS", None
