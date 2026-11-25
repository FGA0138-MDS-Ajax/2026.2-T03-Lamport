"""Associate new token revocations with their account for deletion."""

import sqlalchemy as sa

from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Existing rows only have a random jti. Keep their revocations enforceable until expiry.
    op.add_column("revoked_tokens", sa.Column("user_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_revoked_tokens_user_id_users",
        "revoked_tokens",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_revoked_tokens_user_id", "revoked_tokens", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_revoked_tokens_user_id", table_name="revoked_tokens")
    op.drop_constraint("fk_revoked_tokens_user_id_users", "revoked_tokens", type_="foreignkey")
    op.drop_column("revoked_tokens", "user_id")
