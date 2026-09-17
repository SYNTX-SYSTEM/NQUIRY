"""T1 DOMAIN INVARIANT TEST: `domain.challenge.Challenge`.

13 §6 T1 scope: "Object identity, immutability, relation semantics."
"""

from __future__ import annotations

import dataclasses
import uuid
from datetime import datetime, timezone

import pytest
from domain.challenge import Challenge
from semantic_types.ids import ChallengeId, WorkspaceId
from semantic_types.versions import RecordVersion

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)


def _challenge(**overrides: object) -> Challenge:
    defaults: dict[str, object] = {
        "challenge_id": ChallengeId(uuid.uuid4()),
        "workspace_id": WorkspaceId(uuid.uuid4()),
        "title": "Retention is falling in the onboarding funnel",
        "description": None,
        "context": None,
        "desired_outcome": None,
        "constraints": None,
        "stakeholders": None,
        "created_at": _NOW,
        "updated_at": _NOW,
        "record_version": RecordVersion.initial(),
    }
    defaults.update(overrides)
    return Challenge(**defaults)  # type: ignore[arg-type]


def test_challenge_carries_exactly_one_workspace_scope() -> None:
    """02 §9.3 `[ARCHITECTURAL CLOSURE]`: "Challenge is scoped by exactly
    one Workspace." One field, not a list, not an optional.
    """
    workspace_id = WorkspaceId(uuid.uuid4())
    challenge = _challenge(workspace_id=workspace_id)

    assert challenge.workspace_id == workspace_id
    field_names = {f.name for f in dataclasses.fields(Challenge)}
    assert "workspace_id" in field_names
    assert not any(name.startswith("workspace_ids") for name in field_names)


def test_challenge_is_immutable() -> None:
    """14 §3.1 gives `domain` no canonical write capability, so there is
    no in-place edit path on a canonical snapshot.
    """
    challenge = _challenge()

    with pytest.raises(dataclasses.FrozenInstanceError):
        challenge.title = "something else"  # type: ignore[misc]


def test_challenge_has_no_status_field() -> None:
    """Mandatory adversarial attack (novel): `Challenge.status`
    smuggling.

    03 §12.1 refuses to invent a Challenge status vocabulary and 03
    §12.2 forbids using one as transition guard, authority predicate,
    boundary predicate or prototype acceptance condition while
    GAP-02-012 / GAP-03-013 remain OPEN. If the field existed, a later
    package could reach for it as a guard without noticing it is
    undefined; because it does not exist, that mistake is a
    `AttributeError` at the first attempt rather than a silent
    architectural collapse.
    """
    field_names = {f.name for f in dataclasses.fields(Challenge)}

    assert "status" not in field_names
    assert not hasattr(_challenge(), "status")


def test_challenge_has_no_emotional_temperature_field() -> None:
    """02 §10.5 leaves the technical role of
    `Challenge.emotional_temperature` (initial reading / latest-reading
    projection / compatibility field / denormalized value) unresolved
    and delegates it to 09, which does not resolve it either. Choosing
    one would be invention; 02 §10 models the real thing as a separate
    `EmotionalTemperatureReading` VALUE_RECORD.
    """
    field_names = {f.name for f in dataclasses.fields(Challenge)}

    assert "emotional_temperature" not in field_names


def test_challenge_rejects_a_bare_uuid_identity() -> None:
    """Negative: the strong-ID distinction PKG-00 established must not
    be bypassable by passing a raw UUID where a `ChallengeId` belongs.
    """
    with pytest.raises(TypeError, match="challenge_id must be a ChallengeId"):
        _challenge(challenge_id=uuid.uuid4())


def test_challenge_rejects_a_workspace_id_of_the_wrong_id_type() -> None:
    """Negative: a `ChallengeId` passed as the Workspace scope would
    make the object's own identity look like its container.
    """
    with pytest.raises(TypeError, match="workspace_id must be a WorkspaceId"):
        _challenge(workspace_id=ChallengeId(uuid.uuid4()))


def test_challenge_requires_a_title() -> None:
    with pytest.raises(ValueError, match="title must be non-empty"):
        _challenge(title="")
