"""Initial schema -- deploys the frozen Design Baseline v1.1 schema verbatim.

Revision ID: 0001
Revises:
Create Date: 2026-08-07

Executes docs/knowledge-graph/03-postgresql-schema.sql directly rather than
re-deriving it through SQLAlchemy's autogenerate -- that file is the single
source of truth for the schema (Design Baseline v1.1, frozen); transcribing
it into a second representation risks drift between the two. psycopg
supports multiple ;-separated statements (including the dollar-quoted
set_updated_at() function body) in one execute() call when no bind
parameters are passed.
"""

from pathlib import Path
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA_SQL_PATH = (
    Path(__file__).resolve().parents[4] / "docs" / "knowledge-graph" / "03-postgresql-schema.sql"
)


def upgrade() -> None:
    sql = SCHEMA_SQL_PATH.read_text(encoding="utf-8")
    op.execute(sql)


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS provenance CASCADE;")
    op.execute("DROP SCHEMA IF EXISTS regulatory CASCADE;")
    op.execute("DROP SCHEMA IF EXISTS safety CASCADE;")
    op.execute("DROP SCHEMA IF EXISTS ontology CASCADE;")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at() CASCADE;")
