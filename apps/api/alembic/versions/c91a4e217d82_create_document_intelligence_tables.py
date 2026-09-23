"""create_document_intelligence_tables

Revision ID: c91a4e217d82
Revises: 4b20f7e49d10
Create Date: 2026-09-12 14:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c91a4e217d82'
down_revision: Union[str, Sequence[str], None] = '4b20f7e49d10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create uploaded_materials table
    op.create_table(
        'uploaded_materials',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('stored_filename', sa.String(length=255), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('checksum_sha256', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('storage_path', sa.String(length=512), nullable=False),
        sa.Column('error_code', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_uploaded_materials_employee_id'), 'uploaded_materials', ['employee_id'], unique=False)
    op.create_index(op.f('ix_uploaded_materials_checksum_sha256'), 'uploaded_materials', ['checksum_sha256'], unique=False)
    op.create_index('ix_uploaded_materials_emp_checksum', 'uploaded_materials', ['employee_id', 'checksum_sha256'], unique=False)

    # 2. Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('uploaded_material_id', sa.UUID(), nullable=False),
        sa.Column('document_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.Column('slide_count', sa.Integer(), nullable=True),
        sa.Column('language', sa.String(length=20), server_default='en', nullable=False),
        sa.Column('processing_version', sa.String(length=50), server_default='v1', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['uploaded_material_id'], ['uploaded_materials.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_uploaded_material_id'), 'documents', ['uploaded_material_id'], unique=False)

    # 3. Create document_chunks table
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('document_id', sa.UUID(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('slide_number', sa.Integer(), nullable=True),
        sa.Column('section_title', sa.String(length=255), nullable=True),
        sa.Column('token_count', sa.Integer(), nullable=True),
        sa.Column('competency_id', sa.UUID(), nullable=True),
        sa.Column('embedding', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['competency_id'], ['competencies.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_chunks_document_id'), 'document_chunks', ['document_id'], unique=False)
    op.create_index(op.f('ix_document_chunks_competency_id'), 'document_chunks', ['competency_id'], unique=False)
    op.create_index('ix_document_chunks_doc_chunk_idx', 'document_chunks', ['document_id', 'chunk_index'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_document_chunks_doc_chunk_idx', table_name='document_chunks')
    op.drop_index(op.f('ix_document_chunks_competency_id'), table_name='document_chunks')
    op.drop_index(op.f('ix_document_chunks_document_id'), table_name='document_chunks')
    op.drop_table('document_chunks')

    op.drop_index(op.f('ix_documents_uploaded_material_id'), table_name='documents')
    op.drop_table('documents')

    op.drop_index('ix_uploaded_materials_emp_checksum', table_name='uploaded_materials')
    op.drop_index(op.f('ix_uploaded_materials_checksum_sha256'), table_name='uploaded_materials')
    op.drop_index(op.f('ix_uploaded_materials_employee_id'), table_name='uploaded_materials')
    op.drop_table('uploaded_materials')
