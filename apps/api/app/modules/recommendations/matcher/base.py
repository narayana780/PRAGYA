from abc import ABC, abstractmethod


class SemanticMatcher(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Generate numerical vector embedding for text."""

    @abstractmethod
    def similarity(self, text1: str, text2: str) -> float:
        """Compute semantic similarity score between two texts (0.0 to 1.0)."""

    @abstractmethod
    def match_competency(
        self,
        item_title: str,
        item_description: str,
        competency_name: str,
        competency_description: str | None = None,
    ) -> float:
        """Calculate semantic / lexical alignment between a learning item and a competency (0.0 to 1.0)."""
