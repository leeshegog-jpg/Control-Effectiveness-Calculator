#!/usr/bin/env python3
"""Validate ontology/seed-concepts/*.yaml: unique keys within a scheme, no
cycles in `broader` references, no duplicate aliases -- per
docs/knowledge-graph/06-relationship-rules-catalogue.md §4.

Format: one file per OntologyScheme -- `scheme: {name, description}` +
`concepts: [{key, pref_label, definition?, source_ref?, broader?, aliases?}]`.
`key` is a stable slug used only within this file (for `broader` refs); the
real DB identity is a UUID assigned at seed-load time (scripts/seed_ontology.py).
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

SEED_DIR = Path(__file__).resolve().parents[1] / "ontology" / "seed-concepts"


def load_scheme_files() -> list[dict]:
    files = []
    for path in sorted(SEED_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        files.append({"path": path, **data})
    return files


def check_unique_keys(scheme_file: dict, errors: list[str]) -> None:
    seen = set()
    for concept in scheme_file.get("concepts", []):
        key = concept.get("key")
        if key in seen:
            errors.append(f"{scheme_file['path'].name}: duplicate key {key!r}")
        seen.add(key)


def check_acyclic(scheme_file: dict, errors: list[str]) -> None:
    by_key = {c["key"]: c for c in scheme_file.get("concepts", []) if "key" in c}
    for concept in scheme_file.get("concepts", []):
        seen = {concept.get("key")}
        current = concept
        while current.get("broader"):
            parent_key = current["broader"]
            if parent_key not in by_key:
                errors.append(
                    f"{scheme_file['path'].name}: concept {concept.get('key')!r} "
                    f"has broader={parent_key!r}, not defined in this file"
                )
                break
            if parent_key in seen:
                errors.append(
                    f"{scheme_file['path'].name}: BROADER cycle involving {concept.get('key')!r}"
                )
                break
            seen.add(parent_key)
            current = by_key[parent_key]


def check_duplicate_aliases(scheme_file: dict, errors: list[str]) -> None:
    seen: set[str] = set()
    for concept in scheme_file.get("concepts", []):
        for alias in concept.get("aliases", []):
            if alias in seen:
                errors.append(
                    f"{scheme_file['path'].name}: duplicate alias {alias!r} "
                    f"within scheme {scheme_file.get('scheme', {}).get('name')!r}"
                )
            seen.add(alias)


def main() -> int:
    scheme_files = load_scheme_files()
    if not scheme_files:
        print("OK: no ontology seed concepts yet. Nothing to validate.")
        return 0

    errors: list[str] = []
    total_concepts = 0
    for sf in scheme_files:
        if "scheme" not in sf or "name" not in sf["scheme"]:
            errors.append(f"{sf['path'].name}: missing scheme.name")
            continue
        check_unique_keys(sf, errors)
        check_acyclic(sf, errors)
        check_duplicate_aliases(sf, errors)
        total_concepts += len(sf.get("concepts", []))

    if errors:
        print(f"FAIL: {len(errors)} ontology integrity error(s):")
        for e in errors:
            print(f"  {e}")
        return 1

    print(
        f"OK: {len(scheme_files)} schemes, {total_concepts} concepts, no cycles, no duplicate keys/aliases."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
