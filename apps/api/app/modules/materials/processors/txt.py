import re
from pathlib import Path
from typing import ClassVar

from app.core.exceptions import PragyaException
from app.core.logging import logger
from app.modules.materials.processors.base import (
    DocumentContent,
    DocumentProcessor,
    ExtractedDocument,
)


class TXTProcessor(DocumentProcessor):
    """Extracts text from plain text files with safe explicit encoding handling."""

    SUPPORTED_MIMES: ClassVar[set[str]] = {
        "text/plain",
        "text/markdown",
        "text/x-markdown",
        "text/csv",
    }
    SUPPORTED_EXTENSIONS: ClassVar[set[str]] = {".txt", ".md", ".csv"}

    def supports(self, mime_type: str, extension: str) -> bool:
        ext = extension.lower() if extension.startswith(".") else f".{extension.lower()}"
        return mime_type.lower() in self.SUPPORTED_MIMES or ext in self.SUPPORTED_EXTENSIONS

    def clean_text(self, text: str) -> str:
        """Clean empty lines and excessive whitespace."""
        if not text:
            return ""
        text = text.replace("\xa0", " ")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def decode_bytes(self, file_bytes: bytes) -> str:
        """Decode bytes trying UTF-8 first, then fallback encodings safely."""
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
        for enc in encodings:
            try:
                return file_bytes.decode(enc)
            except UnicodeDecodeError:
                continue
        raise PragyaException(
            message="Unable to decode text file. File must be UTF-8 or standard ASCII encoded.",
            status_code=400,
            error_code="UNSUPPORTED_ENCODING",
        )

    def extract(self, file_bytes: bytes, filename: str) -> ExtractedDocument:
        logger.info(f"Extracting TXT content from {filename} ({len(file_bytes)} bytes)")
        raw_text = self.decode_bytes(file_bytes)
        cleaned = self.clean_text(raw_text)
        title = Path(filename).stem

        # Divide large plain text files by logical double-newline paragraphs or sections
        paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [cleaned] if cleaned else []

        contents: list[DocumentContent] = []
        # Group into ~1-2 page equivalent logical blocks if needed, or paragraphs
        for idx, para in enumerate(paragraphs):
            lines = [ln.strip() for ln in para.split("\n") if ln.strip()]
            section_title = lines[0][:80] if lines and len(lines[0]) < 80 and lines[0].startswith(("#", "Chapter", "Section", "1", "2", "3", "4", "5", "6", "7", "8", "9")) else None

            contents.append(
                DocumentContent(
                    text=para,
                    page_number=idx + 1,  # Section/paragraph block as virtual page
                    slide_number=None,
                    section_title=section_title,
                    metadata={"block_index": idx},
                )
            )

        return ExtractedDocument(
            document_type="TXT",
            title=title,
            page_count=len(contents),
            slide_count=None,
            language="en",
            contents=contents,
            metadata={"paragraphs_count": len(contents)},
        )
