"""add user profile fields

Revision ID: 03edfcd5969f
Revises: 65cd875fe67e
Create Date: 2026-02-03 14:07:34.153795

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '03edfcd5969f'
down_revision: Union[str, Sequence[str], None] = '65cd875fe67e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
