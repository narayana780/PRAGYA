"""create_virtual_lab_tables

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-09-13 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create lab_datasets table
    op.create_table(
        'lab_datasets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('scenario_type', sa.String(length=100), nullable=False),
        sa.Column('schema_definition', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('dataset_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('row_count', sa.Integer(), nullable=False),
        sa.Column('is_synthetic', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_lab_datasets_scenario_type'), 'lab_datasets', ['scenario_type'], unique=False)

    # 2. Create lab_scenarios table
    op.create_table(
        'lab_scenarios',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('scenario_type', sa.String(length=100), nullable=False),
        sa.Column('competency_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('competencies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('difficulty', sa.String(length=50), nullable=False),
        sa.Column('estimated_minutes', sa.Integer(), server_default=sa.text('20'), nullable=False),
        sa.Column('learning_objectives', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('instructions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lab_datasets.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('status', sa.String(length=50), server_default=sa.text("'READY'"), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_lab_scenarios_competency_id'), 'lab_scenarios', ['competency_id'], unique=False)
    op.create_index(op.f('ix_lab_scenarios_dataset_id'), 'lab_scenarios', ['dataset_id'], unique=False)
    op.create_index(op.f('ix_lab_scenarios_scenario_type'), 'lab_scenarios', ['scenario_type'], unique=False)
    op.create_index(op.f('ix_lab_scenarios_status'), 'lab_scenarios', ['status'], unique=False)

    # 3. Create lab_sessions table
    op.create_table(
        'lab_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('scenario_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lab_scenarios.id', ondelete='CASCADE'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=50), server_default=sa.text("'IN_PROGRESS'"), nullable=False),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('percentage', sa.Float(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_lab_sessions_employee_id'), 'lab_sessions', ['employee_id'], unique=False)
    op.create_index(op.f('ix_lab_sessions_scenario_id'), 'lab_sessions', ['scenario_id'], unique=False)
    op.create_index(op.f('ix_lab_sessions_status'), 'lab_sessions', ['status'], unique=False)

    # 4. Create lab_actions table
    op.create_table(
        'lab_actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lab_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('step_number', sa.Integer(), nullable=False),
        sa.Column('action_type', sa.String(length=100), nullable=False),
        sa.Column('action_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('score_awarded', sa.Float(), nullable=False),
        sa.Column('feedback', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_lab_actions_session_id'), 'lab_actions', ['session_id'], unique=False)

    # 5. Create lab_results table
    op.create_table(
        'lab_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lab_sessions.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('total_score', sa.Float(), nullable=False),
        sa.Column('percentage', sa.Float(), nullable=False),
        sa.Column('passed', sa.Boolean(), nullable=False),
        sa.Column('competency_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('competencies.id', ondelete='SET NULL'), nullable=True),
        sa.Column('evidence_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('competency_evidence.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_lab_results_session_id'), 'lab_results', ['session_id'], unique=True)
    op.create_index(op.f('ix_lab_results_competency_id'), 'lab_results', ['competency_id'], unique=False)
    op.create_index(op.f('ix_lab_results_evidence_id'), 'lab_results', ['evidence_id'], unique=False)


def downgrade() -> None:
    op.drop_table('lab_results')
    op.drop_table('lab_actions')
    op.drop_table('lab_sessions')
    op.drop_table('lab_scenarios')
    op.drop_table('lab_datasets')
