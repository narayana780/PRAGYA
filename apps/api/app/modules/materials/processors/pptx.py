import io
import re
from pathlib import Path
from typing import ClassVar

from pptx import Presentation

from app.core.logging import logger
from app.modules.materials.processors.base import (
    DocumentContent,
    DocumentProcessor,
    ExtractedDocument,
)


class PPTProcessor(DocumentProcessor):
    """Extracts text, slide numbers, and slide titles from PPT/PPTX files using python-pptx."""

    SUPPORTED_MIMES: ClassVar[set[str]] = {
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }
    SUPPORTED_EXTENSIONS: ClassVar[set[str]] = {".ppt", ".pptx"}

    def supports(self, mime_type: str, extension: str) -> bool:
        ext = extension.lower() if extension.startswith(".") else f".{extension.lower()}"
        return mime_type.lower() in self.SUPPORTED_MIMES or ext in self.SUPPORTED_EXTENSIONS

    def clean_text(self, text: str) -> str:
        """Clean extracted slide text."""
        if not text:
            return ""
        text = text.replace("\xa0", " ")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def extract(self, file_bytes: bytes, filename: str) -> ExtractedDocument:
        logger.info(f"Extracting PPT content from {filename} ({len(file_bytes)} bytes)")
        prs = Presentation(io.BytesIO(file_bytes))
        slide_count = len(prs.slides)
        ext = Path(filename).suffix.upper().replace(".", "") or "PPTX"
        title = Path(filename).stem

        contents: list[DocumentContent] = []
        for slide_idx, slide in enumerate(prs.slides):
            slide_num = slide_idx + 1
            slide_title = None
            slide_texts: list[str] = []

            # Check if slide has a title shape
            if slide.shapes.title and slide.shapes.title.text:
                slide_title = slide.shapes.title.text.strip()

            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text:
                    clean_shape_text = self.clean_text(shape.text)
                    if clean_shape_text and clean_shape_text != slide_title:
                        slide_texts.append(clean_shape_text)

            combined_text = "\n\n".join(slide_texts)
            if slide_title and not combined_text:
                combined_text = slide_title
            elif slide_title:
                combined_text = f"Title: {slide_title}\n\n{combined_text}"

            cleaned = self.clean_text(combined_text)
            if not cleaned:
                continue

            contents.append(
                DocumentContent(
                    text=cleaned,
                    page_number=None,
                    slide_number=slide_num,
                    section_title=slide_title,
                    metadata={
                        "slide_number": slide_num,
                        "total_slides": slide_count,
                    },
                )
            )

        return ExtractedDocument(
            document_type=ext if ext in ("PPT", "PPTX") else "PPTX",
            title=title,
            page_count=None,
            slide_count=slide_count,
            language="en",
            contents=contents,
            metadata={"total_slides": slide_count},
        )
