"""BND-014 PERSISTENCE / COMMIT BOUNDARY.

Source: 06_BOUNDARY_ARCHITECTURE.md section 20 (full spec: PURPOSE
"serve as the final authority-sensitive control point before any
consequential canonical persistence or transition commit"; VALIDATION
"immediately before commit revalidate at minimum: current state,
current authority, current scope, ... concurrency/object version where
implementation requires"; TESTABLE INVARIANT "No consequential
persistence can commit solely from an earlier ALLOW or from direct
write access. Every commit uses fresh current-state, scope and
authority revalidation."), section 21 (AC-06-001: "BND-014 approval
exists only for: one operation, one correlation context, one
current-state snapshot/revalidation point, one commit attempt. It is
not a reusable permission.").

WHY THIS EVALUATOR DUPLICATES BND-005's RESOLVE-AND-TRANSLATE LOGIC
RATHER THAN COMPOSING `Bnd005HumanAuthorityEvaluator`
--------------------------------------------------------------------
06 section 20's own AUTHORITY REQUIREMENT ("Fresh authority evaluation.
No stale ALLOW.") is the identical mechanism BND-005 already
implements. Composing the BND-005 evaluator class here would either
require BND-014 to fabricate a synthetic upstream `BoundaryInput`
carrying BND-005's own identity (blurring which boundary actually
produced which proof) or hide the fact that BND-014 also runs version/
upstream-chain checks BND-005 has no concept of at all -- keeping the
resolve-and-translate step local, small, and independently reasoned
about matches this package's own "do not compress into one function"
precedent (PKG-09) in the opposite direction: two boundaries with
genuinely distinct validation scopes stay distinct evaluators, even
where one small sub-check happens to coincide.

WHY `current_versions` IS CALLER-SUPPLIED, NOT READ BY THIS EVALUATOR
--------------------------------------------------------------------
A generic engine has no way to know which table an opaque `target_ref`
string belongs to (the same reasoning `BoundaryInput` itself is a
near-empty structural Protocol, PKG-08). The freshness this boundary
requires ("immediately before commit") is satisfied by the CALLER
(`commit.coordinator.CommitCoordinator`) performing the actual reads
inside its own transaction, immediately before invoking this evaluator
-- this module only compares what it is handed, it does not perform
I/O of any kind, matching `authority.resolver.AuthorityResolver`'s own
"never caches, always reads live" discipline one layer up.

WHY `evidence_freshness` IS OPTIONAL AND DEFAULTS TO `None` (PKG-17)
--------------------------------------------------------------------
09 section 114 (Evidence Commit Materialization): "BND-014 compares
member versions/current states. If any member: invalidated /
superseded ... / unavailable ... / wrong Workspace / changed content
version -- then stale ALLOW fails." Every existing caller (PKG-13's
own tests, and every commit PKG-14/PKG-15 built) commits an operation
with no `evidence_set_ref` at all -- an optional field defaulting to
`None` is the same non-breaking widening precedent
`commit.coordinator.MutationOutcome.relation_refs` already established
(PKG-14): old callers are unaffected, a future Evidence-dependent
Command supplies a real `EvidenceSetFreshnessResult` (re-resolved by
the CALLER immediately before this evaluator runs, the identical
"caller performs the fresh read, this module only compares" split as
`current_versions` above).
"""

from __future__ import annotations

import uuid
from collections.abc import Mapping
from dataclasses import dataclass

from authority.resolver import AuthorityRequest, AuthorityResolver, AuthorityVerdict
from evidence.freshness import EvidenceSetFreshnessResult
from governance.authority_binding import AuthorityClass
from semantic_types.versions import ContractVersion, RecordVersion

from boundaries.types import BoundaryContext, BoundaryId, BoundaryProof, BoundaryResult


@dataclass(frozen=True, slots=True)
class Bnd014Input:
    boundary_id: BoundaryId
    context: BoundaryContext
    required_authority_class: AuthorityClass
    authority_scope_type: str
    authority_scope_id: uuid.UUID
    expected_versions: Mapping[str, RecordVersion]
    current_versions: Mapping[str, RecordVersion | None]
    upstream_chain_result: BoundaryResult
    evidence_freshness: EvidenceSetFreshnessResult | None = None

    def __post_init__(self) -> None:
        if self.boundary_id is not BoundaryId.BND_014:
            raise ValueError(f"Bnd014Input.boundary_id must be BND_014, got {self.boundary_id}")
        if not self.authority_scope_type:
            raise ValueError("Bnd014Input.authority_scope_type must be non-empty")
        if not isinstance(self.upstream_chain_result, BoundaryResult):
            raise TypeError(
                f"upstream_chain_result must be a BoundaryResult, got "
                f"{type(self.upstream_chain_result)!r}"
            )
        if self.evidence_freshness is not None and not isinstance(
            self.evidence_freshness, EvidenceSetFreshnessResult
        ):
            raise TypeError(
                "evidence_freshness must be an EvidenceSetFreshnessResult or None, got "
                f"{type(self.evidence_freshness)!r}"
            )


class Bnd014CommitEvaluator:
    """The final, fresh commit-time revalidation gate. Mandatory
    adversarial attacks this evaluator alone (independent of
    `CommitCoordinator`'s own transactional atomicity) defends against:
    "authority revoked after preparation" and "state version changed".
    """

    boundary_id = BoundaryId.BND_014
    boundary_version = ContractVersion("1.0")

    def __init__(self, resolver: AuthorityResolver) -> None:
        self._resolver = resolver

    def evaluate(self, boundary_input: Bnd014Input, context: BoundaryContext) -> BoundaryProof:
        def deny(reason_code: str) -> BoundaryProof:
            return BoundaryProof(
                boundary_id=self.boundary_id,
                boundary_version=self.boundary_version,
                result=BoundaryResult.DENY,
                reason_code=reason_code,
                workspace_id=context.workspace_id,
                actor=context.actor,
                input_refs=tuple(sorted(boundary_input.expected_versions.keys())),
                authoritative_version_refs=(),
                authority_proof=None,
                evidence_proof_refs=(),
                evaluated_at=context.evaluated_at,
                correlation_id=context.correlation_id,
            )

        # PRECONDITIONS: "Every applicable upstream boundary currently
        # allows. No upstream DENY/REQUIRE/ESCALATE remains unresolved."
        if boundary_input.upstream_chain_result is not BoundaryResult.ALLOW:
            return deny(f"UPSTREAM_CHAIN_NOT_ALLOW:{boundary_input.upstream_chain_result.value}")

        # VALIDATION: "concurrency/object version where implementation
        # requires." Mandatory adversarial attack: state version changed.
        if boundary_input.expected_versions != boundary_input.current_versions:
            stale = sorted(
                ref
                for ref, expected in boundary_input.expected_versions.items()
                if boundary_input.current_versions.get(ref) != expected
            )
            return deny(f"STALE_VERSION:{','.join(stale)}")

        # 09 section 114: "BND-014 compares member versions/current
        # states... then stale ALLOW fails." Mandatory adversarial
        # attacks: Evidence invalidated/unavailable after prepare, set
        # membership no longer resolvable, cross-Workspace Evidence.
        if (
            boundary_input.evidence_freshness is not None
            and not boundary_input.evidence_freshness.is_fresh
        ):
            if not boundary_input.evidence_freshness.evidence_set_found:
                return deny("EVIDENCE_SET_NOT_FOUND")
            return deny(f"STALE_EVIDENCE:{','.join(boundary_input.evidence_freshness.stale_refs)}")

        # VALIDATION: "current authority... No stale ALLOW." Mandatory
        # adversarial attack: authority revoked after preparation.
        resolution = self._resolver.resolve(
            AuthorityRequest(
                actor=context.actor,
                workspace_id=context.workspace_id,
                operation=context.operation,
                required_authority_class=boundary_input.required_authority_class,
                scope_type=boundary_input.authority_scope_type,
                scope_id=boundary_input.authority_scope_id,
            )
        )
        if resolution.verdict is not AuthorityVerdict.GRANTED:
            return BoundaryProof(
                boundary_id=self.boundary_id,
                boundary_version=self.boundary_version,
                result=BoundaryResult.DENY,
                reason_code=f"AUTHORITY_NOT_CURRENT:{resolution.proof.reason.value}",
                workspace_id=context.workspace_id,
                actor=context.actor,
                input_refs=tuple(sorted(boundary_input.expected_versions.keys())),
                authoritative_version_refs=(),
                authority_proof=resolution.proof,
                evidence_proof_refs=(),
                evaluated_at=context.evaluated_at,
                correlation_id=context.correlation_id,
            )

        return BoundaryProof(
            boundary_id=self.boundary_id,
            boundary_version=self.boundary_version,
            result=BoundaryResult.ALLOW,
            reason_code="COMMIT_SENSITIVE_PREDICATES_CURRENT",
            workspace_id=context.workspace_id,
            actor=context.actor,
            input_refs=tuple(sorted(boundary_input.expected_versions.keys())),
            authoritative_version_refs=tuple(
                f"{ref}:{version.value}"
                for ref, version in sorted(boundary_input.current_versions.items())
                if version is not None
            ),
            authority_proof=resolution.proof,
            evidence_proof_refs=(
                ()
                if boundary_input.evidence_freshness is None
                else (str(boundary_input.evidence_freshness.evidence_set_ref_id.value),)
            ),
            evaluated_at=context.evaluated_at,
            correlation_id=context.correlation_id,
        )


__all__ = ["Bnd014Input", "Bnd014CommitEvaluator"]
