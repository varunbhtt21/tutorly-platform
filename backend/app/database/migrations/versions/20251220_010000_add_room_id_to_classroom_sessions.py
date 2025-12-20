"""Add room_id to classroom_sessions table.

Revision ID: add_room_id_001
Revises: fix_student_profile_001
Create Date: 2025-12-20 01:00:00.000000

This migration adds the room_id column to classroom_sessions table.
The room_id is the provider-specific identifier returned when creating
a video room (e.g., 100ms room ID). It's required for SDK initialization.

Domain Entity: ClassroomSession (app/domains/classroom/entities/classroom_session.py)
- room_id: Provider-specific room ID (e.g., 100ms room ID for SDK)

This migration is idempotent - safe to run multiple times.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'add_room_id_001'
down_revision: Union[str, Sequence[str], None] = 'fix_student_profile_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def get_existing_columns(table_name: str) -> set:
    """Get set of existing column names for a table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    try:
        columns = inspector.get_columns(table_name)
        return {col['name'] for col in columns}
    except Exception:
        return set()


def table_exists(table_name: str) -> bool:
    """Check if a table exists."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    """
    Add room_id column to classroom_sessions table.

    The room_id stores the provider-specific ID (e.g., 100ms room ID)
    which is required for initializing the 100ms SDK on the frontend.
    """
    # Check if table exists (it may not exist if classroom feature not yet used)
    if not table_exists('classroom_sessions'):
        # Create the table with room_id included
        op.create_table(
            'classroom_sessions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('session_id', sa.Integer(), nullable=False),
            sa.Column('instructor_id', sa.Integer(), nullable=False),
            sa.Column('student_id', sa.Integer(), nullable=False),
            sa.Column('room_id', sa.String(length=255), nullable=True),
            sa.Column('room_name', sa.String(length=255), nullable=False),
            sa.Column('room_url', sa.String(length=500), nullable=False),
            sa.Column('provider', sa.String(length=50), nullable=False),
            sa.Column('status', sa.String(length=20), nullable=False, server_default='created'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('expires_at', sa.DateTime(), nullable=True),
            sa.Column('started_at', sa.DateTime(), nullable=True),
            sa.Column('ended_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_classroom_sessions_id', 'classroom_sessions', ['id'], unique=False)
        op.create_index('ix_classroom_sessions_session_id', 'classroom_sessions', ['session_id'], unique=True)
        op.create_index('ix_classroom_sessions_room_name', 'classroom_sessions', ['room_name'], unique=True)
        op.create_index('idx_classroom_instructor_status', 'classroom_sessions', ['instructor_id', 'status'])
        op.create_index('idx_classroom_student_status', 'classroom_sessions', ['student_id', 'status'])
        op.create_index('idx_classroom_status', 'classroom_sessions', ['status'])
        return

    # Table exists, check if room_id column needs to be added
    existing_columns = get_existing_columns('classroom_sessions')

    if 'room_id' not in existing_columns:
        with op.batch_alter_table('classroom_sessions', schema=None) as batch_op:
            batch_op.add_column(
                sa.Column('room_id', sa.String(length=255), nullable=True)
            )


def downgrade() -> None:
    """
    Remove room_id column from classroom_sessions table.

    Note: This will cause the JoinClassroomUseCase to fail as it
    expects room_id to be present. Use with caution.
    """
    if not table_exists('classroom_sessions'):
        return

    existing_columns = get_existing_columns('classroom_sessions')

    if 'room_id' in existing_columns:
        with op.batch_alter_table('classroom_sessions', schema=None) as batch_op:
            batch_op.drop_column('room_id')
