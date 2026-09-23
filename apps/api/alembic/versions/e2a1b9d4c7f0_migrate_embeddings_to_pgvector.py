"""migrate_embeddings_to_pgvector

Revision ID: e2a1b9d4c7f0
Revises: c91a4e217d82
Create Date: 2026-09-12 16:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = 'e2a1b9d4c7f0'
down_revision: Union[str, Sequence[str], None] = 'c91a4e217d82'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Ensure the vector extension is enabled in PostgreSQL
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Safely convert document_chunks.embedding from JSONB to vector(384)
    # preserving all existing data and document metadata
    op.execute("""
        ALTER TABLE document_chunks
        ALTER COLUMN embedding TYPE vector(384)
        USING (
            CASE
                WHEN embedding IS NOT NULL THEN (embedding::text)::vector(384)
                ELSE NULL
            END
        );
    """)


def downgrade() -> None:
    # Revert document_chunks.embedding from vector(384) to JSONB
    op.execute("""
        ALTER TABLE document_chunks
        ALTER COLUMN embedding TYPE jsonb
        USING (
            CASE
                WHEN embedding IS NOT NULL THEN (embedding::text)::jsonb
                ELSE NULL
            END
        );
    """)
