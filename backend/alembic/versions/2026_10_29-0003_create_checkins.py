"""create checkins

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-29 20:40:00.000000

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
        sa.Column("pensamento_risco", sa.Boolean(), nullable=False),
        sa.Column("humor", sa.SmallInteger(), nullable=True),
        sa.Column("ansiedade", sa.SmallInteger(), nullable=True),
        sa.Column("sono", sa.SmallInteger(), nullable=True),
        sa.Column("sobrecarga", sa.SmallInteger(), nullable=True),
        sa.Column(
            "nivel",
            sa.Enum(
                "autocuidado",
                "atencao",
                "prioritario",
                "crise",
                name="nivel",
                native_enum=False,
                create_constraint=True,
                length=20,
            ),
            server_default="autocuidado",
            nullable=False,
        ),
        sa.Column(
            "tags",
            postgresql.ARRAY(sa.String(length=30)),
            server_default="{}",
            nullable=False,
        ),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "ansiedade IS NULL OR (ansiedade >= 0 AND ansiedade <= 3)",
            name=op.f("ck_checkins_ansiedade_range"),
        ),
        sa.CheckConstraint(
            "humor IS NULL OR (humor >= 1 AND humor <= 5)",
            name=op.f("ck_checkins_humor_range"),
        ),
        sa.CheckConstraint(
            "sobrecarga IS NULL OR (sobrecarga >= 0 AND sobrecarga <= 3)",
            name=op.f("ck_checkins_sobrecarga_range"),
        ),
        sa.CheckConstraint(
            "sono IS NULL OR (sono >= 1 AND sono <= 5)",
            name=op.f("ck_checkins_sono_range"),
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
    op.create_index(op.f("ix_checkins_data"), "checkins", ["data"])
    op.create_index(op.f("ix_checkins_user_id"), "checkins", ["user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_checkins_user_id"), table_name="checkins")
    op.drop_index(op.f("ix_checkins_data"), table_name="checkins")
    op.drop_table("checkins")
