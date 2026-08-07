"""Integration test fixtures -- require a real Postgres + Neo4j, per
DATABASE_URL/NEO4J_* env vars. Not run by the fast unit CI job; run by
pr-validation.yml's integration-tests job (Postgres/Neo4j service
containers) or manually against docker-compose.test.yml. See
DEVELOPMENT.md.
"""

import sys
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "apps" / "api"))

from app.dependencies.db import SessionLocal
from app.dependencies.graph import get_graph_driver
from app.main import app


@pytest.fixture()
def db() -> Session:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture()
def graph_driver():
    return next(get_graph_driver())


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient

    return TestClient(app)
