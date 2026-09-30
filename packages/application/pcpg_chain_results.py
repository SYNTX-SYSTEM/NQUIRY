"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — R-09: chain results: FBR, MLT, NVT,
HAR, PARTIAL (Architecture 26).

Source: `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md`
R-09: "INPUT: the delta records, their dependency order, the composition
result and the Pulse." PRECONDITION: "R-08 is complete." FAILURE STATE:
"if the order is undeterminable (for example, cyclic or ambiguous
dependencies), FBR is INDETERMINATE and the MLT is empty."

E1 re-derivation (2026-10-01, independent, against `checkpoint-PFC-PCPG-8`):
`grep` for `FIRST_BROKEN_RELATION`/`FirstBrokenRelation`/`ChainResult`/
`derive_chain_result` outside this module and its own test: zero hits.
R-08 (composed effect) is real and has no consumer yet. R-09's own INPUT
("the delta records, their dependency order, the composition result and
the Pulse") is satisfied now: R-07's records, R-06's dependency order
(disclosed below), R-08's `ComposedEffect`, R-04's `Pulse` are all real.
R-09 is the next First Broken Relation.

SCOPE OF THIS WORK UNIT (disclosed, not silently narrowed)
------------------------------------------------------------
`04_OBSERVATION_RESULT.md` §7.2–§7.6 define the five chain-result
elements this increment produces: FIRST_BROKEN_RELATION,
MAXIMUM_LEGITIMATE_TRANSITION, NEXT_VALID_TRANSITION,
HUMAN_AUTHORITY_REQUIRED, PARTIAL.

DEPENDENCY ORDER — "the deltas' dependency order" is the given tuple
order. R-06's own disclosed DIRECT-delta scope (`pcpg_candidate_deltas.
py`) makes `dependency_edges` always `()`; with zero edges there is
nothing to topologically sort and no cycle is possible, so "dependency
order" and "the order the records were given in" coincide today. This
mirrors R-08's own already-disclosed simplification for the identical
reason (`pcpg_composed_effect.py`'s own docstring). The FAILURE STATE
("cyclic or ambiguous dependencies") cannot occur while this fact holds;
no cycle-detection producer is built to handle a case that has no real
input data to exercise it. If R-06 ever grows real IMPLIED-delta edges,
this module's own ordering assumption must be re-examined then, not
guessed at now.

FIRST_BROKEN_RELATION — exactly §7.2's own definition: the first record
in order whose RESULT is neither ALLOWED nor HUMAN_ACTION_AVAILABLE,
expressed as `<predecessor> → <broken>` (the predecessor is, by
construction, the immediately preceding record, which must already be
legitimate — otherwise IT would be the first broken one instead). `None`
when every record is legitimate, including the empty-records case.

MAXIMUM_LEGITIMATE_TRANSITION — exactly `composed_effect.retained`
(already dependency-order-preserving, already restricted to `ALLOWED`
records by R-08's own producer). §7.3's own further requirement —
"contains only PROVIDER_COMPUTATION deltas; HUMAN_COMMAND ... never
enter it, even when HUMAN_ACTION_AVAILABLE" — needs no extra filtering
here: `Result.ALLOWED` is never emitted by R-07 for a HUMAN_COMMAND delta
(cited fact, `pcpg_delta_evaluation.py`'s own algorithm), so the
HUMAN_COMMAND exclusion already holds by construction, not by a second
check invented in this module.

NEXT_VALID_TRANSITION — this increment materializes only rule 1 of
§7.4's three: "the first HUMAN_ACTION_AVAILABLE delta at or before the
FBR." When an FBR exists, the search range is every record up to and
including the FBR's own broken record (its own predecessor, if
legitimate-but-not-HUMAN_ACTION_AVAILABLE, is correctly skipped by the
same rule). When no FBR exists (every record already legitimate), "at or
before" places no upper bound, so the whole record list is searched —
the literal, unforced reading of a rule with no stated ceiling. Rule 2
("the product transition ... that the FBR depends on") is explicitly NOT
materialized: it requires a canonical-chain-to-product-transition lookup
(for example "compare → recommend → select → approve → order") that has
no producer anywhere in this codebase; inventing one now would be
designing new mapping surface, not deriving this relation's minimum
coherent implementation from what exists. Rule 3 ("else none") is the
correct fallback whenever rule 1 finds nothing, which this increment
never masks with a guessed rule-2 answer.

HUMAN_AUTHORITY_REQUIRED — produced only for the two RESULT classes that
already carry a real, existing authority answer: AUTHORITY_BOUNDARY
(the delta's own `reason`, one of the closed six codes R-07's own
`_AUTHORITY_REASON_CODES` grepped from `inquiry_queries.py`) and
GOVERNANCE_BOUNDARY (`00_FIELD.md` §13's own cited, genuinely OPEN
question `HA-PCPG-1`: "May a user-authored instruction ever become the
instruction of a provider computation? ... This defines what SEND is.").
STATE_BOUNDARY, DATA_BOUNDARY, DENIED and INDETERMINATE deltas get no
HAR entry: a state-legality wall or an unresolved/unknown delta names no
"required existing authority class ... and holder class" (there is
nothing to hold), and DATA_BOUNDARY/DENIED are never emitted by R-07
today regardless (their own producers do not exist, R-07's own disclosed
scope). Rendering the full RED-described shape — "the SESSION_CONTROL_
RIGHT holder of this Session", "the QUESTION_SELECTION_RIGHT holder who
selected the current primary" — for all six codes would require
resolving who actually holds each right today (a binding-holder lookup
this module does not perform); this increment discloses the real reason
code instead of inventing prose holder-class descriptions beyond the two
literal examples the RED text itself gives, and does not fabricate them
for the other four codes.

PARTIAL — exactly §7.6: true iff the retained set is strictly narrower
than the requested deltas. "Requested deltas" is `records` itself (R-06's
own producer already forms one candidate delta per REQUESTED-modality
clause, so every record given to this relation IS a requested delta).

PULSE — accepted as a parameter because R-09's own declared INPUT names
it explicitly, but not consumed by any branch in this increment: no
producer in this codebase translates a bare `Pulse.governance_blockers`
entry (for example `HA-23`) into a delta-shaped FBR/HAR entry when no
corresponding delta exists, and `Pulse` does not change any already-
computed `DeltaRecord.result` (R-07's own disclosed non-consumption of
Pulse, `pcpg_delta_evaluation.py`/`test_pcpg_delta_evaluation.py`, is the
precedent this increment follows rather than silently re-deciding).
Synthesizing a phantom delta from a bare Pulse blocker would fabricate
delta fields (`source_clause`, `span`, ...) that do not exist for it —
never done here.
"""

from __future__ import annotations

from dataclasses import dataclass

from application.pcpg_composed_effect import ComposedEffect
from application.pcpg_delta_evaluation import DeltaRecord, Result
from application.pcpg_field_pulse import Pulse

GOVERNANCE_QUESTION_HA_PCPG_1 = "HA-PCPG-1"
"""`00_FIELD.md` §13, verbatim: the genuinely OPEN Human Authority
question that governs `OPERATION_CLASS_NOT_ADMITTED` — the only reason
R-07 ever attaches to a `GOVERNANCE_BOUNDARY` result today."""

_LEGITIMATE_RESULTS = frozenset({Result.ALLOWED, Result.HUMAN_ACTION_AVAILABLE})
"""§7.2's own definition of "legitimate": neither of these two blocks the
chain."""

_AUTHORITY_ANSWERABLE_RESULTS = frozenset({Result.AUTHORITY_BOUNDARY, Result.GOVERNANCE_BOUNDARY})
"""The two RESULT classes for which this Field already has a real,
citable authority answer (see the module docstring's HUMAN_AUTHORITY_
REQUIRED section)."""


@dataclass(frozen=True, slots=True)
class FirstBrokenRelation:
    """§7.2's own form: `<predecessor> → <broken>`. `predecessor` is
    `None` exactly when `broken` is the first record in dependency
    order."""

    predecessor: DeltaRecord | None
    broken: DeltaRecord


@dataclass(frozen=True, slots=True)
class AuthorityRequirement:
    """§7.5, this increment's own disclosed subset (see module
    docstring): the delta's own already-real (`result`, `reason`), for
    the two RESULT classes this Field can already answer honestly."""

    delta_id: str
    result: Result
    reason: str | None


@dataclass(frozen=True, slots=True)
class ChainResult:
    first_broken_relation: FirstBrokenRelation | None
    maximum_legitimate_transition: tuple[DeltaRecord, ...]
    next_valid_transition: DeltaRecord | None
    human_authority_required: tuple[AuthorityRequirement, ...]
    partial: bool


def derive_chain_result(
    records: tuple[DeltaRecord, ...],
    composed_effect: ComposedEffect,
    pulse: Pulse,
) -> ChainResult:
    """The R-09 producer (this increment's own disclosed scope). Pure,
    deterministic, no I/O. PRECONDITION: `composed_effect` was produced
    by R-08 from exactly `records`."""
    del pulse  # explicit: accepted, not consumed today (see module docstring)

    first_broken_relation: FirstBrokenRelation | None = None
    broken_index: int | None = None
    for index, record in enumerate(records):
        if record.result not in _LEGITIMATE_RESULTS:
            predecessor = records[index - 1] if index > 0 else None
            first_broken_relation = FirstBrokenRelation(predecessor=predecessor, broken=record)
            broken_index = index
            break

    search_range = records[: broken_index + 1] if broken_index is not None else records
    next_valid_transition = next(
        (r for r in search_range if r.result is Result.HUMAN_ACTION_AVAILABLE), None
    )

    human_authority_required = tuple(
        AuthorityRequirement(delta_id=r.delta_id, result=r.result, reason=r.reason)
        for r in records
        if r.result in _AUTHORITY_ANSWERABLE_RESULTS
    )

    partial = len(composed_effect.retained) < len(records)

    return ChainResult(
        first_broken_relation=first_broken_relation,
        maximum_legitimate_transition=composed_effect.retained,
        next_valid_transition=next_valid_transition,
        human_authority_required=human_authority_required,
        partial=partial,
    )


__all__ = [
    "GOVERNANCE_QUESTION_HA_PCPG_1",
    "AuthorityRequirement",
    "ChainResult",
    "FirstBrokenRelation",
    "derive_chain_result",
]
