import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.employees.service import EmployeeService
from app.modules.quizzes.generation_service import QuizGenerationService
from app.modules.quizzes.schemas import (
    AnswerResponse,
    QuizGenerateRequest,
    QuizAttemptItem,
    QuizDetail,
    QuizItem,
    QuizResultResponse,
    QuizReviewResponse,
    SubmitAnswerRequest,
)
from app.modules.quizzes.service import QuizService

router = APIRouter(prefix="", tags=["Quizzes"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_employee_id(
    db: DbSession,
    x_employee_id: Annotated[str | None, Header()] = None,
) -> uuid.UUID:
    """Resolve current authenticated employee context with X-Employee-Id override for tests."""
    if x_employee_id:
        try:
            return uuid.UUID(x_employee_id.strip())
        except ValueError:
            pass
    service = EmployeeService(db)
    me = await service.get_me()
    return me.id


CurrentEmployeeId = Annotated[uuid.UUID, Depends(get_current_employee_id)]



@router.post(
    "/quizzes/generate",
    response_model=QuizDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a source-grounded AI Quiz from learning material",
)
async def generate_quiz(
    req: QuizGenerateRequest,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> QuizDetail:
    gen_service = QuizGenerationService(db)
    quiz_obj = await gen_service.generate_quiz(employee_id, req)
    
    quiz_service = QuizService(db)
    return await quiz_service.get_quiz(employee_id, quiz_obj.id, include_correctness=True)


@router.get(
    "/quizzes",
    response_model=list[QuizItem],
    summary="List available AI quizzes for the employee",
)
async def list_quizzes(
    db: DbSession,
    employee_id: CurrentEmployeeId,
    limit: int = Query(default=50, ge=1, le=100),
) -> list[QuizItem]:
    service = QuizService(db)
    return await service.list_quizzes(employee_id, limit=limit)


@router.get(
    "/quizzes/{quiz_id}",
    response_model=QuizDetail,
    summary="Get quiz details and questions for active practice",
)
async def get_quiz(
    quiz_id: uuid.UUID,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> QuizDetail:
    service = QuizService(db)
    return await service.get_quiz(employee_id, quiz_id, include_correctness=False)


@router.post(
    "/quizzes/{quiz_id}/attempts",
    response_model=QuizAttemptItem,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new quiz attempt",
)
async def create_attempt(
    quiz_id: uuid.UUID,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> QuizAttemptItem:
    service = QuizService(db)
    return await service.create_attempt(employee_id, quiz_id)


@router.get(
    "/quizzes/{quiz_id}/attempts",
    response_model=list[QuizAttemptItem],
    summary="List attempts for a specific quiz",
)
async def list_quiz_attempts(
    quiz_id: uuid.UUID,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> list[QuizAttemptItem]:
    service = QuizService(db)
    return await service.list_attempts(employee_id, quiz_id=quiz_id)


@router.post(
    "/quiz-attempts/{attempt_id}/answers",
    response_model=AnswerResponse,
    summary="Submit an answer to a question with instant feedback & source explanation",
)
async def submit_answer(
    attempt_id: uuid.UUID,
    req: SubmitAnswerRequest,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> AnswerResponse:
    service = QuizService(db)
    return await service.submit_answer(employee_id, attempt_id, req)


@router.post(
    "/quiz-attempts/{attempt_id}/complete",
    response_model=QuizResultResponse,
    summary="Complete a quiz attempt, calculate score & record competency evidence",
)
async def complete_attempt(
    attempt_id: uuid.UUID,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> QuizResultResponse:
    service = QuizService(db)
    return await service.complete_attempt(employee_id, attempt_id)


@router.get(
    "/quiz-attempts/{attempt_id}/result",
    response_model=QuizResultResponse,
    summary="Get final score analytics for a completed quiz attempt",
)
async def get_attempt_result(
    attempt_id: uuid.UUID,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> QuizResultResponse:
    service = QuizService(db)
    return await service.get_result(employee_id, attempt_id)


@router.get(
    "/quiz-attempts/{attempt_id}/review",
    response_model=QuizReviewResponse,
    summary="Get question-by-question review with explanations & material citations",
)
async def get_attempt_review(
    attempt_id: uuid.UUID,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> QuizReviewResponse:
    service = QuizService(db)
    return await service.get_review(employee_id, attempt_id)
