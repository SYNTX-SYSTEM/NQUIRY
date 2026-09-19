"""ConsequenceCertaintyResolver: 10 section 5's exact 7-value closed
Consequence Certainty Model.

Source: 10_FAILURE_RECOVERY_ROLLBACK.md section 4 (Preserve 03
Consequential Outcomes -- the four outcomes DENIED/FAILED_PRECOMMIT/
COMMITTED/INDETERMINATE, already materialized as `command.envelope.
CommandOutcome`/`commit.coordinator.CommitOutcome`/`commit.idempotency.
IdempotencyOutcome`; section 4.3: "A later notification failure/broker
failure/projection failure/external post-commit failure/client timeout
does not retroactively change COMMITTED into FAILED_PRECOMMIT"),
section 5 ("[ARCHITECTURAL CLOSURE] AC-10-002" -- the exact 7-value
list; "missing telemetry != proven absence; timeout != proven failure;
local error != external non-occurrence; event missing != canonical
non-commit; projection missing != canonical non-commit; database row
present != legitimate commit; audit projection missing != audit record
absent"); 14_IMPLEMENTATION_SEQUENCE.md section 29 (FAILURE, CONSEQUENCE
CERTAINTY AND INDETERMINATE -- "ConsequenceCertaintyResolver uses:
Command/Attempt history, CommitUnit, canonical versions, governance
versions, AuditEvent, outbox, external consequence records where
applicable, idempotency, AI/tool lineage and correlation").

WHY `ConsequenceCertaintyInput` CARRIES PLAIN BOOLEANS FOR
AUDIT/OUTBOX/GOVERNANCE, NOT THE REAL `AuditEvent`/`OutboxRecord` TYPES
--------------------------------------------------------------------
`recovery`'s own 14 section 3.1 allow-list is exactly `command,
boundaries, commit, recovery ports` -- it does NOT include `audit`,
`events`, `evidence`, `ai_contracts`, or `governance`, even though 14
section 29's own input list for this exact resolver names AuditEvent,
outbox, governance versions, and AI/tool lineage. This is the same
dependency-ceiling tension `ai_gateway.gateway.AIGateway.run_operation`
(PKG-19) and `nquiry_worker.outbox_worker.OutboxWorker`/
`nquiry_worker.projection_worker.ProjectionWorker` (PKG-20/21) already
resolved the same way: the resolver accepts caller-supplied, ALREADY-
RESOLVED facts (plain `bool | None` per question, never the concrete
upstream record) rather than importing the forbidden packages itself.
A future package with broader import rights (`application`) is where
these facts would be resolved from the real `AuditRepository`/
`OutboxRepository`/`AuthorityBindingRepository` reads -- disclosed as
`SUCCESSOR_NOT_BUILT`, not fabricated here. `command`/`commit`
themselves ARE on this package's own allow-list, so `CommandOutcome`/
`CommitOutcome`/`IdempotencyOutcome` are reused directly, not
re-derived as booleans -- the one part of 14 section 29's own input
list this package CAN type precisely.

WHY EVERY BOOLEAN FIELD IS TRI-STATE (`bool | None`), NEVER PLAIN `bool`
--------------------------------------------------------------------
10 section 5's own rules are explicit: "missing telemetry != proven
absence". A plain `bool` cannot distinguish "confirmed absent" from
"never checked" -- collapsing that distinction is exactly the
"database row present != legitimate commit" / "ambiguous connection
loss" failure mode this resolver exists to prevent. `None` always means
"not verified"; `True`/`False` are both POSITIVE, checked facts.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from command.envelope import CommandOutcome
from commit.coordinator import CommitOutcome
from commit.idempotency import IdempotencyOutcome
from semantic_types.ids import CorrelationId


class ConsequenceCertainty(Enum):
    """10 section 5's exact 7-value closed vocabulary. These are
    recovery classifications, not new 03 domain states (10's own
    explicit disclaimer).
    """

    PROVEN_COMMITTED = "PROVEN_COMMITTED"
    PROVEN_NOT_COMMITTED = "PROVEN_NOT_COMMITTED"
    EXTERNAL_CONSEQUENCE_PROVEN = "EXTERNAL_CONSEQUENCE_PROVEN"
    EXTERNAL_CONSEQUENCE_PROVEN_ABSENT = "EXTERNAL_CONSEQUENCE_PROVEN_ABSENT"
    EXTERNAL_CONSEQUENCE_UNKNOWN = "EXTERNAL_CONSEQUENCE_UNKNOWN"
    CANONICAL_STATE_UNKNOWN = "CANONICAL_STATE_UNKNOWN"
    GOVERNANCE_STATE_UNKNOWN = "GOVERNANCE_STATE_UNKNOWN"


class ExternalConsequenceProofState(Enum):
    """The caller's own already-resolved proof state for an external
    (non-canonical) side effect -- `NOT_APPLICABLE` when the attempt in
    question has no external side-effect dimension at all.
    """

    NOT_APPLICABLE = "NOT_APPLICABLE"
    PROVEN = "PROVEN"
    PROVEN_ABSENT = "PROVEN_ABSENT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class ConsequenceCertaintyInput:
    """Every field a caller has ALREADY verified, or `None` if not
    verified. No field here represents a raw technical event (a
    timeout, a dropped connection, a missing projection row) -- see
    this module's own docstring for why, and `packages/recovery/
    failure_classifier.py`'s identical discipline for `FailureSignals`.
    """

    command_outcome: CommandOutcome | None
    commit_outcome: CommitOutcome | None
    commit_unit_found: bool | None
    canonical_version_confirmed_after_commit: bool | None
    governance_state_confirmed: bool | None
    audit_record_durable: bool | None
    outbox_record_durable: bool | None
    external_consequence_proof: ExternalConsequenceProofState
    idempotency_outcome: IdempotencyOutcome | None = None
    correlation_id: CorrelationId | None = None


def resolve_consequence_certainty(
    certainty_input: ConsequenceCertaintyInput,
) -> ConsequenceCertainty:
    """Pure decision function, no I/O. Ordered, fail-closed: a
    positive classification (`PROVEN_COMMITTED`/`PROVEN_NOT_COMMITTED`)
    requires every relevant fact to be POSITIVELY confirmed; anything
    less specific falls through to an explicitly uncertain class,
    never a guess (10 section 5: "database row present != legitimate
    commit").
    """

    # 10 section 6: governance state at commit time is one of the
    # required reconstruction components. An explicit failure to
    # reconstruct it is its own distinct, informative classification,
    # not folded into the generic canonical-uncertainty bucket.
    if certainty_input.governance_state_confirmed is False:
        return ConsequenceCertainty.GOVERNANCE_STATE_UNKNOWN

    # PROVEN_COMMITTED requires the full, positively-confirmed chain --
    # removing any ONE required proof link (P-25's own mandatory
    # attack) must NOT still yield this result.
    if (
        certainty_input.commit_outcome is CommitOutcome.COMMITTED
        and certainty_input.commit_unit_found is True
        and certainty_input.canonical_version_confirmed_after_commit is True
        and certainty_input.governance_state_confirmed is True
    ):
        return ConsequenceCertainty.PROVEN_COMMITTED

    # 10 section 4.1: a DENIED request never legitimately executes at
    # all. 10 section 4.2 + this module's own tri-state discipline: a
    # FAILED_PRECOMMIT outcome only proves non-commit once the absence
    # of any CommitUnit has ALSO been positively confirmed -- a
    # FAILED_PRECOMMIT outcome with `commit_unit_found is None`
    # (unverified) must not be over-claimed as proof either.
    if certainty_input.command_outcome is CommandOutcome.DENIED or (
        certainty_input.commit_outcome is CommitOutcome.FAILED_PRECOMMIT
        and certainty_input.commit_unit_found is False
    ):
        return ConsequenceCertainty.PROVEN_NOT_COMMITTED

    # The external-consequence dimension is independent of canonical
    # commit proof (relevant to F-EXT/F-PROVDR-shaped attempts) --
    # mapped directly once it is the question actually being asked.
    if certainty_input.external_consequence_proof is ExternalConsequenceProofState.PROVEN:
        return ConsequenceCertainty.EXTERNAL_CONSEQUENCE_PROVEN
    if certainty_input.external_consequence_proof is ExternalConsequenceProofState.PROVEN_ABSENT:
        return ConsequenceCertainty.EXTERNAL_CONSEQUENCE_PROVEN_ABSENT
    if certainty_input.external_consequence_proof is ExternalConsequenceProofState.UNKNOWN:
        return ConsequenceCertainty.EXTERNAL_CONSEQUENCE_UNKNOWN

    # Fail-closed default: nothing above positively proved anything.
    # Covers INDETERMINATE outcomes, ambiguous connection loss
    # (`commit_unit_found is None`), and any other combination this
    # resolver was not given enough verified fact to resolve --
    # 10 section 5's own "CANONICAL_STATE_UNKNOWN -> dependent
    # consequence blocked" default, never a guessed branch.
    return ConsequenceCertainty.CANONICAL_STATE_UNKNOWN


__all__ = [
    "ConsequenceCertainty",
    "ExternalConsequenceProofState",
    "ConsequenceCertaintyInput",
    "resolve_consequence_certainty",
]
