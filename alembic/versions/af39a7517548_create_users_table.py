"""create users table

Revision ID: af39a7517548
Revises:
Create Date: 2026-07-27 13:34:34.650825

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "af39a7517548"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create users table."""

    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "name",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "city",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Drop users table."""

    op.drop_table("users")