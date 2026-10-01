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
definition) — all 8 real values exist.

WU-PFC-PCPG-15 UPDATE: BINDING HD-29 INTO THE PROVIDER_COMPUTATION BRANCH
--------------------------------------------------------------------------
Until `checkpoint-PFC-PCPG-14`, every `PROVIDER_COMPUTATION` delta was
unconditionally `GOVERNANCE_BOUNDARY`/`OPERATION_CLASS_NOT_ADMITTED`,
quoting HA-PCPG-1's own then-undecided fail-closed default. HD-29
(`HUMAN_DECISIONS.md`, recorded at `checkpoint-PFC-PCPG-13`)
conditionally resolved HA-PCPG-1: `PROVIDER_COMPUTATION` is admitted as
an operation class under the contract `USER_AUTHORED_INSTRUCTION ->
governed source material`, never a direct provider command. The old
unconditional placeholder is now stale as a JUSTIFICATION — the
operation class is not always inadmissible any more — so the branch is
rebuilt as a real, three-step conditional decision, consuming only
facts already real at R-07's own point in the pipeline:

1. Is `delta.operation` one of the two real `PROVIDER_COMPUTATION`
   operations in `pcpg_operation_index.py`'s own closed catalog
   (FBR-PCPG-2, CLOSED), mapped to a contract ID that is a member of
   `snapshot.ai_contracts_admitted` (R-03's own already-real per-call
   fact)? If NOT: unchanged from before — `GOVERNANCE_BOUNDARY`/
   `OPERATION_CLASS_NOT_ADMITTED`, the literally correct, still-
   applicable reason for any operation HD-29 itself does not name.
2. If the operation class IS admitted: HD-29's own text distinguishes
   "admit the operation class" from "becomes ELIGIBLE", naming "Data
   Governance" among its own further "at minimum" prerequisites.
   `pcpg_data_classification.classify_prompt_content` (FBR-PCPG-3,
   CLOSED, `checkpoint-PFC-PCPG-14`) is the real producer, consumed here
   via a caller-supplied `data_classifications_by_delta_id` mapping —
   the SAME established pattern this module's own `flags_by_delta_id`
   parameter already uses for R-05's own `DECISION_SUBSTITUTION_
   REQUESTED` flag (R-07 never re-derives a fact a real producer already
   computed). No classification supplied, or the supplied one honestly
   reports `unknown=True` (HA-PCPG-4's own "UNKNOWN must remain
   UNKNOWN... never guessed", preserved exactly): `INDETERMINATE`,
   reason `DATA_GOVERNANCE_NOT_MATERIALIZED` or `DATA_CLASS_UNKNOWN`
   respectively — an unresolved/unknown input (I-04), never a guess
   toward `ALLOWED`.
3. If the data class IS known: `11_SECURITY_PRIVACY_OBSERVABILITY.md`
   §26's own Data Class Handling Matrix conditions EVERY class's own
   "AI / Provider Eligibility" on "if provider policy allows"/"permits"
   — and no such per-class eligibility policy has a producer anywhere in
   this codebase (`00_FIELD.md` §12, FBR-PCPG-5's own cited
   `GAP-08-002/008`: "Required policy dimensions ... D3, D4 and D9
   remain unresolved. 11 does not fabricate their answers."). A KNOWN
   classification therefore still cannot lawfully cross into a provider
   computation today: `DATA_BOUNDARY` (§6's own verbatim definition,
   "the inputs cannot lawfully cross (11)"), reason
   `PROVIDER_ELIGIBILITY_POLICY_NOT_MATERIALIZED`, citing GAP-08-008 —
   never `ALLOWED`.

`ALLOWED` is therefore STILL never produced by this increment for a
`PROVIDER_COMPUTATION` delta today — not because the decision is
unconditional any more (it genuinely is not: it now branches on real,
admitted-operation and real-classification facts), but because
independent, genuinely still-open gaps each separately and sufficiently
block it: GAP-08-008's own per-class provider-eligibility policy here,
and, upstream of this module entirely, I-12's own "Source status"
producer — deliberately NOT built or consulted here (see
`WU-PFC-PCPG-15.md` §4). `CLASSIFICATION != AUTHORITY`; admission of the
operation class is not equivalence to authority; `GOVERNANCE_ADMISSIBLE
!= CAN_SEND`. This module computes none of those equivalences.

`DENIED` is still never emitted: its own producer (an immutable-source-
mutation detector) does not exist anywhere in this codebase.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import cast

from application.pcpg_candidate_deltas import CandidateDelta
from application.pcpg_data_classification import DataClassification
from application.pcpg_field_snapshot import FieldSnapshot
from application.pcpg_operation_index import ExecutionClass

OPERATION_CLASS_NOT_ADMITTED = "OPERATION_CLASS_NOT_ADMITTED"
"""Still the correct reason for any `PROVIDER_COMPUTATION` operation HD-29
(`HUMAN_DECISIONS.md`) does not name — `00_FIELD.md` §13 HA-PCPG-1's own
fail-closed default remains the governing reason for everything outside
HD-29's own conditional admission (WU-PFC-PCPG-15 update, module
docstring)."""

DATA_GOVERNANCE_NOT_MATERIALIZED = "DATA_GOVERNANCE_NOT_MATERIALIZED"
"""HD-29's own "Data Governance" prerequisite was not supplied for this
delta at all — an unresolved input (I-04), never a guess toward
`ALLOWED`."""

DATA_CLASS_UNKNOWN = "DATA_CLASS_UNKNOWN"
"""`classify_prompt_content` (FBR-PCPG-3) was supplied and honestly
reports `unknown=True` — HA-PCPG-4's own "UNKNOWN must remain UNKNOWN...
never guessed", preserved here exactly."""

PROVIDER_ELIGIBILITY_POLICY_NOT_MATERIALIZED = "PROVIDER_ELIGIBILITY_POLICY_NOT_MATERIALIZED"
"""The data class IS known, but `11_SECURITY_PRIVACY_OBSERVABILITY.md`
§26's own Handling Matrix conditions every class's AI/Provider
Eligibility on a per-class policy that has no producer anywhere in this
codebase (`00_FIELD.md` §12, FBR-PCPG-5's own cited `GAP-08-002/008`).
`DATA_BOUNDARY`'s own verbatim definition: "the inputs cannot lawfully
cross (11)\""""

NO_AUTHORITATIVE_PRODUCER = "NO_AUTHORITATIVE_PRODUCER"
"""R-07's own FAILURE STATE, verbatim: "A delta with no authoritative
producer for its authority gives INDETERMINATE with reason
NO_AUTHORITATIVE_PRODUCER.\""""

SEMANTIC_UNKNOWN = "SEMANTIC_UNKNOWN"
"""I-04: an UNKNOWN operation (no catalog match with certainty) makes
the delta INDETERMINATE — never a guess."""

_PROVIDER_COMPUTATION_CONTRACTS: dict[str, str] = {
    "REQUEST_QUESTION_ANALYSIS": "AIOP-001",
    "REQUEST_QUESTION_CLUSTERING": "AIOP-002",
}
"""The closed, exhaustive operation -> contract correspondence for the
two `PROVIDER_COMPUTATION` operations in `pcpg_operation_index.py`'s own
closed catalog (FBR-PCPG-2, CLOSED) — grepped directly from that
module's own cited `architecture_ref` strings ("08 AIOP-001" /
"08 AIOP-002"), not invented. Deliberately duplicated from
`pcpg_capability.py`'s own identical table rather than imported: that
module already imports FROM this one (`Result`, `DeltaRecord`), so an
import in the other direction would be circular. Both tables cite the
exact same real source and must be kept in step by hand if the real
catalog ever grows a third `PROVIDER_COMPUTATION` operation."""

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
    data_classifications_by_delta_id: Mapping[str, DataClassification] | None = None,
) -> tuple[DeltaRecord, ...]:
    """The R-07 producer (this increment's own disclosed scope). Pure,
    deterministic, no I/O. `flags_by_delta_id` lets a caller attach the
    real, already-computed `DECISION_SUBSTITUTION_REQUESTED` flag from
    R-05's own `SemanticAction` — this module never re-derives it.
    `data_classifications_by_delta_id` is the same established pattern
    for HD-29's own "Data Governance" prerequisite, from FBR-PCPG-3's
    real `classify_prompt_content` producer (WU-PFC-PCPG-15 update,
    module docstring) — this module never re-derives it either."""
    flags_by_delta_id = flags_by_delta_id or {}
    data_classifications_by_delta_id = data_classifications_by_delta_id or {}
    session_actions = snapshot.session.actions if snapshot.session is not None else {}

    records: list[DeltaRecord] = []
    for delta in deltas:
        result: Result
        reason: str | None

        if delta.operation is None:
            result, reason = Result.INDETERMINATE, SEMANTIC_UNKNOWN
        elif delta.execution_class is ExecutionClass.PROVIDER_COMPUTATION:
            contract = _PROVIDER_COMPUTATION_CONTRACTS.get(delta.operation)
            if contract is None or contract not in snapshot.ai_contracts_admitted:
                result, reason = Result.GOVERNANCE_BOUNDARY, OPERATION_CLASS_NOT_ADMITTED
            else:
                classification = data_classifications_by_delta_id.get(delta.delta_id)
                if classification is None:
                    result, reason = Result.INDETERMINATE, DATA_GOVERNANCE_NOT_MATERIALIZED
                elif classification.unknown:
                    result, reason = Result.INDETERMINATE, DATA_CLASS_UNKNOWN
                else:
                    result, reason = (
                        Result.DATA_BOUNDARY,
                        PROVIDER_ELIGIBILITY_POLICY_NOT_MATERIALIZED,
                    )
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
    "DATA_CLASS_UNKNOWN",
    "DATA_GOVERNANCE_NOT_MATERIALIZED",
    "NO_AUTHORITATIVE_PRODUCER",
    "OPERATION_CLASS_NOT_ADMITTED",
    "PROVIDER_ELIGIBILITY_POLICY_NOT_MATERIALIZED",
    "SEMANTIC_UNKNOWN",
    "DeltaRecord",
    "Result",
    "evaluate_deltas",
]
