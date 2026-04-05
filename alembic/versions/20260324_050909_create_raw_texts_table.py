"""create raw_texts table

Revision ID: 1e9780771a87
Revises: 1c48bd2274ea
Create Date: 2026-03-24 05:09:09.448741

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = '1e9780771a87'
down_revision: Union[str, Sequence[str], None] = '1c48bd2274ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

LONG_TEXT = sa.Text().with_variant(mysql.LONGTEXT(), 'mysql')


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'upload_files',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('content_type', sa.String(length=255), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'raw_texts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('upload_file_id', sa.Integer(), nullable=False),
        sa.Column('parse_type', sa.String(length=255), nullable=False),
        sa.Column('chunk_size', sa.Integer(), nullable=False, server_default='800'),
        sa.Column('chunk_overlap', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('text', LONG_TEXT, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_raw_texts_upload_file_id'), 'raw_texts', ['upload_file_id'], unique=False)

    op.create_table(
        'chunks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('upload_file_id', sa.Integer(), nullable=False),
        sa.Column('raw_text_id', sa.Integer(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('start_offset', sa.Integer(), nullable=False),
        sa.Column('end_offset', sa.Integer(), nullable=False),
        sa.Column('qdrant_point_id', sa.String(length=26), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_chunks_upload_file_id'), 'chunks', ['upload_file_id'], unique=False)
    op.create_index(op.f('ix_chunks_raw_text_id'), 'chunks', ['raw_text_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_chunks_raw_text_id'), table_name='chunks')
    op.drop_index(op.f('ix_chunks_upload_file_id'), table_name='chunks')
    op.drop_table('chunks')

    op.drop_index(op.f('ix_raw_texts_upload_file_id'), table_name='raw_texts')
    op.drop_table('raw_texts')
    op.drop_table('upload_files')
