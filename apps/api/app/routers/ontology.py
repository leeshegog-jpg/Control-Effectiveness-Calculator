"""R0 scaffold placeholder -- ontology router (OpenAPI tag).
No endpoints implemented. Contract: docs/knowledge-graph/10-openapi.yaml.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/ontology", tags=["ontology"])
