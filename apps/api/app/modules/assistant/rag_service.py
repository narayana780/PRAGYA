import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.materials.service import MaterialService
from app.modules.assistant.prompts import format_retrieved_evidence


class AssistantRAGService:
    """
    RAG evidence retrieval bridge for PRAGYA AI Learning Assistant.
    Reuses existing MaterialService and PgVectorStore directly without duplicating vector logic.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.material_service = MaterialService(db)

    async def retrieve_context(
        self,
        employee_id: uuid.UUID,
        query: str,
        document_id: uuid.UUID | None = None,
        competency_id: uuid.UUID | None = None,
        top_k: int | None = None,
    ) -> tuple[list[dict[str, Any]], str, str | None]:
        """
        Retrieves grounded evidence chunks using Stage 8 PgVectorStore.
        Returns:
            - chunks: list of chunk dictionaries with scores, titles, text
            - status: "SUCCESS" or "INSUFFICIENT_EVIDENCE"
            - message: error or advisory message if any
        """
        k = top_k or settings.MAX_CONTEXT_CHUNKS

        results, is_vector, status, message = await self.material_service.retrieve_evidence(
            employee_id=employee_id,
            query=query,
            document_id=document_id,
            competency_id=competency_id,
            top_k=k,
            min_score=settings.MIN_RETRIEVAL_SCORE,
        )

        # Format chunks into dictionary representations
        chunks = []
        for r in results:
            chunks.append({
                "chunk_id": r.chunk_id,
                "document_id": r.document_id,
                "text": r.text,
                "score": r.score,
                "page_number": r.page_number,
                "slide_number": r.slide_number,
                "section_title": r.section_title,
                "document_title": r.document_title,
            })

        # Deduplicate identical chunks if any
        deduped = self.deduplicate_context(chunks)

        return deduped, status, message

    @staticmethod
    def deduplicate_context(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Deduplicate chunks based on document_id, page/slide, and text prefix."""
        seen = set()
        unique_chunks = []
        for c in chunks:
            sig = (
                str(c.get("document_id")),
                c.get("page_number"),
                c.get("slide_number"),
                c.get("text", "").strip()[:100].lower(),
            )
            if sig not in seen:
                seen.add(sig)
                unique_chunks.append(c)
        return unique_chunks

    @staticmethod
    def build_context_block(chunks: list[dict[str, Any]]) -> str:
        """Format chunks into untrusted reference text block for the LLM."""
        return format_retrieved_evidence(chunks)
