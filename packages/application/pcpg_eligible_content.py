"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — R-11: provider-safe projection
eligibility, constraints only (Architecture 26).

Source: `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md`
R-11: "INPUT: the MLT, its composed inputs and data classes ... OUTPUT:
the eligible content set: the minimum necessary inputs and the retained
instruction semantics, with explicit exclusions. It is not a provider
payload, it is not transmitted, and it produces no manifest."
PRECONDITION: "R-09 and R-10 are complete. It exists only if the MLT is
non-empty." FAILURE STATE, verbatim: "any content that cannot be
classified, or that is not provably necessary, is excluded. An empty MLT
gives no eligible set." PROOF, verbatim: "no blocked delta, forbidden
instruction, secret, cross-Workspace datum, DC-07 datum or governance
internal is ever in the eligible set (P-13)."

E1 re-derivation (2026-10-01, independent, against `checkpoint-PFC-PCPG-11`):
`grep` for `EligibleContentSet`/`derive_eligible_content`/
`EligibilityResult` outside the RED text itself: zero hits in
`packages/`. R-12 (actor-safe projection) is real and R-10 has two named
consumers (R-12, closed; R-11, not yet). R-11 is the one ordinary
relation in `02_RELATIONS.md`'s own table not yet materialized — R-13
(future SEND gate) and R-14 (reconstruction after material change) are
both explicitly marked "boundary relation; not materialized" /
cross-cutting by the RED text itself, never ordinary Work Units. **R-11
is the next First Broken Relation.** It is NOT a Human Authority boundary
and NOT the SEND path: its own OUTPUT is explicitly "not a provider
payload, it is not transmitted, and it produces no manifest" — a
backend-only, pre-SEND relation like every other one in this Field.

A FURTHER SIMPLIFICATION THIS WORK UNIT'S OWN ANALYSIS FOUND
----------------------------------------------------------------
The relation's own FAILURE STATE states TWO independent reasons the
eligible set is empty: "any content that cannot be classified ... is
excluded" AND "an empty MLT gives no eligible set" (stated separately,
as if they were two different cases). They are not, in this Field today:
no data-class classifier exists anywhere in this codebase (FBR-PCPG-3,
GAP-11-006, still OPEN — the same already-disclosed gap R-07's, R-08's
and R-10's own module docstrings each cite independently). Since NOTHING
can ever be classified today, EVERY delta's content — whether the MLT is
empty or (hypothetically) non-empty — is excluded under the FIRST clause
alone. The eligible content set (`eligible_inputs`,
`retained_instruction_semantics`) is therefore `()` unconditionally
today, for both reasons at once, not merely for the one the RED text's
own worked example emphasizes. This is a disclosed, proven simplification
(`test_the_eligible_set_is_empty_for_both_an_empty_and_a_hypothetical_
non_empty_mlt`), not a redesign of the relation: the two FAILURE STATE
clauses are not contradicted, both are honored, and the `result`/`reason`
fields still distinguish which clause actually applied for diagnostic
honesty.

SCOPE OF THIS WORK UNIT (disclosed, not silently narrowed)
------------------------------------------------------------
This increment computes the empty-set case fully and honestly (real,
proven for both the empty-MLT case and the always-reachable
cannot-classify case). The richer, real-world content of a genuinely
non-empty, classifiable MLT — "the minimum necessary inputs", "the
retained instruction semantics", the composed-input/data-class
inspection R-11's own INPUT names — has no producer anywhere in this
codebase (no data-class classifier exists at all) and is not built here;
building it now would be materializing FBR-PCPG-3's own still-OPEN scope
under this Work Unit, not R-11's minimum coherent delta.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from application.pcpg_delta_evaluation import DeltaRecord

CONTENT_NOT_CLASSIFIABLE = "CONTENT_NOT_CLASSIFIABLE"
"""R-11's own FAILURE STATE, verbatim: "any content that cannot be
classified ... is excluded." No data-class classifier exists anywhere in
this codebase (FBR-PCPG-3/GAP-11-006, still OPEN) — every retained
delta's content is therefore unclassifiable today, unconditionally."""

MLT_EMPTY = "MLT_EMPTY"
"""R-11's own FAILURE STATE, verbatim: "an empty MLT gives no eligible
set." Reuses the exact same name `pcpg_capability.MLT_EMPTY` already
established for the identical real-world condition (I-20: one
definition, not a second divergent name for the same fact)."""


class EligibilityResult(Enum):
    """Not a RED-cited enum (R-11's own OUTPUT text names no fixed
    vocabulary the way R-07's `Result`/R-08's `CompositionResult` are
    named) — a minimal, disclosed `[IMPLEMENTATION CHOICE]` distinguishing
    the two FAILURE STATE clauses for diagnostic honesty, not a value
    with real-world provider-facing meaning."""

    NO_ELIGIBLE_CONTENT = "NO_ELIGIBLE_CONTENT"


@dataclass(frozen=True, slots=True)
class EligibleContentSet:
    eligible_inputs: tuple[str, ...]
    retained_instruction_semantics: tuple[str, ...]
    excluded_delta_ids: tuple[str, ...]
    result: EligibilityResult
    reasons: frozenset[str]


def derive_eligible_content(mlt: tuple[DeltaRecord, ...]) -> EligibleContentSet:
    """The R-11 producer (this increment's own disclosed scope). Pure,
    deterministic, no I/O. PRECONDITION: `mlt` is
    `ChainResult.maximum_legitimate_transition` (R-09) for a delta set
    whose composition (R-08) and capability (R-10) are already complete.

    Always returns an empty eligible set today: an empty `mlt` is MLT_
    EMPTY by the relation's own first clause; a non-empty `mlt` is
    CONTENT_NOT_CLASSIFIABLE by its second (no classifier producer exists
    anywhere), so every retained delta is excluded either way (see the
    module docstring's own disclosed simplification)."""
    if not mlt:
        return EligibleContentSet(
            eligible_inputs=(),
            retained_instruction_semantics=(),
            excluded_delta_ids=(),
            result=EligibilityResult.NO_ELIGIBLE_CONTENT,
            reasons=frozenset({MLT_EMPTY}),
        )

    return EligibleContentSet(
        eligible_inputs=(),
        retained_instruction_semantics=(),
        excluded_delta_ids=tuple(delta.delta_id for delta in mlt),
        result=EligibilityResult.NO_ELIGIBLE_CONTENT,
        reasons=frozenset({CONTENT_NOT_CLASSIFIABLE}),
    )


__all__ = [
    "CONTENT_NOT_CLASSIFIABLE",
    "MLT_EMPTY",
    "EligibilityResult",
    "EligibleContentSet",
    "derive_eligible_content",
]
