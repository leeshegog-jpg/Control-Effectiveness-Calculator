"""SQLAlchemy ORM models, one module per Postgres schema namespace.
Source of truth for column definitions: docs/knowledge-graph/03-postgresql-schema.sql.
No models populated yet -- R0 scaffold only.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
