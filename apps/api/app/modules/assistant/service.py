import time
import uuid
from typing import Any

from fastapi import status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.exceptions import PragyaException
from app.core.logging import logger
from app.modules.assistant.citations import CitationValidator
from app.modules.assistant.intents import AssistantIntent, IntentClassifier
from app.modules.assistant.level_selector import ExplanationLevel, ExplanationLevelSelector
from app.modules.assistant.llm.base import LLMProvider
from app.modules.assistant.llm.factory import get_llm_provider
from app.modules.assistant.models import (
    AssistantContextType,
    AssistantConversation,
    AssistantGroundingStatus,
    AssistantMessage,
    AssistantMessageRole,
    AssistantSource,
)
from app.modules.assistant.prompts import build_system_prompt
from app.modules.assistant.rag_service import AssistantRAGService
from app.modules.assistant.schemas import (
    AssistantConversationDetail,
    AssistantConversationItem,
    AssistantMessageItem,
    AssistantResponse,
    AssistantSourceItem,
    CreateConversationRequest,
    SendMessageRequest,
    StatelessAnswerRequest,
)
from app.modules.competencies.models import Competency
from app.modules.employees.models import Employee
from app.modules.skill_gaps.models import SkillGap


class AssistantService:
    def __init__(
        self,
        db: AsyncSession,
        rag_service: AssistantRAGService | None = None,
        llm_provider: LLMProvider | None = None,
    ):
        self.db = db
        self.rag_service = rag_service or AssistantRAGService(db)
        self.llm_provider = llm_provider or get_llm_provider()

    # ==================================================
    # CONVERSATION MANAGEMENT (CRUD)
    # ==================================================

    async def create_conversation(
        self, employee_id: uuid.UUID, req: CreateConversationRequest
    ) -> AssistantConversationItem:
        title = req.title or (
            req.initial_query[:50] + "..." if req.initial_query else "Learning Discussion"
        )
        conversation = AssistantConversation(
            employee_id=employee_id,
            title=title,
            context_type=req.context_type,
            course_id=req.course_id,
            document_id=req.document_id,
            competency_id=req.competency_id,
            skill_gap_id=req.skill_gap_id,
        )
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)

        return AssistantConversationItem(
            id=conversation.id,
            employee_id=conversation.employee_id,
            title=conversation.title,
            context_type=conversation.context_type,
            course_id=conversation.course_id,
            document_id=conversation.document_id,
            competency_id=conversation.competency_id,
            skill_gap_id=conversation.skill_gap_id,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            message_count=0,
            last_message=None,
        )

    async def get_conversations(
        self, employee_id: uuid.UUID, limit: int = 50
    ) -> list[AssistantConversationItem]:
        # Enforce employee ownership
        stmt = (
            select(AssistantConversation)
            .where(AssistantConversation.employee_id == employee_id)
            .order_by(desc(AssistantConversation.updated_at))
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        conversations = res.scalars().all()

        items = []
        for c in conversations:
            # Count messages
            count_stmt = select(func.count(AssistantMessage.id)).where(
                AssistantMessage.conversation_id == c.id
            )
            msg_count = (await self.db.execute(count_stmt)).scalar() or 0

            # Get last message
            last_stmt = (
                select(AssistantMessage)
                .where(AssistantMessage.conversation_id == c.id)
                .order_by(desc(AssistantMessage.created_at))
                .limit(1)
            )
            last_msg = (await self.db.execute(last_stmt)).scalar_one_or_none()

            last_msg_item = None
            if last_msg:
                last_msg_item = AssistantMessageItem(
                    id=last_msg.id,
                    conversation_id=last_msg.conversation_id,
                    role=last_msg.role,
                    content=last_msg.content,
                    created_at=last_msg.created_at,
                    metadata=last_msg.message_metadata,
                    sources=[],
                )

            items.append(
                AssistantConversationItem(
                    id=c.id,
                    employee_id=c.employee_id,
                    title=c.title,
                    context_type=c.context_type,
                    course_id=c.course_id,
                    document_id=c.document_id,
                    competency_id=c.competency_id,
                    skill_gap_id=c.skill_gap_id,
                    created_at=c.created_at,
                    updated_at=c.updated_at,
                    message_count=msg_count,
                    last_message=last_msg_item,
                )
            )
        return items

    async def get_conversation(
        self, employee_id: uuid.UUID, conversation_id: uuid.UUID
    ) -> AssistantConversationDetail:
        stmt = (
            select(AssistantConversation)
            .where(
                AssistantConversation.id == conversation_id,
                AssistantConversation.employee_id == employee_id,
            )
            .options(
                selectinload(AssistantConversation.messages).selectinload(AssistantMessage.sources)
            )
        )
        res = await self.db.execute(stmt)
        conversation = res.scalar_one_or_none()
        if not conversation:
            raise PragyaException(
                code="CONVERSATION_NOT_FOUND",
                message="Conversation not found or does not belong to the active employee.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        messages = [
            AssistantMessageItem(
                id=m.id,
                conversation_id=m.conversation_id,
                role=m.role,
                content=m.content,
                created_at=m.created_at,
                metadata=m.message_metadata,
                sources=[
                    AssistantSourceItem(
                        id=s.id,
                        message_id=s.message_id,
                        document_id=s.document_id,
                        chunk_id=s.chunk_id,
                        page_number=s.page_number,
                        slide_number=s.slide_number,
                        similarity_score=s.similarity_score,
                        citation_label=s.citation_label,
                        created_at=s.created_at,
                    )
                    for s in m.sources
                ],
            )
            for m in conversation.messages
        ]

        return AssistantConversationDetail(
            id=conversation.id,
            employee_id=conversation.employee_id,
            title=conversation.title,
            context_type=conversation.context_type,
            course_id=conversation.course_id,
            document_id=conversation.document_id,
            competency_id=conversation.competency_id,
            skill_gap_id=conversation.skill_gap_id,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            message_count=len(messages),
            messages=messages,
        )

    async def delete_conversation(
        self, employee_id: uuid.UUID, conversation_id: uuid.UUID
    ) -> bool:
        stmt = select(AssistantConversation).where(
            AssistantConversation.id == conversation_id,
            AssistantConversation.employee_id == employee_id,
        )
        conversation = (await self.db.execute(stmt)).scalar_one_or_none()
        if not conversation:
            raise PragyaException(
                code="CONVERSATION_NOT_FOUND",
                message="Conversation not found or access denied.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        await self.db.delete(conversation)
        await self.db.commit()
        return True

    async def get_messages(
        self,
        employee_id: uuid.UUID,
        conversation_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AssistantMessageItem]:
        conv_stmt = select(AssistantConversation).where(
            AssistantConversation.id == conversation_id,
            AssistantConversation.employee_id == employee_id,
        )
        conversation = (await self.db.execute(conv_stmt)).scalar_one_or_none()
        if not conversation:
            raise PragyaException(
                code="CONVERSATION_NOT_FOUND",
                message="Conversation not found or access denied.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        stmt = (
            select(AssistantMessage)
            .where(AssistantMessage.conversation_id == conversation_id)
            .options(selectinload(AssistantMessage.sources))
            .order_by(AssistantMessage.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        res = await self.db.execute(stmt)
        messages = res.scalars().all()
        return [self._msg_to_item(m) for m in messages]

    async def get_recent_conversation_messages(
        self,
        conversation_id: uuid.UUID,
        limit: int = 8,
    ) -> list[AssistantMessage]:
        stmt = (
            select(AssistantMessage)
            .where(AssistantMessage.conversation_id == conversation_id)
            .order_by(desc(AssistantMessage.created_at))
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(reversed(res.scalars().all()))

    def validate_response(
        self,
        raw_citations: list[Any],
        answer_text: str,
        retrieved_chunks: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], str]:
        return CitationValidator.extract_and_validate(raw_citations, answer_text, retrieved_chunks)

    async def store_sources(
        self,
        message_id: uuid.UUID,
        verified_sources: list[dict[str, Any]],
    ) -> list[AssistantSource]:
        sources_to_add = []
        for s in verified_sources:
            src = AssistantSource(
                message_id=message_id,
                document_id=uuid.UUID(str(s["document_id"])),
                chunk_id=uuid.UUID(str(s["chunk_id"])),
                page_number=s.get("page_number"),
                slide_number=s.get("slide_number"),
                similarity_score=s.get("similarity_score", 0.0),
                citation_label=s.get("citation_label", f"[{s.get('source_index', 1)}] Document"),
            )
            self.db.add(src)
            sources_to_add.append(src)
        await self.db.commit()
        return sources_to_add

    # ==================================================
    # CONTEXT & PEDAGOGICAL HELPERS
    # ==================================================

    async def build_learning_context(
        self,
        employee_id: uuid.UUID,
        competency_id: uuid.UUID | None = None,
        skill_gap_id: uuid.UUID | None = None,
    ) -> tuple[dict[str, Any], ExplanationLevel]:
        """
        Builds safe pedagogical context without leaking PII, credentials, or DB secrets.
        Determines the deterministic ExplanationLevel.
        """
        comp_info = {
            "role_name": "Statistical Officer",
            "competency_title": "Statistical Operations",
            "current_level": 1,
            "target_level": 3,
            "priority": "MEDIUM",
        }

        # 1. Fetch employee role
        emp = await self.db.get(Employee, employee_id)
        if emp and emp.designation:
            comp_info["role_name"] = emp.designation

        # 2. Check skill gap context if specified
        current_level = 1
        if skill_gap_id:
            sg = await self.db.get(SkillGap, skill_gap_id)
            if sg:
                current_level = int(sg.current_level)
                comp_info["current_level"] = current_level
                comp_info["target_level"] = int(sg.required_level)
                comp_info["priority"] = str(sg.priority_level)
                if sg.competency:
                    comp_info["competency_title"] = sg.competency.title

        # 3. Check direct competency context if specified
        elif competency_id:
            comp = await self.db.get(Competency, competency_id)
            if comp:
                comp_info["competency_title"] = comp.title

        level = ExplanationLevelSelector.select(current_level)
        return comp_info, level

    # ==================================================
    # CORE GROUNDED CONVERSATION PIPELINE
    # ==================================================

    async def send_message(
        self,
        employee_id: uuid.UUID,
        conversation_id: uuid.UUID,
        req: SendMessageRequest,
    ) -> AssistantResponse:
        t_start = time.perf_counter()

        # 1. Verify conversation ownership
        conv_stmt = select(AssistantConversation).where(
            AssistantConversation.id == conversation_id,
            AssistantConversation.employee_id == employee_id,
        )
        conversation = (await self.db.execute(conv_stmt)).scalar_one_or_none()
        if not conversation:
            raise PragyaException(
                code="CONVERSATION_NOT_FOUND",
                message="Conversation not found or unauthorized.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Update conversation title if default
        if conversation.title in ("New Conversation", "Learning Discussion", "New Learning Session") or (
            conversation.title and conversation.title.startswith("New ")
        ):
            conversation.title = req.content[:50].strip() + ("..." if len(req.content) > 50 else "")

        # 2. Save User Message
        user_msg = AssistantMessage(
            conversation_id=conversation.id,
            role=AssistantMessageRole.USER,
            content=req.content,
        )
        self.db.add(user_msg)
        await self.db.flush()

        # 3. Classify intent deterministically
        intent = IntentClassifier.classify(req.content)

        # 4. Resolve competency context & explanation level
        competency_id = req.competency_id or conversation.competency_id
        skill_gap_id = req.skill_gap_id or conversation.skill_gap_id
        document_id = req.document_id or conversation.document_id

        comp_info, explanation_level = await self.build_learning_context(
            employee_id=employee_id,
            competency_id=competency_id,
            skill_gap_id=skill_gap_id,
        )

        # 5. Retrieve Grounded Evidence via AssistantRAGService
        t_rag_start = time.perf_counter()
        retrieved_chunks, rag_status, rag_message = await self.rag_service.retrieve_context(
            employee_id=employee_id,
            query=req.content,
            document_id=document_id,
            competency_id=competency_id,
        )
        rag_latency = time.perf_counter() - t_rag_start

        # 6. CIRCUIT BREAKER: If retrieval returns INSUFFICIENT_EVIDENCE, STOP grounded LLM generation
        if rag_status == "INSUFFICIENT_EVIDENCE" or len(retrieved_chunks) == 0:
            safe_text = "I couldn't find enough evidence in your uploaded learning materials to answer this confidently."
            assistant_msg = AssistantMessage(
                conversation_id=conversation.id,
                role=AssistantMessageRole.ASSISTANT,
                content=safe_text,
                message_metadata={
                    "grounding_status": AssistantGroundingStatus.INSUFFICIENT_EVIDENCE,
                    "intent": intent,
                    "explanation_level": explanation_level,
                    "model": "none",
                    "retrieval_count": 0,
                    "rag_message": rag_message,
                },
            )
            self.db.add(assistant_msg)
            conversation.updated_at = func.now()
            await self.db.commit()
            await self.db.refresh(assistant_msg)

            return AssistantResponse(
                conversation_id=conversation.id,
                user_message=self._msg_to_item(user_msg),
                assistant_message=self._msg_to_item(assistant_msg),
                answer=safe_text,
                explanation=None,
                example=None,
                citations=[],
                grounding_status=AssistantGroundingStatus.INSUFFICIENT_EVIDENCE,
                retrieval_used=True,
                retrieval_count=0,
                model="none",
                context_type=conversation.context_type,
                explanation_level=explanation_level,
                intent=intent,
            )

        # 7. Build LLM messages & prompt injection defense
        context_block = self.rag_service.build_context_block(retrieved_chunks)
        system_prompt = build_system_prompt(
            intent=intent,
            explanation_level=explanation_level,
            competency_info=comp_info,
            language=req.language or "en",
        )

        # Context Window History: fetch last N messages (ASSISTANT_HISTORY_MESSAGES)
        history_limit = settings.ASSISTANT_HISTORY_MESSAGES
        hist_stmt = (
            select(AssistantMessage)
            .where(AssistantMessage.conversation_id == conversation.id)
            .order_by(desc(AssistantMessage.created_at))
            .limit(history_limit)
        )
        recent_msgs = list(reversed((await self.db.execute(hist_stmt)).scalars().all()))

        llm_messages = []
        for m in recent_msgs:
            role_str = "user" if m.role == AssistantMessageRole.USER else "assistant"
            llm_messages.append({"role": role_str, "content": m.content})

        # 8. Generate Structured Grounded Answer via LLMProvider
        t_llm_start = time.perf_counter()
        try:
            llm_resp = await self.llm_provider.generate(
                messages=llm_messages,
                system_prompt=system_prompt,
                context=context_block,
                max_tokens=settings.MAX_TOKENS_PER_REQUEST,
            )
            llm_latency = time.perf_counter() - t_llm_start
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            # Controlled fallback: "PRAGYA AI is temporarily unavailable."
            safe_text = "PRAGYA AI is temporarily unavailable."
            assistant_msg = AssistantMessage(
                conversation_id=conversation.id,
                role=AssistantMessageRole.ASSISTANT,
                content=safe_text,
                message_metadata={
                    "grounding_status": AssistantGroundingStatus.ERROR,
                    "error": "LLM_PROVIDER_UNAVAILABLE",
                },
            )
            self.db.add(assistant_msg)
            await self.db.commit()
            await self.db.refresh(assistant_msg)

            return AssistantResponse(
                conversation_id=conversation.id,
                user_message=self._msg_to_item(user_msg),
                assistant_message=self._msg_to_item(assistant_msg),
                answer=safe_text,
                citations=[],
                grounding_status=AssistantGroundingStatus.ERROR,
                retrieval_used=True,
                retrieval_count=len(retrieved_chunks),
                model=self.llm_provider.model_name,
                context_type=conversation.context_type,
                explanation_level=explanation_level,
                intent=intent,
            )

        # 9. Validate citations against actual retrieved evidence
        verified_sources_data, validated_answer = CitationValidator.extract_and_validate(
            raw_citations=llm_resp.citations,
            answer_text=llm_resp.answer,
            retrieved_chunks=retrieved_chunks,
        )

        grounding_status = (
            AssistantGroundingStatus.GROUNDED
            if verified_sources_data
            else AssistantGroundingStatus.PARTIALLY_GROUNDED
        )

        # 10. Store Assistant Message + Assistant Sources
        assistant_msg = AssistantMessage(
            conversation_id=conversation.id,
            role=AssistantMessageRole.ASSISTANT,
            content=validated_answer,
            message_metadata={
                "grounding_status": grounding_status,
                "intent": intent,
                "explanation_level": explanation_level,
                "model": llm_resp.model,
                "explanation": llm_resp.explanation,
                "example": llm_resp.example,
                "usage": llm_resp.usage,
                "rag_latency_ms": round(rag_latency * 1000, 2),
                "llm_latency_ms": round(llm_latency * 1000, 2),
                "total_latency_ms": round((time.perf_counter() - t_start) * 1000, 2),
            },
        )
        self.db.add(assistant_msg)
        await self.db.flush()

        # Attach sources
        saved_sources = []
        for s in verified_sources_data:
            src = AssistantSource(
                message_id=assistant_msg.id,
                document_id=uuid.UUID(str(s["document_id"])),
                chunk_id=uuid.UUID(str(s["chunk_id"])),
                page_number=s.get("page_number"),
                slide_number=s.get("slide_number"),
                similarity_score=s["similarity_score"],
                citation_label=s["citation_label"],
            )
            self.db.add(src)
            saved_sources.append(src)

        conversation.updated_at = func.now()
        await self.db.commit()
        await self.db.refresh(assistant_msg)

        # Format citation items for response
        citation_items = [
            AssistantSourceItem(
                id=s.id,
                message_id=s.message_id,
                document_id=s.document_id,
                chunk_id=s.chunk_id,
                page_number=s.page_number,
                slide_number=s.slide_number,
                similarity_score=s.similarity_score,
                citation_label=s.citation_label,
                created_at=s.created_at,
                document_title=data.get("document_title"),
                snippet=data.get("snippet"),
            )
            for s, data in zip(saved_sources, verified_sources_data)
        ]

        assistant_msg_item = self._msg_to_item(assistant_msg)
        assistant_msg_item.sources = citation_items

        return AssistantResponse(
            conversation_id=conversation.id,
            user_message=self._msg_to_item(user_msg),
            assistant_message=assistant_msg_item,
            answer=validated_answer,
            explanation=llm_resp.explanation,
            example=llm_resp.example,
            citations=citation_items,
            grounding_status=grounding_status,
            retrieval_used=True,
            retrieval_count=len(retrieved_chunks),
            model=llm_resp.model,
            context_type=conversation.context_type,
            explanation_level=explanation_level,
            intent=intent,
        )

    # ==================================================
    # STATELESS DIRECT ANSWER ENDPOINT
    # ==================================================

    async def stateless_answer(
        self, employee_id: uuid.UUID, req: StatelessAnswerRequest
    ) -> AssistantResponse:
        """Execute a one-off grounded answer without persisting a full conversation thread."""
        conv_req = CreateConversationRequest(
            title=req.query[:40],
            context_type=AssistantContextType.GENERAL_LEARNING,
            document_id=req.document_id,
            competency_id=req.competency_id,
        )
        conv = await self.create_conversation(employee_id, conv_req)
        send_req = SendMessageRequest(
            content=req.query,
            document_id=req.document_id,
            competency_id=req.competency_id,
            language=req.language,
        )
        return await self.send_message(employee_id, conv.id, send_req)

    def _msg_to_item(self, m: AssistantMessage) -> AssistantMessageItem:
        return AssistantMessageItem(
            id=m.id,
            conversation_id=m.conversation_id,
            role=m.role,
            content=m.content,
            created_at=m.created_at,
            metadata=m.message_metadata,
            sources=[],
        )
