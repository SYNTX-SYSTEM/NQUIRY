"""BoundaryRegistry and the monotonic-restriction chain evaluator.

Source: 06_BOUNDARY_ARCHITECTURE.md §3 (Boundary Composition Algebra),
§4 (Canonical Consequential Request Path), §34 (Boundary Ordering
Invariant), §36-39/§47 (AC-06-002 ALLOW non-transitive, AC-06-003
downstream cannot override upstream DENY, AC-06-004 REQUIRE is named
and re-evaluated, AC-06-005 ESCALATE is non-authorizing, AC-06-013
least-permissive interpretation under uncertainty);
14_IMPLEMENTATION_SEQUENCE.md §15 (BOUNDARY ENGINE).

WHAT `evaluate_chain` GUARANTEES
------------------------------------
1. Evaluation is strictly sequential and stops at the first
   non-`ALLOW` result (06 §3: "ALLOW only permits evaluation of the
   next required boundary"). A boundary later in the ordered sequence
   is never even invoked once an earlier one returns `DENY`/`REQUIRE`/
   `ESCALATE` -- not "invoked but ignored". This is the strongest
   available proof against "downstream ALLOW overrides upstream DENY"
   (AC-06-003): the downstream evaluator's `evaluate()` method is
   provably never called, so it cannot influence the outcome no matter
   what it would have returned.
2. `DENY`/`REQUIRE`/`ESCALATE` are all chain-terminal from this
   function's point of view (06 §3's algebra treats all three
   identically as "cannot become downstream ALLOW"); which one a
   boundary returns is preserved in the result, but none of the three
   receives any special further precedence over another here --
   06/AC-06-003 do not define one.
3. An unregistered `boundary_id`, a missing `BoundaryInput` for a
   requested `boundary_id`, an evaluator that raises, or an evaluator
   that returns something other than a well-formed `BoundaryProof` for
   the boundary actually requested, are all indistinguishable failure
   classes from this function's caller's point of view: each produces
   a fail-closed synthetic `DENY` proof and terminates the chain
   there. This is AC-06-013 applied literally ("If a boundary cannot
   determine whether a consequential operation is permitted: do not
   permit consequence... use DENY, REQUIRE, ESCALATE according to the
   known failure type") -- none of these four failure classes has a
   known, more specific type this generic engine could name, so `DENY`
   (the strictest of the three, and the one 06 §2.2 calls outright
   terminal) is the correct default rather than guessing at `REQUIRE`
   or `ESCALATE`, which each imply a *specific*, nameable missing
   prerequisite or escalation target this function does not have.
4. Nothing here caches a `BoundaryProof` or accepts one as input to
   short-circuit a future evaluation -- there is no method anywhere in
   this module whose signature accepts a `BoundaryProof`. A "cached
   ALLOW" attack has no surface to land on: `evaluate_chain` always
   re-invokes every evaluator up to the terminal result, every time it
   is called (mirroring `AuthorityResolver.resolve()`'s own "always
   reads live" discipline from PKG-03).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from semantic_types.versions import ContractVersion

from boundaries.types import (
    BoundaryContext,
    BoundaryEvaluator,
    BoundaryId,
    BoundaryInput,
    BoundaryProof,
    BoundaryResult,
)

_FAIL_CLOSED_VERSION = ContractVersion("0")
"""Placeholder version stamped on a synthetic fail-closed proof, where
no real evaluator produced one to carry its own declared
`boundary_version`. `"0"` is not a claim that a boundary named "0"
exists; it is the lowest value `ContractVersion` accepts, chosen so a
fail-closed proof can never be mistaken for a genuine evaluator's
output at any real version.
"""


class BoundaryRegistrationError(Exception):
    """Raised when a second evaluator attempts to register for a
    `BoundaryId` that already has one. No silent overwrite: exactly
    one evaluator may claim a given boundary at a time, matching the
    default-deny posture the rest of this codebase's registries use
    (14 §45).
    """


class BoundaryRegistry:
    """Maps `BoundaryId` to the one `BoundaryEvaluator` currently
    registered for it. Holds no evaluation state of its own -- looking
    an evaluator up does not evaluate anything, and nothing here is
    ever treated as a cached decision.
    """

    def __init__(self) -> None:
        self._evaluators: dict[BoundaryId, BoundaryEvaluator] = {}

    def register(self, evaluator: BoundaryEvaluator) -> None:
        if evaluator.boundary_id in self._evaluators:
            raise BoundaryRegistrationError(
                f"a BoundaryEvaluator is already registered for {evaluator.boundary_id!r}"
            )
        self._evaluators[evaluator.boundary_id] = evaluator

    def get(self, boundary_id: BoundaryId) -> BoundaryEvaluator | None:
        return self._evaluators.get(boundary_id)


@dataclass(frozen=True, slots=True)
class BoundaryChainResult:
    """The outcome of evaluating one ordered sequence of boundaries for
    one request. `result` is the chain's overall verdict: `ALLOW` only
    if every evaluated boundary returned `ALLOW`; otherwise the first
    non-`ALLOW` result encountered. `proofs` holds every proof actually
    produced, in evaluation order, up to and including the terminal
    one -- a boundary after the terminal one contributes no proof at
    all, because it was never invoked (see module docstring, point 1).
    """

    result: BoundaryResult
    proofs: tuple[BoundaryProof, ...]
    terminal_boundary_id: BoundaryId | None

    @property
    def is_allowed(self) -> bool:
        return self.result is BoundaryResult.ALLOW


def _fail_closed_proof(
    boundary_id: BoundaryId, context: BoundaryContext, *, reason_code: str
) -> BoundaryProof:
    return BoundaryProof(
        boundary_id=boundary_id,
        boundary_version=_FAIL_CLOSED_VERSION,
        result=BoundaryResult.DENY,
        reason_code=reason_code,
        workspace_id=context.workspace_id,
        actor=context.actor,
        input_refs=(),
        authoritative_version_refs=(),
        authority_proof=None,
        evidence_proof_refs=(),
        evaluated_at=context.evaluated_at,
        correlation_id=context.correlation_id,
    )


def evaluate_chain(
    registry: BoundaryRegistry,
    ordered_boundary_ids: Sequence[BoundaryId],
    boundary_inputs: Mapping[BoundaryId, BoundaryInput],
    context: BoundaryContext,
) -> BoundaryChainResult:
    """Evaluate `ordered_boundary_ids` against `registry`, in order,
    stopping at the first non-`ALLOW` result. An empty sequence is a
    vacuous `ALLOW` with no proofs -- 06 §4: "Not every operation uses
    every boundary. The required subset is operation-specific"; a
    caller determines which boundaries apply to *its* operation, this
    function does not second-guess that list.
    """
    proofs: list[BoundaryProof] = []

    for boundary_id in ordered_boundary_ids:
        evaluator = registry.get(boundary_id)
        if evaluator is None:
            # Mandatory adversarial attack: unknown boundary.
            proof = _fail_closed_proof(
                boundary_id, context, reason_code="UNKNOWN_BOUNDARY_NOT_REGISTERED"
            )
            proofs.append(proof)
            return BoundaryChainResult(BoundaryResult.DENY, tuple(proofs), boundary_id)

        boundary_input = boundary_inputs.get(boundary_id)
        if boundary_input is None:
            proof = _fail_closed_proof(boundary_id, context, reason_code="MISSING_BOUNDARY_INPUT")
            proofs.append(proof)
            return BoundaryChainResult(BoundaryResult.DENY, tuple(proofs), boundary_id)

        try:
            proof = evaluator.evaluate(boundary_input, context)
        except Exception as exc:  # noqa: BLE001 -- deliberate: any evaluator failure fails closed
            # Mandatory adversarial attack: evaluator exception.
            proof = _fail_closed_proof(
                boundary_id,
                context,
                reason_code=f"EVALUATOR_EXCEPTION:{type(exc).__name__}",
            )
            proofs.append(proof)
            return BoundaryChainResult(BoundaryResult.DENY, tuple(proofs), boundary_id)

        if (
            not isinstance(proof, BoundaryProof)
            or not isinstance(proof.result, BoundaryResult)
            or proof.boundary_id is not boundary_id
        ):
            # Mandatory adversarial attack: missing result (an
            # evaluator returning None, a bare string, or a proof for
            # the wrong boundary_id is treated identically -- none of
            # them is a well-formed decision for the boundary actually
            # requested).
            proof = _fail_closed_proof(
                boundary_id, context, reason_code="MALFORMED_EVALUATOR_RESULT"
            )
            proofs.append(proof)
            return BoundaryChainResult(BoundaryResult.DENY, tuple(proofs), boundary_id)

        proofs.append(proof)
        if proof.result is not BoundaryResult.ALLOW:
            # DENY, REQUIRE, or ESCALATE: chain-terminal (06 section 3).
            return BoundaryChainResult(proof.result, tuple(proofs), boundary_id)

    terminal = ordered_boundary_ids[-1] if ordered_boundary_ids else None
    return BoundaryChainResult(BoundaryResult.ALLOW, tuple(proofs), terminal)


__all__ = ["BoundaryRegistrationError", "BoundaryRegistry", "BoundaryChainResult", "evaluate_chain"]
