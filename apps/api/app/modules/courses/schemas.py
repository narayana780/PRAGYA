"""PRAGYA Course Domain Pydantic Schemas"""
import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class ResourceProgressUpdateRequest(BaseModel):
    module_id: int = Field(..., ge=1, le=4)
    resource_type: str = Field(..., description="VIDEO or READING")
    progress_seconds: float = Field(default=0.0, ge=0.0)
    duration_seconds: float = Field(default=0.0, ge=0.0)
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    is_completed: bool = False


class ResourceProgressResponse(BaseModel):
    resource_id: str
    module_id: int
    resource_type: str
    progress_seconds: float
    duration_seconds: float
    progress_percentage: float
    is_completed: bool
    completed_at: datetime | None = None
    status: str = "NOT_STARTED"  # NOT_STARTED, LAUNCHED, IN_PROGRESS, COMPLETED
    verification_status: str = "NOT_VERIFIED"  # NOT_VERIFIED, PENDING, VERIFIED
    provider: str = "PRAGYA"


class ResourceLaunchResponse(BaseModel):
    resource_id: str
    status: str = "LAUNCHED"
    verification_status: str = "NOT_VERIFIED"
    provider: str = "iGOT"
    external_url: str | None = None
    message: str = "Resource launched on external learning provider."


class ProviderSyncResponse(BaseModel):
    resource_id: str | None = None
    provider: str = "iGOT"
    verified: bool = False
    reason: str = "IGOT_INTEGRATION_NOT_CONFIGURED"
    status: str = "NOT_VERIFIED"  # NOT_VERIFIED, IN_PROGRESS, COMPLETED
    completed_at: datetime | None = None
    message: str = "Official iGOT completion verification requires external provider API integration."



class KnowledgeCheckSubmitRequest(BaseModel):
    answers: dict[str, int] = Field(..., description="Mapping of question_id to selected_option_index")


class QuestionEvaluationResult(BaseModel):
    question_id: str
    selected_index: int
    correct_index: int
    is_correct: bool
    explanation: str


class KnowledgeCheckResultResponse(BaseModel):
    module_id: int
    total_questions: int
    correct_answers: int
    score: float
    percentage: float
    passed: bool
    pass_threshold: float
    question_results: list[QuestionEvaluationResult]
    module_completed: bool


class AssignmentSubmitRequest(BaseModel):
    sampling_method: str
    allocation_strategy: str
    non_response_buffer: str
    justification_code: str


class AssignmentResultResponse(BaseModel):
    module_id: int
    score: float
    max_score: float
    percentage: float
    passed: bool
    feedback: str
    rubric_breakdown: dict[str, Any]
    evidence_id: str | None = None
    module_completed: bool


class FinalAssessmentSubmitRequest(BaseModel):
    answers: dict[str, int] = Field(..., description="Mapping of question_id to selected_option_index")


class FinalAssessmentResultResponse(BaseModel):
    total_questions: int
    correct_answers: int
    score: float
    percentage: float
    passed: bool
    pass_threshold: float
    question_results: list[QuestionEvaluationResult]
    evidence_id: str | None = None


class CourseProgressResponse(BaseModel):
    learning_item_id: str
    employee_id: str
    status: str
    progress_percentage: float
    completed_modules: list[int]
    unlocked_modules: list[int]
    resource_progress: dict[str, dict[str, Any]]
    activities_status: dict[str, Any]
    is_lab_verified: bool
    final_assessment_passed: bool
    final_assessment_score: float | None = None
    course_completed: bool
    enrolled_at: datetime
    completed_at: datetime | None = None


class CourseCompleteResponse(BaseModel):
    success: bool
    message: str
    progress_percentage: float
    completed_at: datetime
    evidence_id: str | None = None


class RecalibrateCourseResponse(BaseModel):
    recalibrated: bool
    recalibrated_competencies: list[dict[str, Any]]
    message: str
