import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.assistant.schemas import (
    AssistantConversationDetail,
    AssistantConversationItem,
    AssistantMessageItem,
    AssistantResponse,
    CreateConversationRequest,
    SendMessageRequest,
    StatelessAnswerRequest,
)
from app.modules.assistant.service import AssistantService
from app.modules.employees.service import EmployeeService

router = APIRouter(prefix="/assistant", tags=["PRAGYA AI Learning Assistant"])
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
    "/conversations",
    response_model=AssistantConversationItem,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new learning assistant conversation",
)
async def create_conversation(
    req: CreateConversationRequest,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> AssistantConversationItem:
    service = AssistantService(db)
    return await service.create_conversation(employee_id, req)


@router.get(
    "/conversations",
    response_model=list[AssistantConversationItem],
    summary="List learning assistant conversations for the current employee",
)
async def get_conversations(
    db: DbSession,
    employee_id: CurrentEmployeeId,
    limit: int = Query(default=50, ge=1, le=100),
) -> list[AssistantConversationItem]:
    service = AssistantService(db)
    return await service.get_conversations(employee_id, limit=limit)


@router.get(
    "/conversations/{conversation_id}",
    response_model=AssistantConversationDetail,
    summary="Get conversation detail with all messages and citations",
)
async def get_conversation(
    conversation_id: uuid.UUID,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> AssistantConversationDetail:
    service = AssistantService(db)
    return await service.get_conversation(employee_id, conversation_id)


@router.delete(
    "/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a learning assistant conversation",
)
async def delete_conversation(
    conversation_id: uuid.UUID,
    db: DbSession,
    employee_id: CurrentEmployeeId,
):
    service = AssistantService(db)
    await service.delete_conversation(employee_id, conversation_id)


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[AssistantMessageItem],
    summary="Get message history for a specific conversation",
)
async def get_messages(
    conversation_id: uuid.UUID,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> list[AssistantMessageItem]:
    service = AssistantService(db)
    detail = await service.get_conversation(employee_id, conversation_id)
    return detail.messages


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=AssistantResponse,
    summary="Send a learning inquiry and receive a source-grounded response",
)
async def send_message(
    conversation_id: uuid.UUID,
    req: SendMessageRequest,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> AssistantResponse:
    service = AssistantService(db)
    return await service.send_message(employee_id, conversation_id, req)


@router.post(
    "/answer",
    response_model=AssistantResponse,
    summary="Stateless direct grounded answer query",
)
async def stateless_answer(
    req: StatelessAnswerRequest,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> AssistantResponse:
    service = AssistantService(db)
    return await service.stateless_answer(employee_id, req)
