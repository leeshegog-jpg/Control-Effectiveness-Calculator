"""Contract test setup -- validates the live FastAPI app against the frozen
docs/knowledge-graph/10-openapi.yaml via Schemathesis, driven in-process
(ASGI, no live server). Requires a real Postgres + Neo4j, same as
tests/integration -- see tests/integration/conftest.py and DEVELOPMENT.md.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "apps" / "api"))
