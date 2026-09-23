import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.modules.assistant.schemas import AssistantGroundingStatus


@pytest.mark.asyncio
async def test_assistant_api_conversations_flow():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # 1. Create a conversation
        create_res = await ac.post(
            "/api/v1/assistant/conversations",
            json={"title": "HTTP API Test Conversation", "context_type": "GENERAL_LEARNING"},
        )
        assert create_res.status_code == 201
        conv_data = create_res.json()
        assert "id" in conv_data
        conv_id = conv_data["id"]

        # 2. List conversations
        list_res = await ac.get("/api/v1/assistant/conversations")
        assert list_res.status_code == 200
        conversations = list_res.json()
        assert any(c["id"] == conv_id for c in conversations)

        # 3. Get specific conversation
        get_res = await ac.get(f"/api/v1/assistant/conversations/{conv_id}")
        assert get_res.status_code == 200
        assert get_res.json()["id"] == conv_id

        # 4. Send a message
        msg_res = await ac.post(
            f"/api/v1/assistant/conversations/{conv_id}/messages",
            json={"content": "What is stratified sampling?"},
        )
        assert msg_res.status_code == 200
        answer_data = msg_res.json()
        assert "answer" in answer_data
        assert "grounding_status" in answer_data
        assert "citations" in answer_data

        # 5. Get conversation messages
        msgs_res = await ac.get(f"/api/v1/assistant/conversations/{conv_id}/messages")
        assert msgs_res.status_code == 200
        msgs = msgs_res.json()
        assert len(msgs) >= 2  # user message and assistant message

        # 6. Stateless answer endpoint
        direct_res = await ac.post(
            "/api/v1/assistant/answer",
            json={"query": "Explain stratified sampling"},
        )
        assert direct_res.status_code == 200
        direct_data = direct_res.json()
        assert "answer" in direct_data

        # 7. Delete conversation (Strict 204 No Content)
        del_res = await ac.delete(f"/api/v1/assistant/conversations/{conv_id}")
        assert del_res.status_code == 204
        assert del_res.content == b""

        # Confirm 404 after deletion
        get_after_del = await ac.get(f"/api/v1/assistant/conversations/{conv_id}")
        assert get_after_del.status_code == 404

        # Confirm double-deletion returns 404
        del_again = await ac.delete(f"/api/v1/assistant/conversations/{conv_id}")
        assert del_again.status_code == 404


@pytest.mark.asyncio
async def test_assistant_api_cross_employee_security():
    other_emp_id = str(uuid.uuid4())
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Create as default employee
        res1 = await ac.post(
            "/api/v1/assistant/conversations",
            json={"title": "Private Chat"},
        )
        conv_id = res1.json()["id"]

        # Attempt access as other employee using X-Employee-Id header -> 404 Forbidden/NotFound
        unauth_res = await ac.get(
            f"/api/v1/assistant/conversations/{conv_id}",
            headers={"x-employee-id": other_emp_id},
        )
        assert unauth_res.status_code == 404

        # Attempt delete as unauthorized employee -> 404 Forbidden/NotFound
        unauth_del = await ac.delete(
            f"/api/v1/assistant/conversations/{conv_id}",
            headers={"x-employee-id": other_emp_id},
        )
        assert unauth_del.status_code == 404

        # Verify conversation still exists for the owner
        owner_res = await ac.get(f"/api/v1/assistant/conversations/{conv_id}")
        assert owner_res.status_code == 200

        # Clean up as owner -> 204 No Content
        owner_del = await ac.delete(f"/api/v1/assistant/conversations/{conv_id}")
        assert owner_del.status_code == 204


@pytest.mark.asyncio
async def test_assistant_api_cascade_deletion_and_no_orphans():
    from app.db.session import AsyncSessionLocal
    from app.modules.assistant.models import (
        AssistantConversation,
        AssistantMessage as AssistantMessageModel,
        AssistantSource,
    )
    from sqlalchemy import select

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # 1. Create conversation
        res = await ac.post(
            "/api/v1/assistant/conversations",
            json={"title": "Cascade Deletion Verification", "context_type": "GENERAL_LEARNING"},
        )
        assert res.status_code == 201
        conv_id = res.json()["id"]
        conv_uuid = uuid.UUID(conv_id)

        # 2. Send message so messages and citations are created
        msg_res = await ac.post(
            f"/api/v1/assistant/conversations/{conv_id}/messages",
            json={"content": "What is stratified sampling?"},
        )
        assert msg_res.status_code == 200

        # 3. Verify in DB that messages and sources exist
        async with AsyncSessionLocal() as db:
            m_res = await db.execute(
                select(AssistantMessageModel).where(
                    AssistantMessageModel.conversation_id == conv_uuid
                )
            )
            msgs = m_res.scalars().all()
            assert len(msgs) >= 2
            msg_ids = [m.id for m in msgs]

        # 4. Perform DELETE on conversation
        del_res = await ac.delete(f"/api/v1/assistant/conversations/{conv_id}")
        assert del_res.status_code == 204
        assert del_res.content == b""

        # 5. Verify conversation is completely removed from DB
        async with AsyncSessionLocal() as db:
            conv_db = (
                await db.execute(
                    select(AssistantConversation).where(AssistantConversation.id == conv_uuid)
                )
            ).scalar_one_or_none()
            assert conv_db is None

            # 6. Verify dependent messages are CASCADE removed (no orphan messages)
            remaining_msgs = (
                await db.execute(
                    select(AssistantMessageModel).where(
                        AssistantMessageModel.conversation_id == conv_uuid
                    )
                )
            ).scalars().all()
            assert len(remaining_msgs) == 0

            # 7. Verify dependent sources are CASCADE removed (no orphan sources)
            remaining_sources = (
                await db.execute(
                    select(AssistantSource).where(
                        AssistantSource.message_id.in_(msg_ids)
                    )
                )
            ).scalars().all()
            assert len(remaining_sources) == 0

            # 8. Verify globally 0 orphan messages and 0 orphan sources
            orphan_msgs = (
                await db.execute(
                    select(AssistantMessageModel).where(
                        AssistantMessageModel.conversation_id.not_in(
                            select(AssistantConversation.id)
                        )
                    )
                )
            ).scalars().all()
            assert len(orphan_msgs) == 0

            orphan_sources = (
                await db.execute(
                    select(AssistantSource).where(
                        AssistantSource.message_id.not_in(
                            select(AssistantMessageModel.id)
                        )
                    )
                )
            ).scalars().all()
            assert len(orphan_sources) == 0
