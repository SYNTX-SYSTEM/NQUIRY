"""Boundary engine core types: BoundaryInput, BoundaryContext, BoundaryResult,
BoundaryProof, and the BoundaryEvaluator contract.

Source: 06_BOUNDARY_ARCHITECTURE.md §1 (Boundary Definition), §2 (Boundary
Decision Semantics — the exact 4-value result vocabulary), §4 (Canonical
Consequential Request Path — the 18 named boundary IDs);
14_IMPLEMENTATION_SEQUENCE.md §15 (BOUNDARY ENGINE — the exact
`BoundaryProof` field list).

WHAT THIS MODULE IS
--------------------
The generic engine vocabulary every concrete boundary evaluator (BND-001
through BND-018) will be built against. 14's own file-level implementation
map assigns exactly `packages/boundaries/types.py` (BoundaryProof) and
`packages/boundaries/registry.py` (BND registry) to this package -- no
concrete evaluator file. PKG-08's manifest confirms this narrowly
("PUBLIC INTERFACES: BoundaryEvaluator registry"); the next package in
the DAG, PKG-09 ("Prototype boundaries 001-008"), separately claims
"PUBLIC INTERFACES: BND-001..008" as its own scope. Building a concrete
evaluator here would be exactly the "successor behavior" the package
boundary forbids.

WHY `BoundaryInput` IS A PROTOCOL WITH NO CONCRETE FIELDS
------------------------------------------------------------
06 gives every one of the 18 boundaries its own, different INPUT list
(e.g. BND-008's own: "Burst state, Session state, Burst mode, input
text, actor origin, Question origin, capture membership, AI operation
type"). There is no single field list 06 defines for "boundary input in
general" -- inventing one here would mean guessing at semantics that
belong to whichever future package registers that specific boundary.
`BoundaryInput` is instead the minimal *structural* contract every
concrete per-boundary input type must satisfy: which boundary it is for,
and the shared request context it was evaluated under. A future
`Bnd008Input` (PKG-09+) would be its own frozen dataclass with 06 §14's
actual fields, satisfying this Protocol by having `boundary_id` and
`context` attributes -- not a subclass of some artificially widened base
class, and never a raw `dict` (14 PKG-08 PUBLIC_INTERFACES: "unversioned
consequential dict payloads are forbidden where they erase semantics").

WHY `BoundaryProof.boundary_version` IS A `ContractVersion`
----------------------------------------------------------------
14 §15 names `boundary_version` as one of `BoundaryProof`'s fields, and
14 (line ~1258, CONTRACT VERSIONING) already states: "Commands, Events,
AIOPs, AI outputs and materially changed boundary contracts are
versioned" -- boundary contracts are explicitly grouped with the other
contract classes `ContractVersion` (PKG-00, `semantic_types.versions`)
already exists for. Reusing it avoids inventing a second versioning
scheme for one concept.

WHY `BoundaryProof` CARRIES A REAL `AuthorityResolutionProof`, NOT A
GENERIC "authority ref"
------------------------------------------------------------------------
14 §15 lists "authority proof refs where applicable" as one of
`BoundaryProof`'s fields. The one authority proof type that actually
exists is PKG-03's `authority.resolver.AuthorityResolutionProof` --
using it directly (rather than an untyped placeholder) is what "Boundary
engine consumes authority proof but does not create it" (14 PKG-08
AUTHORITY line) means concretely: this module can *carry* a real proof a
future evaluator produced, but has no code path that calls
`AuthorityResolver` itself. `evidence_proof_refs` stays a plain opaque
tuple: no Evidence persistence or proof type exists yet
(`packages/evidence` remains a PKG-00 stub), so there is nothing typed
to reference -- disclosed as `SUCCESSOR_NOT_BUILT`, not stubbed with
invented structure.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol, runtime_checkable

from authority.actor import ActorIdentity
from authority.resolver import AuthorityResolutionProof
from semantic_types.ids import CorrelationId, WorkspaceId
from semantic_types.versions import ContractVersion

from boundaries.authority_source import AuthoritySourceProof


class BoundaryId(Enum):
    """The 18 named boundaries 06 defines. Closed -- a boundary not
    listed here does not exist architecturally. Enumerating the IDs is
    pure vocabulary (06 already names and numbers exactly these);
    materializing what any of them *does* is not this package's scope.
    """

    BND_001 = "BND-001"  # Identity
    BND_002 = "BND-002"  # Workspace
    BND_003 = "BND-003"  # Membership
    BND_004 = "BND-004"  # Role / Governance Context
    BND_005 = "BND-005"  # Human Authority
    BND_006 = "BND-006"  # Human Decision Authority
    BND_007 = "BND-007"  # Session / State Transition
    BND_008 = "BND-008"  # Question Burst Contamination
    BND_009 = "BND-009"  # AI Invocation
    BND_010 = "BND-010"  # AI Output / Canonical State
    BND_011 = "BND-011"  # SYSTEM_DERIVED Authority
    BND_012 = "BND-012"  # Method Approval
    BND_013 = "BND-013"  # Evidence
    BND_014 = "BND-014"  # Persistence / Commit
    BND_015 = "BND-015"  # Audit
    BND_016 = "BND-016"  # Export
    BND_017 = "BND-017"  # Failure / Indeterminate
    BND_018 = "BND-018"  # Recovery / Rollback


class BoundaryResult(Enum):
    """06 §2's exact 4-value result vocabulary. Closed -- there is no
    fifth outcome, and none of these four may be reinterpreted as a
    different one (06 §2.1: ALLOW "does not mean... the operation is
    authorized overall... the persistence write may occur"; §2.3
    REQUIRE "is not permission"; §2.4 ESCALATE "never authorizes the
    requested transition").
    """

    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE = "REQUIRE"
    ESCALATE = "ESCALATE"


TERMINAL_BOUNDARY_RESULTS = frozenset(
    {BoundaryResult.DENY, BoundaryResult.REQUIRE, BoundaryResult.ESCALATE}
)
"""06 §3: "upstream DENY cannot become downstream ALLOW... upstream
REQUIRE cannot become downstream ALLOW without satisfying and
re-evaluating the prerequisite... upstream ESCALATE cannot become
downstream ALLOW without completing the authorized escalation." All
three block the chain identically from `evaluate_chain`'s point of
view: only `ALLOW` "permits evaluation of the next required boundary."
AC-06-003's precedence list ("DENY is terminal; REQUIRE blocks;
ESCALATE blocks; ALLOW continues") states no further precedence among
DENY/REQUIRE/ESCALATE themselves -- evaluation is sequential, so
whichever of the three a boundary returns first is simply the result
that stops the chain there.
"""


@dataclass(frozen=True, slots=True)
class BoundaryContext:
    """The one request context shared by every boundary evaluated for a
    single consequential request chain (06 §4's "canonical consequential
    request path" -- one request, many boundaries, one context).
    """

    workspace_id: WorkspaceId
    operation: str
    actor: ActorIdentity
    correlation_id: CorrelationId
    evaluated_at: datetime

    def __post_init__(self) -> None:
        if not self.operation:
            raise ValueError("BoundaryContext.operation must be non-empty")


@runtime_checkable
class BoundaryInput(Protocol):
    """Structural contract every concrete per-boundary input type must
    satisfy. See module docstring for why this carries no concrete
    request fields of its own.
    """

    boundary_id: BoundaryId
    context: BoundaryContext


@dataclass(frozen=True, slots=True)
class BoundaryProof:
    """14 §15's exact field list: "boundary_id, boundary_version,
    result, reason_code, workspace_id, actor/service ref, input refs,
    authoritative version refs, authority proof refs where applicable,
    Evidence proof refs where applicable, timestamp, correlation_id."
    "Free text may accompany a reason code but cannot be the only
    proof" -- `reason_code` is a required, non-empty structured label;
    `input_refs`/`authoritative_version_refs` are the additional
    structured references that make the proof reconstructable without
    relying on that label alone.
    """

    boundary_id: BoundaryId
    boundary_version: ContractVersion
    result: BoundaryResult
    reason_code: str
    workspace_id: WorkspaceId
    actor: ActorIdentity
    input_refs: tuple[str, ...]
    authoritative_version_refs: tuple[str, ...]
    authority_proof: AuthorityResolutionProof | None
    evidence_proof_refs: tuple[str, ...]
    evaluated_at: datetime
    correlation_id: CorrelationId
    authority_source: AuthoritySourceProof | None = None
    """F02 HD-6: the typed authority source BND-014 proved on ALLOW
    (BINDING/ROLE/FOUNDING). `None` for every other boundary and for any
    non-ALLOW BND-014 proof."""

    def __post_init__(self) -> None:
        if not isinstance(self.boundary_id, BoundaryId):
            raise TypeError(f"boundary_id must be a BoundaryId, got {type(self.boundary_id)!r}")
        if not isinstance(self.result, BoundaryResult):
            # Mandatory adversarial attack: missing result. A caller
            # (or a miswired evaluator) passing a raw string/None must
            # not produce a proof that merely *looks* like it holds one.
            raise TypeError(f"result must be a BoundaryResult, got {type(self.result)!r}")
        if not self.reason_code:
            raise ValueError("BoundaryProof.reason_code must be non-empty")
        if not isinstance(self.boundary_version, ContractVersion):
            raise TypeError(
                f"boundary_version must be a ContractVersion, got {type(self.boundary_version)!r}"
            )


@runtime_checkable
class BoundaryEvaluator(Protocol):
    """The contract every concrete BND-001..018 evaluator (PKG-09+)
    implements. `evaluate` is synchronous and pure with respect to this
    module: it consumes `boundary_input`/`context` and returns exactly
    one `BoundaryProof` -- it does not itself cache, retry, or consult
    anything this module does not pass it.
    """

    boundary_id: BoundaryId
    boundary_version: ContractVersion

    def evaluate(
        self, boundary_input: BoundaryInput, context: BoundaryContext
    ) -> BoundaryProof: ...


__all__ = [
    "BoundaryId",
    "BoundaryResult",
    "TERMINAL_BOUNDARY_RESULTS",
    "BoundaryContext",
    "BoundaryInput",
    "BoundaryProof",
    "BoundaryEvaluator",
]
