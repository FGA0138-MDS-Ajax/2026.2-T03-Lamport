"""create avaliacoes and add avaliacao_id to recomendacoes

Revision ID: 0006
Revises: 0005
Create Date: 2026-11-24 09:20:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0006"
down_revision: str | Sequence[str] | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "avaliacoes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column(
            "respostas_phq9",
            postgresql.ARRAY(sa.SmallInteger()),
            nullable=False,
        ),
        sa.Column(
            "respostas_gad7",
            postgresql.ARRAY(sa.SmallInteger()),
            nullable=False,
        ),
        sa.Column("escore_phq9", sa.SmallInteger(), nullable=False),
        sa.Column("escore_gad7", sa.SmallInteger(), nullable=False),
        sa.Column(
            "faixa_phq9",
            sa.Enum(
                "minima",
                "leve",
                "moderada",
                "moderadamente_grave",
                "grave",
                name="faixa_phq9",
                native_enum=False,
                create_constraint=True,
                length=30,
            ),
            nullable=False,
        ),
        sa.Column(
            "faixa_gad7",
            sa.Enum(
                "minima",
                "leve",
                "moderada",
                "moderadamente_grave",
                "grave",
                name="faixa_gad7",
                native_enum=False,
                create_constraint=True,
                length=30,
            ),
            nullable=False,
        ),
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
            nullable=False,
        ),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "escore_gad7 >= 0 AND escore_gad7 <= 21",
            name=op.f("ck_avaliacoes_escore_gad7_range"),
        ),
        sa.CheckConstraint(
            "escore_phq9 >= 0 AND escore_phq9 <= 27",
            name=op.f("ck_avaliacoes_escore_phq9_range"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_avaliacoes_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_avaliacoes")),
    )
    op.create_index(op.f("ix_avaliacoes_user_id"), "avaliacoes", ["user_id"])

    op.add_column("recomendacoes", sa.Column("avaliacao_id", sa.Uuid(), nullable=True))
    op.create_index(
        op.f("ix_recomendacoes_avaliacao_id"),
        "recomendacoes",
        ["avaliacao_id"],
    )
    op.create_foreign_key(
        op.f("fk_recomendacoes_avaliacao_id_avaliacoes"),
        "recomendacoes",
        "avaliacoes",
        ["avaliacao_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_recomendacoes_avaliacao_id_avaliacoes"),
        "recomendacoes",
        type_="foreignkey",
    )
    op.drop_index(op.f("ix_recomendacoes_avaliacao_id"), table_name="recomendacoes")
    op.drop_column("recomendacoes", "avaliacao_id")

    op.drop_index(op.f("ix_avaliacoes_user_id"), table_name="avaliacoes")
    op.drop_table("avaliacoes")
