import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

from app.modules.assistant.intents import AssistantIntent
from app.modules.assistant.level_selector import ExplanationLevel
from app.modules.assistant.models import (
    AssistantContextType,
    AssistantGroundingStatus,
    AssistantMessageRole,
)


class CreateConversationRequest(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    context_type: AssistantContextType = Field(default=AssistantContextType.GENERAL_LEARNING)
    course_id: uuid.UUID | None = None
    document_id: uuid.UUID | None = None
    competency_id: uuid.UUID | None = None
    skill_gap_id: uuid.UUID | None = None
    initial_query: str | None = None


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)
    document_id: uuid.UUID | None = None
    competency_id: uuid.UUID | None = None
    course_id: uuid.UUID | None = None
    skill_gap_id: uuid.UUID | None = None
    language: str = Field(default="en", max_length=10)


class StatelessAnswerRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    document_id: uuid.UUID | None = None
    competency_id: uuid.UUID | None = None
    language: str = Field(default="en", max_length=10)


class AssistantSourceItem(BaseModel):
    id: uuid.UUID
    message_id: uuid.UUID
    document_id: uuid.UUID
    chunk_id: uuid.UUID
    page_number: int | None = None
    slide_number: int | None = None
    similarity_score: float
    citation_label: str
    created_at: datetime
    document_title: str | None = None
    snippet: str | None = None


class AssistantMessageItem(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: AssistantMessageRole
    content: str
    created_at: datetime
    metadata: dict[str, Any] | None = None
    sources: list[AssistantSourceItem] = Field(default_factory=list)


class AssistantConversationItem(BaseModel):
    id: uuid.UUID
    employee_id: uuid.UUID
    title: str
    context_type: AssistantContextType
    course_id: uuid.UUID | None = None
    document_id: uuid.UUID | None = None
    competency_id: uuid.UUID | None = None
    skill_gap_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    last_message: AssistantMessageItem | None = None


class AssistantConversationDetail(AssistantConversationItem):
    messages: list[AssistantMessageItem] = Field(default_factory=list)


class AssistantResponse(BaseModel):
    conversation_id: uuid.UUID
    user_message: AssistantMessageItem
    assistant_message: AssistantMessageItem
    answer: str
    explanation: str | None = None
    example: str | None = None
    citations: list[AssistantSourceItem] = Field(default_factory=list)
    grounding_status: AssistantGroundingStatus
    retrieval_used: bool
    retrieval_count: int
    model: str
    context_type: AssistantContextType
    explanation_level: ExplanationLevel
    intent: AssistantIntent
