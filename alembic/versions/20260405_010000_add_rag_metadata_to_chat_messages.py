"""add rag metadata to chat messages

Revision ID: e2b7a9c4d1f0
Revises: 9f0d1f4a6c2b
Create Date: 2026-04-05 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e2b7a9c4d1f0'
down_revision: Union[str, Sequence[str], None] = '9f0d1f4a6c2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'chat_messages',
        sa.Column('used_rag', sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        'chat_messages',
        sa.Column('retrieved_chunk_count', sa.Integer(), nullable=False, server_default='0'),
    )


def downgrade() -> None:
    op.drop_column('chat_messages', 'retrieved_chunk_count')
    op.drop_column('chat_messages', 'used_rag')
