"""T8 LPVS TEST: LpvsCandidate/LpvsResult/resolve_lpvs, pure, no
database.

14 section 48's own PKG-23 scope: `packages/recovery/lpvs.py`.
"""

from __future__ import annotations

import dataclasses
import uuid
from datetime import datetime, timezone

import pytest
from recovery.lpvs import LpvsCandidate, resolve_lpvs
from semantic_types.ids import CommitId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_EARLIER = datetime(2029, 12, 31, tzinfo=timezone.utc)

_FULLY_PROVEN = dict(
    legal_prior_state_confirmed=True,
    legal_transition_confirmed=True,
    actor_identity_confirmed=True,
    authority_current_at_commit_confirmed=True,
    human_decision_confirmed=True,
    evidence_confirmed=True,
    boundary_and_commit_proof_confirmed=True,
    canonical_resulting_version_confirmed=True,
    audit_provenance_confirmed=True,
)


def _candidate(
    *, state_ref: str, committed_at: datetime = _NOW, **overrides: object
) -> LpvsCandidate:
    fields = dict(_FULLY_PROVEN)
    fields.update(overrides)
    return LpvsCandidate(
        commit_id=CommitId(uuid.uuid4()),
        committed_at=committed_at,
        state_ref=state_ref,
        **fields,  # type: ignore[arg-type]
    )


def test_fully_proven_candidate_is_selected() -> None:
    candidate = _candidate(state_ref="session:1@v2")
    result = resolve_lpvs([candidate])
    assert result.resolved is True
    assert result.state_ref == "session:1@v2"
    assert result.selected_commit_id == candidate.commit_id
    assert result.later_unresolved_state_refs == ()


def test_no_fully_proven_candidate_is_unresolved() -> None:
    candidate = _candidate(state_ref="session:1@v2", evidence_confirmed=None)
    result = resolve_lpvs([candidate])
    assert result.resolved is False
    assert result.state_ref is None
    assert result.selected_commit_id is None
    assert result.later_unresolved_state_refs == ("session:1@v2",)


def test_empty_candidate_list_is_unresolved() -> None:
    result = resolve_lpvs([])
    assert result.resolved is False
    assert result.later_unresolved_state_refs == ()


def test_selects_the_first_fully_proven_candidate_and_retains_earlier_scanned_ones() -> None:
    """Mandatory adversarial attack: later illegitimate row. Caller
    supplies candidates newest-first -- an unproven NEWER candidate
    must not block selection of an older, fully-proven one, and must
    itself be retained as unresolved consequence evidence (10 section 8
    step 12).
    """
    newer_unproven = _candidate(
        state_ref="session:1@v3", committed_at=_NOW, authority_current_at_commit_confirmed=None
    )
    older_proven = _candidate(state_ref="session:1@v2", committed_at=_EARLIER)

    result = resolve_lpvs([newer_unproven, older_proven])

    assert result.resolved is True
    assert result.state_ref == "session:1@v2"
    assert result.later_unresolved_state_refs == ("session:1@v3",)


@pytest.mark.parametrize(
    "field_name",
    [
        "legal_prior_state_confirmed",
        "legal_transition_confirmed",
        "actor_identity_confirmed",
        "authority_current_at_commit_confirmed",
        "human_decision_confirmed",
        "evidence_confirmed",
        "boundary_and_commit_proof_confirmed",
        "canonical_resulting_version_confirmed",
        "audit_provenance_confirmed",
    ],
)
def test_removing_one_proof_dimension_makes_the_candidate_not_fully_proven(
    field_name: str,
) -> None:
    """Mandatory adversarial attacks: missing authority proof; missing
    audit -- generalized across every one of 10 section 7's own named
    proof-chain dimensions.
    """
    candidate = _candidate(state_ref="session:1@v2")
    weakened = dataclasses.replace(candidate, **{field_name: None})
    assert weakened.is_fully_proven() is False
    result = resolve_lpvs([weakened])
    assert result.resolved is False


def test_a_confirmed_false_dimension_is_treated_the_same_as_unverified() -> None:
    """A POSITIVELY confirmed absence (`False`) is just as disqualifying
    as an unverified (`None`) dimension -- neither is "probably fine."
    """
    candidate = _candidate(state_ref="session:1@v2", legal_transition_confirmed=False)
    assert candidate.is_fully_proven() is False


def test_backup_like_stale_snapshot_is_never_selected_on_presence_alone() -> None:
    """Mandatory adversarial attack: backup-like stale snapshot. A
    candidate that merely EXISTS (has a `state_ref` and a `commit_id`)
    but carries no positively-confirmed proof at all must never be
    selected.
    """
    bare_candidate = LpvsCandidate(
        commit_id=CommitId(uuid.uuid4()),
        committed_at=_NOW,
        state_ref="session:1@stale",
        legal_prior_state_confirmed=None,
        legal_transition_confirmed=None,
        actor_identity_confirmed=None,
        authority_current_at_commit_confirmed=None,
        human_decision_confirmed=None,
        evidence_confirmed=None,
        boundary_and_commit_proof_confirmed=None,
        canonical_resulting_version_confirmed=None,
        audit_provenance_confirmed=None,
    )
    result = resolve_lpvs([bare_candidate])
    assert result.resolved is False


def test_lpvs_candidate_has_no_projection_or_event_or_cache_field() -> None:
    """Mandatory adversarial attacks: latest Event differs; projection
    newer. Structural proof: `LpvsCandidate` has no field naming a
    projection, a cache, or a bare "latest Event" -- 10 section 5's own
    "projection missing != canonical non-commit" / "event missing !=
    canonical non-commit" apply here exactly as they did to
    `recovery.certainty.ConsequenceCertaintyInput` (PKG-22).
    """
    forbidden_substrings = ("projection", "cache", "latest_event", "event_ref")
    for field in dataclasses.fields(LpvsCandidate):
        for forbidden in forbidden_substrings:
            assert forbidden not in field.name.lower(), field.name


def test_lpvs_candidate_denies_empty_state_ref() -> None:
    with pytest.raises(ValueError, match="state_ref"):
        _candidate(state_ref="")
