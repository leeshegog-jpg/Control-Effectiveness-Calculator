"""SQLAlchemy ORM models, one module per Postgres schema namespace.
Source of truth for column definitions: docs/knowledge-graph/03-postgresql-schema.sql.
Models are added per-milestone, not all at once -- see each module's
docstring for what's in scope and what's deliberately deferred.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


# Imported for side effect: registers each module's mapped classes on
# Base.metadata so `alembic revision --autogenerate` compares against the
# real model set instead of an empty one. Must come after Base is defined.
from app.models import ontology, provenance, safety  # noqa: E402,F401
