#!/usr/bin/env python3
"""Validate docs/knowledge-graph/10-openapi.yaml: parses as YAML and every
internal $ref resolves to a real node. No external network dependency
(no redocly/swagger-cli) so it runs the same in CI and locally.

See docs/implementation-blueprint/07-cicd-architecture.md §2.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

SPEC_PATH = Path(__file__).resolve().parents[1] / "docs" / "knowledge-graph" / "10-openapi.yaml"


def resolve_ref(spec: dict, ref: str) -> bool:
    if not ref.startswith("#/"):
        return False
    node = spec
    for part in ref[2:].split("/"):
        if not isinstance(node, dict) or part not in node:
            return False
        node = node[part]
    return True


def walk(spec: dict, node, path: str, errors: list[str]) -> None:
    if isinstance(node, dict):
        if "$ref" in node and isinstance(node["$ref"], str):
            if not resolve_ref(spec, node["$ref"]):
                errors.append(f"{path}: dangling $ref {node['$ref']!r}")
        for key, value in node.items():
            walk(spec, value, f"{path}/{key}", errors)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            walk(spec, item, f"{path}[{i}]", errors)


def main() -> int:
    if not SPEC_PATH.exists():
        print(f"FAIL: spec not found at {SPEC_PATH}")
        return 1

    spec = yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))

    errors: list[str] = []
    walk(spec, spec, "$", errors)

    paths = spec.get("paths", {})
    schemas = spec.get("components", {}).get("schemas", {})

    if errors:
        print(f"FAIL: {len(errors)} dangling $ref(s):")
        for e in errors:
            print(f"  {e}")
        return 1

    print(f"OK: {len(paths)} paths, {len(schemas)} schemas, 0 dangling $refs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
