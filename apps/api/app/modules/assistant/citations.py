import re
from typing import Any


class CitationValidator:
    """
    Validates and reconstructs citations against actual verified retrieved chunks.
    Ensures the model can never invent sources or cite non-existent documents.
    """

    @staticmethod
    def extract_and_validate(
        raw_citations: list[int | str],
        answer_text: str,
        retrieved_chunks: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], str]:
        """
        Validates citations against the retrieved chunk list:
        1. Identifies 1-indexed source indices (e.g. 1, 2, ... len(retrieved_chunks)).
        2. Discards any source IDs outside [1, len(retrieved_chunks)].
        3. Extracts any additional [1], [2] in answer text if raw_citations was incomplete.
        4. Reconstructs verified AssistantSource dictionaries with backend metadata.
        5. Repairs any malformed citation references in answer text.
        """
        max_idx = len(retrieved_chunks)
        if max_idx == 0:
            # If no chunks were retrieved, strip any fake citations from answer
            cleaned_answer = re.sub(r"\[(?:Source\s+)?\d+\]", "", answer_text)
            return [], cleaned_answer.strip()

        # Combine explicit citations from LLM with regex search in answer
        valid_indices: set[int] = set()
        for c in raw_citations:
            try:
                val = int(c)
                if 1 <= val <= max_idx:
                    valid_indices.add(val)
            except (ValueError, TypeError):
                continue

        # Also find [1], [Source 1], etc. in the text
        text_matches = re.findall(r"\[(?:Source\s+)?(\d+)\]", answer_text)
        for m in text_matches:
            try:
                val = int(m)
                if 1 <= val <= max_idx:
                    valid_indices.add(val)
            except ValueError:
                continue

        # If no citations were present in answer text but chunks were used, associate top chunk
        if not valid_indices and max_idx > 0:
            valid_indices.add(1)

        # Build verified source list in order of index
        verified_sources = []
        for idx in sorted(valid_indices):
            chunk = retrieved_chunks[idx - 1]
            doc_title = chunk.get("document_title", "Official Document")
            page_num = chunk.get("page_number")
            slide_num = chunk.get("slide_number")
            loc_str = f" — Page {page_num}" if page_num else (f" — Slide {slide_num}" if slide_num else "")
            citation_label = f"[{idx}] {doc_title}{loc_str}"

            verified_sources.append({
                "source_index": idx,
                "document_id": chunk.get("document_id"),
                "chunk_id": chunk.get("chunk_id"),
                "document_title": doc_title,
                "page_number": page_num,
                "slide_number": slide_num,
                "similarity_score": round(float(chunk.get("score", 0.0)), 4),
                "citation_label": citation_label,
                "snippet": chunk.get("text", "")[:200],
            })

        # Sanitize answer: replace any [Source 99] that does not exist
        def replace_cite(match):
            m_idx = int(match.group(1))
            if m_idx in valid_indices:
                return f"[{m_idx}]"
            return ""

        cleaned_answer = re.sub(r"\[(?:Source\s+)?(\d+)\]", replace_cite, answer_text)
        # Clean up possible double spaces created by removed citations
        cleaned_answer = re.sub(r" +", " ", cleaned_answer).strip()

        return verified_sources, cleaned_answer
