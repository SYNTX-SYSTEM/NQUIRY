"""T-HTTPWorkspaces END-TO-END TEST (F01 WU-01.8): `POST /workspaces`,
`GET /workspaces`, `GET /workspaces/{workspaceId}`,
`POST /workspaces/{workspaceId}/members`,
`POST /workspaces/{workspaceId}/authority-bindings/{bindingId}/revoke`,
through the REAL FastAPI app, against real PostgreSQL.

Same `http_client` connection-reuse fixture technique as
`test_http_auth.py`/`test_http_session_view.py` -- see those files' own
module docstrings for why `application.http_dispatch.connect` is the
correct monkeypatch target. Every Workspace/membership/binding here is
produced through the real HTTP routes themselves (not a direct
repository call and not `NonProofWorkspaceBootstrap`) -- this is the
first test file in this Field to exercise the full
HTTP -> dispatch -> Command -> real PostgreSQL path for
`create_workspace`/`add_member`/`revoke_human_authority_binding`, not
just the Command layer directly.
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
from nquiry_api.main import app
from persistence.local_auth_repository import SqlAlchemyLocalCredentialRepository
from persistence.tables import users_table
from security.local_auth import hash_password
from semantic_types.ids import UserId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
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


def _register(db_connection: sa.Connection, *, email: str, password: str = _PASSWORD) -> uuid.UUID:
    """A plain, real `users` row plus a real password credential -- NO
    `NonProofWorkspaceBootstrap`, no pre-existing Workspace. F01 WU-01.4
    (HARD-DEP-001 Option A) means the real `POST /workspaces` route
    itself is now how a brand-new human founds their first Workspace;
    seeding one via a fixture here would defeat the point of this
    file's own HTTP-first proof."""
    user_id = uuid.uuid4()
    db_connection.execute(
        sa.insert(users_table).values(
            id=user_id,
            email=email,
            name="Real Human",
            record_version=1,
            created_at=_NOW,
            updated_at=_NOW,
        )
    )
    SqlAlchemyLocalCredentialRepository(db_connection).create(
        user_id=UserId(user_id), password_hash=hash_password(password), now=_NOW
    )
    return user_id


def _login(http_client: TestClient, *, email: str, password: str = _PASSWORD) -> None:
    response = http_client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text


# ---------------------------------------------------------------------------
# POST /workspaces
# ---------------------------------------------------------------------------


def test_create_workspace_happy_path(db_connection: sa.Connection, http_client: TestClient) -> None:
    _register(db_connection, email="founder-create@real-human.test")
    _login(http_client, email="founder-create@real-human.test")

    response = http_client.post("/workspaces", json={"name": "My New Workspace"})

    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "ok"
    uuid.UUID(body["workspaceId"])  # a real UUID, not an echo of client input


def test_create_workspace_denies_with_no_session(http_client: TestClient) -> None:
    response = http_client.post("/workspaces", json={"name": "Nope"})
    assert response.status_code == 401
    assert response.json()["kind"] == "denied"


def test_create_workspace_rejects_an_empty_name(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    _register(db_connection, email="founder-empty-name@real-human.test")
    _login(http_client, email="founder-empty-name@real-human.test")

    response = http_client.post("/workspaces", json={"name": "   "})

    assert response.status_code == 200
    assert response.json()["kind"] == "rejected"


# ---------------------------------------------------------------------------
# GET /workspaces
# ---------------------------------------------------------------------------


def test_list_workspaces_shows_only_the_callers_own(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    _register(db_connection, email="owner-list@real-human.test")
    _login(http_client, email="owner-list@real-human.test")
    created = http_client.post("/workspaces", json={"name": "Visible To Me"}).json()

    _register(db_connection, email="stranger-list@real-human.test")
    _login(http_client, email="stranger-list@real-human.test")

    response = http_client.get("/workspaces")

    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "ok"
    workspace_ids = [w["workspaceId"] for w in body["workspaces"]]
    assert created["workspaceId"] not in workspace_ids


def test_list_workspaces_is_empty_for_a_human_with_none_yet(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    _register(db_connection, email="nobody-list@real-human.test")
    _login(http_client, email="nobody-list@real-human.test")

    response = http_client.get("/workspaces")

    assert response.status_code == 200
    assert response.json() == {"kind": "ok", "workspaces": []}


def test_list_workspaces_denies_with_no_session(http_client: TestClient) -> None:
    response = http_client.get("/workspaces")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /workspaces/{workspaceId}  -- orientation (WU-01.3 + WU-01.7)
# ---------------------------------------------------------------------------


def test_orientation_shows_the_founder_as_governance_capable(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    _register(db_connection, email="founder-orientation@real-human.test")
    _login(http_client, email="founder-orientation@real-human.test")
    workspace_id = http_client.post("/workspaces", json={"name": "Orientation Target"}).json()[
        "workspaceId"
    ]

    response = http_client.get(f"/workspaces/{workspace_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "ok"
    assert body["role"] == "Owner"
    assert body["governanceCapable"] is True
    assert body["authorized"] is True
    assert body["heldAuthorityClasses"] == ["WORKSPACE_GOVERNANCE_RIGHT"]
    assert body["workspace"]["workspaceId"] == workspace_id


def test_orientation_denies_a_non_member(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    _register(db_connection, email="founder-orientation-stranger@real-human.test")
    _login(http_client, email="founder-orientation-stranger@real-human.test")
    workspace_id = http_client.post("/workspaces", json={"name": "Not Yours"}).json()["workspaceId"]

    _register(db_connection, email="stranger-orientation@real-human.test")
    _login(http_client, email="stranger-orientation@real-human.test")

    response = http_client.get(f"/workspaces/{workspace_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "denied"
    assert body["reasonCode"] == "NOT_A_WORKSPACE_MEMBER"


def test_orientation_denies_a_non_existent_workspace(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    _register(db_connection, email="founder-orientation-nowhere@real-human.test")
    _login(http_client, email="founder-orientation-nowhere@real-human.test")

    response = http_client.get(f"/workspaces/{uuid.uuid4()}")

    assert response.status_code == 200
    assert response.json()["reasonCode"] == "WORKSPACE_NOT_FOUND"


def test_orientation_rejects_a_malformed_workspace_id(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    _register(db_connection, email="founder-orientation-malformed@real-human.test")
    _login(http_client, email="founder-orientation-malformed@real-human.test")

    response = http_client.get("/workspaces/not-a-real-uuid")

    assert response.status_code == 400


def test_orientation_denies_with_no_session(http_client: TestClient) -> None:
    response = http_client.get(f"/workspaces/{uuid.uuid4()}")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# POST /workspaces/{workspaceId}/members
# ---------------------------------------------------------------------------


def test_add_member_happy_path(db_connection: sa.Connection, http_client: TestClient) -> None:
    _register(db_connection, email="owner-add-member@real-human.test")
    _login(http_client, email="owner-add-member@real-human.test")
    workspace_id = http_client.post("/workspaces", json={"name": "Add Member Target"}).json()[
        "workspaceId"
    ]
    new_member_id = _register(db_connection, email="new-member-add@real-human.test")

    response = http_client.post(
        f"/workspaces/{workspace_id}/members",
        json={"userId": str(new_member_id), "role": "Contributor"},
    )

    assert response.status_code == 200
    assert response.json() == {"kind": "ok"}


def test_add_member_refuses_owner_role(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    _register(db_connection, email="owner-add-owner-role@real-human.test")
    _login(http_client, email="owner-add-owner-role@real-human.test")
    workspace_id = http_client.post("/workspaces", json={"name": "No Co-Owners"}).json()[
        "workspaceId"
    ]
    new_member_id = _register(db_connection, email="wants-co-owner-http@real-human.test")

    response = http_client.post(
        f"/workspaces/{workspace_id}/members",
        json={"userId": str(new_member_id), "role": "Owner"},
    )

    assert response.status_code == 200
    assert response.json()["kind"] == "rejected"
    assert "OWNER_ROLE_NOT_ASSIGNABLE" in response.json()["reasonCode"]


def test_add_member_denies_a_non_owner_caller(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    _register(db_connection, email="owner-add-nonowner@real-human.test")
    _login(http_client, email="owner-add-nonowner@real-human.test")
    workspace_id = http_client.post("/workspaces", json={"name": "Non-Owner Attack"}).json()[
        "workspaceId"
    ]
    contributor_id = _register(db_connection, email="contributor-add-nonowner@real-human.test")
    add_response = http_client.post(
        f"/workspaces/{workspace_id}/members",
        json={"userId": str(contributor_id), "role": "Contributor"},
    )
    assert add_response.status_code == 200

    _login(http_client, email="contributor-add-nonowner@real-human.test")
    victim_id = _register(db_connection, email="victim-add-nonowner@real-human.test")

    response = http_client.post(
        f"/workspaces/{workspace_id}/members",
        json={"userId": str(victim_id), "role": "Contributor"},
    )

    assert response.status_code == 200
    assert response.json()["kind"] == "denied"


def test_add_member_rejects_an_unknown_role_string(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    _register(db_connection, email="owner-add-unknown-role@real-human.test")
    _login(http_client, email="owner-add-unknown-role@real-human.test")
    workspace_id = http_client.post("/workspaces", json={"name": "Unknown Role Target"}).json()[
        "workspaceId"
    ]
    new_member_id = _register(db_connection, email="new-member-unknown-role@real-human.test")

    response = http_client.post(
        f"/workspaces/{workspace_id}/members",
        json={"userId": str(new_member_id), "role": "SuperAdmin"},
    )

    assert response.status_code == 200
    assert response.json()["kind"] == "rejected"
    assert "UNKNOWN_ROLE" in response.json()["reasonCode"]


def test_add_member_denies_with_no_session(http_client: TestClient) -> None:
    response = http_client.post(
        f"/workspaces/{uuid.uuid4()}/members",
        json={"userId": str(uuid.uuid4()), "role": "Contributor"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# POST /workspaces/{workspaceId}/authority-bindings/{bindingId}/revoke
# ---------------------------------------------------------------------------


def test_revoke_authority_binding_refuses_to_orphan_the_workspace(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    _register(db_connection, email="owner-revoke-http-orphan@real-human.test")
    _login(http_client, email="owner-revoke-http-orphan@real-human.test")
    workspace_id = http_client.post("/workspaces", json={"name": "No Self-Orphan HTTP"}).json()[
        "workspaceId"
    ]
    orientation = http_client.get(f"/workspaces/{workspace_id}").json()
    assert orientation["heldAuthorityClasses"] == ["WORKSPACE_GOVERNANCE_RIGHT"]
    binding_row = db_connection.execute(
        sa.text(
            "SELECT id FROM human_authority_bindings WHERE workspace_id = :ws "
            "AND authority_class = 'WORKSPACE_GOVERNANCE_RIGHT'"
        ),
        {"ws": workspace_id},
    ).one()
    binding_id = str(binding_row[0])

    response = http_client.post(
        f"/workspaces/{workspace_id}/authority-bindings/{binding_id}/revoke"
    )

    assert response.status_code == 200
    assert response.json()["kind"] == "rejected"
    assert "GOVERNANCE_ROOT_ORPHANING_REFUSED" in response.json()["reasonCode"]


def test_revoke_authority_binding_denies_a_non_existent_binding(
    db_connection: sa.Connection, http_client: TestClient
) -> None:
    _register(db_connection, email="owner-revoke-http-notfound@real-human.test")
    _login(http_client, email="owner-revoke-http-notfound@real-human.test")
    workspace_id = http_client.post("/workspaces", json={"name": "Not Found HTTP"}).json()[
        "workspaceId"
    ]

    response = http_client.post(
        f"/workspaces/{workspace_id}/authority-bindings/{uuid.uuid4()}/revoke"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "denied"
    assert body["reasonCode"] == "AUTHORITY_BINDING_NOT_FOUND"


def test_revoke_authority_binding_denies_with_no_session(http_client: TestClient) -> None:
    response = http_client.post(
        f"/workspaces/{uuid.uuid4()}/authority-bindings/{uuid.uuid4()}/revoke"
    )
    assert response.status_code == 401
