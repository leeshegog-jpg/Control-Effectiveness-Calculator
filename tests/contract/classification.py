"""Runtime classification of frozen-contract operations into
*implemented* vs *deferred*, for the OpenAPI contract test suite.

ADR-007 D1/D3: all 113 contracted operations stay visible in the test
collection. The operations the application actually serves are asserted as
strict Schemathesis conformance; the rest are skipped at runtime with a
documented reason. "Actually serves" is derived from the application's own
OpenAPI (``app.openapi()``) -- which reflects the mounted routers exactly --
not from a checked-in allowlist, so a newly implemented operation leaves the
deferred population on its own with no edit here.

Path templates are compared with parameter *names* collapsed: the frozen
spec writes ``/incidents/{id}`` where the implementation writes
``/incidents/{incident_id}``; both normalise to ``/incidents/{}``.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI

_HTTP_METHODS = frozenset({"GET", "POST", "PUT", "PATCH", "DELETE"})
_PATH_PARAM = re.compile(r"\{[^}]+\}")


def normalise_path(path: str) -> str:
    """Collapse path-parameter names and any trailing slash so that spec and
    implementation path templates compare equal when they only differ in
    parameter naming."""
    return _PATH_PARAM.sub("{}", path.rstrip("/")) or "/"


def implemented_operations(app: FastAPI) -> frozenset[tuple[str, str]]:
    """``(normalised_path, METHOD)`` for every operation the app serves,
    taken from its own generated OpenAPI document."""
    paths = app.openapi().get("paths", {})
    return frozenset(
        (normalise_path(path), method.upper())
        for path, item in paths.items()
        for method in item
        if method.upper() in _HTTP_METHODS
    )


def is_implemented(app: FastAPI, path: str, method: str) -> bool:
    """Does the app serve the operation the frozen spec calls ``method path``?"""
    return (normalise_path(path), method.upper()) in implemented_operations(app)
