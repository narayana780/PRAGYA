from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class ProviderLearningItem(BaseModel):
    id: str
    provider: str
    provider_item_id: str
    title: str
    description: str
    type: str  # COURSE, PROGRAMME, LAB, PATH
    difficulty: str  # BEGINNER, INTERMEDIATE, ADVANCED
    level: int  # 1 to 5
    duration_minutes: int
    language: str
    format: str  # SELF_PACED, INSTRUCTOR_LED, BLENDED, INTERACTIVE_LAB
    url: str | None = None
    prerequisites: list[dict[str, Any]] = Field(default_factory=list)
    competencies: list[dict[str, Any]] = Field(default_factory=list)
    is_active: bool = True
    source_mode: str = "MOCK"
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProviderEnrollmentStatus(BaseModel):
    employee_id: str
    provider_item_id: str
    status: str  # NOT_ENROLLED, ENROLLED, IN_PROGRESS, COMPLETED
    enrolled_at: str | None = None
    progress_pct: float = 0.0


class ProviderCompletionStatus(BaseModel):
    employee_id: str
    provider_item_id: str
    is_completed: bool
    completed_at: str | None = None
    certificate_id: str | None = None
    score: float | None = None


class ProviderInfo(BaseModel):
    provider: str
    name: str
    mode: str  # MOCK or LIVE
    status: str  # AVAILABLE, DEGRADED, OFFLINE
    description: str
    catalogue_count: int = 0


class LearningProvider(ABC):
    @property
    @abstractmethod
    def provider_code(self) -> str:
        """Unique provider code: IGOT, NSSTA_TPAC, PRAGYA."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider display name."""

    @property
    @abstractmethod
    def source_mode(self) -> str:
        """Integration mode: MOCK or LIVE."""

    @abstractmethod
    async def search_learning_items(
        self,
        query: str | None = None,
        competency_ids: list[str] | None = None,
        difficulty: str | None = None,
        level: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ProviderLearningItem]:
        """Search learning items exposed by this provider."""

    @abstractmethod
    async def get_learning_item(self, provider_item_id: str) -> ProviderLearningItem | None:
        """Retrieve a specific learning item by provider item ID."""

    @abstractmethod
    async def get_learning_history(self, employee_id: str) -> list[ProviderCompletionStatus]:
        """Retrieve historical completions for an employee from this provider."""

    @abstractmethod
    async def get_enrollment_status(
        self, employee_id: str, provider_item_id: str
    ) -> ProviderEnrollmentStatus:
        """Check enrollment / progress status for an employee."""

    @abstractmethod
    async def get_completion_status(
        self, employee_id: str, provider_item_id: str
    ) -> ProviderCompletionStatus:
        """Check whether an employee has verified completion from this provider."""

    def get_info(self, catalogue_count: int = 0) -> ProviderInfo:
        """Return metadata describing provider status and mode."""
        return ProviderInfo(
            provider=self.provider_code,
            name=self.provider_name,
            mode=self.source_mode,
            status="AVAILABLE",
            description=f"{self.provider_name} ({self.source_mode} integration architecture)",
            catalogue_count=catalogue_count,
        )
