#!/usr/bin/env python3
"""Load ontology/seed-concepts/*.yaml into Postgres. Idempotent: re-running
against an already-seeded database updates existing rows (matched by scheme
name + pref_label) rather than duplicating them.

Run scripts/validate_ontology.py first -- this script does not re-validate
acyclic/duplicate-key structure, it trusts that gate already passed.

Usage: python scripts/seed_ontology.py (run from repo root, with apps/api
installed in the active environment -- see DEVELOPMENT.md)
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "api"))

from app.dependencies.db import SessionLocal
from app.models.ontology import Concept, Scheme

SEED_DIR = Path(__file__).resolve().parents[1] / "ontology" / "seed-concepts"


def seed_scheme_file(db: Session, path: Path) -> tuple[str, int]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    scheme_data = data["scheme"]

    scheme = db.query(Scheme).filter_by(name=scheme_data["name"]).one_or_none()
    if scheme is None:
        scheme = Scheme(
            name=scheme_data["name"], description=scheme_data.get("description")
        )
        db.add(scheme)
        db.flush()

    key_to_concept: dict[str, Concept] = {}
    for concept_data in data.get("concepts", []):
        concept = (
            db.query(Concept)
            .filter_by(scheme_id=scheme.id, pref_label=concept_data["pref_label"])
            .one_or_none()
        )
        if concept is None:
            concept = Concept(
                scheme_id=scheme.id,
                pref_label=concept_data["pref_label"],
                definition=concept_data.get("definition"),
                source_ref=concept_data.get("source_ref"),
                status="published",  # seed data ported from V1 with a real source -- not a curator draft
            )
            db.add(concept)
            db.flush()
        key_to_concept[concept_data["key"]] = concept

    # Second pass: resolve `broader` refs now every concept in this file has an id.
    for concept_data in data.get("concepts", []):
        broader_key = concept_data.get("broader")
        if broader_key:
            key_to_concept[concept_data["key"]].parent_concept_id = key_to_concept[
                broader_key
            ].id

    return scheme_data["name"], len(data.get("concepts", []))


def main() -> int:
    files = sorted(SEED_DIR.glob("*.yaml"))
    if not files:
        print("No seed files found in ontology/seed-concepts/ -- nothing to load.")
        return 0

    db = SessionLocal()
    try:
        for path in files:
            name, count = seed_scheme_file(db, path)
            print(f"Seeded scheme {name!r}: {count} concepts ({path.name})")
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
