"""Unit tests for the contract suite's own wiring -- ADR-007 D1/D2/D3.

These are Postgres/Neo4j-free: they exercise the classification logic and
the suite's check configuration, not the API. They are the local
verification that the suite behaves as ADR-007 approved while the suite
itself is not yet wired into CI (D4).
"""

from __future__ import annotations

from pathlib import Path

import yaml
from app.main import app
from schemathesis.specs.openapi.checks import ignored_auth, missing_required_header

from .classification import implemented_operations, is_implemented, normalise_path
from .test_openapi_contract import _EXCLUDED_CHECKS

_SPEC_PATH = (
    Path(__file__).resolve().parents[2] / "docs" / "knowledge-graph" / "10-openapi.yaml"
)
_HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}

# ADR-007 D1: the frozen contract has 113 operations; 46 are implemented in
# R1, 67 are roadmap deferrals. These counts are asserted deliberately --
# when a deferred operation is implemented, this test fails and forces the
# follow-up ADR-007 requires (confirm the operation left the deferred pool,
# update the count).
_EXPECTED_TOTAL = 113
_EXPECTED_IMPLEMENTED = 46
_EXPECTED_DEFERRED = 67


def _spec_operations() -> list[tuple[str, str]]:
    spec = yaml.safe_load(_SPEC_PATH.read_text(encoding="utf-8"))
    return [
        (path, method.upper())
        for path, item in spec["paths"].items()
        for method in item
        if method.upper() in _HTTP_METHODS
    ]


def test_normalise_path_collapses_parameter_names_and_trailing_slash():
    assert normalise_path("/incidents/{id}") == "/incidents/{}"
    assert normalise_path("/incidents/{incident_id}") == "/incidents/{}"
    assert (
        normalise_path("/incidents/{id}/actions/{action_id}")
        == "/incidents/{}/actions/{}"
    )
    assert normalise_path("/assets/") == "/assets"
    assert normalise_path("/") == "/"


def test_spec_has_the_expected_operation_count():
    assert len(_spec_operations()) == _EXPECTED_TOTAL


def test_every_contracted_operation_is_implemented_xor_deferred():
    ops = _spec_operations()
    implemented = [(p, m) for p, m in ops if is_implemented(app, p, m)]
    deferred = [(p, m) for p, m in ops if not is_implemented(app, p, m)]

    assert len(implemented) + len(deferred) == len(ops)
    assert len(implemented) == _EXPECTED_IMPLEMENTED, sorted(implemented)
    assert len(deferred) == _EXPECTED_DEFERRED, sorted(deferred)


def test_classification_reads_the_live_app_not_a_static_list():
    # implemented_operations is derived from app.openapi(); the app serves
    # /health and /ready, which are not in the frozen contract at all.
    impl = implemented_operations(app)
    assert ("/health", "GET") in impl
    assert ("/ready", "GET") in impl
    # and a known-implemented contracted operation resolves through the
    # name-insensitive path match (spec: /assets/{id}, app: /assets/{asset_id})
    assert is_implemented(app, "/assets/{id}", "GET")
    # a known roadmap deferral does not
    assert not is_implemented(app, "/safety-assessments", "GET")


def test_classification_accepts_the_lowercase_method_the_suite_passes_in():
    # The suite keys on `case.operation.method`, which Schemathesis reports
    # lowercase. `GET /assets/{id}` and `PATCH /assets/{id}` are both
    # implemented -- keying on the case's (coverage-phase-mutable) `case.method`
    # instead would wrongly skip one of them.
    assert is_implemented(app, "/assets/{id}", "get")
    assert is_implemented(app, "/assets/{id}", "patch")
    assert not is_implemented(app, "/assets/{id}", "delete")


def test_suite_excludes_exactly_the_two_auth_conformance_checks():
    # ADR-007 D2: ignored_auth + missing_required_header, nothing else.
    assert set(_EXCLUDED_CHECKS) == {ignored_auth, missing_required_header}
