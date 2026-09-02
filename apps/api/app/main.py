"""FastAPI app factory. Mounts every router. R1 Milestone 0: assets and
ontology carry real endpoints; the remaining 18 stay empty until their
milestone (see docs/implementation-blueprint/16-r1-planning.md).
Contract: docs/knowledge-graph/10-openapi.yaml.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.logging_config import configure_logging
from app.dependencies.db import SessionLocal
from app.dependencies.graph import get_graph_driver
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

    @app.exception_handler(IntegrityError)
    async def _integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
        """ACR-010 defence-in-depth: a database constraint violation that got
        past the explicit referential pre-checks (see services/referential.py).
        Deliberately sanitised -- never expose the SQL statement, the psycopg
        DETAIL, the constraint name, bound parameters, or a traceback.
        """
        return JSONResponse(
            status_code=409,
            content={"detail": "The request could not be completed due to a data constraint."},
        )

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.environment}

    @app.get("/ready", tags=["health"])
    def ready() -> dict[str, str]:
        """Readiness check -- verifies real Postgres and Neo4j connectivity,
        not just that the process is running. Distinct from /health, which
        only confirms the ASGI app itself is up (R0 constraint: no live DB
        was required for /health to pass)."""
        checks: dict[str, str] = {}

        db: Session = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            checks["postgres"] = "ok"
        except Exception as exc:  # noqa: BLE001 -- readiness probe reports, doesn't raise
            checks["postgres"] = f"unreachable: {exc}"
        finally:
            db.close()

        try:
            driver = next(get_graph_driver())
            driver.verify_connectivity()
            checks["neo4j"] = "ok"
        except Exception as exc:  # noqa: BLE001
            checks["neo4j"] = f"unreachable: {exc}"

        all_ok = all(v == "ok" for k, v in checks.items() if k != "status")
        checks["status"] = "ready" if all_ok else "not_ready"
        return checks

    return app


app = create_app()
