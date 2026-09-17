"""T1 DOMAIN INVARIANT TEST: `domain.session.Session` / `SessionState`.

13 §6 T1 scope: "Object identity, immutability, relation semantics."
The transition *topology* is T2 and lives in `tests/transitions/`.
"""

from __future__ import annotations

import dataclasses
import uuid
from datetime import datetime, timezone

import pytest
from domain.session import (
    INITIAL_SESSION_STATE,
    TERMINAL_SESSION_STATES,
    Session,
    SessionState,
)
from semantic_types.ids import ChallengeId, SessionId, WorkspaceId
from semantic_types.versions import MethodVersion, RecordVersion

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)

# 03 §13.1, transcribed independently of the enum under test so that a
# silent edit to `SessionState` fails here instead of agreeing with
# itself.
_SOURCE_DEFINED_STATES = (
    "DRAFT",
    "SETUP",
    "CHALLENGE_CAPTURE",
    "QUESTION_GENERATION",
    "QUESTION_CAPTURE",
    "ANALYSIS",
    "REFLECTION",
    "QUESTION_SELECTION",
    "INVESTIGATION",
    "EXPERIMENT",
    "ACTION",
    "REVIEW",
    "CLOSED",
)


def _session(**overrides: object) -> Session:
    defaults: dict[str, object] = {
        "session_id": SessionId(uuid.uuid4()),
        "challenge_id": ChallengeId(uuid.uuid4()),
        "workspace_id": WorkspaceId(uuid.uuid4()),
        "applied_method_key": "QUESTION_BURST",
        "applied_method_version": MethodVersion("1.0"),
        "state": SessionState.DRAFT,
        "created_at": _NOW,
        "updated_at": _NOW,
        "closed_at": None,
        "record_version": RecordVersion.initial(),
    }
    defaults.update(overrides)
    return Session(**defaults)  # type: ignore[arg-type]


def test_state_vocabulary_is_exactly_the_thirteen_source_defined_states() -> None:
    """03 §13.1 `[SPECIFIED]`, restated identically by 02 §11.5 and
    09 §27. Order matters: 03 §13.2 presents them as an ordered chain.
    """
    assert tuple(state.value for state in SessionState) == _SOURCE_DEFINED_STATES


def test_state_vocabulary_contains_no_cancellation_state() -> None:
    """03 §18 (GAP-03-001): LEVEL 1 defines no CANCELLED / ABANDONED /
    EXPIRED / VOID state and "03 does not invent one". A Session
    abandoned before REVIEW has no source-defined terminal transition,
    and 03 is explicit that this "is not a hidden skip to CLOSED".
    """
    names = {state.name for state in SessionState}

    assert names.isdisjoint({"CANCELLED", "ABANDONED", "EXPIRED", "VOID"})


def test_direct_enum_coercion_of_an_unknown_state_is_rejected() -> None:
    """Mandatory adversarial attack: direct enum coercion.

    A caller reaching `SessionState(...)` with a value from outside 03
    §13.1 gets a `ValueError`, not a new member. This is what makes the
    vocabulary closed rather than merely conventional.
    """
    with pytest.raises(ValueError):
        SessionState("DONE")
    with pytest.raises(ValueError):
        SessionState("closed")  # casing is part of the vocabulary


def test_session_is_immutable_and_exposes_no_state_setter() -> None:
    """14 PKG-05 ARCHITECTURAL_INVARIANTS: "ILLEGAL TRANSITION MUST NOT
    BE ENABLED BY GENERIC SETTER." The strongest form of that guarantee
    is that no setter exists at all -- checked structurally, not by
    convention.
    """
    session = _session()

    with pytest.raises(dataclasses.FrozenInstanceError):
        session.state = SessionState.CLOSED  # type: ignore[misc]

    setter_shaped = [
        name
        for name in dir(Session)
        if name.startswith(("set_", "update_", "advance", "transition_to", "setStatus"))
    ]
    assert setter_shaped == []


def test_state_must_be_a_session_state_not_a_string() -> None:
    """`STATE != STATUS STRING`: a Session holding the *string*
    "CLOSED" would be a status string wearing a state's name.
    """
    with pytest.raises(TypeError, match="state must be a SessionState"):
        _session(state="CLOSED")


def test_initial_state_is_draft() -> None:
    """03 TRN-SESS-001 CREATE_SESSION, NEXT STATE: DRAFT."""
    assert INITIAL_SESSION_STATE is SessionState.DRAFT


def test_closed_is_the_only_terminal_state() -> None:
    """03 §13.3 CLOSED: "The Session is terminal." No other state in
    the machine is.
    """
    assert frozenset({SessionState.CLOSED}) == TERMINAL_SESSION_STATES
    assert _session(state=SessionState.REVIEW).is_terminal is False
    assert _session(state=SessionState.CLOSED).is_terminal is True


def test_closed_at_may_not_be_set_on_a_session_that_is_not_closed() -> None:
    """03 TRN-SESS-013: "CLOSED must not be used to hide unresolved
    failure." The inverse also has to hold -- a closure timestamp on a
    mid-chain Session would claim a closure that never happened.
    """
    with pytest.raises(ValueError, match="closed_at may only be set when state is CLOSED"):
        _session(state=SessionState.ACTION, closed_at=_NOW)

    # Negative control: the same timestamp on a genuinely CLOSED
    # Session is accepted.
    assert _session(state=SessionState.CLOSED, closed_at=_NOW).closed_at == _NOW


def test_session_belongs_to_exactly_one_challenge() -> None:
    """02 §11.3 `[ARCHITECTURAL CLOSURE]`: "Each Session belongs to one
    Challenge."
    """
    challenge_id = ChallengeId(uuid.uuid4())
    assert _session(challenge_id=challenge_id).challenge_id == challenge_id

    with pytest.raises(TypeError, match="challenge_id must be a ChallengeId"):
        _session(challenge_id=uuid.uuid4())


def test_applied_method_version_is_a_pinned_version_not_free_text() -> None:
    """09 §27 pins `applied_method_version`; 12 §9 classes the
    InquiryMethod reference as "CONFIGURATION | Pinned Session
    configuration only". Pinning configuration never grants authority,
    but it does have to be a real version.
    """
    with pytest.raises(TypeError, match="applied_method_version must be a MethodVersion"):
        _session(applied_method_version="1.0")
