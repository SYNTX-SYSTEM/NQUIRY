#!/usr/bin/env python3
"""Idempotent local demo seed: creates (or reuses) one demo Workspace
scenario and a real local login credential for it, so a human can start
the local stack (`docs/RUNTIME_OPERATION.md`), open a browser, log in,
and actually see something.

DEV-ONLY, NOT A PRODUCTION BOOTSTRAP: uses
`test_support.nonproof_bootstrap.NonProofWorkspaceBootstrap` for the
Workspace/owner/membership/governance root -- that module's own
docstring already names exactly this use ("test/dev-only Workspace
governance-root fixture"). `scripts/check_test_only_imports.py` does
not scan `scripts/` (only `packages/`, `apps/api/src`, `apps/worker/src`
-- this script is a manual local dev tool, never imported by production
code), so this is not a violation of that guard; it is still, and
remains, exactly the disclosed `NON_PROOF_FIXTURE` HARD-DEP-001
limitation every other fixture in this codebase carries -- printed
below, not hidden. Running this script never closes, and does not
attempt to close, HARD-DEP-001 (legitimate first Workspace
governance-root bootstrap) or HARD-DEP-002 (real AI provider
eligibility).

The local login credential this script creates
(`local_auth_credentials`, migration `05794035ef3c`) is real: a genuine
PBKDF2 password hash, checked by a real `POST /auth/login` call. GAP-14-001
(real OIDC provider selection) remains open — this is the local
"deterministic test adapter" 14 §32 authorizes, not a production
identity provider.

Idempotent: safe to run multiple times against the same database. On a
fresh database it seeds a new demo Workspace/Challenge/Session/Burst/
Decision. Against a database that already has this demo owner
(matched by `DEMO_OWNER_EMAIL`), it reuses the existing Workspace/
Session and only adds the login credential if one does not already
exist.

Usage: DATABASE_URL=postgresql+psycopg://... python scripts/seed_local_demo.py
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone

import sqlalchemy as sa
from governance.authority_binding import AuthorityBindingState, AuthorityClass
from governance.membership import WorkspaceRole
from persistence.local_auth_repository import SqlAlchemyLocalCredentialRepository
from persistence.tables import (
    burst_question_memberships_table,
    challenges_table,
    decisions_table,
    human_authority_bindings_table,
    question_bursts_table,
    questions_table,
    role_assignments_table,
    sessions_table,
    users_table,
    workspaces_table,
)
from security.local_auth import hash_password
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import ChallengeId, DecisionId, SessionId, UserId, WorkspaceId
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

DEMO_OWNER_EMAIL = "demo-owner@nonproof.test"
DEMO_PASSWORD = "nquiry-demo-2026"  # documented in docs/RUNTIME_OPERATION.md, local dev only


class _RealClock:
    """`semantic_types.clock.Clock` port, real wall-clock -- avoids this
    script depending on `test_support.clock.FixedClock` for what is a
    genuine, timestamped local dev seed, not a deterministic test."""

    def now(self) -> datetime:
        return datetime.now(timezone.utc)


def _seed_demo_scenario(
    connection: sa.Connection, *, workspace_id: WorkspaceId, owner_user_id: UserId, now: datetime
) -> tuple[SessionId]:
    id_gen = SystemIdGenerator()
    challenge_id = ChallengeId(id_gen.new_uuid())
    connection.execute(
        sa.insert(challenges_table).values(
            id=challenge_id.value,
            workspace_id=workspace_id.value,
            title="Signup conversion dropped 18% after the redesign",
            description="Investigate the cause and decide the next step.",
            context=None,
            desired_outcome=None,
            constraints=None,
            stakeholders=None,
            created_at=now,
            updated_at=now,
            record_version=1,
        )
    )
    session_id = SessionId(id_gen.new_uuid())
    connection.execute(
        sa.insert(sessions_table).values(
            id=session_id.value,
            challenge_id=challenge_id.value,
            workspace_id=workspace_id.value,
            applied_method_key="QUESTION_BURST",
            applied_method_version="1.0",
            state="DRAFT",
            created_at=now,
            updated_at=now,
            closed_at=None,
            record_version=1,
        )
    )
    burst_id = id_gen.new_uuid()
    connection.execute(
        sa.insert(question_bursts_table).values(
            id=burst_id,
            session_id=session_id.value,
            workspace_id=workspace_id.value,
            state="PREPARED",
            mode="HUMAN_ONLY",
            started_at=None,
            paused_at=None,
            completed_at=None,
            frozen_membership_fingerprint=None,
            record_version=1,
        )
    )
    demo_questions = (
        "Did the new checkout flow introduce extra required fields?",
        "Is the drop concentrated in mobile or desktop traffic?",
        "Did page load time regress after the redesign shipped?",
    )
    for order, text in enumerate(demo_questions, start=1):
        question_id = id_gen.new_uuid()
        connection.execute(
            sa.insert(questions_table).values(
                id=question_id,
                challenge_id=challenge_id.value,
                workspace_id=workspace_id.value,
                original_text=text,
                normalized_text=None,
                origin="HUMAN",
                author_user_id=owner_user_id.value,
                created_at=now,
                record_version=1,
            )
        )
        connection.execute(
            sa.insert(burst_question_memberships_table).values(
                id=id_gen.new_uuid(),
                question_burst_id=burst_id,
                question_id=question_id,
                workspace_id=workspace_id.value,
                captured_order=order,
                captured_at=now,
                capture_actor_user_id=owner_user_id.value,
                capture_origin="HUMAN",
                record_version=1,
            )
        )
    decision_id = DecisionId(id_gen.new_uuid())
    binding_id = id_gen.new_uuid()
    connection.execute(
        sa.insert(human_authority_bindings_table).values(
            id=binding_id,
            workspace_id=workspace_id.value,
            human_user_id=owner_user_id.value,
            authority_class=AuthorityClass.DECISION_RIGHT.value,
            scope_type="DECISION",
            scope_id=decision_id.value,
            authority_source="LEVEL_1_EXPLICIT",
            granted_by_user_id=owner_user_id.value,
            granted_at=now,
            state=AuthorityBindingState.ACTIVE.value,
            revoked_at=None,
            revoked_by_user_id=None,
            record_version=1,
        )
    )
    connection.execute(
        sa.insert(decisions_table).values(
            id=decision_id.value,
            workspace_id=workspace_id.value,
            challenge_id=challenge_id.value,
            decision_question_ref=None,
            decision_question_text="What should we ship first to recover conversion?",
            options=["fix_checkout_fields", "fix_mobile_perf", "run_more_research"],
            criteria=["expected_impact", "implementation_effort"],
            selected_option=None,
            rationale=None,
            confidence=None,
            state="UNDER_CONSIDERATION",
            opened_by_user_id=owner_user_id.value,
            decision_authority_binding_id=binding_id,
            decided_by_user_id=None,
            created_at=now,
            decided_at=None,
            record_version=1,
            provenance_ref=None,
        )
    )
    return (session_id,)


def main() -> int:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL is not set.", file=sys.stderr)
        return 1

    engine = sa.create_engine(database_url)
    now = datetime.now(timezone.utc)
    with engine.begin() as connection:
        existing_user = (
            connection.execute(
                sa.select(users_table).where(users_table.c.email == DEMO_OWNER_EMAIL)
            )
            .mappings()
            .one_or_none()
        )
        if existing_user is not None:
            owner_user_id = UserId(existing_user["id"])
            workspace_row = (
                connection.execute(
                    sa.select(workspaces_table).where(
                        workspaces_table.c.owner_id == existing_user["id"]
                    )
                )
                .mappings()
                .one()
            )
            workspace_id = WorkspaceId(workspace_row["id"])
            session_row = (
                connection.execute(
                    sa.select(sessions_table).where(
                        sessions_table.c.workspace_id == workspace_id.value
                    )
                )
                .mappings()
                .first()
            )
            if session_row is None:
                (session_id,) = _seed_demo_scenario(
                    connection, workspace_id=workspace_id, owner_user_id=owner_user_id, now=now
                )
                print(f"Reused existing owner {DEMO_OWNER_EMAIL}; seeded a new demo scenario.")
            else:
                session_id = SessionId(session_row["id"])
                print(f"Reused existing owner {DEMO_OWNER_EMAIL} and existing demo scenario.")
        else:
            result = NonProofWorkspaceBootstrap(connection, _RealClock(), SystemIdGenerator()).seed(
                owner_email=DEMO_OWNER_EMAIL
            )
            connection.execute(
                sa.insert(role_assignments_table).values(
                    id=SystemIdGenerator().new_uuid(),
                    workspace_id=result.workspace_id.value,
                    membership_id=result.membership_id,
                    role=WorkspaceRole.OWNER.value,
                    granted_by_user_id=result.owner_user_id.value,
                    granted_at=now,
                    revoked_at=None,
                    record_version=1,
                )
            )
            owner_user_id = result.owner_user_id
            workspace_id = result.workspace_id
            (session_id,) = _seed_demo_scenario(
                connection, workspace_id=workspace_id, owner_user_id=owner_user_id, now=now
            )
            print(f"Seeded a fresh demo Workspace for a new owner {DEMO_OWNER_EMAIL}.")

        credential_repository = SqlAlchemyLocalCredentialRepository(connection)
        if credential_repository.get_by_email(DEMO_OWNER_EMAIL) is None:
            credential_repository.create(
                user_id=owner_user_id, password_hash=hash_password(DEMO_PASSWORD), now=now
            )
            print(f"Created a local login credential for {DEMO_OWNER_EMAIL}.")
        else:
            print(f"A local login credential for {DEMO_OWNER_EMAIL} already exists.")

    print()
    print("NON_PROOF_FIXTURE — this Workspace's own governance root comes from")
    print("NonProofWorkspaceBootstrap, disclosed test/dev-only fixture legitimacy.")
    print("HARD-DEP-001 (legitimate first Workspace governance-root bootstrap)")
    print("remains open and untouched by this script.")
    print()
    print(f"Login email:    {DEMO_OWNER_EMAIL}")
    print(f"Login password: {DEMO_PASSWORD}")
    print("Open:           http://localhost:3000/")
    print(
        f"After login you land on: "
        f"http://localhost:3000/workspaces/{workspace_id.value}/sessions/{session_id.value}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
