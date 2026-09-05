"""OpenAPI contract tests -- Schemathesis conformance for the FastAPI app
against the frozen ``docs/knowledge-graph/10-openapi.yaml``.

Behaviour is fixed by ADR-007
(``.adr/ADR-007-contract-test-suite-scope-and-ci-treatment.md``):

* **D1 -- population.** Every one of the 113 contracted operations is
  collected. The operations the app actually serves are asserted as strict
  conformance; the rest are skipped at runtime (see ``classification.py`` --
  the implemented set comes from ``app.openapi()``, not a hand-maintained
  list, so a newly implemented operation leaves the deferred population on
  its own).
* **D2 -- authentication.** The suite enforces no ``bearerAuth`` and sends no
  token. Two auth-conformance checks are excluded: ``ignored_auth`` (a 2xx
  response to an unauthenticated request) and ``missing_required_header``
  (which, for this globally ``security: [bearerAuth]`` spec, only ever
  exercises the missing-``Authorization`` scenario -- the frozen spec
  declares no other header parameters). The contract declares ``bearerAuth``
  and the R1 implementation does not enforce it; that discrepancy is tracked
  as risk **S4** in
  ``docs/implementation-blueprint/11-implementation-risk-register.md`` -- it
  is neither masked with a fake token nor resolved here.
* **D3 -- deferred operations.** A ``404`` from a not-yet-implemented
  operation is not a failure: those operations are skipped before any
  request is sent.
* **P5 -- Allow header conformance.** The Schemathesis ``Allow``-header check
  is excluded. Starlette constructs the ``Allow`` header for the coverage
  ``OPTIONS`` request from the mounted route, while Schemathesis compares it
  with the frozen operation-method set. The resulting mismatch is a
  test-methodology finding, not an application defect in the implemented
  operation. The decision is recorded in ACR-012; the unsupported-method
  check remains enabled.

Driven in-process against the app (ASGI, no live server). The implemented
operations need a real Postgres + Neo4j, same as ``tests/integration`` --
see ``tests/integration/conftest.py`` and ``DEVELOPMENT.md``.

Schema is loaded from the frozen spec file, not the app's self-reported
``/openapi.json``, so drift between contract and implementation is caught
rather than tautologically hidden.

This suite is not wired into CI (ADR-007 D4 -- a dedicated report-only job
is a separate change).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import schemathesis
import yaml
from app.main import app
from hypothesis import settings
from schemathesis.specs.openapi.checks import (
    allow_header_conformance,
    ignored_auth,
    missing_required_header,
)

from .classification import is_implemented

OPENAPI_SPEC_PATH = (
    Path(__file__).resolve().parents[2] / "docs" / "knowledge-graph" / "10-openapi.yaml"
)

# ADR-007 D2 -- exclude the authentication-conformance checks for this suite.
# ACR-012 P5 -- exclude the known Allow-header methodology mismatch only.
_EXCLUDED_CHECKS = [ignored_auth, missing_required_header, allow_header_conformance]

# The frozen spec's servers[0].url carries a deployment-only /v1 prefix
# (gateway-fronted); every existing test in this repo (see tests/integration)
# calls the app at bare paths with no prefix. The spec file on disk is read,
# never written -- only this in-memory copy's `servers` entry is substituted,
# matching the existing convention of overriding deployment-specific values
# (e.g. DATABASE_URL) for local test execution without altering the
# source-of-truth artifact.
with open(OPENAPI_SPEC_PATH, encoding="utf-8") as f:
    _raw_spec = yaml.safe_load(f)
_raw_spec["servers"] = [{"url": "http://testserver"}]

schema = schemathesis.openapi.from_dict(_raw_spec)


@schema.parametrize()
@settings(max_examples=1, deadline=None)
def test_api_contract(case):
    # `case.operation` is the contracted operation; `case.operation.method` is
    # its own method. Do not use `case.method` -- Schemathesis's coverage phase
    # deliberately mutates that (e.g. sending an unsupported method to check the
    # 405 response), which would misclassify a valid operation as deferred.
    if not is_implemented(app, case.operation.path, case.operation.method):
        pytest.skip(
            f"deferred: {case.operation.label} is contracted but not implemented "
            f"(roadmap) -- ADR-007 D1/D3"
        )
    case.call_and_validate(app=app, excluded_checks=_EXCLUDED_CHECKS)
