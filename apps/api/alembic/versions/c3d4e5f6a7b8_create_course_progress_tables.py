"""create_course_progress_tables

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-09-14 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create course_progress table
    op.create_table(
        'course_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('learning_item_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('learning_items.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='NOT_STARTED'),
        sa.Column('progress_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('completed_modules', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('final_assessment_score', sa.Float(), nullable=True),
        sa.Column('final_assessment_passed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('enrolled_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('employee_id', 'learning_item_id', name='uq_employee_course_progress'),
    )
    op.create_index(op.f('ix_course_progress_employee_id'), 'course_progress', ['employee_id'], unique=False)
    op.create_index(op.f('ix_course_progress_learning_item_id'), 'course_progress', ['learning_item_id'], unique=False)
    op.create_index(op.f('ix_course_progress_status'), 'course_progress', ['status'], unique=False)

    # 2. Create course_resource_progress table
    op.create_table(
        'course_resource_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('learning_item_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('learning_items.id', ondelete='CASCADE'), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('resource_id', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('progress_seconds', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('duration_seconds', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('progress_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('employee_id', 'learning_item_id', 'module_id', 'resource_id', name='uq_emp_course_module_res'),
    )
    op.create_index(op.f('ix_course_resource_progress_employee_id'), 'course_resource_progress', ['employee_id'], unique=False)
    op.create_index(op.f('ix_course_resource_progress_learning_item_id'), 'course_resource_progress', ['learning_item_id'], unique=False)

    # 3. Create module_activity_attempts table
    op.create_table(
        'module_activity_attempts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('learning_item_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('learning_items.id', ondelete='CASCADE'), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('activity_type', sa.String(50), nullable=False),
        sa.Column('score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('max_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('passed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('submission_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('feedback_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('evidence_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('competency_evidence.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_module_activity_attempts_employee_id'), 'module_activity_attempts', ['employee_id'], unique=False)
    op.create_index(op.f('ix_module_activity_attempts_learning_item_id'), 'module_activity_attempts', ['learning_item_id'], unique=False)
    op.create_index(op.f('ix_module_activity_attempts_activity_type'), 'module_activity_attempts', ['activity_type'], unique=False)


def downgrade() -> None:
    op.drop_table('module_activity_attempts')
    op.drop_table('course_resource_progress')
    op.drop_table('course_progress')
