#!/usr/bin/env python3
"""Run tests/graph -- the executable form of
docs/knowledge-graph/06-relationship-rules-catalogue.md's business rules
(docs/implementation-blueprint/08-testing-strategy.md §4).

R0: tests/graph is empty (no Neo4j instance graph exists yet -- no business
logic implemented). Reports that explicitly and exits 0, rather than
relying on pytest's "no tests collected" exit code 5, which is easy to
mis-handle as a CI failure.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

GRAPH_TESTS_DIR = Path(__file__).resolve().parents[1] / "tests" / "graph"


def main() -> int:
    test_files = list(GRAPH_TESTS_DIR.glob("test_*.py"))
    if not test_files:
        print(
            "OK: no graph tests yet (R0 -- no Neo4j instance graph, no business logic). Nothing to run."
        )
        return 0

    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(GRAPH_TESTS_DIR), "-v"],
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
