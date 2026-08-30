"""Contract test setup.

Puts ``apps/api`` on ``sys.path`` so ``app.main`` imports the same way it
does for ``tests/integration``. The Schemathesis suite itself is described
in ``test_openapi_contract.py``; its scope and CI treatment are fixed by
ADR-007. The implemented-operation assertions need a real Postgres + Neo4j
(same as ``tests/integration`` -- see ``tests/integration/conftest.py`` and
``DEVELOPMENT.md``); the deferred operations are skipped and need neither.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "apps" / "api"))
