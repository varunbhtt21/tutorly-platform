"""Fix student_profiles schema to match domain entity.

Revision ID: fix_student_profile_001
Revises: 5faa72b43b46
Create Date: 2025-12-19 23:05:00.000000

This migration ensures the student_profiles table matches the StudentProfile
domain entity. It's idempotent - safe to run regardless of current state.

The previous migration (5faa72b43b46) had operations that may or may not have
been applied correctly. This migration verifies the schema matches the domain.

Domain Entity Fields (app/domains/student/entities/student_profile.py):
- id, user_id (identity)
- profile_photo_url, learning_goals, preferred_language (profile info)
- notification_preferences, preferred_session_duration (preferences)
- total_sessions_completed, total_spent (statistics)
- created_at, updated_at (timestamps)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'fix_student_profile_001'
down_revision: Union[str, Sequence[str], None] = '5faa72b43b46'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def get_existing_columns(table_name: str) -> set:
    """Get set of existing column names for a table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = inspector.get_columns(table_name)
    return {col['name'] for col in columns}


def upgrade() -> None:
    """
    Ensure student_profiles schema matches domain entity.

    This migration is idempotent - it checks which columns exist
    and only adds/removes what's necessary.
    """
    existing_columns = get_existing_columns('student_profiles')

    # Define columns required by domain entity
    required_columns = {
        'profile_photo_url': sa.Column('profile_photo_url', sa.String(length=500), nullable=True),
        'preferred_language': sa.Column('preferred_language', sa.String(length=50), nullable=True),
        'notification_preferences': sa.Column('notification_preferences', sa.JSON(), nullable=True),
        'preferred_session_duration': sa.Column('preferred_session_duration', sa.Integer(), nullable=True, server_default='50'),
        'total_sessions_completed': sa.Column('total_sessions_completed', sa.Integer(), nullable=True, server_default='0'),
        'total_spent': sa.Column('total_spent', sa.Float(), nullable=True, server_default='0.0'),
    }

    # Column that should NOT exist (not in domain entity)
    invalid_columns = {'preferred_learning_style'}

    with op.batch_alter_table('student_profiles', schema=None) as batch_op:
        # Add missing columns
        for col_name, col_def in required_columns.items():
            if col_name not in existing_columns:
                batch_op.add_column(col_def)

        # Remove invalid columns
        for col_name in invalid_columns:
            if col_name in existing_columns:
                batch_op.drop_column(col_name)


def downgrade() -> None:
    """
    Revert schema changes.

    Note: This restores a schema that doesn't match the domain entity,
    which will cause application errors. Use with caution.
    """
    existing_columns = get_existing_columns('student_profiles')

    with op.batch_alter_table('student_profiles', schema=None) as batch_op:
        # Add back the column not in domain entity
        if 'preferred_learning_style' not in existing_columns:
            batch_op.add_column(sa.Column('preferred_learning_style', sa.String(length=50), nullable=True))

        # Remove domain entity columns (dangerous!)
        columns_to_remove = [
            'total_spent', 'total_sessions_completed', 'preferred_session_duration',
            'notification_preferences', 'preferred_language', 'profile_photo_url'
        ]
        for col_name in columns_to_remove:
            if col_name in existing_columns:
                batch_op.drop_column(col_name)
