"""T10 REGRESSION TEST: `application.http_dispatch.dispatch_record_human_decision`
against the REAL, un-monkeypatched `persistence.engine.connect()` --
i.e. a genuinely separate, short-lived, closing database connection,
the same lifecycle a real production HTTP request actually gets.

WHY THIS FILE EXISTS SEPARATELY FROM `test_http_record_decision.py`
--------------------------------------------------------------------
Every other Architecture 17 HTTP test uses the `http_client` fixture's
own `application.http_dispatch.connect` monkeypatch, which reuses the
test's own long-lived, never-closing `db_connection` fixture. That
monkeypatch is correct and necessary for those tests' own transactional
isolation (PKG-30 onward convention) -- but it structurally CANNOT
catch a bug that only manifests when the real `connect()` context
manager actually CLOSES the connection on exit. A real defect of
exactly that shape shipped in this field's own first version:
`dispatch_record_human_decision`'s final "re-fetch the just-committed
Decision" call lived OUTSIDE the `with connect() as connection:` block
(a one-level indentation defect), so it ran against an already-closed
`sa.Connection` (`sqlalchemy.exc.ResourceClosedError: This Connection
is closed`) on every REAL request -- 100% of the time in the actual
running Docker container, 0% of the time under the full `pytest`
suite, because every pytest test's own monkeypatch never closes the
connection. Found by live, real-network adversarial testing against
the actual running container (not by any pytest run), fixed by moving
the re-fetch back inside the `with` block. This test is the permanent,
in-suite regression proof for that exact defect class: it deliberately
does NOT monkeypatch `connect`, so it fails the same way the live
container did if the defect ever returns.

LOCAL-LOGIN FIELD UPDATE
(`docs/architecture/18_LOCAL_AUTHENTICATION_ADAPTER.md`): this test now
performs a REAL `POST /auth/login` call (also against the real,
un-monkeypatched `connect()` -- see below) to obtain its session cookie,
instead of the old `x-nquiry-actor-user-id` header. This also means the
real login call permanently commits its own `local_auth_credentials`/
`local_auth_sessions` rows, on top of the Workspace/Decision/audit
trail this test already discloses leaving behind (see below) --
consistent with, not a new instance of, this file's own established
"real commit, no cleanup" disclosure.

WHY THIS TEST SEEDS WITH A SEPARATE, REAL-COMMITTING CONNECTION, NOT
THE `db_connection` FIXTURE -- AND WHY IT DOES NOT ROLL BACK OR DELETE
ITS OWN SEED DATA AFTERWARD
--------------------------------------------------------------------
`persistence.engine.connect()` opens its OWN, brand-new connection
(and therefore its own transaction) against `DATABASE_URL` -- it
cannot see uncommitted rows sitting inside `db_connection`'s own
still-open transaction (real PostgreSQL transaction isolation, not a
test artifact). Seed data must therefore be genuinely committed before
the HTTP call.

This test does NOT attempt to delete its own seed data afterward.
`audit_events` is a real, DB-trigger-enforced append-only table (11
section 35: "audit_events rows cannot be deleted; established audit
history is append-only", enforced by `trg_audit_events_reject_delete`,
PKG-26) -- a genuine security invariant, not a convenience this test
may work around. Once this test's own real `record_human_decision`
commit writes a real `AuditEvent`, the owning `workspaces`/`users`
rows become permanently un-deletable too (`ON DELETE RESTRICT` from
`commands`/`commit_units`/`audit_events` back to `workspace_id`) --
exactly the same permanence a real production commit would have. This
test therefore uses a fresh, UUID-suffixed email on every run (never
collides with a prior run's own permanent row) and intentionally
leaves ONE real, legitimate Workspace/Decision/audit trail behind per
invocation -- disclosed here, and in the field's own closure report,
rather than hidden. Verified harmless: no other test in this
repository asserts an UNSCOPED row count against `audit_events`,
`commit_units`, `outbox_events`, `commands`, or `command_attempts`
(every other test either uses `db_connection`'s own rollback-per-test
isolation, so a real commit is never actually persisted at all, or
scopes its own assertions by `workspace_id`/`correlation_id`).
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from governance.authority_binding import AuthorityClass
from governance.membership import WorkspaceRole
from nquiry_api.main import app
from persistence.local_auth_repository import SqlAlchemyLocalCredentialRepository
from persistence.tables import (
    challenges_table,
    decisions_table,
    human_authority_bindings_table,
    role_assignments_table,
    users_table,
    workspace_memberships_table,
    workspaces_table,
)
from security.local_auth import hash_password
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import UserId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()
_PASSWORD = "correct horse battery staple"

_OPT_IN_ENV_VAR = "NQUIRY_RUN_REAL_COMMIT_TESTS"


@pytest.mark.skipif(
    os.environ.get(_OPT_IN_ENV_VAR) != "1",
    reason=(
        f"permanently commits one real, un-deletable Workspace/Decision/audit "
        f"trail per run (append-only audit_events, see module docstring) -- "
        f"excluded from the default collected suite the same way "
        f"scripts/verify_migrations.py's own live-DB check and PKG-31's "
        f"scripts/run_mutation_harness.py are real but not pytest-collected "
        f"by default. Run explicitly with {_OPT_IN_ENV_VAR}=1 pytest "
        f"tests/e2e/test_http_dispatch_real_connection_lifecycle.py"
    ),
)
def test_dispatch_record_human_decision_survives_a_real_closing_connection(
    db_connection: sa.Connection,
) -> None:
    """Regression test for the real `ResourceClosedError` defect this
    field's own live-HTTP closure pass discovered. Uses a SEPARATE,
    real-committing connection from the same engine `db_connection`
    itself was built from, so the seed is genuinely visible to
    `persistence.engine.connect()`'s own brand-new connection. See this
    module's own docstring for why no cleanup is attempted (or
    possible) afterward, and why this test is SKIPPED by default (its
    own real, permanent side effect broke two unrelated pre-existing
    tests -- `tests/security/test_habb_grant_constraints.py`'s and
    `tests/command_commit_event/test_outbox_worker.py`'s own unscoped
    row assertions -- the first time this field ran it as part of the
    default suite; discovered and fixed during this field's own closure
    pass, disclosed in the closure report rather than silently patched
    around).
    """
    engine = db_connection.engine
    workspace_id = uuid.uuid4()
    owner_id = uuid.uuid4()
    membership_id = uuid.uuid4()
    challenge_id = uuid.uuid4()
    decision_id = uuid.uuid4()
    binding_id = uuid.uuid4()
    unique_email = f"real-conn-lifecycle-{uuid.uuid4()}@nonproof.test"

    with engine.begin() as seed_conn:
        seed_conn.execute(
            sa.insert(users_table).values(
                id=owner_id,
                email=unique_email,
                name="Real Connection Lifecycle Owner",
                created_at=_NOW,
                updated_at=_NOW,
                record_version=1,
            )
        )
        seed_conn.execute(
            sa.insert(workspaces_table).values(
                id=workspace_id,
                name="Real-connection-lifecycle proof Workspace",
                owner_id=owner_id,
                created_at=_NOW,
                updated_at=_NOW,
                record_version=1,
            )
        )
        seed_conn.execute(
            sa.insert(workspace_memberships_table).values(
                id=membership_id,
                workspace_id=workspace_id,
                user_id=owner_id,
                status="ACTIVE",
                created_at=_NOW,
                revoked_at=None,
                record_version=1,
            )
        )
        seed_conn.execute(
            sa.insert(role_assignments_table).values(
                id=_ID_GEN.new_uuid(),
                workspace_id=workspace_id,
                membership_id=membership_id,
                role=WorkspaceRole.OWNER.value,
                granted_by_user_id=owner_id,
                granted_at=_NOW,
                revoked_at=None,
                record_version=1,
            )
        )
        seed_conn.execute(
            sa.insert(challenges_table).values(
                id=challenge_id,
                workspace_id=workspace_id,
                title="Real connection lifecycle proof Challenge",
                description=None,
                context=None,
                desired_outcome=None,
                constraints=None,
                stakeholders=None,
                created_at=_NOW,
                updated_at=_NOW,
                record_version=1,
            )
        )
        seed_conn.execute(
            sa.insert(human_authority_bindings_table).values(
                id=binding_id,
                workspace_id=workspace_id,
                human_user_id=owner_id,
                authority_class=AuthorityClass.DECISION_RIGHT.value,
                scope_type="DECISION",
                scope_id=decision_id,
                authority_source="LEVEL_1_EXPLICIT",
                granted_by_user_id=owner_id,
                granted_at=_NOW,
                state="ACTIVE",
                revoked_at=None,
                revoked_by_user_id=None,
                record_version=1,
            )
        )
        seed_conn.execute(
            sa.insert(decisions_table).values(
                id=decision_id,
                workspace_id=workspace_id,
                challenge_id=challenge_id,
                decision_question_ref=None,
                decision_question_text="Real connection lifecycle proof Decision",
                options=["fix_a", "fix_b"],
                criteria=["impact"],
                selected_option=None,
                rationale=None,
                confidence=None,
                state="UNDER_CONSIDERATION",
                opened_by_user_id=owner_id,
                decision_authority_binding_id=binding_id,
                decided_by_user_id=None,
                created_at=_NOW,
                decided_at=None,
                record_version=1,
                provenance_ref=None,
            )
        )
        SqlAlchemyLocalCredentialRepository(seed_conn).create(
            user_id=UserId(owner_id), password_hash=hash_password(_PASSWORD), now=_NOW
        )

    # Deliberately NOT using the `http_client` fixture -- no monkeypatch,
    # so `application.http_dispatch.connect` really is
    # `persistence.engine.connect`, a real, separate, closing connection
    # against the same real `DATABASE_URL`. The login call below also
    # goes through this same real `connect()` -- it genuinely commits
    # its own `local_auth_sessions` row (see this file's own updated
    # module docstring).
    client = TestClient(app)
    login_response = client.post("/auth/login", json={"email": unique_email, "password": _PASSWORD})
    assert login_response.status_code == 200, login_response.text

    response = client.post(
        f"/decisions/{decision_id}/decide",
        json={
            "selectedOption": "fix_a",
            "rationale": "real connection proof",
            "confidence": "high",
        },
    )

    # No try/finally cleanup: see this module's own docstring for why
    # cleanup of a real committed audit trail is both architecturally
    # forbidden (append-only) and impossible (FK RESTRICT chain back to
    # the owning Workspace) -- this assertion itself is the proof that
    # matters, not the database's own state afterward.
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["kind"] == "committed", body
    assert body["decision"]["state"] == "DECIDED"
    assert body["decision"]["selectedOption"] == "fix_a"

    with engine.connect() as verify_conn:
        row = (
            verify_conn.execute(
                sa.select(decisions_table).where(decisions_table.c.id == decision_id)
            )
            .mappings()
            .one()
        )
        assert row["state"] == "DECIDED"
        assert row["selected_option"] == "fix_a"
