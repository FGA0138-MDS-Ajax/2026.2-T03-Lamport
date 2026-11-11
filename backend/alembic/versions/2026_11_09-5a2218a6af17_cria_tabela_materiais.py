"""cria_tabela_materiais

Revision ID: 5a2218a6af17
Revises: 0003
Create Date: 2026-11-09 10:23:52.152673

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "5a2218a6af17"
down_revision: str | Sequence[str] | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "materiais",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("titulo", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("fonte", sa.String(length=100), nullable=False),
        sa.Column("resumo", sa.String(length=500), nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.String(length=30)), nullable=False),
        sa.Column("ativo", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("revisado_em", sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_materiais")),
        sa.UniqueConstraint("slug", name=op.f("uq_materiais_slug")),
    )


def downgrade() -> None:
    op.drop_table("materiais")
