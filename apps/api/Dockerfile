# Build context is the repo root (see docker-compose.dev.yml) so this can
# COPY packages/ontology-client/py, the API's one cross-package dependency.
FROM python:3.12-slim AS runtime
WORKDIR /repo

COPY apps/api/pyproject.toml apps/api/pyproject.toml
COPY apps/api/app apps/api/app
COPY packages/ontology-client/py packages/ontology-client/py

RUN pip install --no-cache-dir ./apps/api ./packages/ontology-client/py

ENV PYTHONUNBUFFERED=1
EXPOSE 8000
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
