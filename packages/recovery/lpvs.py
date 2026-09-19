"""LPVSResolver: LAST_PROVEN_VALID_STATE, 10 sections 7/8's own
[ARCHITECTURAL CLOSURE] AC-10-004 algorithm.

Source: 10_FAILURE_RECOVERY_ROLLBACK.md section 7 ("[ARCHITECTURAL
CLOSURE] AC-10-004" -- "the most recent reconstructable system state
for which legitimacy is proven through all predicates required for the
consequence that produced it"; explicitly NOT "latest timestamp/latest
database row/latest Event/latest projection/latest cache/latest UI
state/latest backup row"), section 8 (Last-Proven-Valid-State Selection
Algorithm -- the exact 12-step procedure; "If step 11 cannot produce a
unique legitimate state: CANONICAL_STATE_UNKNOWN -> dependent
consequence blocked -> reconciliation remains UNRESOLVED");
14_IMPLEMENTATION_SEQUENCE.md this package's own OBJECTIVE line: "LPVS
proof uses legal prior state, legal transition, actor, authority at
commit, human Decision where required, Evidence where required,
boundaries, commit, canonical resulting version, audit and provenance.
Return UNRESOLVED if unique legitimate state cannot be proven."

WHY `LpvsCandidate` CARRIES PLAIN TRI-STATE BOOLEANS FOR EACH PROOF
DIMENSION, NOT THE REAL AuthorityResolver/EvidenceRepository/BoundaryProof
TYPES
--------------------------------------------------------------------
`recovery`'s own 14 section 3.1 allow-list is exactly `command,
boundaries, commit, recovery ports` -- the SAME dependency-ceiling
tension `recovery.certainty.ConsequenceCertaintyResolver` (PKG-22)
already resolved, and this module follows the identical pattern:
every one of 10 section 8's own numbered reconstruction steps (2
through 9 -- CommitUnit, canonical versions, authority/governance,
human Decision, Evidence, boundary/commit proof, audit/outbox
correlation) becomes one tri-state (`bool | None`) field a caller has
ALREADY resolved from the real `AuthorityResolver`/`EvidenceRepository`/
`BoundaryProof`/`AuditRepository` reads this package cannot import.
`None` always means "not verified"; `True`/`False` are both positive,
checked facts -- identical discipline to `certainty.py`'s own
`ConsequenceCertaintyInput`.

WHY CANDIDATES ARE SCANNED NEWEST-FIRST AND ORDER IS CALLER-SUPPLIED
--------------------------------------------------------------------
10 section 8 step 10 requires ordering "only states whose causal/commit
relation is proven" before step 11 selects "the latest state with
complete legitimacy proof." This module does not itself reconstruct
causal order (it has no access to real commit history) -- the caller
supplies `candidates` already in proven newest-to-oldest order; this
resolver only enforces steps 11/12 (select the first fully-proven one;
retain every earlier-scanned, not-yet-selected candidate as unresolved
consequence evidence, 10 section 8's own step 12).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from semantic_types.ids import CommitId


@dataclass(frozen=True, slots=True)
class LpvsCandidate:
    """One candidate historical state, already resolved by the caller
    into its own full legitimacy-proof bundle (10 section 7's own proof
    chain: legal prior state, legal transition, actor, current-at-commit
    authority, human Decision, Evidence set/version, boundary results,
    commit, canonical resulting version, audit/provenance correlation).
    """

    commit_id: CommitId
    committed_at: datetime
    state_ref: str
    legal_prior_state_confirmed: bool | None
    legal_transition_confirmed: bool | None
    actor_identity_confirmed: bool | None
    authority_current_at_commit_confirmed: bool | None
    human_decision_confirmed: bool | None
    evidence_confirmed: bool | None
    boundary_and_commit_proof_confirmed: bool | None
    canonical_resulting_version_confirmed: bool | None
    audit_provenance_confirmed: bool | None

    def __post_init__(self) -> None:
        if not isinstance(self.commit_id, CommitId):
            raise TypeError(f"commit_id must be a CommitId, got {type(self.commit_id)!r}")
        if not self.state_ref:
            raise ValueError("LpvsCandidate.state_ref must be non-empty")

    def is_fully_proven(self) -> bool:
        """10 section 7: every predicate in the proof chain must be
        POSITIVELY confirmed -- `None` (unverified) or `False`
        (confirmed absent) both fail this, never treated as "probably
        fine."
        """
        return all(
            (
                self.legal_prior_state_confirmed,
                self.legal_transition_confirmed,
                self.actor_identity_confirmed,
                self.authority_current_at_commit_confirmed,
                self.human_decision_confirmed,
                self.evidence_confirmed,
                self.boundary_and_commit_proof_confirmed,
                self.canonical_resulting_version_confirmed,
                self.audit_provenance_confirmed,
            )
        )


@dataclass(frozen=True, slots=True)
class LpvsResult:
    """`resolved=False` means UNRESOLVED (10 section 8: "CANONICAL_STATE_UNKNOWN
    -> dependent consequence blocked -> reconciliation remains
    UNRESOLVED") -- `state_ref` is `None` in that case, never a guess.
    `later_unresolved_state_refs` is step 12's own "retain every later
    uncertain artifact as unresolved consequence evidence" -- every
    candidate scanned before (newer than) the selected one, or every
    candidate at all when nothing was selected.
    """

    resolved: bool
    state_ref: str | None
    selected_commit_id: CommitId | None
    later_unresolved_state_refs: tuple[str, ...]


def resolve_lpvs(candidates: Sequence[LpvsCandidate]) -> LpvsResult:
    """Pure decision function, no I/O. `candidates` must already be in
    caller-proven newest-to-oldest order (see this module's own
    docstring for why this resolver does not reconstruct that order
    itself).
    """

    later_unresolved: list[str] = []
    for candidate in candidates:
        if candidate.is_fully_proven():
            return LpvsResult(
                resolved=True,
                state_ref=candidate.state_ref,
                selected_commit_id=candidate.commit_id,
                later_unresolved_state_refs=tuple(later_unresolved),
            )
        later_unresolved.append(candidate.state_ref)

    # Step 11 could not produce a unique legitimate state.
    return LpvsResult(
        resolved=False,
        state_ref=None,
        selected_commit_id=None,
        later_unresolved_state_refs=tuple(later_unresolved),
    )


__all__ = ["LpvsCandidate", "LpvsResult", "resolve_lpvs"]
