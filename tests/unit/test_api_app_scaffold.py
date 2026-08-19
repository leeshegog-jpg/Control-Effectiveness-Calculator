"""Scaffold-level checks: the app constructs, health endpoints work with no
live DB, and exactly the routers a given milestone has implemented carry
real routes -- everything else stays an empty placeholder until its own
milestone. See docs/implementation-blueprint/16-r1-planning.md.
"""

from app.main import ROUTERS, app

# Update this set only when a router gains real endpoints in an approved
# milestone, not ad hoc. R1 Milestone 0: assets, ontology. R1 Milestone 1:
# hazards, risks. R1 Milestone 2: controls, critical_controls, verification,
# evidence. R1 Incident Management -- API, Service & Graph Synchronisation:
# incidents (CRUD + relational hazard-link endpoints only -- see
# docs/implementation-blueprint/22-r1-incident-reconciliation-decision-review.md).
IMPLEMENTED_ROUTERS = {
    "assets",
    "ontology",
    "hazards",
    "risks",
    "controls",
    "critical_controls",
    "verification",
    "evidence",
    "incidents",
}


def test_app_constructs():
    assert app.title.startswith("TP Risk Management SMS")


def test_health_endpoint_registered():
    paths = {getattr(route, "path", None) for route in app.routes}
    assert "/health" in paths


def test_ready_endpoint_registered():
    paths = {getattr(route, "path", None) for route in app.routes}
    assert "/ready" in paths


def test_router_implementation_matches_milestone_scope():
    for module in ROUTERS:
        name = module.__name__.rsplit(".", 1)[-1]
        has_routes = len(module.router.routes) > 0
        if name in IMPLEMENTED_ROUTERS:
            assert has_routes, (
                f"{name} router is in IMPLEMENTED_ROUTERS but has no routes"
            )
        else:
            assert not has_routes, (
                f"{name} router has routes but isn't in IMPLEMENTED_ROUTERS"
            )
