"""create_quiz_tables

Revision ID: f3a4b5c6d7e8
Revises: d9e3f1c2a5b6
Create Date: 2026-09-12 19:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f3a4b5c6d7e8'
down_revision: Union[str, Sequence[str], None] = 'd9e3f1c2a5b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create quizzes table
    op.create_table(
        'quizzes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source_document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='SET NULL'), nullable=True),
        sa.Column('competency_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('competencies.id', ondelete='SET NULL'), nullable=True),
        sa.Column('question_count', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('difficulty', sa.String(length=50), nullable=False, server_default='BEGINNER'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='DRAFT'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_quizzes_employee_id', 'quizzes', ['employee_id'])
    op.create_index('ix_quizzes_source_document_id', 'quizzes', ['source_document_id'])
    op.create_index('ix_quizzes_competency_id', 'quizzes', ['competency_id'])

    # 2. Create quiz_questions table
    op.create_table(
        'quiz_questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('quiz_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('question_type', sa.String(length=50), nullable=False, server_default='MCQ_SINGLE'),
        sa.Column('difficulty', sa.String(length=50), nullable=False, server_default='BEGINNER'),
        sa.Column('bloom_level', sa.String(length=50), nullable=False, server_default='REMEMBER'),
        sa.Column('competency_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('competencies.id', ondelete='SET NULL'), nullable=True),
        sa.Column('source_document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_chunk_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('document_chunks.id', ondelete='SET NULL'), nullable=True),
        sa.Column('source_page_number', sa.Integer(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_quiz_questions_quiz_id', 'quiz_questions', ['quiz_id'])
    op.create_index('ix_quiz_questions_competency_id', 'quiz_questions', ['competency_id'])
    op.create_index('ix_quiz_questions_source_document_id', 'quiz_questions', ['source_document_id'])
    op.create_index('ix_quiz_questions_source_chunk_id', 'quiz_questions', ['source_chunk_id'])

    # 3. Create question_options table
    op.create_table(
        'question_options',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('quiz_questions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('option_text', sa.Text(), nullable=False),
        sa.Column('option_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_correct', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_question_options_question_id', 'question_options', ['question_id'])

    # 4. Create quiz_attempts table
    op.create_table(
        'quiz_attempts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('quiz_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('percentage', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='IN_PROGRESS'),
    )
    op.create_index('ix_quiz_attempts_quiz_id', 'quiz_attempts', ['quiz_id'])
    op.create_index('ix_quiz_attempts_employee_id', 'quiz_attempts', ['employee_id'])

    # 5. Create quiz_responses table
    op.create_table(
        'quiz_responses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('attempt_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('quiz_attempts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('quiz_questions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('selected_option_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('question_options.id', ondelete='CASCADE'), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('answered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_quiz_responses_attempt_id', 'quiz_responses', ['attempt_id'])
    op.create_index('ix_quiz_responses_question_id', 'quiz_responses', ['question_id'])
    op.create_index('ix_quiz_responses_selected_option_id', 'quiz_responses', ['selected_option_id'])


def downgrade() -> None:
    op.drop_table('quiz_responses')
    op.drop_table('quiz_attempts')
    op.drop_table('question_options')
    op.drop_table('quiz_questions')
    op.drop_table('quizzes')
