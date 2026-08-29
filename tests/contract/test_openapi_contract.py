"""OpenAPI contract tests -- validates every implemented operation against
the frozen docs/knowledge-graph/10-openapi.yaml via Schemathesis, driven
in-process against the FastAPI app (ASGI, no live server). Requires a real
Postgres + Neo4j, same as tests/integration -- see
tests/integration/conftest.py and DEVELOPMENT.md.

Schema is loaded from the frozen spec file (not the app's own
self-reported /openapi.json) so drift between the contract and the
implementation is actually caught, not tautologically hidden.
"""

from pathlib import Path

import schemathesis
import yaml
from hypothesis import settings

from app.main import app

OPENAPI_SPEC_PATH = Path(__file__).resolve().parents[2] / "docs" / "knowledge-graph" / "10-openapi.yaml"

# The frozen spec's servers[0].url carries a deployment-only /v1 prefix
# (gateway-fronted); every existing test in this repo (see
# tests/integration) calls the app at bare paths with no prefix. The spec
# file on disk is read, never written -- only this in-memory copy's
# `servers` entry is substituted, matching the existing convention of
# overriding deployment-specific values (e.g. DATABASE_URL) for local test
# execution without altering the source-of-truth artifact.
with open(OPENAPI_SPEC_PATH, encoding="utf-8") as f:
    _raw_spec = yaml.safe_load(f)
_raw_spec["servers"] = [{"url": "http://testserver"}]

schema = schemathesis.openapi.from_dict(_raw_spec)


@schema.parametrize()
@settings(max_examples=1, deadline=None)
def test_api_contract(case):
    case.call_and_validate(app=app)
