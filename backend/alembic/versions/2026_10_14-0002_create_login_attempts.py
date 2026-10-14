"""create login_attempts

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-14 10:12:01.941845

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "login_attempts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column(
            "attempted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_login_attempts")),
    )
    op.create_index(op.f("ix_login_attempts_attempted_at"), "login_attempts", ["attempted_at"])
    op.create_index(op.f("ix_login_attempts_key"), "login_attempts", ["key"])


def downgrade() -> None:
    op.drop_index(op.f("ix_login_attempts_key"), table_name="login_attempts")
    op.drop_index(op.f("ix_login_attempts_attempted_at"), table_name="login_attempts")
    op.drop_table("login_attempts")
