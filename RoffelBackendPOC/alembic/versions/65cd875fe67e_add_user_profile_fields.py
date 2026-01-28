"""add user profile fields

Revision ID: 65cd875fe67e
Revises: 4f7df44aad7a
Create Date: 2026-01-28 12:00:22.513165

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '65cd875fe67e'
down_revision: Union[str, Sequence[str], None] = '4f7df44aad7a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("first_name", sa.String(), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(), nullable=True))
    op.add_column("users", sa.Column("function", sa.String(), nullable=True))


def downgrade() -> None:
    pass
