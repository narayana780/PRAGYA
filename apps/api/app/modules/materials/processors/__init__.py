from pathlib import Path

from app.core.exceptions import PragyaException
from app.modules.materials.processors.base import (
    DocumentContent,
    DocumentProcessor,
    ExtractedDocument,
)
from app.modules.materials.processors.pdf import PDFProcessor
from app.modules.materials.processors.pptx import PPTProcessor
from app.modules.materials.processors.txt import TXTProcessor

AVAILABLE_PROCESSORS: list[DocumentProcessor] = [
    PDFProcessor(),
    PPTProcessor(),
    TXTProcessor(),
]


def get_processor(mime_type: str, filename: str) -> DocumentProcessor:
    """Find appropriate processor for given mime type or filename extension."""
    ext = Path(filename).suffix.lower()
    for processor in AVAILABLE_PROCESSORS:
        if processor.supports(mime_type, ext):
            return processor

    raise PragyaException(
        message=f"Unsupported document format: {ext or mime_type}. Supported formats: PDF, PPT, PPTX, TXT.",
        status_code=400,
        error_code="UNSUPPORTED_FILE_TYPE",
    )


__all__ = [
    "DocumentContent",
    "DocumentProcessor",
    "ExtractedDocument",
    "PDFProcessor",
    "PPTProcessor",
    "TXTProcessor",
    "get_processor",
]
