"""T0 semantic tests: strong identity value objects.

Source: 14_IMPLEMENTATION_SEQUENCE.md §5. Proof oracle here is the
type/value itself (construction succeeds/fails, equality, hashing) —
there is no canonical/governance state yet at Phase 0 to prefer over
it per the test oracle priority in 15 §1.
"""

from __future__ import annotations

import uuid

import pytest
from semantic_types.ids import InvalidIdentityValue, SessionId, UserId, WorkspaceId


def test_distinct_identity_types_are_not_interchangeable() -> None:
    """P-22-adjacent non-collapse check: a WorkspaceId and a UserId built
    from the *same* UUID value must remain distinct types and must not
    compare equal — mixing them is the exact class of bug 14 §5 exists
    to make structurally impossible.
    """
    raw = uuid.uuid4()
    workspace_id = WorkspaceId(raw)
    user_id = UserId(raw)

    assert workspace_id != user_id
    assert type(workspace_id) is not type(user_id)
    assert not isinstance(workspace_id, UserId)
    assert not isinstance(user_id, WorkspaceId)


def test_identity_is_frozen_and_hashable() -> None:
    session_id = SessionId(uuid.uuid4())
    with pytest.raises(AttributeError):
        session_id.value = uuid.uuid4()  # type: ignore[misc]
    # Hashable => usable as a dict/set key, needed for e.g. Workspace-keyed lookups later.
    lookup = {session_id: "ok"}
    assert lookup[session_id] == "ok"


def test_identity_equality_is_by_value() -> None:
    raw = uuid.uuid4()
    assert WorkspaceId(raw) == WorkspaceId(raw)
    assert WorkspaceId(raw) != WorkspaceId(uuid.uuid4())


def test_identity_rejects_non_uuid_value() -> None:
    with pytest.raises(InvalidIdentityValue):
        WorkspaceId("not-a-uuid")  # type: ignore[arg-type]


def test_identity_from_str_round_trips() -> None:
    raw = uuid.uuid4()
    assert WorkspaceId.from_str(str(raw)) == WorkspaceId(raw)


def test_identity_from_str_rejects_malformed_string() -> None:
    with pytest.raises(InvalidIdentityValue):
        WorkspaceId.from_str("not-a-uuid")
