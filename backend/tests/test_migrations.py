from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext

from app.infrastructure.database import get_engine
from app.infrastructure.models import Base


def test_migrations_match_models():
    with get_engine().connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn), Base.metadata)

    assert diff == []
