"""add chunk_text to chunks

Revision ID: 2f6f5f3d9c21
Revises: 7b6619f3f9f0
Create Date: 2026-03-24 08:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '2f6f5f3d9c21'
down_revision: Union[str, Sequence[str], None] = '7b6619f3f9f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'chunks',
        sa.Column(
            'chunk_text',
            sa.Text().with_variant(mysql.LONGTEXT(), 'mysql'),
            nullable=True,
        ),
    )
    op.execute("UPDATE chunks SET chunk_text = '' WHERE chunk_text IS NULL")
    op.alter_column('chunks', 'chunk_text', existing_type=sa.Text(), nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('chunks', 'chunk_text')
