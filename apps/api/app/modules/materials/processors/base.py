import abc
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DocumentContent:
    """Normalized content unit (page, slide, or text block)."""
    text: str
    page_number: int | None = None
    slide_number: int | None = None
    section_title: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractedDocument:
    """Full extracted document payload across any format."""
    document_type: str
    title: str
    page_count: int | None = None
    slide_count: int | None = None
    language: str = "en"
    contents: list[DocumentContent] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class DocumentProcessor(abc.ABC):
    """Abstract interface for format-specific text extraction."""

    @abc.abstractmethod
    def supports(self, mime_type: str, extension: str) -> bool:
        """Check if processor supports the given mime type or file extension."""

    @abc.abstractmethod
    def extract(self, file_bytes: bytes, filename: str) -> ExtractedDocument:
        """Extract text and structure into normalized document representations."""
