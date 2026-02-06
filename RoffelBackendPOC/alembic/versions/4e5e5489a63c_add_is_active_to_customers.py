"""add is_active to customers

Revision ID: 4e5e5489a63c
Revises: 03edfcd5969f
Create Date: 2026-02-05 15:08:23.363952

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e5e5489a63c'
down_revision: Union[str, Sequence[str], None] = '03edfcd5969f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "customers",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_column("customers", "is_active")

    # ### end Alembic commands ###
