"""create recomendacoes

Revision ID: 0005
Revises: 5a2218a6af17
Create Date: 2026-11-18 18:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0005"
down_revision: str | Sequence[str] | None = "5a2218a6af17"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "recomendacoes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("material_id", sa.Integer(), nullable=False),
        sa.Column("checkin_id", sa.Uuid(), nullable=True),
        sa.Column("regra", sa.String(length=20), nullable=False),
        sa.Column("motivo", sa.String(length=500), nullable=False),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["checkin_id"],
            ["checkins.id"],
            name=op.f("fk_recomendacoes_checkin_id_checkins"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["material_id"],
            ["materiais.id"],
            name=op.f("fk_recomendacoes_material_id_materiais"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_recomendacoes_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_recomendacoes")),
    )
    op.create_index(op.f("ix_recomendacoes_checkin_id"), "recomendacoes", ["checkin_id"])
    op.create_index(op.f("ix_recomendacoes_material_id"), "recomendacoes", ["material_id"])
    op.create_index(op.f("ix_recomendacoes_user_id"), "recomendacoes", ["user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_recomendacoes_user_id"), table_name="recomendacoes")
    op.drop_index(op.f("ix_recomendacoes_material_id"), table_name="recomendacoes")
    op.drop_index(op.f("ix_recomendacoes_checkin_id"), table_name="recomendacoes")
    op.drop_table("recomendacoes")
