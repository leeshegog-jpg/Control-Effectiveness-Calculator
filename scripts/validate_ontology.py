#!/usr/bin/env python3
"""Validate ontology/seed-concepts/*.yaml (or .yml/.json): no cycles in
BROADER edges, no duplicate alias within a scheme -- per
docs/knowledge-graph/06-relationship-rules-catalogue.md §4.

R0: ontology/seed-concepts is empty (no database population yet, per the R0
constraint) -- this passes trivially and reports that explicitly, rather
than silently skipping. Real concept files land at R0 exit
(docs/implementation-blueprint/04-implementation-roadmap.md).
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

SEED_DIR = Path(__file__).resolve().parents[1] / "ontology" / "seed-concepts"


def load_concepts() -> list[dict]:
    concepts: list[dict] = []
    for path in sorted(SEED_DIR.glob("*.y*ml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        concepts.extend(data.get("concepts", []))
    return concepts


def check_acyclic(concepts: list[dict], errors: list[str]) -> None:
    by_id = {c["id"]: c for c in concepts if "id" in c}
    for concept in concepts:
        seen = {concept.get("id")}
        current = concept
        while current.get("broader"):
            parent_id = current["broader"]
            if parent_id in seen:
                errors.append(f"BROADER cycle involving concept {concept.get('id')!r}")
                break
            seen.add(parent_id)
            current = by_id.get(parent_id, {})


def check_duplicate_aliases(concepts: list[dict], errors: list[str]) -> None:
    by_scheme: dict[str, set[str]] = {}
    for concept in concepts:
        scheme = concept.get("scheme", "")
        seen = by_scheme.setdefault(scheme, set())
        for alias in concept.get("aliases", []):
            if alias in seen:
                errors.append(f"Duplicate alias {alias!r} within scheme {scheme!r}")
            seen.add(alias)


def main() -> int:
    if not SEED_DIR.exists() or not any(SEED_DIR.glob("*.y*ml")):
        print("OK: no ontology seed concepts yet (R0 -- no database population). Nothing to validate.")
        return 0

    concepts = load_concepts()
    errors: list[str] = []
    check_acyclic(concepts, errors)
    check_duplicate_aliases(concepts, errors)

    if errors:
        print(f"FAIL: {len(errors)} ontology integrity error(s):")
        for e in errors:
            print(f"  {e}")
        return 1

    print(f"OK: {len(concepts)} concepts, no cycles, no duplicate aliases.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
