"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — R-07: per-delta governance
evaluation (Architecture 26).

Source: `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md`
R-07: "INPUT: each delta, the Field snapshot and the Pulse... OUTPUT: one
delta record per delta ... and exactly one RESULT class with its reason."
PRECONDITION, verbatim: "For NQUIRY operations, the required authority,
the actual authority and the state availability are taken from the
existing readiness producer for that operation. For operations with a
projected capability, that is the `session_position.actions` entry at
the same basis. The evaluation never re-implements a readiness rule."

SCOPE (disclosed; full reasoning in `test_pcpg_delta_evaluation.py`'s own
module docstring, not repeated here): this increment produces `result`
and `reason` for each delta, plus a passthrough of the delta fields
already real from R-05/R-06. `Result` is `04_OBSERVATION_RESULT.md` §6's
own vocabulary, materialized here for the first time (I-20: one
definition) — all 8 real values exist, though this producer only ever
emits `INDETERMINATE`, `GOVERNANCE_BOUNDARY`, `HUMAN_ACTION_AVAILABLE`,
`AUTHORITY_BOUNDARY` and `STATE_BOUNDARY`. `ALLOWED` is correctly never
emitted: `00_FIELD.md` §13 HA-PCPG-1's own fail-closed default
(restated by `04_OBSERVATION_RESULT.md` §8 as the Field's current,
already-decided value) makes every `PROVIDER_COMPUTATION` delta
`GOVERNANCE_BOUNDARY` today, unconditionally — an architectural fact
this module quotes, not a gap in it. `DATA_BOUNDARY` and `DENIED` are
never emitted either: their own producers (a data-class classifier,
FBR-PCPG-3, still OPEN; an immutable-source-mutation detector) do not
exist anywhere in this codebase.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import cast

from application.pcpg_candidate_deltas import CandidateDelta
from application.pcpg_field_snapshot import FieldSnapshot
from application.pcpg_operation_index import ExecutionClass

OPERATION_CLASS_NOT_ADMITTED = "OPERATION_CLASS_NOT_ADMITTED"
"""`00_FIELD.md` §13 HA-PCPG-1's own fail-closed default, restated
verbatim by `04_OBSERVATION_RESULT.md` §8 as the Field's current value:
"GOVERNANCE_ADMISSIBLE is false for every observation ... This holds
even for a delta mapping to AIOP-001." A static, cited fact — not
computed per call."""

NO_AUTHORITATIVE_PRODUCER = "NO_AUTHORITATIVE_PRODUCER"
"""R-07's own FAILURE STATE, verbatim: "A delta with no authoritative
producer for its authority gives INDETERMINATE with reason
NO_AUTHORITATIVE_PRODUCER.\""""

SEMANTIC_UNKNOWN = "SEMANTIC_UNKNOWN"
"""I-04: an UNKNOWN operation (no catalog match with certainty) makes
the delta INDETERMINATE — never a guess."""

_AUTHORITY_REASON_CODES = frozenset(
    {
        "NO_SESSION_CONTROL",
        "NO_QUESTION_SELECTION_RIGHT",
        "NOT_GOVERNANCE_ROOT",
        "NOT_A_PARTICIPANT",
        "NO_CHALLENGE_SESSION_CONTROL",
        "NOT_FACILITATOR",
    }
)
"""The closed, directly-verified set of real reason codes
`application.inquiry_queries.py` actually produces for "the actor lacks
the required authority" (grepped from that module's own source, not
guessed). Any OTHER real, non-null `reasonCode` on an unavailable
relevant action is a state-topology fact instead (`blocked_or()`'s own
structure checks authority first, so a non-authority code is
necessarily a state one) — the residual/default category below, also
matching `04_OBSERVATION_RESULT.md` §6's own precedence order
(STATE_BOUNDARY before AUTHORITY_BOUNDARY)."""


class Result(Enum):
    """`04_OBSERVATION_RESULT.md` §6, verbatim vocabulary. This Field's
    own classification, reused by every later relation that needs it
    (I-20: one definition, not a second divergent one)."""

    ALLOWED = "ALLOWED"
    HUMAN_ACTION_AVAILABLE = "HUMAN_ACTION_AVAILABLE"
    STATE_BOUNDARY = "STATE_BOUNDARY"
    AUTHORITY_BOUNDARY = "AUTHORITY_BOUNDARY"
    DATA_BOUNDARY = "DATA_BOUNDARY"
    GOVERNANCE_BOUNDARY = "GOVERNANCE_BOUNDARY"
    DENIED = "DENIED"
    INDETERMINATE = "INDETERMINATE"


@dataclass(frozen=True, slots=True)
class DeltaRecord:
    delta_id: str
    operation: str | None
    execution_class: ExecutionClass
    target: str | None
    source_clause: str
    span: tuple[int, int]
    current_state: str | None
    result: Result
    reason: str | None
    flags: frozenset[str]


def evaluate_deltas(
    deltas: tuple[CandidateDelta, ...],
    snapshot: FieldSnapshot,
    *,
    flags_by_delta_id: Mapping[str, frozenset[str]] | None = None,
) -> tuple[DeltaRecord, ...]:
    """The R-07 producer (this increment's own disclosed scope). Pure,
    deterministic, no I/O. `flags_by_delta_id` lets a caller attach the
    real, already-computed `DECISION_SUBSTITUTION_REQUESTED` flag from
    R-05's own `SemanticAction` — this module never re-derives it."""
    flags_by_delta_id = flags_by_delta_id or {}
    session_actions = snapshot.session.actions if snapshot.session is not None else {}

    records: list[DeltaRecord] = []
    for delta in deltas:
        result: Result
        reason: str | None

        if delta.operation is None:
            result, reason = Result.INDETERMINATE, SEMANTIC_UNKNOWN
        elif delta.execution_class is ExecutionClass.PROVIDER_COMPUTATION:
            result, reason = Result.GOVERNANCE_BOUNDARY, OPERATION_CLASS_NOT_ADMITTED
        elif delta.operation not in session_actions:
            result, reason = Result.INDETERMINATE, NO_AUTHORITATIVE_PRODUCER
        elif delta.execution_class is ExecutionClass.HUMAN_COMMAND:
            action = cast("Mapping[str, object]", session_actions[delta.operation])
            if action["available"]:
                result, reason = Result.HUMAN_ACTION_AVAILABLE, None
            else:
                code = cast("str | None", action["reasonCode"])
                if code in _AUTHORITY_REASON_CODES:
                    result, reason = Result.AUTHORITY_BOUNDARY, code
                else:
                    result, reason = Result.STATE_BOUNDARY, code
        else:
            # EXTERNAL_EFFECT / DISCLOSURE: no real catalog entry is
            # either today (confirmed, FBR-PCPG-2's own closure) — never
            # reached in practice; defensive, honest fallback.
            result, reason = Result.INDETERMINATE, NO_AUTHORITATIVE_PRODUCER

        records.append(
            DeltaRecord(
                delta_id=delta.delta_id,
                operation=delta.operation,
                execution_class=delta.execution_class,
                target=delta.target,
                source_clause=delta.source_clause,
                span=delta.span,
                current_state=delta.current_state,
                result=result,
                reason=reason,
                flags=flags_by_delta_id.get(delta.delta_id, frozenset()),
            )
        )
    return tuple(records)


__all__ = [
    "NO_AUTHORITATIVE_PRODUCER",
    "OPERATION_CLASS_NOT_ADMITTED",
    "SEMANTIC_UNKNOWN",
    "DeltaRecord",
    "Result",
    "evaluate_deltas",
]
