import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class QuestionOptionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    question_id: uuid.UUID
    option_text: str
    option_order: int
    is_correct: bool | None = None  # Hidden during student quiz attempt


class QuizQuestionItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    quiz_id: uuid.UUID
    question_text: str
    question_type: str = "MCQ_SINGLE"
    difficulty: str = "BEGINNER"
    bloom_level: str = "REMEMBER"
    competency_id: uuid.UUID | None = None
    source_document_id: uuid.UUID
    source_chunk_id: uuid.UUID | None = None
    source_page_number: int | None = None
    explanation: str
    options: list[QuestionOptionSchema] = Field(default_factory=list)
    document_title: str | None = None
    competency_name: str | None = None


class QuizItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID | None = None
    title: str
    description: str | None = None
    source_document_id: uuid.UUID | None = None
    competency_id: uuid.UUID | None = None
    question_count: int
    difficulty: str
    status: str
    created_at: datetime
    updated_at: datetime
    document_title: str | None = None
    competency_name: str | None = None


class QuizDetail(QuizItem):
    questions: list[QuizQuestionItem] = Field(default_factory=list)


class QuizGenerateRequest(BaseModel):
    document_id: uuid.UUID | None = None
    material_id: uuid.UUID | None = None
    competency_id: uuid.UUID | None = None
    difficulty: str = "BEGINNER"  # BEGINNER, INTERMEDIATE, ADVANCED
    question_count: int = Field(default=5, ge=1, le=20)
    bloom_level: str | None = None  # REMEMBER, UNDERSTAND, APPLY, ANALYZE


class QuizAttemptItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    quiz_id: uuid.UUID
    employee_id: uuid.UUID
    started_at: datetime
    completed_at: datetime | None = None
    score: float | None = None
    percentage: float | None = None
    status: str
    quiz_title: str | None = None


class SubmitAnswerRequest(BaseModel):
    question_id: uuid.UUID
    selected_option_id: uuid.UUID


class CitationDetail(BaseModel):
    document_title: str | None = None
    page_number: int | None = None


class AnswerResponse(BaseModel):
    response_id: uuid.UUID
    question_id: uuid.UUID
    selected_option_id: uuid.UUID
    is_correct: bool
    correct_option_id: uuid.UUID
    explanation: str
    citation: CitationDetail | None = None


class QuizResultResponse(BaseModel):
    attempt_id: uuid.UUID
    quiz_id: uuid.UUID
    score: float
    total_questions: int
    percentage: float
    completed_at: datetime
    competencies_tested: list[str] = Field(default_factory=list)
    difficulty_distribution: dict[str, int] = Field(default_factory=dict)


class QuizReviewItem(BaseModel):
    question_id: uuid.UUID
    question_text: str
    selected_option_id: uuid.UUID
    correct_option_id: uuid.UUID
    is_correct: bool
    options: list[QuestionOptionSchema] = Field(default_factory=list)
    explanation: str
    source_document_title: str | None = None
    source_page_number: int | None = None


class QuizReviewResponse(BaseModel):
    attempt_id: uuid.UUID
    quiz_id: uuid.UUID
    score: float
    percentage: float
    items: list[QuizReviewItem] = Field(default_factory=list)
