import abc
import os
import uuid
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import PragyaException
from app.core.logging import logger


class FileStorage(abc.ABC):
    """Abstract interface for storing and retrieving uploaded document binaries."""

    @abc.abstractmethod
    def save(self, content: bytes, original_filename: str) -> tuple[str, str]:
        """Save file content and return (stored_filename, storage_path)."""

    @abc.abstractmethod
    def open(self, storage_path: str) -> bytes:
        """Read and return binary file content from storage."""

    @abc.abstractmethod
    def delete(self, storage_path: str) -> bool:
        """Delete physical file from storage. Return True if deleted."""

    @abc.abstractmethod
    def exists(self, storage_path: str) -> bool:
        """Check if file exists at storage_path."""


class LocalFileStorage(FileStorage):
    """Local filesystem storage implementation with path traversal protection."""

    def __init__(self, base_dir: str | None = None):
        self.base_dir = Path(base_dir or settings.STORAGE_UPLOAD_DIR).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_safe_path(self, storage_path: str) -> Path:
        """Resolve path and verify it stays inside base_dir to prevent path traversal."""
        resolved = Path(storage_path).resolve()
        try:
            # Check if resolved is relative to base_dir
            resolved.relative_to(self.base_dir)
        except ValueError:
            logger.error(f"Path traversal attempt detected: {storage_path}")
            raise PragyaException(
                message="Invalid file storage path: Access denied.",
                status_code=400,
                error_code="INVALID_STORAGE_PATH",
            )
        return resolved

    def save(self, content: bytes, original_filename: str) -> tuple[str, str]:
        """Save content under a random UUID-based filename preserving sanitized extension."""
        ext = Path(original_filename).suffix.lower()
        # Enforce safe alphanumeric extension
        clean_ext = "".join(c for c in ext if c.isalnum() or c == ".")
        stored_filename = f"{uuid.uuid4().hex}{clean_ext}"
        target_path = self.base_dir / stored_filename

        with open(target_path, "wb") as f:
            f.write(content)

        return stored_filename, str(target_path)

    def open(self, storage_path: str) -> bytes:
        """Open and read file content safely."""
        safe_path = self._resolve_safe_path(storage_path)
        if not safe_path.is_file():
            raise PragyaException(
                message="Stored file not found on disk.",
                status_code=404,
                error_code="FILE_NOT_FOUND",
            )
        with open(safe_path, "rb") as f:
            return f.read()

    def delete(self, storage_path: str) -> bool:
        """Delete file safely from disk."""
        try:
            safe_path = self._resolve_safe_path(storage_path)
            if safe_path.is_file():
                os.remove(safe_path)
                return True
            return False
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Failed to delete file {storage_path}: {e}")
            return False

    def exists(self, storage_path: str) -> bool:
        """Check if file exists."""
        try:
            safe_path = self._resolve_safe_path(storage_path)
            return safe_path.is_file()
        except Exception:  # noqa: BLE001
            return False


# Default storage instance
default_storage: FileStorage = LocalFileStorage()
