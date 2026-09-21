"""T10 END-TO-END TEST: `POST /decisions/{decisionId}/decide`
(Architecture 17), through the REAL FastAPI app, against real
PostgreSQL.

LOCAL-LOGIN FIELD UPDATE
(`docs/architecture/18_LOCAL_AUTHENTICATION_ADAPTER.md`): identity now
comes from a real, verified `nquiry_session` cookie issued by a real
`POST /auth/login` call -- see `test_http_session_view.py`'s own
updated module docstring for the full rationale (shared verbatim,
since both routes call the identical `_resolve_actor_from_session`
internally). The cross-cutting adversarial session-verification matrix
lives once in `tests/e2e/test_http_auth.py`; this file keeps its own
write-path-specific happy paths and denials, plus one dedicated
forged-header-is-inert proof (this is the CONSEQUENTIAL write route --
worth its own explicit proof, not just an inference from the read
route's own coverage).

Same `http_client` connection-reuse fixture technique as
`test_http_session_view.py` -- see that file's own module docstring for
why `application.http_dispatch.connect` (not `persistence.engine.connect`,
a different name binding) is the correct monkeypatch target.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone

import application.http_dispatch as http_dispatch
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
)
from security.local_auth import hash_password
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import ChallengeId, DecisionId, UserId, WorkspaceId
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import (
    NonProofWorkspaceBootstrap,
    NonProofWorkspaceBootstrapResult,
)

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()
_PASSWORD = "correct horse battery staple"


@pytest.fixture
def http_client(
    db_connection: sa.Connection, monkeypatch: pytest.MonkeyPatch
) -> Iterator[TestClient]:
    @contextmanager
    def _reuse_test_connection() -> Iterator[sa.Connection]:
        yield db_connection

    monkeypatch.setattr(http_dispatch, "connect", _reuse_test_connection)
    yield TestClient(app)


def _bootstrap(db_connection: sa.Connection, *, email: str) -> NonProofWorkspaceBootstrapResult:
    result = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN).seed(
        owner_email=email
    )
    db_connection.execute(
        sa.insert(role_assignments_table).values(
            id=_ID_GEN.new_uuid(),
            workspace_id=result.workspace_id.value,
            membership_id=result.membership_id,
            role=WorkspaceRole.OWNER.value,
            granted_by_user_id=result.owner_user_id.value,
            granted_at=_NOW,
            revoked_at=None,
            record_version=1,
        )
    )
    SqlAlchemyLocalCredentialRepository(db_connection).create(
        user_id=result.owner_user_id, password_hash=hash_password(_PASSWORD), now=_NOW
    )
    return result


def _login(http_client: TestClient, *, email: str) -> None:
    response = http_client.post("/auth/login", json={"email": email, "password": _PASSWORD})
    assert response.status_code == 200, response.text


def _seed_challenge(db_connection: sa.Connection, *, workspace_id: WorkspaceId) -> ChallengeId:
    challenge_id = ChallengeId(_ID_GEN.new_uuid())
    db_connection.execute(
        sa.insert(challenges_table).values(
            id=challenge_id.value,
            workspace_id=workspace_id.value,
            title="Architecture 17 decide-endpoint proof Challenge",
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
    return challenge_id


def _seed_decision_under_consideration(
    db_connection: sa.Connection,
    *,
    workspace_id: WorkspaceId,
    challenge_id: ChallengeId,
    decided_by_user_id: UserId,
) -> DecisionId:
    decision_id = DecisionId(_ID_GEN.new_uuid())
    binding_id = _ID_GEN.new_uuid()
    db_connection.execute(
        sa.insert(human_authority_bindings_table).values(
            id=binding_id,
            workspace_id=workspace_id.value,
            human_user_id=decided_by_user_id.value,
            authority_class=AuthorityClass.DECISION_RIGHT.value,
            scope_type="DECISION",
            scope_id=decision_id.value,
            authority_source="LEVEL_1_EXPLICIT",
            granted_by_user_id=decided_by_user_id.value,
            granted_at=_NOW,
            state="ACTIVE",
            revoked_at=None,
            revoked_by_user_id=None,
            record_version=1,
        )
    )
    db_connection.execute(
        sa.insert(decisions_table).values(
            id=decision_id.value,
            workspace_id=workspace_id.value,
            challenge_id=challenge_id.value,
            decision_question_ref=None,
            decision_question_text="Which fix ships first?",
            options=["fix_a", "fix_b"],
            criteria=["impact", "effort"],
            selected_option=None,
            rationale=None,
            confidence=None,
            state="UNDER_CONSIDERATION",
            opened_by_user_id=decided_by_user_id.value,
            decision_authority_binding_id=binding_id,
            decided_by_user_id=None,
            created_at=_NOW,
            decided_at=None,
            record_version=1,
            provenance_ref=None,
        )
    )
    return decision_id


def test_http_record_decision_happy_path_commits_a_real_decision(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    result = _bootstrap(db_connection, email="http-decide-happy@nonproof.test")
    challenge_id = _seed_challenge(db_connection, workspace_id=result.workspace_id)
    decision_id = _seed_decision_under_consideration(
        db_connection,
        workspace_id=result.workspace_id,
        challenge_id=challenge_id,
        decided_by_user_id=result.owner_user_id,
    )
    _login(http_client, email="http-decide-happy@nonproof.test")

    response = http_client.post(
        f"/decisions/{decision_id.value}/decide",
        json={"selectedOption": "fix_a", "rationale": "higher impact", "confidence": "high"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "committed"
    assert body["decision"]["decisionId"] == str(decision_id.value)
    assert body["decision"]["state"] == "DECIDED"
    assert body["decision"]["selectedOption"] == "fix_a"
    assert body["decision"]["decidedByUserId"] == str(result.owner_user_id.value)

    # The proof is the REAL row, independent of the response body.
    row = (
        db_connection.execute(
            sa.select(decisions_table).where(decisions_table.c.id == decision_id.value)
        )
        .mappings()
        .one()
    )
    assert row["state"] == "DECIDED"
    assert row["selected_option"] == "fix_a"


def test_http_record_decision_denies_a_request_with_no_session(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    result = _bootstrap(db_connection, email="http-decide-nosession@nonproof.test")
    challenge_id = _seed_challenge(db_connection, workspace_id=result.workspace_id)
    decision_id = _seed_decision_under_consideration(
        db_connection,
        workspace_id=result.workspace_id,
        challenge_id=challenge_id,
        decided_by_user_id=result.owner_user_id,
    )

    response = http_client.post(
        f"/decisions/{decision_id.value}/decide",
        json={"selectedOption": "fix_a", "rationale": None, "confidence": None},
    )

    assert response.status_code == 401
    assert response.json()["kind"] == "denied"

    row = (
        db_connection.execute(
            sa.select(decisions_table).where(decisions_table.c.id == decision_id.value)
        )
        .mappings()
        .one()
    )
    assert row["state"] == "UNDER_CONSIDERATION"


def test_http_record_decision_ignores_a_forged_actor_class_header(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    """Adversarial, write-path-specific: a real, logged-in session
    smuggling an `x-nquiry-actor-class: AI_PROCESSOR` header alongside
    it still commits as the real logged-in HUMAN_USER -- the header is
    fully inert dead input on the consequential write route too, not
    only the read route (`test_http_auth.py`'s own sibling proof)."""
    result = _bootstrap(db_connection, email="http-decide-headerignored@nonproof.test")
    challenge_id = _seed_challenge(db_connection, workspace_id=result.workspace_id)
    decision_id = _seed_decision_under_consideration(
        db_connection,
        workspace_id=result.workspace_id,
        challenge_id=challenge_id,
        decided_by_user_id=result.owner_user_id,
    )
    _login(http_client, email="http-decide-headerignored@nonproof.test")

    response = http_client.post(
        f"/decisions/{decision_id.value}/decide",
        headers={
            "x-nquiry-actor-user-id": str(uuid.uuid4()),
            "x-nquiry-actor-class": "AI_PROCESSOR",
        },
        json={"selectedOption": "fix_a", "rationale": None, "confidence": None},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "committed"
    assert body["decision"]["decidedByUserId"] == str(result.owner_user_id.value)


def test_http_record_decision_denies_role_only_actor_with_no_binding(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    result = _bootstrap(db_connection, email="http-decide-denial@nonproof.test")
    challenge_id = _seed_challenge(db_connection, workspace_id=result.workspace_id)
    decision_id = DecisionId(_ID_GEN.new_uuid())
    binding_id = _ID_GEN.new_uuid()
    # Binding scoped to a DIFFERENT decision -- the owner has SOME
    # DECISION_RIGHT binding, just not one that covers this decision.
    db_connection.execute(
        sa.insert(human_authority_bindings_table).values(
            id=binding_id,
            workspace_id=result.workspace_id.value,
            human_user_id=result.owner_user_id.value,
            authority_class=AuthorityClass.DECISION_RIGHT.value,
            scope_type="DECISION",
            scope_id=uuid.uuid4(),
            authority_source="LEVEL_1_EXPLICIT",
            granted_by_user_id=result.owner_user_id.value,
            granted_at=_NOW,
            state="ACTIVE",
            revoked_at=None,
            revoked_by_user_id=None,
            record_version=1,
        )
    )
    db_connection.execute(
        sa.insert(decisions_table).values(
            id=decision_id.value,
            workspace_id=result.workspace_id.value,
            challenge_id=challenge_id.value,
            decision_question_ref=None,
            decision_question_text="Which fix ships first?",
            options=["fix_a", "fix_b"],
            criteria=[],
            selected_option=None,
            rationale=None,
            confidence=None,
            state="UNDER_CONSIDERATION",
            opened_by_user_id=result.owner_user_id.value,
            decision_authority_binding_id=binding_id,
            decided_by_user_id=None,
            created_at=_NOW,
            decided_at=None,
            record_version=1,
            provenance_ref=None,
        )
    )
    _login(http_client, email="http-decide-denial@nonproof.test")

    response = http_client.post(
        f"/decisions/{decision_id.value}/decide",
        json={"selectedOption": "fix_a", "rationale": None, "confidence": None},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "denied"
    assert body["result"] == "DENY"

    row = (
        db_connection.execute(
            sa.select(decisions_table).where(decisions_table.c.id == decision_id.value)
        )
        .mappings()
        .one()
    )
    assert row["state"] == "UNDER_CONSIDERATION"


def test_http_record_decision_rejects_a_non_candidate_option(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    result = _bootstrap(db_connection, email="http-decide-notcandidate@nonproof.test")
    challenge_id = _seed_challenge(db_connection, workspace_id=result.workspace_id)
    decision_id = _seed_decision_under_consideration(
        db_connection,
        workspace_id=result.workspace_id,
        challenge_id=challenge_id,
        decided_by_user_id=result.owner_user_id,
    )
    _login(http_client, email="http-decide-notcandidate@nonproof.test")

    response = http_client.post(
        f"/decisions/{decision_id.value}/decide",
        json={"selectedOption": "fix_z_not_a_real_option", "rationale": None, "confidence": None},
    )

    assert response.status_code == 200
    assert response.json()["kind"] == "rejected"


def test_http_record_decision_rejects_an_unknown_decision_id(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    _bootstrap(db_connection, email="http-decide-unknown@nonproof.test")
    _login(http_client, email="http-decide-unknown@nonproof.test")

    response = http_client.post(
        f"/decisions/{uuid.uuid4()}/decide",
        json={"selectedOption": "fix_a", "rationale": None, "confidence": None},
    )

    assert response.status_code == 200
    assert response.json()["kind"] == "rejected"


def test_duplicate_decide_request_does_not_double_commit(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    """Adversarial: replaying the same POST after a real commit does
    not silently re-commit -- the second call's own fresh boundary
    re-evaluation sees `state == DECIDED` already and denies (BND-007
    state-transition legality), never a second `committed` result."""
    result = _bootstrap(db_connection, email="http-decide-duplicate@nonproof.test")
    challenge_id = _seed_challenge(db_connection, workspace_id=result.workspace_id)
    decision_id = _seed_decision_under_consideration(
        db_connection,
        workspace_id=result.workspace_id,
        challenge_id=challenge_id,
        decided_by_user_id=result.owner_user_id,
    )
    _login(http_client, email="http-decide-duplicate@nonproof.test")
    payload = {"selectedOption": "fix_a", "rationale": None, "confidence": None}

    first = http_client.post(f"/decisions/{decision_id.value}/decide", json=payload)
    second = http_client.post(f"/decisions/{decision_id.value}/decide", json=payload)

    assert first.json()["kind"] == "committed"
    assert second.json()["kind"] != "committed"
