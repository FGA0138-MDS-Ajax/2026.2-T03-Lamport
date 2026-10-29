"""create checkins

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-29 16:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "checkins",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("humor", sa.SmallInteger(), nullable=True),
        sa.Column("ansiedade", sa.SmallInteger(), nullable=True),
        sa.Column("sono", sa.SmallInteger(), nullable=True),
        sa.Column("sobrecarga", sa.SmallInteger(), nullable=True),
        sa.Column("pensamento_risco", sa.Boolean(), nullable=False),
        sa.Column("nivel", sa.String(length=20), nullable=False),
        sa.Column(
            "tags",
            postgresql.ARRAY(sa.String(length=30)),
            server_default="{}",
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_checkins_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_checkins")),
        sa.UniqueConstraint("user_id", "data", name=op.f("uq_checkins_user_id_data")),
    )


def downgrade() -> None:
    op.drop_table("checkins")
