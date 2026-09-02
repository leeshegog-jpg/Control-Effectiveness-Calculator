"""Referential-integrity pre-checks for write operations (ACR-010).

A client-supplied foreign-key UUID is validated against its target table
*before* the row is flushed, so a reference to a non-existent row produces a
typed ``ReferentialIntegrityError`` -- which the router maps to HTTP 422 --
rather than an uncaught ``sqlalchemy.exc.IntegrityError`` / HTTP 500 that
leaks the INSERT statement, bound parameters, and the psycopg ``DETAIL``.

Scope: the 8 implemented POST operations audited in
``.acr/ACR-010-referential-integrity-error-handling.md``. Path-parameter
parents are pre-checked in the router (-> 404); the body foreign keys here
are pre-checked in the service ``create_*`` functions (-> 422).
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import text

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.models import Base


class ReferentialIntegrityError(Exception):
    """A client-supplied foreign key references a row that does not exist.

    Mapped to HTTP 422 at the router boundary (mirrors ``SfarpJustificationError``
    / ``ControlNotClassifiedError``), never surfaced as a 500.
    """

    def __init__(self, field: str, entity: str) -> None:
        super().__init__(f"{field} references a {entity} that does not exist")
        self.field = field
        self.entity = entity


def require_exists(
    db: Session,
    target: type[Base] | str,
    id_: uuid.UUID | None,
    *,
    field: str,
    entity: str,
) -> None:
    """No-op when ``id_`` is ``None`` (nullable / optional FK column).
    Otherwise raise :class:`ReferentialIntegrityError` unless a row with that
    primary key exists in ``target``.

    ``target`` is an ORM model class, or a ``"schema.table"`` string for the
    two frozen-schema tables not yet ORM-mapped (``safety.documents``,
    ``safety.device_boundaries``). That string is always a code constant from
    the call sites -- never client input.
    """
    if id_ is None:
        return
    if isinstance(target, str):
        exists = (
            db.execute(
                text(f"SELECT 1 FROM {target} WHERE id = :id"),  # noqa: S608 - constant table name
                {"id": id_},
            ).first()
            is not None
        )
    else:
        model: type[Any] = target
        exists = db.get(model, id_) is not None
    if not exists:
        raise ReferentialIntegrityError(field, entity)
