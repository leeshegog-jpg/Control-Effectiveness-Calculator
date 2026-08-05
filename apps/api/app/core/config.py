"""Settings object -- reads environment variables per
docs/implementation-blueprint/09-configuration-management.md §1.

Secret values (ANTHROPIC_API_KEY, ENTRA_CLIENT_SECRET, database passwords embedded
in connection strings) are Key Vault-injected at runtime in Test/UAT/Prod and never
committed -- see .env.example for the variable names this reads, values only.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Postgres -- system of record (docs/knowledge-graph/03-postgresql-schema.sql)
    database_url: str = "postgresql+psycopg://sms:sms@localhost:5432/sms_dev"

    # Neo4j -- synced projection (knowledge-graph/01-enterprise-knowledge-graph-spec.md §4)
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "dev-password-change-me"

    # Qdrant -- vector search
    qdrant_url: str = "http://localhost:6333"

    # AI Extraction Service + Demonstration Engine (Key Vault-injected in Test/UAT/Prod)
    anthropic_api_key: str | None = None

    # Entra ID AuthN/AuthZ (per-environment app registrations)
    entra_tenant_id: str | None = None
    entra_client_id: str | None = None
    entra_client_secret: str | None = None

    # Azure Blob Storage -- document/evidence storage
    azure_blob_connection_string: str | None = None

    # OpenAPI contract version pin for client codegen
    openapi_spec_version: str = "0.2.0-draft"

    # Feature flags -- docs/implementation-blueprint/09-configuration-management.md §4
    demonstration_auto_generate: bool = False
    extraction_auto_accept_enabled: bool = False
    ontology_curator_approval_required: bool = True
    moc_risk_reassessment_enforced: bool = True

    environment: str = "dev"


@lru_cache
def get_settings() -> Settings:
    return Settings()
