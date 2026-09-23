import abc
from dataclasses import dataclass, field
from typing import Any, AsyncIterator


@dataclass
class LLMMessage:
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMCitation:
    source_id: int
    quote: str | None = None


@dataclass
class LLMResponse:
    answer: str
    explanation: str | None = None
    example: str | None = None
    citations: list[int] = field(default_factory=list)  # 1-indexed source IDs
    model: str = "unknown"
    usage: dict[str, Any] = field(default_factory=dict)
    raw_output: str | None = None


class LLMProvider(abc.ABC):
    """Abstract interface for LLM providers."""

    @property
    @abc.abstractmethod
    def model_name(self) -> str:
        """Model identifier."""

    @abc.abstractmethod
    async def generate(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        context: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """Generate a grounded completion."""

    @abc.abstractmethod
    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        context: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        """Stream generation tokens."""

    @abc.abstractmethod
    async def health_check(self) -> bool:
        """Verify LLM provider availability."""
