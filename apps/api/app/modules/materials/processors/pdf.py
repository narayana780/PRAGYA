import re
from pathlib import Path
from typing import ClassVar

import fitz  # PyMuPDF

from app.core.logging import logger
from app.modules.materials.processors.base import (
    DocumentContent,
    DocumentProcessor,
    ExtractedDocument,
)


class PDFProcessor(DocumentProcessor):
    """Extracts text, page numbers, and structural metadata from PDF files using PyMuPDF."""

    SUPPORTED_MIMES: ClassVar[set[str]] = {
        "application/pdf",
        "application/x-pdf",
    }
    SUPPORTED_EXTENSIONS: ClassVar[set[str]] = {".pdf"}

    def supports(self, mime_type: str, extension: str) -> bool:
        ext = extension.lower() if extension.startswith(".") else f".{extension.lower()}"
        return mime_type.lower() in self.SUPPORTED_MIMES or ext in self.SUPPORTED_EXTENSIONS

    def clean_text(self, text: str) -> str:
        """Clean obvious extraction artifacts while preserving mathematical notation and table structure."""
        if not text:
            return ""
        # Replace non-breaking spaces
        text = text.replace("\xa0", " ")
        # Replace multiple spaces with single space
        text = re.sub(r"[ \t]+", " ", text)
        # Collapse 3+ newlines to 2 newlines
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def extract(self, file_bytes: bytes, filename: str) -> ExtractedDocument:
        logger.info(f"Extracting PDF content from {filename} ({len(file_bytes)} bytes)")
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        page_count = len(doc)

        meta = doc.metadata or {}
        title = meta.get("title") or Path(filename).stem
        if not title.strip():
            title = Path(filename).stem

        contents: list[DocumentContent] = []
        for page_idx in range(page_count):
            page = doc[page_idx]
            page_num = page_idx + 1
            raw_text = page.get_text("text")
            cleaned = self.clean_text(raw_text)
            if not cleaned:
                continue

            # Detect potential section title from first line
            lines = [ln.strip() for ln in cleaned.split("\n") if ln.strip()]
            section_title = lines[0][:100] if lines and len(lines[0]) < 100 else None

            contents.append(
                DocumentContent(
                    text=cleaned,
                    page_number=page_num,
                    slide_number=None,
                    section_title=section_title,
                    metadata={
                        "page_number": page_num,
                        "total_pages": page_count,
                    },
                )
            )

        doc.close()
        return ExtractedDocument(
            document_type="PDF",
            title=title,
            page_count=page_count,
            slide_count=None,
            language="en",
            contents=contents,
            metadata={
                "author": meta.get("author"),
                "subject": meta.get("subject"),
                "creator": meta.get("creator"),
                "producer": meta.get("producer"),
            },
        )
