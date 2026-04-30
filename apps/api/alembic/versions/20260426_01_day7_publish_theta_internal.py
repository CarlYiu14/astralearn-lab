"""lesson publish + ability theta

Revision ID: 20260426_01
Revises: 20260425_01
Create Date: 2026-04-26
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260426_01"
down_revision: Union[str, None] = "20260425_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("lesson_units", sa.Column("published_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_lesson_units_status_published_at", "lesson_units", ["status", "published_at"], unique=False)

    op.add_column(
        "assessment_sessions",
        sa.Column("ability_theta", sa.Float(), server_default=sa.text("0"), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("assessment_sessions", "ability_theta")

    op.drop_index("ix_lesson_units_status_published_at", table_name="lesson_units")
    op.drop_column("lesson_units", "published_at")
