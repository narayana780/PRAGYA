"""create_adaptive_assessment_tables

Revision ID: a1b2c3d4e5f6
Revises: f3a4b5c6d7e8
Create Date: 2026-09-12 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f3a4b5c6d7e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create adaptive_assessment_sessions table
    op.create_table(
        'adaptive_assessment_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('competency_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('competencies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='SET NULL'), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('initial_level', sa.String(length=50), nullable=False),
        sa.Column('current_level', sa.String(length=50), nullable=False),
        sa.Column('question_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('correct_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('incorrect_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('status', sa.String(length=50), server_default='IN_PROGRESS', nullable=False),
        sa.Column('confidence', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_adaptive_assessment_sessions_employee_id'), 'adaptive_assessment_sessions', ['employee_id'], unique=False)
    op.create_index(op.f('ix_adaptive_assessment_sessions_competency_id'), 'adaptive_assessment_sessions', ['competency_id'], unique=False)
    op.create_index(op.f('ix_adaptive_assessment_sessions_source_document_id'), 'adaptive_assessment_sessions', ['source_document_id'], unique=False)
    op.create_index(op.f('ix_adaptive_assessment_sessions_status'), 'adaptive_assessment_sessions', ['status'], unique=False)

    # 2. Create adaptive_assessment_responses table
    op.create_table(
        'adaptive_assessment_responses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('adaptive_assessment_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('quiz_questions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('difficulty', sa.String(length=50), nullable=False),
        sa.Column('selected_option_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('question_options.id', ondelete='CASCADE'), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_adaptive_assessment_responses_session_id'), 'adaptive_assessment_responses', ['session_id'], unique=False)
    op.create_index(op.f('ix_adaptive_assessment_responses_question_id'), 'adaptive_assessment_responses', ['question_id'], unique=False)

    # 3. Create competency_recalibrations table
    op.create_table(
        'competency_recalibrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('competency_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('competencies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('previous_score', sa.Float(), nullable=False),
        sa.Column('new_score', sa.Float(), nullable=False),
        sa.Column('delta', sa.Float(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('evidence_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_competency_recalibrations_employee_id'), 'competency_recalibrations', ['employee_id'], unique=False)
    op.create_index(op.f('ix_competency_recalibrations_competency_id'), 'competency_recalibrations', ['competency_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_competency_recalibrations_competency_id'), table_name='competency_recalibrations')
    op.drop_index(op.f('ix_competency_recalibrations_employee_id'), table_name='competency_recalibrations')
    op.drop_table('competency_recalibrations')

    op.drop_index(op.f('ix_adaptive_assessment_responses_question_id'), table_name='adaptive_assessment_responses')
    op.drop_index(op.f('ix_adaptive_assessment_responses_session_id'), table_name='adaptive_assessment_responses')
    op.drop_table('adaptive_assessment_responses')

    op.drop_index(op.f('ix_adaptive_assessment_sessions_status'), table_name='adaptive_assessment_sessions')
    op.drop_index(op.f('ix_adaptive_assessment_sessions_source_document_id'), table_name='adaptive_assessment_sessions')
    op.drop_index(op.f('ix_adaptive_assessment_sessions_competency_id'), table_name='adaptive_assessment_sessions')
    op.drop_index(op.f('ix_adaptive_assessment_sessions_employee_id'), table_name='adaptive_assessment_sessions')
    op.drop_table('adaptive_assessment_sessions')
