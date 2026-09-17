"""Row -> domain mapping for `challenges` and `sessions`. Read-only.

Source: 14_IMPLEMENTATION_SEQUENCE.md §3.1 (`persistence`:
"PostgreSQL adapters implementing typed ports", may depend on
"semantic contracts"); PKG-05 `FILES_ALLOWED_TO_CREATE`: "persistence
mapping".

WHY THERE IS NO ChallengeRepository / SessionRepository HERE
------------------------------------------------------------
14 §10 does define both ports, but with contracts PKG-05 cannot yet
honour:

    ChallengeRepository: canonical read and mutation-plan application
                         inside CommitUnit.
    SessionRepository:   canonical current version, state mutation only
                         through transition plan.

CommitUnit is Phase 4 and the transition plan needs the boundary
pipeline (Phase 3). A repository written now could only offer a write
path with neither, which is precisely 14's "direct persistence"
forbidden shortcut and would hand the generic-setter collapse a
ready-made vector. Deferred, not stubbed -- PKG-05's
`PUBLIC_INTERFACES` are `Challenge, Session, TransitionSpec`, and no
repository is among them.

What is here instead is the narrowest thing the package genuinely
needs: pure functions turning an already-fetched row into the
corresponding frozen domain value. They read; they never write, never
open a transaction, and return no authority conclusion (14 §10: "No
repository returns an authority conclusion").

A row that cannot be mapped raises rather than producing a
half-populated domain object -- an unreadable canonical row is not
silently downgraded into a usable one.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from domain.challenge import Challenge
from domain.session import Session, SessionState
from semantic_types.ids import ChallengeId, SessionId, WorkspaceId
from semantic_types.versions import MethodVersion, RecordVersion


class UnmappableRow(ValueError):
    """A canonical row does not satisfy its domain type's invariants.

    Raised rather than swallowed: 14 §45's default-DENY posture applies
    to reads too. A `sessions` row whose `state` is outside 03 §13.1's
    vocabulary should be impossible (migration 003 CHECK-constrains it),
    so encountering one means the database was written around its own
    constraints -- a condition to surface, not to coerce into something
    that looks valid.
    """


def challenge_from_row(row: Mapping[str, Any]) -> Challenge:
    """Map a `challenges` row to `domain.challenge.Challenge`.

    There is deliberately no `status` or `emotional_temperature` to
    map -- neither column exists (see migration 003's docstring for the
    03 §12.1/§12.2 and 02 §10.5 reasoning).
    """
    try:
        return Challenge(
            challenge_id=ChallengeId(row["id"]),
            workspace_id=WorkspaceId(row["workspace_id"]),
            title=row["title"],
            description=row["description"],
            context=row["context"],
            desired_outcome=row["desired_outcome"],
            constraints=row["constraints"],
            stakeholders=row["stakeholders"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            record_version=RecordVersion(row["record_version"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise UnmappableRow(f"challenges row is not a valid Challenge: {exc}") from exc


def session_from_row(row: Mapping[str, Any]) -> Session:
    """Map a `sessions` row to `domain.session.Session`.

    `state` is converted through `SessionState(...)`, so a stored value
    outside 03 §13.1's 13 raises here instead of travelling on as an
    opaque string. This is the read-side half of `STATE != STATUS
    STRING`: the column is text in PostgreSQL, but nothing downstream
    of this function ever sees it as text.
    """
    try:
        return Session(
            session_id=SessionId(row["id"]),
            challenge_id=ChallengeId(row["challenge_id"]),
            workspace_id=WorkspaceId(row["workspace_id"]),
            applied_method_key=row["applied_method_key"],
            applied_method_version=MethodVersion(row["applied_method_version"]),
            state=SessionState(row["state"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            closed_at=row["closed_at"],
            record_version=RecordVersion(row["record_version"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise UnmappableRow(f"sessions row is not a valid Session: {exc}") from exc


__all__ = ["UnmappableRow", "challenge_from_row", "session_from_row"]
