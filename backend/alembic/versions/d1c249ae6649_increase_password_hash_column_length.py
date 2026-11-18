"""increase password hash column length

Revision ID: d1c249ae6649
Revises: 272c48699a09
Create Date: 2026-11-18 21:34:42.098404

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1c249ae6649'
down_revision: Union[str, Sequence[str], None] = '272c48699a09'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Increase password hash column length."""
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "hashed_password",
            existing_type=sa.String(length=20),
            type_=sa.String(length=255),
            existing_nullable=False,
        )


def downgrade() -> None:
    """Restore previous password hash column length."""
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "hashed_password",
            existing_type=sa.String(length=255),
            type_=sa.String(length=20),
            existing_nullable=False,
        )
