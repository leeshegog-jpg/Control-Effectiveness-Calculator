"""ACR-010 -- the global ``IntegrityError`` handler is defence-in-depth only
and must never leak database internals.

No live DB required: the handler is invoked directly with a synthetic
``IntegrityError`` whose text/params/orig deliberately contain the kind of
detail a real psycopg ``ForeignKeyViolation`` carries.
"""

import asyncio

from app.main import app
from app.services.referential import ReferentialIntegrityError, require_exists
from sqlalchemy.exc import IntegrityError


def test_global_integrity_handler_is_registered():
    assert IntegrityError in app.exception_handlers


def test_global_integrity_handler_returns_sanitised_409():
    handler = app.exception_handlers[IntegrityError]
    exc = IntegrityError(
        statement="INSERT INTO safety.assets (name, park_id) VALUES (%(name)s, %(park_id)s)",
        params={
            "name": "secret payload",
            "park_id": "00000000-0000-0000-0000-000000000000",
        },
        orig=Exception(
            'insert or update on table "assets" violates foreign key constraint '
            '"assets_park_id_fkey"\nDETAIL:  Key (park_id)=(...) is not present in table "parks".'
        ),
    )

    response = asyncio.run(handler(None, exc))
    body = response.body.decode()

    assert response.status_code == 409
    assert "data constraint" in body
    for leaked in (
        "INSERT",
        "safety.assets",
        "assets_park_id_fkey",
        "DETAIL",
        "park_id",
        "secret payload",
        "psycopg",
        "Traceback",
    ):
        assert leaked not in body, f"handler leaked {leaked!r}: {body}"


def test_referential_integrity_error_message_names_field_not_sql():
    exc = ReferentialIntegrityError("park_id", "park")
    assert str(exc) == "park_id references a park that does not exist"


def test_require_exists_noop_on_none():
    # id_ is None -> optional/nullable FK -> never raises, never touches the db.
    require_exists(
        db=None, target="safety.parks", id_=None, field="park_id", entity="park"
    )
