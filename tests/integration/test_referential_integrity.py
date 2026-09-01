"""ACR-010 -- referential-integrity error handling for the 8 implemented
write operations, against a real Postgres + Neo4j.

Before ACR-010 a client-supplied foreign key that referenced no existing
row produced an uncaught ``sqlalchemy.exc.IntegrityError`` -> HTTP 500 with
the INSERT statement, bound parameters, and the psycopg ``DETAIL`` in the
server log. After ACR-010:

* a missing URL-path parent -> 404 (pre-check in the router);
* a missing body foreign key -> 422 (pre-check in the service, mapped from
  ``ReferentialIntegrityError``);
* no SQL / constraint name / ``DETAIL`` / traceback in any response body.

See ``.acr/ACR-010-referential-integrity-error-handling.md``.
"""

import uuid

_LEAK_TOKENS = (
    "INSERT",
    "psycopg",
    "sqlalchemy",
    "IntegrityError",
    "ForeignKeyViolation",
    "DETAIL",
    "_fkey",
    "safety.",
    "ontology.",
    "Traceback",
)


def _assert_no_db_leak(resp) -> None:
    body = resp.text
    for token in _LEAK_TOKENS:
        assert token not in body, f"response leaked {token!r}: {body}"


def _missing() -> str:
    return str(uuid.uuid4())


def _hazard(client) -> str:
    return client.post(
        "/hazards", json={"name": f"RI Hazard {uuid.uuid4()}", "description": "d"}
    ).json()["id"]


def _risk(client) -> str:
    return client.post(
        "/risks", json={"hazard_id": _hazard(client), "description": "RI risk"}
    ).json()["id"]


# ── P3-b: body foreign key references a non-existent row -> 422 ──────────────


def test_post_assets_bad_park_id_is_422(client):
    resp = client.post("/assets", json={"name": "RI", "park_id": _missing()})
    assert resp.status_code == 422
    assert "park_id" in resp.json()["detail"]
    _assert_no_db_leak(resp)


def test_post_assets_bad_asset_type_concept_is_422(client):
    resp = client.post(
        "/assets",
        json={"name": "RI", "asset_type": {"concept_id": _missing(), "pref_label": ""}},
    )
    assert resp.status_code == 422
    assert "asset_type" in resp.json()["detail"]
    _assert_no_db_leak(resp)


def test_post_hazards_bad_asset_id_is_422(client):
    resp = client.post(
        "/hazards", json={"name": "RI", "description": "d", "asset_id": _missing()}
    )
    assert resp.status_code == 422
    assert "asset_id" in resp.json()["detail"]
    _assert_no_db_leak(resp)


def test_post_hazards_bad_owner_person_is_422(client):
    resp = client.post(
        "/hazards",
        json={"name": "RI", "description": "d", "owner_person_id": _missing()},
    )
    assert resp.status_code == 422
    assert "owner_person_id" in resp.json()["detail"]
    _assert_no_db_leak(resp)


def test_post_hazards_bad_device_boundary_is_422(client):
    resp = client.post(
        "/hazards",
        json={"name": "RI", "description": "d", "device_boundary_id": _missing()},
    )
    assert resp.status_code == 422
    assert "device_boundary_id" in resp.json()["detail"]
    _assert_no_db_leak(resp)


def test_post_risks_bad_hazard_id_is_422(client):
    resp = client.post("/risks", json={"hazard_id": _missing(), "description": "d"})
    assert resp.status_code == 422
    assert "hazard_id" in resp.json()["detail"]
    _assert_no_db_leak(resp)


def test_post_incidents_bad_incident_type_is_422(client):
    resp = client.post(
        "/incidents",
        json={
            "datetime": "2026-01-01T00:00:00Z",
            "description": "d",
            "incident_type": {"concept_id": _missing(), "pref_label": ""},
        },
    )
    assert resp.status_code == 422
    assert "incident_type" in resp.json()["detail"]
    _assert_no_db_leak(resp)


def test_post_incidents_bad_reporter_person_is_422(client):
    resp = client.post(
        "/incidents",
        json={
            "datetime": "2026-01-01T00:00:00Z",
            "description": "d",
            "reporter_person_id": _missing(),
        },
    )
    assert resp.status_code == 422
    assert "reporter_person_id" in resp.json()["detail"]
    _assert_no_db_leak(resp)


def test_post_actions_bad_source_type_is_422(client):
    resp = client.post(
        "/actions",
        json={
            "description": "d",
            "source_type": {"concept_id": _missing(), "pref_label": ""},
        },
    )
    assert resp.status_code == 422
    assert "source_type" in resp.json()["detail"]
    _assert_no_db_leak(resp)


def test_post_actions_bad_assigned_person_is_422(client):
    resp = client.post(
        "/actions", json={"description": "d", "assigned_to_person_id": _missing()}
    )
    assert resp.status_code == 422
    assert "assigned_to_person_id" in resp.json()["detail"]
    _assert_no_db_leak(resp)


# ── P3-a: URL-path parent does not exist -> 404 ─────────────────────────────


def test_post_controls_for_missing_risk_is_404(client):
    resp = client.post(
        f"/risks/{_missing()}/controls",
        json={"risk_id": _missing(), "description": "d", "control_type": "Prevention"},
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Risk not found"
    _assert_no_db_leak(resp)


def test_post_verification_activities_for_missing_standard_is_404(client):
    resp = client.post(
        f"/performance-standards/{_missing()}/verification-activities", json={}
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Performance standard not found"
    _assert_no_db_leak(resp)


def test_post_evidence_for_missing_verification_activity_is_404(client):
    resp = client.post(f"/verification-activities/{_missing()}/evidence", json={})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Verification activity not found"
    _assert_no_db_leak(resp)


# ── P3-a op, real parent, bad body FK -> 422 ────────────────────────────────


def test_post_controls_real_risk_bad_hierarchy_is_422(client):
    risk_id = _risk(client)
    resp = client.post(
        f"/risks/{risk_id}/controls",
        json={
            "risk_id": risk_id,
            "description": "d",
            "control_type": "Prevention",
            "hierarchy": {"concept_id": _missing(), "pref_label": ""},
        },
    )
    assert resp.status_code == 422
    assert "hierarchy" in resp.json()["detail"]
    _assert_no_db_leak(resp)


# ── happy path: a valid existing foreign key still works ────────────────────


def test_post_assets_with_real_park_still_creates(client, db):
    from sqlalchemy import text

    park_id = db.execute(
        text("INSERT INTO safety.parks (name) VALUES (:n) RETURNING id"),
        {"n": f"RI Park {uuid.uuid4()}"},
    ).scalar_one()
    db.commit()

    resp = client.post(
        "/assets", json={"name": f"RI Asset {uuid.uuid4()}", "park_id": str(park_id)}
    )
    assert resp.status_code == 201
    assert resp.json()["park_id"] == str(park_id)


def test_post_risks_with_real_hazard_still_creates(client):
    resp = client.post(
        "/risks", json={"hazard_id": _hazard(client), "description": "valid FK path"}
    )
    assert resp.status_code == 201
