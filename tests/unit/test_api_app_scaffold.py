"""R0 scaffold smoke test -- verifies the FastAPI app constructs and every
router mounts with zero live endpoints, per the R0 constraint (no business
logic, no API endpoints implemented). Real per-module unit tests land here
once R1+ implementation begins -- see docs/implementation-blueprint/08-testing-strategy.md §1.
"""
from app.main import ROUTERS, app


def test_app_constructs():
    assert app.title.startswith("TP Risk Management SMS")


def test_health_endpoint_registered():
    paths = {getattr(route, "path", None) for route in app.routes}
    assert "/health" in paths


def test_every_router_mounted_with_no_endpoints():
    # R0 constraint: routers exist (contract scaffolding) but carry no
    # endpoint implementations yet.
    assert len(ROUTERS) == 20
    for module in ROUTERS:
        assert module.router.routes == []
