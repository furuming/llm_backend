"""add projects and rooms to chat

Revision ID: 9f0d1f4a6c2b
Revises: 2f6f5f3d9c21
Create Date: 2026-04-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f0d1f4a6c2b'
down_revision: Union[str, Sequence[str], None] = '2f6f5f3d9c21'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CHAT_MESSAGES_ROOM_ID_FK = 'fk_chat_messages_room_id_chat_rooms'


def upgrade() -> None:
    op.create_table(
        'chat_projects',
        sa.Column('id', sa.String(length=26), nullable=False),
        sa.Column('user_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_chat_projects_user_id'), 'chat_projects', ['user_id'], unique=False)

    op.create_table(
        'chat_rooms',
        sa.Column('id', sa.String(length=26), nullable=False),
        sa.Column('project_id', sa.String(length=26), nullable=False),
        sa.Column('user_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['chat_projects.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_chat_rooms_project_id'), 'chat_rooms', ['project_id'], unique=False)
    op.create_index(op.f('ix_chat_rooms_user_id'), 'chat_rooms', ['user_id'], unique=False)

    op.add_column('chat_messages', sa.Column('room_id', sa.String(length=26), nullable=True))
    op.add_column(
        'chat_messages',
        sa.Column('model', sa.String(length=100), server_default='unknown', nullable=False),
    )
    op.create_index(op.f('ix_chat_messages_room_id'), 'chat_messages', ['room_id'], unique=False)
    op.create_foreign_key(CHAT_MESSAGES_ROOM_ID_FK, 'chat_messages', 'chat_rooms', ['room_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint(CHAT_MESSAGES_ROOM_ID_FK, 'chat_messages', type_='foreignkey')
    op.drop_index(op.f('ix_chat_messages_room_id'), table_name='chat_messages')
    op.drop_column('chat_messages', 'model')
    op.drop_column('chat_messages', 'room_id')

    op.drop_index(op.f('ix_chat_rooms_user_id'), table_name='chat_rooms')
    op.drop_index(op.f('ix_chat_rooms_project_id'), table_name='chat_rooms')
    op.drop_table('chat_rooms')

    op.drop_index(op.f('ix_chat_projects_user_id'), table_name='chat_projects')
    op.drop_table('chat_projects')
