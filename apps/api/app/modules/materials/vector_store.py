import abc
import math
import re
import uuid
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import delete, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.materials.models import (
    Document,
    DocumentChunk,
    MaterialStatus,
    UploadedMaterial,
)


@dataclass
class RetrievalResult:
    """Standardized retrieval search result across vector and fallback stores."""
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    text: str
    score: float
    page_number: int | None
    slide_number: int | None
    section_title: str | None
    document_title: str
    metadata: dict[str, Any] = field(default_factory=dict)


class VectorStore(abc.ABC):
    """Abstract vector storage and semantic retrieval interface."""

    @abc.abstractmethod
    def is_vector_supported(self) -> bool:
        """Return True if native pgvector storage and indexing is active."""

    @abc.abstractmethod
    async def add_chunks(
        self,
        document_id: uuid.UUID,
        chunks_data: list[dict[str, Any]],
    ) -> list[DocumentChunk]:
        """Insert or bulk update chunks and their embeddings."""

    @abc.abstractmethod
    async def search(
        self,
        query_embedding: list[float],
        query_text: str,
        employee_id: uuid.UUID,
        top_k: int = 5,
        document_id: uuid.UUID | None = None,
        competency_id: uuid.UUID | None = None,
    ) -> list[RetrievalResult]:
        """Retrieve top_k semantic matches strictly isolated to employee_id."""

    @abc.abstractmethod
    async def delete_document(self, document_id: uuid.UUID) -> int:
        """Delete all chunks belonging to a document."""

    @abc.abstractmethod
    async def delete_chunks(self, chunk_ids: list[uuid.UUID]) -> int:
        """Delete specific chunk IDs."""


class PgVectorStore(VectorStore):
    """Native PostgreSQL + pgvector store utilizing vector similarity search."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def is_vector_supported(self) -> bool:
        return True

    async def add_chunks(
        self,
        document_id: uuid.UUID,
        chunks_data: list[dict[str, Any]],
    ) -> list[DocumentChunk]:
        created: list[DocumentChunk] = []
        for d in chunks_data:
            chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=d["chunk_index"],
                text=d["text"],
                page_number=d.get("page_number"),
                slide_number=d.get("slide_number"),
                section_title=d.get("section_title"),
                token_count=d.get("token_count"),
                competency_id=d.get("competency_id"),
                embedding=d.get("embedding"),
                chunk_metadata=d.get("metadata", {}),
            )
            self.db.add(chunk)
            created.append(chunk)
        await self.db.flush()
        return created

    async def search(
        self,
        query_embedding: list[float],
        query_text: str,
        employee_id: uuid.UUID,
        top_k: int = 5,
        document_id: uuid.UUID | None = None,
        competency_id: uuid.UUID | None = None,
    ) -> list[RetrievalResult]:
        """
        Execute native PostgreSQL pgvector cosine distance search with employee isolation.
        
        Scoring convention:
          - pgvector operator `<=>` computes Cosine Distance d in [0, 2].
          - Cosine Similarity score s = 1.0 - d in [-1.0, 1.0], where 1.0 indicates identical direction.
          - Score is rounded to 4 decimal places.
        """
        if not query_embedding:
            return []

        # Cosine distance operator (<=>) via pgvector.sqlalchemy
        distance_expr = DocumentChunk.embedding.cosine_distance(query_embedding).label("distance")

        stmt = (
            select(
                DocumentChunk,
                Document.title.label("document_title"),
                distance_expr,
            )
            .join(Document, Document.id == DocumentChunk.document_id)
            .join(UploadedMaterial, UploadedMaterial.id == Document.uploaded_material_id)
            .where(
                UploadedMaterial.employee_id == employee_id,
                UploadedMaterial.status == MaterialStatus.PROCESSED,
                DocumentChunk.embedding.isnot(None),
            )
        )

        if document_id:
            stmt = stmt.where(
                or_(
                    DocumentChunk.document_id == document_id,
                    Document.uploaded_material_id == document_id,
                )
            )
        if competency_id:
            stmt = stmt.where(DocumentChunk.competency_id == competency_id)

        stmt = stmt.order_by(distance_expr.asc()).limit(top_k)
        res = await self.db.execute(stmt)
        rows = res.all()

        results: list[RetrievalResult] = []
        for chunk, doc_title, distance in rows:
            # Distance d in [0, 2]; Similarity score s = 1.0 - d in [-1, 1]
            similarity = 1.0 - float(distance) if distance is not None else 0.0
            results.append(
                RetrievalResult(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    text=chunk.text,
                    score=round(float(similarity), 4),
                    page_number=chunk.page_number,
                    slide_number=chunk.slide_number,
                    section_title=chunk.section_title,
                    document_title=doc_title,
                    metadata=chunk.chunk_metadata,
                )
            )
        return results

    async def delete_document(self, document_id: uuid.UUID) -> int:
        stmt = delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
        res = await self.db.execute(stmt)
        return res.rowcount or 0

    async def delete_chunks(self, chunk_ids: list[uuid.UUID]) -> int:
        if not chunk_ids:
            return 0
        stmt = delete(DocumentChunk).where(DocumentChunk.id.in_(chunk_ids))
        res = await self.db.execute(stmt)
        return res.rowcount or 0


class DevelopmentLexicalStore(VectorStore):
    """
    Explicit fallback store for environments where PostgreSQL native pgvector extension
    is not installed (e.g. Windows PostgreSQL 18.6).
    Computes exact cosine similarity over stored chunk embedding vectors in Python,
    with keyword ranking assistance, while strictly maintaining employee isolation.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    def is_vector_supported(self) -> bool:
        # Explicitly signals fallback mode
        return False

    async def add_chunks(
        self,
        document_id: uuid.UUID,
        chunks_data: list[dict[str, Any]],
    ) -> list[DocumentChunk]:
        created: list[DocumentChunk] = []
        for d in chunks_data:
            chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=d["chunk_index"],
                text=d["text"],
                page_number=d.get("page_number"),
                slide_number=d.get("slide_number"),
                section_title=d.get("section_title"),
                token_count=d.get("token_count"),
                competency_id=d.get("competency_id"),
                embedding=d.get("embedding"),
                chunk_metadata=d.get("metadata", {}),
            )
            self.db.add(chunk)
            created.append(chunk)
        await self.db.flush()
        return created

    def _cosine_similarity(self, vec_a: list[float], vec_b: list[float]) -> float:
        """Compute cosine similarity between two float vectors."""
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a, b in zip(vec_a, vec_b)))
        norm_b = math.sqrt(sum(b * b for a, b in zip(vec_a, vec_b)))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    async def search(
        self,
        query_embedding: list[float],
        query_text: str,
        employee_id: uuid.UUID,
        top_k: int = 5,
        document_id: uuid.UUID | None = None,
        competency_id: uuid.UUID | None = None,
    ) -> list[RetrievalResult]:
        """
        Execute search strictly filtered to employee_id.
        Computes cosine similarity in Python over stored embeddings.
        """
        # Join with UploadedMaterial to enforce employee ownership
        stmt = (
            select(DocumentChunk, Document.title.label("document_title"))
            .join(Document, Document.id == DocumentChunk.document_id)
            .join(UploadedMaterial, UploadedMaterial.id == Document.uploaded_material_id)
            .where(
                UploadedMaterial.employee_id == employee_id,
                UploadedMaterial.status == "PROCESSED",
            )
        )

        if document_id:
            stmt = stmt.where(
                or_(
                    DocumentChunk.document_id == document_id,
                    Document.uploaded_material_id == document_id,
                )
            )
        if competency_id:
            stmt = stmt.where(DocumentChunk.competency_id == competency_id)

        res = await self.db.execute(stmt)
        rows = res.all()

        scored: list[tuple[float, DocumentChunk, str]] = []
        query_words = set(re.findall(r"\w+", query_text.lower())) if "re" in globals() else set(query_text.lower().split())

        for chunk, doc_title in rows:
            sim = 0.0
            if chunk.embedding and query_embedding:
                # Cosine similarity over vector embeddings
                sim = self._cosine_similarity(query_embedding, chunk.embedding)
            else:
                # Lexical word overlap fallback if no embeddings
                chunk_words = set(chunk.text.lower().split())
                overlap = len(query_words & chunk_words)
                sim = min(1.0, overlap / max(1, len(query_words)))

            # Small boost for title/section match
            if chunk.section_title and any(w in chunk.section_title.lower() for w in query_words):
                sim = min(1.0, sim + 0.05)

            scored.append((sim, chunk, doc_title))

        # Sort descending by similarity
        scored.sort(key=lambda x: x[0], reverse=True)
        top_matches = scored[:top_k]

        results: list[RetrievalResult] = []
        for sim, chunk, doc_title in top_matches:
            results.append(
                RetrievalResult(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    text=chunk.text,
                    score=round(float(sim), 4),
                    page_number=chunk.page_number,
                    slide_number=chunk.slide_number,
                    section_title=chunk.section_title,
                    document_title=doc_title,
                    metadata=chunk.chunk_metadata,
                )
            )
        return results

    async def delete_document(self, document_id: uuid.UUID) -> int:
        stmt = delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
        res = await self.db.execute(stmt)
        return res.rowcount or 0

    async def delete_chunks(self, chunk_ids: list[uuid.UUID]) -> int:
        if not chunk_ids:
            return 0
        stmt = delete(DocumentChunk).where(DocumentChunk.id.in_(chunk_ids))
        res = await self.db.execute(stmt)
        return res.rowcount or 0


def get_vector_store(db: AsyncSession) -> VectorStore:
    """
    Factory returning VectorStore based on configuration.
    Returns PgVectorStore when VECTOR_BACKEND == 'pgvector' (default).
    Falls back to DevelopmentLexicalStore when explicitly configured or in fallback mode.
    """
    backend = getattr(settings, "VECTOR_BACKEND", "pgvector").lower()
    if backend == "pgvector":
        return PgVectorStore(db)
    return DevelopmentLexicalStore(db)
