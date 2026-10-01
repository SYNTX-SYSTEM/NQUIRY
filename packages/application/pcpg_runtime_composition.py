"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — FBR-PCPG-18: runtime composition
of R-03 through R-12 for one real ingress result (Architecture 26).

RED reconciliation (recorded in the companion WU report, not a new
Architecture 26 text): the real prompt-observation request path
(`http_pcpg.dispatch_submit_observation`) executed only R-01/R-02 —
every producer from R-03 through R-12 already exists, individually
materialized and falsified in its own Work Unit, but nothing composed
them for one real request. No RED amendment: `02_RELATIONS.md`'s own
R-01..R-12 chain already specifies exactly this composition; this module
executes it, invents no new relation.

CANONICAL ORDER, EXACTLY AS DIRECTED
----------------------------------------
R-01/R-02 ingress (already real, called by the caller of this module,
`pcpg_observation.observe`) -> R-03 `reconstruct_field` -> R-04
`derive_pulse` -> R-05 `observe_semantics` -> R-06 `form_candidate_deltas`
-> R-07 `evaluate_deltas` -> R-08 `compose_effect` -> R-09
`derive_chain_result` -> R-10 `derive_capability` -> R-12
`derive_actor_safe_projection`. **R-11 is deliberately never called**:
its own PRECONDITION ("it exists only if the MLT is non-empty") is
vacuously never satisfied today (WU-7 through WU-17's own cross-checked
architectural fact), and its own OUTPUT (`EligibleContentSet`) is
explicitly on B-10's own DENY list for this projection — never produced,
never at risk of leaking.

`RUNTIME COMPOSITION != NEW GOVERNANCE SEMANTICS`: every call below is
exactly the same function, with exactly the same parameters, each
already real, already falsified, already closed in its own Work Unit.
This module computes nothing a prior relation did not already compute;
it only sequences the real calls in the real order and fails closed
honestly when one of them cannot honestly proceed.

SCOPE OF THIS WORK UNIT (disclosed, not silently narrowed)
------------------------------------------------------------
- `data_classifications_by_delta_id` (R-07) and `flags_by_delta_id`
  (R-07) are NOT populated here: both require correlating a
  `CandidateDelta`'s own `delta_id` back to the originating
  `SemanticAction` it was formed from, a correlation this Work Unit does
  not build (it would mean either inventing a new index convention or
  reaching into R-06's own internal enumeration, neither authorized
  here, "do not refactor [producer modules] for convenience"). Every
  `PROVIDER_COMPUTATION` delta in the real runtime therefore resolves to
  `INDETERMINATE`/`DATA_GOVERNANCE_NOT_MATERIALIZED` today (R-07's own
  already-honest, already-proven branch, WU-PFC-PCPG-15) — not a
  regression, not a guess, the same honest value R-07 already produces
  for an unsupplied classification.
- `observe_semantics` is called without `in_scope_references`/
  `out_of_scope_references`: resolving which canonical objects are
  "in scope" for a real Session is a separate correlation this Work Unit
  does not build. Every `target` therefore resolves honestly to `None`
  (UNKNOWN) rather than ever becoming a real reference or a guessed
  `"OUT_OF_SCOPE"` — I-04's own "never a guess", not a gap introduced by
  this module.

FAIL-CLOSED, NEVER A SYNTHESIZED PARTIAL VALUE
----------------------------------------------------
Each of the three wire-contract `reasonCode` values maps to exactly one
real failure this composition can honestly distinguish:
- `SEMANTIC_OBSERVATION_UNAVAILABLE`: R-05's own `SemanticObservation
  Unavailable` (00_FIELD.md: "not even one clause... can be parsed").
- `FIELD_RECONSTRUCTION_UNAVAILABLE`: R-03's own `reconstruct_field`
  RAISING (`QueryDenied`, via `workspace_overview`'s own `_context()`
  translation) — a structural failure, never R-03's own honestly-
  disclosed `unresolved` tuple being non-empty. An unresolved session or
  provider fact is NOT a reason to fail the whole composition (R-03's
  own module docstring: "the snapshot still returns... never a stack
  trace that takes down the whole reconstruction") — `ABSENT != FALSE`,
  `UNKNOWN != DENIED`: the rest of this Field's own pipeline already
  carries an unresolved session gracefully (R-07's own `NO_
  AUTHORITATIVE_PRODUCER` branch, proven since `checkpoint-PFC-PCPG-7`).
- `PROJECTION_INCOMPLETE`: any other, genuinely unexpected failure from
  R-04 onward — caught broadly, deliberately, so a real production
  incident never surfaces as an uncaught 500 with no honest reason code,
  and never as a silently-synthesized, partially-fabricated capability
  value either.
"""

from __future__ import annotations

from dataclasses import dataclass

from security.identity import AuthenticatedPrincipal

from application.composition import GovernedPorts
from application.inquiry_queries import QueryDenied
from application.pcpg_actor_projection import ActorSafeProjection, derive_actor_safe_projection
from application.pcpg_candidate_deltas import form_candidate_deltas
from application.pcpg_capability import derive_capability
from application.pcpg_chain_results import derive_chain_result
from application.pcpg_composed_effect import compose_effect
from application.pcpg_delta_evaluation import evaluate_deltas
from application.pcpg_field_pulse import derive_pulse
from application.pcpg_field_snapshot import reconstruct_field
from application.pcpg_observation import ObservationIngressResult
from application.pcpg_simplix import SemanticObservationUnavailable, observe_semantics

SEMANTIC_OBSERVATION_UNAVAILABLE = "SEMANTIC_OBSERVATION_UNAVAILABLE"
FIELD_RECONSTRUCTION_UNAVAILABLE = "FIELD_RECONSTRUCTION_UNAVAILABLE"
PROJECTION_INCOMPLETE = "PROJECTION_INCOMPLETE"

_REASON_CODES = frozenset(
    {SEMANTIC_OBSERVATION_UNAVAILABLE, FIELD_RECONSTRUCTION_UNAVAILABLE, PROJECTION_INCOMPLETE}
)


@dataclass(frozen=True, slots=True)
class GovernanceObservationUnavailable:
    reason_code: str

    def __post_init__(self) -> None:
        if self.reason_code not in _REASON_CODES:
            raise ValueError(f"not a real wire-contract reason code: {self.reason_code!r}")


def derive_governance_observation(
    ports: GovernedPorts,
    principal: AuthenticatedPrincipal,
    ingress: ObservationIngressResult,
) -> ActorSafeProjection | GovernanceObservationUnavailable:
    """FBR-PCPG-18's own producer: R-03 through R-12, in canonical order,
    for one real `ObservationIngressResult` (R-01/R-02's own already-real
    output). Never calls R-11, R-13, or any provider path."""
    try:
        semantic_observation = observe_semantics(ingress.raw_intent, ingress.declared_purpose)
    except SemanticObservationUnavailable:
        return GovernanceObservationUnavailable(SEMANTIC_OBSERVATION_UNAVAILABLE)

    try:
        snapshot = reconstruct_field(
            ports,
            principal,
            workspace_id=ingress.workspace_id,
            session_id=ingress.session_id,
            now=ingress.observed_at,
        )
    except QueryDenied:
        return GovernanceObservationUnavailable(FIELD_RECONSTRUCTION_UNAVAILABLE)

    try:
        pulse = derive_pulse(
            ports,
            snapshot,
            workspace_id=ingress.workspace_id,
            session_id=ingress.session_id,
        )
        deltas = form_candidate_deltas(semantic_observation, snapshot)
        records = evaluate_deltas(deltas, snapshot)
        composed_effect = compose_effect(records)
        chain_result = derive_chain_result(records, composed_effect, pulse)
        capability = derive_capability(
            chain_result,
            composed_effect,
            pulse,
            snapshot.ai_contracts_admitted,
            snapshot.provider,
        )
        return derive_actor_safe_projection(
            ingress,
            semantic_observation,
            records,
            chain_result,
            capability,
            composed_effect,
        )
    except Exception:  # noqa: BLE001 -- deliberate: fail closed, never an uncaught 500 (module docstring)
        return GovernanceObservationUnavailable(PROJECTION_INCOMPLETE)


__all__ = [
    "FIELD_RECONSTRUCTION_UNAVAILABLE",
    "PROJECTION_INCOMPLETE",
    "SEMANTIC_OBSERVATION_UNAVAILABLE",
    "GovernanceObservationUnavailable",
    "derive_governance_observation",
]
