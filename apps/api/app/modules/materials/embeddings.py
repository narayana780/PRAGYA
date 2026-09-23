import abc
import hashlib
import math
import threading
from typing import Any

from app.core.config import settings
from app.core.logging import logger


class EmbeddingProvider(abc.ABC):
    """Abstract interface for text and batch embeddings."""

    @property
    @abc.abstractmethod
    def dimension(self) -> int:
        """Embedding dimension size."""

    @abc.abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """Generate embedding vector for a single text."""

    @abc.abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate normalized embedding vectors for a batch of texts in deterministic order."""

    def embed_chunks(self, chunks: list[Any]) -> list[list[float]]:
        """Batch embed document chunks in deterministic order."""
        if not chunks:
            return []
        texts = [chunk.text for chunk in chunks]
        return self.embed_batch(texts)


class MockEmbeddingProvider(EmbeddingProvider):
    """Deterministic hash-based embedding provider for testing and offline environments."""

    def __init__(self, dimension: int = 384):
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def _hash_vector(self, text: str) -> list[float]:
        """Create deterministic unit vector based on text token frequencies and hashes."""
        vec = [0.0] * self._dimension
        words = text.lower().split()
        for w in words:
            h = int(hashlib.sha256(w.encode("utf-8")).hexdigest(), 16)
            slot = h % self._dimension
            sign = 1.0 if (h // self._dimension) % 2 == 0 else -1.0
            vec[slot] += sign

        # Add positional component
        h_full = int(hashlib.md5(text.encode("utf-8", errors="ignore")).hexdigest(), 16)
        for i in range(min(16, self._dimension)):
            vec[i] += ((h_full >> (i * 4)) & 0xF) / 15.0

        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        else:
            vec[0] = 1.0
        return vec

    def embed_text(self, text: str) -> list[float]:
        return self._hash_vector(text)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self._hash_vector(t) for t in texts]


class LocalEmbeddingProvider(EmbeddingProvider):
    """Production multilingual Sentence Transformers embedding provider."""

    def __init__(self, model_name: str | None = None, local_files_only: bool = True):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.local_files_only = local_files_only
        self._model = None
        self._dimension = settings.EMBEDDING_DIMENSION
        self._lock = threading.Lock()

    def _get_model(self):
        if self._model is None:
            with self._lock:
                if self._model is None:
                    logger.info(f"Loading SentenceTransformer model locally: {self.model_name}")
                    try:
                        from sentence_transformers import SentenceTransformer

                        self._model = SentenceTransformer(
                            self.model_name,
                            local_files_only=self.local_files_only,
                        )
                        # Verify dimension
                        test_emb = self._model.encode("test", normalize_embeddings=True)
                        self._dimension = len(test_emb)
                        if self._dimension != 384:
                            raise ValueError(
                                f"Embedding dimension mismatch: expected 384, got {self._dimension}"
                            )
                        logger.info(
                            f"SentenceTransformer initialized locally. Dimension: {self._dimension}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to load SentenceTransformer locally ({e}). Offline local model required."
                        )
                        raise
        return self._model

    @property
    def dimension(self) -> int:
        if self._model is None:
            return self._dimension
        if isinstance(self._model, MockEmbeddingProvider):
            return self._model.dimension
        dim_func = getattr(
            self._model,
            "get_embedding_dimension",
            getattr(self._model, "get_sentence_embedding_dimension", lambda: self._dimension),
        )
        return dim_func()

    def embed_text(self, text: str) -> list[float]:
        model = self._get_model()
        if isinstance(model, MockEmbeddingProvider):
            return model.embed_text(text)
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        model = self._get_model()
        if isinstance(model, MockEmbeddingProvider):
            return model.embed_batch(texts)
        embeddings = model.encode(texts, batch_size=32, normalize_embeddings=True)
        return embeddings.tolist()


_cached_embedding_provider: EmbeddingProvider | None = None
_provider_lock = threading.Lock()


def get_embedding_provider(force_reload: bool = False) -> EmbeddingProvider:
    """Thread-safe singleton factory to get the application-scoped embedding provider."""
    global _cached_embedding_provider
    if _cached_embedding_provider is not None and not force_reload:
        return _cached_embedding_provider

    with _provider_lock:
        if _cached_embedding_provider is not None and not force_reload:
            return _cached_embedding_provider

        if settings.EMBEDDING_PROVIDER.lower() in ("mock", "hash", "mock_embedding"):
            provider = MockEmbeddingProvider(dimension=settings.EMBEDDING_DIMENSION)
        else:
            provider = LocalEmbeddingProvider(
                model_name=settings.EMBEDDING_MODEL,
                local_files_only=True,
            )
        _cached_embedding_provider = provider
        return _cached_embedding_provider
