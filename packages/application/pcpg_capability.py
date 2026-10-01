"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — R-10: current capability, stratum 4
(Architecture 26).

Source: `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md`
R-10: "INPUT: the MLT, the composition, the Pulse, the admitted operation
classes and the provider route configuration ... OUTPUT:
GOVERNANCE_ADMISSIBLE, PROVIDER_EXECUTABLE and CAN_SEND, each with its
reasons, plus the basis identity." AUTHORITATIVE HOME:
`04_OBSERVATION_RESULT.md` §8. PRECONDITION: "R-09 is complete."
FAILURE STATE, verbatim: "any unresolved input makes the affected value
false, with a reason. The Field has no 'unknown = true' state."

E1 re-derivation (2026-10-01, independent, against `checkpoint-PFC-PCPG-9`):
`grep` for `GOVERNANCE_ADMISSIBLE`/`PROVIDER_EXECUTABLE`/`CAN_SEND`/
`derive_capability` outside this module's own files and the RED text
itself: zero hits in `packages/`. R-09 (chain results) is real and has no
consumer yet; R-10's own PRECONDITION ("R-09 is complete") is satisfied,
and it is the sole named CONSUMER of R-09 with no further open
precondition (R-11 additionally requires a non-empty MLT, vacuously never
true today; R-12 additionally requires R-10 complete). R-10 is the next
First Broken Relation.

SCOPE OF THIS WORK UNIT (disclosed, not silently narrowed)
------------------------------------------------------------
§8 lists 5 GOVERNANCE_ADMISSIBLE bullets. This increment computes 3 of
them from real, already-existing producers:

1. "the MLT is non-empty" — real, from `chain_result.maximum_legitimate_
   transition` (R-09's own output) directly.
2. "the composition is COMPOSABLE" — real, from `composed_effect.
   composition_result` (R-08's own output) directly; its own `reason`
   (only ever `COMPOSITION_CHECKS_NOT_MATERIALIZED` today, since
   `COMPOSITION_<BOUNDARY>` is never emitted — R-08's own disclosed
   scope) is carried through, not re-derived.
4. "every retained delta maps to an admitted operation class whose
   invocation this path may request" — real, via a small, CLOSED,
   grepped (not invented) correspondence: `pcpg_operation_index.py`'s
   own catalog is exhaustively proven to contain exactly two
   `PROVIDER_COMPUTATION` operations (FBR-PCPG-2, both increments
   CLOSED), and their contract IDs are cited verbatim in that module's
   own `architecture_ref` tuples ("08 AIOP-001" for
   `REQUEST_QUESTION_ANALYSIS`, "08 AIOP-002" for
   `REQUEST_QUESTION_CLUSTERING"). `pcpg_field_snapshot.
   AI_CONTRACTS_ADMITTED` already names both as admitted — this bullet
   is checked, never assumed, even though it never actually occurs today
   (there are only ever two possible `PROVIDER_COMPUTATION` operations,
   both already admitted, and — see below — bullets 1 and 2 can never
   both hold at once regardless of bullet 4).

Bullet 3 ("no INDETERMINATE delta is a dependency of, or shares inputs
with, a retained delta") and bullet 5 ("the composed data classes are
eligible for at least one route class") are explicitly NOT covered: no
per-delta input/data-sharing producer and no data-class classifier
(FBR-PCPG-3/GAP-11-006, still OPEN) exist anywhere in this codebase.
Building either now would be designing new classification surface, not
deriving this relation's minimum coherent implementation from what
exists.

PROVIDER_EXECUTABLE — §8's own already-published, cited, CURRENT value
is reused directly rather than re-derived from a producer this codebase
does not have: "PROVIDER_EXECUTABLE is false for every real scope
(`NO_ELIGIBLE_PROVIDER_ROUTE`)." No per-operation provider-route table
exists anywhere in this codebase (the provider-SDK-import-check gate
unconditionally forbids a provider import in this application layer),
so this bullet's FAILURE STATE applies unconditionally: an unresolved
input (no route producer at all) makes the value false, with the
already-cited reason — exactly the same pattern R-07 already uses for
`OPERATION_CLASS_NOT_ADMITTED` (a static, cited fact, not a per-call
guess). The one real, additionally-checkable sub-fact — "the environment
is declared" (AC-11-017), from `pcpg_field_snapshot.ProviderContext.
environment` — is included as an extra honest reason when absent, even
though it never changes the unconditional-false outcome (no route
producer exists regardless).

CAN_SEND = GOVERNANCE_ADMISSIBLE ∧ PROVIDER_EXECUTABLE — exactly §8's own
definition, a plain boolean AND of the two real values above.

A DISCLOSED MUTATION-PROOF LIMITATION — found during this Work Unit's own
mutation proof, not hidden: because `PROVIDER_EXECUTABLE` is an
unconditional `False` constant today and `GOVERNANCE_ADMISSIBLE` can
never be `True` today (see below), no real-input test fixture can ever
make either operand `True` — so a mutation that changes the `∧` combinator
to `∨` produces IDENTICAL observable behavior for every reachable input
today (both read `False` either way). This is not a test-authoring gap to
paper over with a fabricated input (there is no honest way to force
`GOVERNANCE_ADMISSIBLE` or `PROVIDER_EXECUTABLE` true without inventing a
producer this codebase does not have); the mutation proof instead targets
`can_send`'s own hardcoded-constant failure mode (§3), which the real
falsifiers do catch.

A FURTHER ARCHITECTURAL FACT THIS WORK UNIT'S OWN TESTING FOUND
------------------------------------------------------------------
GOVERNANCE_ADMISSIBLE can never be true in this Field as currently
composed — not merely "for every real observation today" (WU-7/8/9's own
already-proven, narrower claim about the MLT being empty), but by
logical construction of R-08's own already-proven design: an empty
retained set is always `COMPOSABLE` (bullet 2 holds) but then always
fails bullet 1 (`MLT_EMPTY`); a non-empty retained set could satisfy
bullet 1, but `compose_effect` always returns `INDETERMINATE` for ANY
non-empty retained set (R-08's own disclosed scope: the real composition
sub-checks have no producer), so it always fails bullet 2. Bullets 1 and
2 are therefore mutually exclusive today, even hypothetically — proven
directly by `test_governance_admissible_can_never_be_true_today_bullets_
one_and_two_are_mutually_exclusive`, not merely asserted in prose. This
is a disclosed, cross-relation consequence of R-08's own already-closed
design, not a defect in R-08 (its own WU report fully justifies the
choice) and not something this Work Unit changes.

BASIS IDENTITY — `04_OBSERVATION_RESULT.md` §9 defines "the basis" as a
cross-cutting re-derivation discipline (derive on read, never cache, no
key proves currency), not a new structured field this relation must
compute. This increment already satisfies that discipline by being pure
and taking no cache (`test_same_inputs_give_the_same_capability_every_
time` proves it); it does not materialize a separate `basis_identity`
output field, since §9 names no concrete producer or shape for one
beyond the general principle this module already honors.

PULSE — accepted as a parameter because R-10's own declared INPUT names
it explicitly, but not consumed by any branch in this increment, for the
same reason already disclosed twice in this field (R-07's and R-09's own
module docstrings): no bullet of §8's own GOVERNANCE_ADMISSIBLE/
PROVIDER_EXECUTABLE definition is itself a Pulse-shaped fact, and no
producer exists to translate a Pulse element into one.
"""

from __future__ import annotations

from dataclasses import dataclass

from application.pcpg_chain_results import ChainResult
from application.pcpg_composed_effect import ComposedEffect, CompositionResult
from application.pcpg_field_pulse import Pulse
from application.pcpg_field_snapshot import ProviderContext

MLT_EMPTY = "MLT_EMPTY"
"""This relation's own disclosed reason for GOVERNANCE_ADMISSIBLE bullet
1 ("the MLT is non-empty") failing — the real-world manifestation,
already cited by `04_OBSERVATION_RESULT.md` §8's own "Current NQUIRY
values" paragraph, of `OPERATION_CLASS_NOT_ADMITTED` (every
`PROVIDER_COMPUTATION` delta is `GOVERNANCE_BOUNDARY` today, so no delta
is ever retained). R-10's own declared INPUT is the MLT itself, not
individual delta records, so this increment names the bullet it can
actually see failing rather than reaching back for the deeper root
cause outside its own declared input shape."""

OPERATION_NOT_ADMITTED_FOR_RETAINED_DELTA = "OPERATION_NOT_ADMITTED_FOR_RETAINED_DELTA"
"""GOVERNANCE_ADMISSIBLE bullet 4's own failure reason — never reachable
today given the closed, exhaustive two-operation `PROVIDER_COMPUTATION`
catalog (both already admitted), but defined and checked honestly rather
than assumed."""

NO_ELIGIBLE_PROVIDER_ROUTE = "NO_ELIGIBLE_PROVIDER_ROUTE"
"""`04_OBSERVATION_RESULT.md` §8, verbatim, cited directly: the real,
already-published, unconditional reason PROVIDER_EXECUTABLE is false for
every real scope today — no per-operation provider-route producer exists
anywhere in this codebase."""

NO_ENVIRONMENT_DECLARED = "NO_ENVIRONMENT_DECLARED"
"""AC-11-017's own requirement ("the environment is declared"), checked
honestly from the real `ProviderContext.environment` even though it
never changes PROVIDER_EXECUTABLE's unconditional-false outcome today."""

_PROVIDER_COMPUTATION_CONTRACTS: dict[str, str] = {
    "REQUEST_QUESTION_ANALYSIS": "AIOP-001",
    "REQUEST_QUESTION_CLUSTERING": "AIOP-002",
}
"""The closed, exhaustive operation -> contract correspondence for the
two `PROVIDER_COMPUTATION` operations in `pcpg_operation_index.py`'s own
closed catalog (FBR-PCPG-2, both increments CLOSED) — grepped directly
from that module's own cited `architecture_ref` strings ("08 AIOP-001" /
"08 AIOP-002"), not invented here."""


@dataclass(frozen=True, slots=True)
class Capability:
    governance_admissible: bool
    governance_admissible_reasons: frozenset[str]
    provider_executable: bool
    provider_executable_reasons: frozenset[str]
    can_send: bool


def derive_capability(
    chain_result: ChainResult,
    composed_effect: ComposedEffect,
    pulse: Pulse,
    admitted_operation_classes: frozenset[str],
    provider: ProviderContext,
) -> Capability:
    """The R-10 producer (this increment's own disclosed scope). Pure,
    deterministic, no I/O. PRECONDITION: `chain_result` was produced by
    R-09 and `composed_effect` by R-08, from the same delta records."""
    del pulse  # accepted (declared INPUT), not consumed (see module docstring)

    governance_reasons: set[str] = set()

    mlt = chain_result.maximum_legitimate_transition
    if not mlt:
        governance_reasons.add(MLT_EMPTY)

    if composed_effect.composition_result is not CompositionResult.COMPOSABLE:
        governance_reasons.add(composed_effect.reason or composed_effect.composition_result.value)

    for delta in mlt:
        contract = _PROVIDER_COMPUTATION_CONTRACTS.get(delta.operation or "")
        if contract is None or contract not in admitted_operation_classes:
            governance_reasons.add(OPERATION_NOT_ADMITTED_FOR_RETAINED_DELTA)

    governance_admissible = not governance_reasons

    provider_reasons: set[str] = {NO_ELIGIBLE_PROVIDER_ROUTE}
    if provider.environment is None:
        provider_reasons.add(NO_ENVIRONMENT_DECLARED)
    provider_executable = False  # unconditional: no route producer exists in this codebase

    can_send = governance_admissible and provider_executable

    return Capability(
        governance_admissible=governance_admissible,
        governance_admissible_reasons=frozenset(governance_reasons),
        provider_executable=provider_executable,
        provider_executable_reasons=frozenset(provider_reasons),
        can_send=can_send,
    )


__all__ = [
    "MLT_EMPTY",
    "NO_ELIGIBLE_PROVIDER_ROUTE",
    "NO_ENVIRONMENT_DECLARED",
    "OPERATION_NOT_ADMITTED_FOR_RETAINED_DELTA",
    "Capability",
    "derive_capability",
]
