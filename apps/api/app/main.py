"""FastAPI app factory. R0 scaffold -- mounts every router (empty, no endpoints
yet) so the ASGI app object is real and importable/runnable end-to-end.
Contract: docs/knowledge-graph/10-openapi.yaml.
"""

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging_config import configure_logging
from app.routers import (
    actions,
    assets,
    audits,
    competency,
    controls,
    critical_controls,
    documents,
    evidence,
    extraction,
    gap_analysis,
    hazards,
    incidents,
    knowledge_graph,
    ontology,
    people,
    requirements,
    risks,
    safety_case,
    tarps,
    verification,
)

ROUTERS = (
    assets,
    hazards,
    risks,
    controls,
    critical_controls,
    verification,
    evidence,
    tarps,
    incidents,
    actions,
    audits,
    safety_case,
    requirements,
    documents,
    extraction,
    ontology,
    knowledge_graph,
    gap_analysis,
    people,
    competency,
)


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()

    app = FastAPI(
        title="TP Risk Management SMS -- Safety Knowledge Graph Platform API",
        version=settings.openapi_spec_version,
        description=(
            "R0 scaffold -- routers mounted, no endpoints implemented. "
            "Contract: docs/knowledge-graph/10-openapi.yaml."
        ),
    )

    for module in ROUTERS:
        app.include_router(module.router)

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.environment}

    return app


app = create_app()
