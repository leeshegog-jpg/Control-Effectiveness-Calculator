"""Ontology retrieval against real seed data -- run scripts/seed_ontology.py
before this test suite (the integration-tests CI job does this). Verifies
the read-only lookup API against the actual ported V1 vocabularies, not
fixture data invented for the test.
"""


def test_seeded_schemes_present(client):
    resp = client.get("/ontology/schemes")
    assert resp.status_code == 200
    names = {s["name"] for s in resp.json()}
    assert {"Control Hierarchy", "Consequence Domain", "Energy Source"} <= names


def test_control_hierarchy_has_six_concepts(client):
    schemes = {s["name"]: s["id"] for s in client.get("/ontology/schemes").json()}
    resp = client.get(
        "/ontology/concepts", params={"scheme_id": schemes["Control Hierarchy"]}
    )
    assert resp.status_code == 200
    labels = {c["pref_label"] for c in resp.json()}
    assert labels == {
        "Elimination",
        "Substitution",
        "Isolation",
        "Engineering",
        "Administrative",
        "PPE",
    }


def test_concept_search_by_partial_label(client):
    resp = client.get("/ontology/concepts", params={"q": "electr"})
    assert resp.status_code == 200
    labels = {c["pref_label"] for c in resp.json()}
    assert "Electrical" in labels


def test_concept_status_filter_valid_value(client):
    # Seed data is ported from V1 with a real source, not curator drafts --
    # scripts/seed_ontology.py sets status="published" (ADR-C / P4).
    resp = client.get("/ontology/concepts", params={"status": "published"})
    assert resp.status_code == 200
    assert resp.json()
    assert all(c["status"] == "published" for c in resp.json())


def test_concept_status_filter_invalid_value_is_422(client):
    # Before ACR-C this reached the DB and raised InvalidTextRepresentation
    # against the `ontology.concept_status` Postgres ENUM -> uncaught 500.
    resp = client.get("/ontology/concepts", params={"status": "bogus"})
    assert resp.status_code == 422
