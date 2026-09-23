import re
import uuid
from dataclasses import dataclass, field
from typing import Any

from app.modules.materials.processors.base import DocumentContent, ExtractedDocument


@dataclass
class ProcessedChunk:
    """Internal chunk representation ready for embedding and database insertion."""
    chunk_index: int
    text: str
    page_number: int | None
    slide_number: int | None
    section_title: str | None
    token_count: int
    metadata: dict[str, Any] = field(default_factory=dict)


class TextChunker:
    """Configurable semantic text chunker targeting 400-700 tokens with 50-100 token overlap."""

    def __init__(
        self,
        min_tokens: int = 350,
        max_tokens: int = 700,
        overlap_tokens: int = 75,
    ):
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens

    def estimate_tokens(self, text: str) -> int:
        """Heuristic token estimation: ~4 chars per token, or words * 1.3."""
        if not text:
            return 0
        words = text.split()
        return max(len(words), int(len(text) / 4))

    def split_into_sentences(self, text: str) -> list[str]:
        """Split text by semantic sentence and paragraph boundaries."""
        # Split on double newline or sentence punctuation
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        units: list[str] = []
        for p in paragraphs:
            # Split paragraph into sentences
            sentences = re.split(r"(?<=[.!?])\s+", p)
            for s in sentences:
                s_clean = s.strip()
                if s_clean:
                    units.append(s_clean)
        return units if units else ([text.strip()] if text.strip() else [])

    def chunk_content_unit(
        self,
        content: DocumentContent,
        base_chunk_index: int,
        document_id: uuid.UUID,
        employee_id: uuid.UUID,
        document_type: str,
        language: str,
    ) -> tuple[list[ProcessedChunk], int]:
        """Chunk a single page or slide, preserving its specific page/slide boundaries."""
        text = content.text.strip()
        if not text:
            return [], base_chunk_index

        total_est_tokens = self.estimate_tokens(text)
        # If the page/slide is comfortably within chunk limit, keep it intact as one coherent chunk!
        if total_est_tokens <= self.max_tokens:
            chunk_metadata = {
                "document_id": str(document_id),
                "employee_id": str(employee_id),
                "chunk_index": base_chunk_index,
                "page": content.page_number,
                "slide": content.slide_number,
                "section": content.section_title,
                "document_type": document_type,
                "language": language,
                **content.metadata,
            }
            chunk = ProcessedChunk(
                chunk_index=base_chunk_index,
                text=text,
                page_number=content.page_number,
                slide_number=content.slide_number,
                section_title=content.section_title,
                token_count=total_est_tokens,
                metadata=chunk_metadata,
            )
            return [chunk], base_chunk_index + 1

        # Larger page/slide: split along semantic boundaries with overlap
        sentence_units = self.split_into_sentences(text)
        chunks: list[ProcessedChunk] = []
        current_sentences: list[str] = []
        current_tokens = 0
        current_idx = base_chunk_index

        for sentence in sentence_units:
            s_tokens = self.estimate_tokens(sentence)
            if current_tokens + s_tokens > self.max_tokens and current_sentences:
                # Emit chunk
                chunk_text = " ".join(current_sentences).strip()
                if self.estimate_tokens(chunk_text) >= 20:  # Avoid tiny fragments
                    chunk_meta = {
                        "document_id": str(document_id),
                        "employee_id": str(employee_id),
                        "chunk_index": current_idx,
                        "page": content.page_number,
                        "slide": content.slide_number,
                        "section": content.section_title,
                        "document_type": document_type,
                        "language": language,
                        **content.metadata,
                    }
                    chunks.append(
                        ProcessedChunk(
                            chunk_index=current_idx,
                            text=chunk_text,
                            page_number=content.page_number,
                            slide_number=content.slide_number,
                            section_title=content.section_title,
                            token_count=self.estimate_tokens(chunk_text),
                            metadata=chunk_meta,
                        )
                    )
                    current_idx += 1

                # Retain overlap sentences
                overlap_accum: list[str] = []
                overlap_count = 0
                for prev_s in reversed(current_sentences):
                    t_count = self.estimate_tokens(prev_s)
                    if overlap_count + t_count <= self.overlap_tokens:
                        overlap_accum.insert(0, prev_s)
                        overlap_count += t_count
                    else:
                        break
                current_sentences = overlap_accum
                current_tokens = overlap_count

            current_sentences.append(sentence)
            current_tokens += s_tokens

        # Emit remaining sentences if any
        if current_sentences:
            chunk_text = " ".join(current_sentences).strip()
            if self.estimate_tokens(chunk_text) >= 15:
                chunk_meta = {
                    "document_id": str(document_id),
                    "employee_id": str(employee_id),
                    "chunk_index": current_idx,
                    "page": content.page_number,
                    "slide": content.slide_number,
                    "section": content.section_title,
                    "document_type": document_type,
                    "language": language,
                    **content.metadata,
                }
                chunks.append(
                    ProcessedChunk(
                        chunk_index=current_idx,
                        text=chunk_text,
                        page_number=content.page_number,
                        slide_number=content.slide_number,
                        section_title=content.section_title,
                        token_count=self.estimate_tokens(chunk_text),
                        metadata=chunk_meta,
                    )
                )
                current_idx += 1

        return chunks, current_idx

    def chunk_document(
        self,
        extracted: ExtractedDocument,
        document_id: uuid.UUID,
        employee_id: uuid.UUID,
    ) -> list[ProcessedChunk]:
        """Chunk all contents of an extracted document sequentially."""
        all_chunks: list[ProcessedChunk] = []
        chunk_idx = 0
        for content in extracted.contents:
            sub_chunks, next_idx = self.chunk_content_unit(
                content=content,
                base_chunk_index=chunk_idx,
                document_id=document_id,
                employee_id=employee_id,
                document_type=extracted.document_type,
                language=extracted.language,
            )
            all_chunks.extend(sub_chunks)
            chunk_idx = next_idx

        return all_chunks
