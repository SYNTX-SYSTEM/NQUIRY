"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — R-04: Field Pulse (Architecture 26).

Source: `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md`
R-04: "PRODUCER: a derived view over existing records... INPUT: the Field
snapshot... OUTPUT: Pulse elements, each citing its canonical source."
I-01 (`01_INVARIANTS.md` I-07): "Every Pulse element is a projection of an
existing canonical record or of an existing producer's result, cited with
its source. Pulse introduces no status, lifecycle, flag or counter of its
own." This module composes REAL, already-proven producers only.

SCOPE (disclosed; "do not redesign R-04" honored by building only what a
real producer already supports)
------------------------------------------------------------------------
`04_OBSERVATION_RESULT.md` §3 lists 10 Pulse elements. Seven are
materialized here, each citing its real home:

- ACTIVE_TRANSITIONS / PENDING_AUTHORITY_REQUIREMENTS: read directly from
  `session_position.actions`'s own `relevant`/`available`/`reasonCode`
  fields (R-04's own citation, verbatim) -- already carried by R-03's
  `SessionContext.actions`. No new producer call.
- IN_FLIGHT_OPERATIONS: `application.reflection_proof._unresolved` --
  `00_FIELD.md` §7's own named home for exactly this element ("unresolved
  -operation checks (`reflection_proof._unresolved`)"). Imported directly
  despite the leading underscore because the RED architecture text itself
  names this precise symbol as the canonical producer -- the same
  reasoning that let WU-1 prefer a public wrapper did not apply here,
  because no public wrapper of the same fact exists.
- STALE_SOURCES: `application.frozen_set.verify_frozen_set` (F03) -- the
  same function `session_position` itself already calls, re-read here
  for the current Burst when one exists and is COMPLETED.
- EXTERNAL_DEPENDENCIES: the identical static, cited fact
  `pcpg_field_snapshot.EXTERNAL_EFFECTS` already materializes.
- UNRESOLVED_ELIGIBILITY: a static, cited fact. GAP-11-006 (no data-class
  classifier exists) and HARD-DEP-002/GAP-08-008 (no eligible provider
  route exists) are ALL unconditionally OPEN today -- eligibility is
  therefore unconditionally unresolved for every observation, not a
  per-call computation.
- GOVERNANCE_BLOCKERS: HA-23 (`docs/implementation/field-reports/PFC/
  HUMAN_AUTHORITY_QUEUE.md`, confirmed OPEN 2026-09-30), R-04's own
  worked example ("open Case 3 questions... for example HA-23 for
  leaving INVESTIGATION") -- cited exactly when the named Session is
  currently in INVESTIGATION. This is the one concrete case the RED text
  itself names; it is not a general Case-3 scanner over the whole HA
  queue, which would require a producer this codebase does not have
  (a generic "which HA question governs which relation" index).

Three are explicitly NOT covered -- named in `Pulse.unresolved`, never
silently dropped, because no real listing producer exists in this
codebase today for any of them:
- PENDING_HUMAN_DECISIONS: `persistence.decision_repository.
  DecisionRepository` has no `list_*` method (get/create/decide only).
- INDETERMINATE_CONSEQUENCES beyond what `_unresolved` already covers:
  `persistence.recovery_repository` has no listing method (get only).
- RECENT_AUTHORITY_CHANGE: its own definition ("a binding changed after
  a source it gates") has no generic, delta-free comparison basis --
  R-04's own INPUT is only the Field snapshot, not a specific delta's
  own source set, which is R-06/R-07's context, not this relation's.

Inventing a new listing method on any of these three ports to fill the
gap would be *designing* new persistence surface under this Work Unit,
not deriving R-04's minimum coherent implementation from what already
exists -- exactly what "do not redesign R-04" warns against.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast

from domain.burst import BurstState
from semantic_types.ids import SessionId, WorkspaceId

from application.composition import GovernedPorts
from application.frozen_set import verify_frozen_set
from application.pcpg_field_snapshot import EXTERNAL_EFFECTS, FieldSnapshot
from application.reflection_proof import _unresolved

UNRESOLVED_ELIGIBILITY_REASONS = frozenset({"GAP-11-006", "HARD-DEP-002", "GAP-08-008"})
"""The real, cited, unconditionally-OPEN architecture gaps that make
provider-route AND data-class eligibility unresolved for every
observation today (`00_FIELD.md` §7; `04_OBSERVATION_RESULT.md` §3's own
UNRESOLVED_ELIGIBILITY row)."""

GOVERNANCE_BLOCKER_HA23 = "HA-23"
"""`docs/implementation/field-reports/PFC/HUMAN_AUTHORITY_QUEUE.md`: OPEN,
"Investigation completion semantics" -- R-04's own worked example ("HA-23
for leaving INVESTIGATION"), 02_RELATIONS.md's §3 GOVERNANCE_BLOCKERS
row, verbatim."""

_NOT_YET_COVERED = (
    "PENDING_HUMAN_DECISIONS",
    "INDETERMINATE_CONSEQUENCES",
    "RECENT_AUTHORITY_CHANGE",
)


@dataclass(frozen=True, slots=True)
class Pulse:
    active_transitions: Mapping[str, object]
    """The `relevant` subset of `session_position.actions`, quoted
    verbatim. Empty when no Session is named."""
    pending_authority_requirements: tuple[str, ...]
    """The `reasonCode` of every relevant-but-unavailable action."""
    in_flight_operations: bool
    """`reflection_proof._unresolved`'s own live result. `False` when no
    Session is named (nothing to check)."""
    stale_sources: tuple[str, ...]
    """Non-empty exactly when the current Burst is COMPLETED and its
    frozen-set verification (F03) does not match."""
    external_dependencies: frozenset[str]
    unresolved_eligibility: bool
    unresolved_eligibility_reasons: frozenset[str]
    governance_blockers: tuple[str, ...]
    unresolved: tuple[str, ...]
    """Pulse element names this Work Unit does not yet materialize (never
    silently dropped -- see the module docstring)."""


def derive_pulse(
    ports: GovernedPorts,
    snapshot: FieldSnapshot,
    *,
    workspace_id: WorkspaceId,
    session_id: SessionId | None,
) -> Pulse:
    """The R-04 producer. PRECONDITION: `snapshot` was produced by R-03
    for this same `(workspace_id, session_id)` at a consistent basis."""
    active_transitions: dict[str, object] = {}
    pending_authority_requirements: list[str] = []
    in_flight_operations = False
    stale_sources: list[str] = []

    if session_id is not None and snapshot.session is not None:
        for name, action in snapshot.session.actions.items():
            action_map = cast("Mapping[str, object]", action)
            if action_map.get("relevant"):
                active_transitions[name] = action
                if not action_map.get("available") and action_map.get("reasonCode"):
                    pending_authority_requirements.append(cast(str, action_map["reasonCode"]))

        session = ports.sessions.get(session_id)
        if session is not None:
            in_flight_operations = _unresolved(ports, session)

        burst = ports.bursts.get_by_session(session_id)
        if burst is not None and burst.state is BurstState.COMPLETED:
            verification = verify_frozen_set(ports, burst)
            if not verification.matches:
                stale_sources.append("FROZEN_SET_VERIFICATION_FAILED")

    governance_blockers: tuple[str, ...] = ()
    if snapshot.session is not None and snapshot.session.state == "INVESTIGATION":
        governance_blockers = (GOVERNANCE_BLOCKER_HA23,)

    return Pulse(
        active_transitions=active_transitions,
        pending_authority_requirements=tuple(pending_authority_requirements),
        in_flight_operations=in_flight_operations,
        stale_sources=tuple(stale_sources),
        external_dependencies=EXTERNAL_EFFECTS,
        unresolved_eligibility=True,
        unresolved_eligibility_reasons=UNRESOLVED_ELIGIBILITY_REASONS,
        governance_blockers=governance_blockers,
        unresolved=_NOT_YET_COVERED,
    )


__all__ = [
    "GOVERNANCE_BLOCKER_HA23",
    "UNRESOLVED_ELIGIBILITY_REASONS",
    "Pulse",
    "derive_pulse",
]
