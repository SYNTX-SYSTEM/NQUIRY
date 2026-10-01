"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — R-12: actor-safe projection → CYAN
(Architecture 26).

Source: `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md`
R-12: "INPUT: the full Observation Result ... OUTPUT: only what the actor
may already read: the actor's own raw intent; the semantic observation;
the delta results with reason codes; FBR, MLT, NVT and HAR (as holder
classes, not other people's binding internals); the capability values
with reasons; the proof ceiling; the basis identity and its derivation
time." PRECONDITION: "R-10 is complete." FAILURE STATE, verbatim: "no
projection without a complete result. On failure, CYAN receives an
honest 'unavailable' state with a reason, never a default capability."

E1 re-derivation (2026-10-01, independent, against `checkpoint-PFC-PCPG-10`):
`grep` for `ActorSafeProjection`/`derive_actor_safe_projection` outside
the RED text itself: zero hits in `packages/`. R-10 (capability) is real
and has no consumer yet. R-10's own DOWNSTREAM names only R-12 (R-13
"must not consume it as authority"). R-11's own PRECONDITION additionally
requires "it exists only if the MLT is non-empty" — vacuously never true
today (WU-7 through WU-10's own cross-checked fact: no delta is ever
`ALLOWED`, so the MLT is always empty) — so R-11 has no real work to
materialize beyond a trivial always-empty-input producer. R-12 has a
full, substantive OUTPUT to assemble from real producers and is named
CONSUMER by both R-09 and R-10 (R-11 is named by R-09 alone) — the same
evidence-based tie-break this field already used once before (R-04 over
R-06, WU-PFC-PCPG-4). **R-12 is the next First Broken Relation.**

SCOPE OF THIS WORK UNIT (disclosed, not silently narrowed)
------------------------------------------------------------
Five of R-12's own seven named OUTPUT items are real today:

1. "the actor's own raw intent" + the fingerprint half of "the basis
   identity" — `pcpg_observation.ObservationIngressResult.raw_intent` /
   `.raw_intent_digest_sha256` (R-01's own already-real producer; the
   module docstring there explicitly computes this digest FOR a future
   basis, naming `04_OBSERVATION_RESULT.md` §9's own "raw-intent
   fingerprint" verbatim).
2. "the semantic observation" — `pcpg_simplix.SemanticObservation` (R-05)
   verbatim.
3. "the delta results with reason codes" — `pcpg_delta_evaluation.
   DeltaRecord` tuple (R-07) verbatim; `reason` is already one of its
   fields.
4. "FBR, MLT, NVT and HAR (as holder classes, not other people's binding
   internals)" — `pcpg_chain_results.ChainResult` (R-09) verbatim. The
   "not other people's binding internals" constraint is already satisfied
   BY CONSTRUCTION, not by a new filter this module adds: every object in
   this Field's own pipeline, from `pcpg_field_snapshot.FieldSnapshot`
   onward, carries only the CURRENT actor's own `AuthorityFact` tuple
   (R-03's own `reconstruct_field` reads bindings for `principal` alone);
   no other actor's identity or binding ever enters a `DeltaRecord`,
   `ChainResult` or `AuthorityRequirement` in the first place —
   `test_no_field_in_the_projection_carries_another_actors_identity`
   proves this directly against the real dataclass shapes, not merely in
   prose.
5. "the capability values with reasons" — `pcpg_capability.Capability`
   (R-10) verbatim.

The "derivation time" half of "the basis identity" is covered by
`pcpg_observation.ObservationIngressResult.observed_at` (the one point in
this pipeline a wall-clock time is already real and cited).

ONE ITEM IS EXPLICITLY NOT COVERED — never silently dropped:
- the richer "basis identity" composite beyond the fingerprint and
  derivation time (`04_OBSERVATION_RESULT.md` §9's full list: the actor
  identity and validated scope — already present via `delta_records`'
  own context, not duplicated into the basis; the canonical facts
  consulted as (reference, version) pairs; the authority facts consulted,
  including absence facts; the Pulse elements consulted, by reference;
  the rule-set version; the data-policy version; the provider-policy
  version and declared environment): none of these is tracked as a
  structured (reference, version) record anywhere in this codebase today
  — `pcpg_capability.py`'s own module docstring already disclosed this
  same gap for its own "basis identity" output field.

WU-PFC-PCPG-17 UPDATE: THE COMPOSED PROOF CEILING, PROJECTED DIRECTLY
  FROM R-08 — NOT ROUTED THROUGH R-09, R-10 OR R-11
--------------------------------------------------------------------------
`01_INVARIANTS.md` I-12's own Session-level composed ceiling
(`pcpg_composed_effect.ComposedEffect.composed_proof_ceiling`,
`checkpoint-PFC-PCPG-16`) is now a sixth parameter here, read verbatim
into `ActorSafeProjection.composed_proof_ceiling` — nothing else. The
companion discovery pass (recorded in this conversation, not a committed
file) reconstructed every candidate carrier from the real code before
this Work Unit began: R-09's `ChainResult` and R-10's `Capability` BOTH
already receive the full `ComposedEffect` object today, but NEITHER
relation's own RED-declared OUTPUT names "proof ceiling" anywhere — R-09
owns FBR/MLT/NVT/HAR/PARTIAL; R-10 owns GOVERNANCE_ADMISSIBLE/
PROVIDER_EXECUTABLE/CAN_SEND/basis identity (a freshness/versioning
key, a different concept). Threading the ceiling through either would be
exactly "a relation whose architecture does not legitimately own it."
R-12's own RED OUTPUT, by contrast, names "the proof ceiling" directly
(quoted at the top of this docstring) — R-12 is the one relation that
legitimately owns it. The precedent for reaching an upstream producer
directly, bypassing an intermediate relation that does not itself carry
the fact, is not new here: `delta_records` (R-07's own output) is
already a direct parameter, not received solely through R-09.

`R-12 MAY PROJECT != R-12 MAY RECOMPUTE`: this module performs a single
attribute read, `composed_effect.composed_proof_ceiling`, never a
computation, inference from `delta_records`, derivation from
`ChainResult`/`Capability`, or a guessed fallback for `None`. `PER-DELTA
CEILING != COMPOSED CEILING`: `delta_records[*].session_proof_ceiling`
(already real since `checkpoint-PFC-PCPG-16`, unaffected by this update)
and `composed_proof_ceiling` (this update) are two independent fields,
never merged or substituted for one another. `UNKNOWN CEILING !=
GOVERNED`: `None` is read and projected as `None`, never defaulted.
`PROOF CEILING != GOVERNANCE RESULT / CAPABILITY / PROVIDER ELIGIBILITY
/ SEND AUTHORITY`: `Capability`, `EligibleContentSet` and the future SEND
path are untouched by this Work Unit and remain the sole owners of their
own values. `SESSION-LEVEL I-12 != FULL I-12`; `PARTIAL I-12 != I-12
COMPLETE`: only `"FIXTURE_NON_PROOF"` / `"GOVERNED"` / `None` are ever
projected — no full source authority, arbitrary-input provenance,
mutability status, evidence status, per-input proof class or
provider-output proof class is claimed anywhere in this module.

THE FAILURE STATE, AND WHY IT IS NOT MODELED AS A SEPARATE BRANCH HERE
--------------------------------------------------------------------------
This function's own six parameters are all non-optional: Python's type
signature itself already enforces "no projection without a complete
result" at the call site — there is no way to call `derive_actor_safe_
projection` with a missing input. Any genuine upstream incompleteness
(an `ObservationInputRejected` raised by R-01 before a Session is even
reached; a `FieldSnapshot.unresolved` entry) is already modeled WITHIN
each upstream object's own disclosed fields (R-03's/R-04's own
`unresolved` tuples), not as a reason to withhold the projection itself —
withholding it would hide, not honestly surface, the very unresolved
facts those tuples exist to disclose. Wiring an actual "CYAN receives an
honest 'unavailable' state" HTTP response for a hard upstream failure (a
raised exception reaching a dispatch layer) is a dispatch-layer concern
this Work Unit does not build — no PCPG relation has an HTTP route yet
(R-10's own WU report: "R-10 has no HTTP surface in this Work Unit"; the
same holds for every relation back to R-03).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from application.pcpg_capability import Capability
from application.pcpg_chain_results import ChainResult
from application.pcpg_composed_effect import ComposedEffect
from application.pcpg_delta_evaluation import DeltaRecord
from application.pcpg_observation import ObservationIngressResult
from application.pcpg_simplix import SemanticObservation


@dataclass(frozen=True, slots=True)
class ActorSafeProjection:
    raw_intent: str
    raw_intent_digest_sha256: str
    derivation_time: datetime
    semantic_observation: SemanticObservation
    delta_records: tuple[DeltaRecord, ...]
    chain_result: ChainResult
    capability: Capability
    composed_proof_ceiling: str | None
    """I-12's own Session-level composed ceiling (WU-PFC-PCPG-17),
    projected verbatim from `ComposedEffect.composed_proof_ceiling` —
    never recomputed, never inferred from `delta_records`, never
    derived from `chain_result` or `capability`."""


def derive_actor_safe_projection(
    ingress: ObservationIngressResult,
    semantic_observation: SemanticObservation,
    delta_records: tuple[DeltaRecord, ...],
    chain_result: ChainResult,
    capability: Capability,
    composed_effect: ComposedEffect,
) -> ActorSafeProjection:
    """The R-12 producer (this increment's own disclosed scope). Pure,
    deterministic, no I/O — a plain re-packaging of six already-real
    producers' own output; it reads no new fact and derives no new
    governance value. PRECONDITION: every argument was produced for the
    same observation (same `raw_intent`, same actor, same basis)."""
    return ActorSafeProjection(
        raw_intent=ingress.raw_intent,
        raw_intent_digest_sha256=ingress.raw_intent_digest_sha256,
        derivation_time=ingress.observed_at,
        semantic_observation=semantic_observation,
        delta_records=delta_records,
        chain_result=chain_result,
        capability=capability,
        composed_proof_ceiling=composed_effect.composed_proof_ceiling,
    )


__all__ = [
    "ActorSafeProjection",
    "derive_actor_safe_projection",
]
