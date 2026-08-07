"""Neo4j driver provider. Driver construction is lazy -- no connection is
opened at import time, only on first query
(docs/knowledge-graph/01-enterprise-knowledge-graph-specification.md §4).
"""

from collections.abc import Generator

from neo4j import Driver, GraphDatabase

from app.core.config import get_settings

_driver: Driver = GraphDatabase.driver(
    get_settings().neo4j_uri,
    auth=(get_settings().neo4j_user, get_settings().neo4j_password),
    connection_timeout=3.0,  # readiness probes must fail fast, never hang
)


def get_graph_driver() -> Generator[Driver, None, None]:
    yield _driver
