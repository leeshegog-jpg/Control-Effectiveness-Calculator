"""R0 scaffold placeholder -- controls router (OpenAPI tag).
No endpoints implemented. Contract: docs/knowledge-graph/10-openapi.yaml.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/controls", tags=["controls"])
