"""create_assistant_tables

Revision ID: d9e3f1c2a5b6
Revises: e2a1b9d4c7f0
Create Date: 2026-09-12 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd9e3f1c2a5b6'
down_revision: Union[str, Sequence[str], None] = 'e2a1b9d4c7f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create assistant_conversations table
    op.create_table(
        'assistant_conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('context_type', sa.String(length=50), nullable=False, server_default='GENERAL_LEARNING'),
        sa.Column('course_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('learning_items.id', ondelete='SET NULL'), nullable=True),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='SET NULL'), nullable=True),
        sa.Column('competency_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('competencies.id', ondelete='SET NULL'), nullable=True),
        sa.Column('skill_gap_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('skill_gaps.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_assistant_conversations_employee_id', 'assistant_conversations', ['employee_id'])
    op.create_index('ix_assistant_conversations_created_at', 'assistant_conversations', ['created_at'])

    # 2. Create assistant_messages table
    op.create_table(
        'assistant_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('assistant_conversations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_assistant_messages_conversation_id', 'assistant_messages', ['conversation_id'])
    op.create_index('ix_assistant_messages_created_at', 'assistant_messages', ['created_at'])

    # 3. Create assistant_sources table
    op.create_table(
        'assistant_sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('message_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('assistant_messages.id', ondelete='CASCADE'), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('chunk_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('document_chunks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('slide_number', sa.Integer(), nullable=True),
        sa.Column('similarity_score', sa.Float(), nullable=False),
        sa.Column('citation_label', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_assistant_sources_message_id', 'assistant_sources', ['message_id'])
    op.create_index('ix_assistant_sources_document_id', 'assistant_sources', ['document_id'])
    op.create_index('ix_assistant_sources_chunk_id', 'assistant_sources', ['chunk_id'])


def downgrade() -> None:
    op.drop_table('assistant_sources')
    op.drop_table('assistant_messages')
    op.drop_table('assistant_conversations')
