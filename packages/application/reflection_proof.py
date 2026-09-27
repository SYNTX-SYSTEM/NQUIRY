"""The eligible proof for TRN-SESS-007 BEGIN_REFLECTION (WU-PFC-B1; HD-24 / NQ-DEC-052).

Source: 03 TRN-SESS-007 (REQUIRED EVIDENCE: "AI_VALIDATION_PROOF that required
analysis operations completed under 08 contracts" and "SYSTEM_PROOF that
derived analysis did not alter raw Questions"; DENY "AI output exists but
failed validation / Analysis is incomplete / Derived output altered protected
source state"); 04 AUTH-DEP-SESS-007 ("No analysis failure"); 12 §39 ("Required:
AIOP-001. Optional: AIOP-002."); 06 BND-017 (an unresolved operation blocks
every dependent consequence); 16 REC-022 (HD-20, enforcement home "proof ->
generation -> provider provenance"); REC-028 (HD-24).

ONE ELIGIBILITY RULE, TWO SOURCES (HD-24 rule 12)
--------------------------------------------------------------------
Whether an accepted, validated AIOP-001 proof may carry a Session into
REFLECTION depends on exactly one question: which proof source admits it.
- `FIXTURE_MOCK` (Option 03): a MockProvider proof, class MOCK_NON_PROOF, for a
  Fixture Session. The result stays NON_PROOF (rules 6, 7).
- `RealProviderProofSource` (Option 01): a non-mock proof, class
  PROVIDER_OUTPUT, from a provider in the eligible set. The set is EMPTY until
  HARD-DEP-002 / NQ-DEC-024 / NQ-DEC-031 are legitimately resolved (rule 9).
  Moving to Option 01 means supplying that set, nothing else. The REFLECTION
  state path (`application.reflection_handler`) does not change.
HD-20 (rule 8) is not a source: a mock proof for a non-Fixture Session is
refused by every source combination.

The proof itself is taken only from write-once records through the F04
provenance resolver (`application.analysis_provenance`: accepted artifact ->
its VALIDATED proof, bound to the validated bytes -> generation -> provider ->
authorization -> the human BEGIN_ANALYSIS root of THIS Session).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ai_contracts.aiop import AIOperationId
from domain.session import Session, SessionState
from persistence.provenance_reader import SqlAlchemyImmutableProvenanceReader

from application.analysis_provenance import ProvenanceBroken, resolve_provenance
from application.analysis_request_handler import _NON_TERMINAL
from application.composition import GovernedPorts
from application.frozen_set import verify_frozen_set

MOCK_PROVIDER = "mock"
MOCK_NON_PROOF = "MOCK_NON_PROOF"
PROVIDER_OUTPUT = "PROVIDER_OUTPUT"
REQUIRED_OPERATIONS = (AIOperationId.AIOP_001,)
"""12 §39: "Required: AIOP-001. Optional: AIOP-002." """
WATCHED_OPERATIONS = (AIOperationId.AIOP_001, AIOperationId.AIOP_002)
"""Any unresolved run of these blocks REFLECTION (BND-017), required or not."""


@dataclass(frozen=True, slots=True)
class ProofEligibility:
    source: str | None
    """The admitting source ("FIXTURE_MOCK" | "ELIGIBLE_REAL_PROVIDER"), or None."""
    reason: str | None
    """Why nothing admits it, when `source` is None."""
    is_real_provider_proof: bool = False


class ReflectionProofSource(Protocol):
    @property
    def name(self) -> str: ...

    def admits(self, *, fixture: bool, provider: str, proof_class: str) -> bool: ...


@dataclass(frozen=True, slots=True)
class FixtureMockProofSource:
    """Option 03 (HD-24 rules 6, 7): a MockProvider proof for a Fixture Session."""

    name: str = "FIXTURE_MOCK"

    def admits(self, *, fixture: bool, provider: str, proof_class: str) -> bool:
        return fixture and provider == MOCK_PROVIDER and proof_class == MOCK_NON_PROOF


@dataclass(frozen=True, slots=True)
class RealProviderProofSource:
    """Option 01 (HD-24 rules 9, 12): a real provider's output from an eligible
    provider. `eligible_providers` is empty until HARD-DEP-002 is resolved."""

    eligible_providers: frozenset[str]
    name: str = "ELIGIBLE_REAL_PROVIDER"

    def admits(self, *, fixture: bool, provider: str, proof_class: str) -> bool:
        return (
            provider != MOCK_PROVIDER
            and proof_class == PROVIDER_OUTPUT
            and provider in self.eligible_providers
        )


FIXTURE_MOCK = FixtureMockProofSource()
ELIGIBLE_PROOF_SOURCES: tuple[ReflectionProofSource, ...] = (
    FIXTURE_MOCK,
    RealProviderProofSource(frozenset()),  # HARD-DEP-002 open: no eligible real provider
)


def decide_eligibility(
    sources: tuple[ReflectionProofSource, ...],
    *,
    fixture: bool,
    provider: str,
    proof_class: str,
) -> ProofEligibility:
    for source in sources:
        if source.admits(fixture=fixture, provider=provider, proof_class=proof_class):
            return ProofEligibility(
                source=source.name,
                reason=None,
                is_real_provider_proof=source.name == "ELIGIBLE_REAL_PROVIDER",
            )
    if provider == MOCK_PROVIDER and not fixture:
        return ProofEligibility(source=None, reason="MOCK_PROOF_NOT_ELIGIBLE_FOR_REAL_SESSION")
    if provider == MOCK_PROVIDER:
        return ProofEligibility(source=None, reason="MOCK_PROOF_CLASS_MISMATCH")
    return ProofEligibility(source=None, reason="NO_ELIGIBLE_PROVIDER_PROOF")


@dataclass(frozen=True, slots=True)
class ReflectionProof:
    """The persisted facts BEGIN_REFLECTION is based on (03 AUDIT CONSEQUENCE:
    "analysis-completion proof reference must be traceable")."""

    analysis_artifact_id: str
    validation_proof_id: str
    provider: str
    proof_class: str
    proof_source: str
    is_real_provider_proof: bool


@dataclass(frozen=True, slots=True)
class ReflectionReadiness:
    blocker: str | None
    proof: ReflectionProof | None


def _unresolved(ports: GovernedPorts, session: Session) -> bool:
    records = ports.ai_records
    for op in WATCHED_OPERATIONS:
        if any(
            g.status in _NON_TERMINAL
            for g in records.list_session_generations(session.session_id, op)
        ):
            return True
        latest = ports.ai_authorizations.latest(session.session_id, op)
        if (
            latest is not None
            and records.get_generation_for_authorization(latest.authorization_id) is None
        ):
            return True  # authorized, never executed: its outcome is not yet known
    return False


def reflection_readiness(
    ports: GovernedPorts,
    session: Session,
    sources: tuple[ReflectionProofSource, ...] = ELIGIBLE_PROOF_SOURCES,
) -> ReflectionReadiness:
    """The one definition of TRN-SESS-007's preconditions, shared by the Command
    and the projection. The first unmet condition is reported."""
    if session.state is not SessionState.ANALYSIS:
        return ReflectionReadiness("SESSION_NOT_IN_ANALYSIS", None)
    if _unresolved(ports, session):
        return ReflectionReadiness("ANALYSIS_IN_PROGRESS", None)
    artifact = ports.ai_records.get_accepted_artifact(session.session_id, AIOperationId.AIOP_001)
    if artifact is None:
        return ReflectionReadiness("REQUIRED_ANALYSIS_NOT_COMPLETED", None)
    try:
        chain = resolve_provenance(
            SqlAlchemyImmutableProvenanceReader(ports.connection), artifact.ai_derived_artifact_id
        )
    except ProvenanceBroken:
        return ReflectionReadiness("ANALYSIS_PROOF_NOT_RECONSTRUCTABLE", None)
    if chain.root.authority_scope_ref != f"SESSION:{session.session_id.value}":
        return ReflectionReadiness("ANALYSIS_PROOF_NOT_RECONSTRUCTABLE", None)
    burst = ports.bursts.get_by_session(session.session_id)
    if burst is None or not verify_frozen_set(ports, burst).matches:
        return ReflectionReadiness("FROZEN_SET_ALTERED", None)
    link = chain.links[0]
    proof_class = artifact.proof_class.value if artifact.proof_class is not None else ""
    eligibility = decide_eligibility(
        sources, fixture=session.fixture, provider=link.provider, proof_class=proof_class
    )
    if eligibility.source is None:
        return ReflectionReadiness(eligibility.reason, None)
    return ReflectionReadiness(
        None,
        ReflectionProof(
            analysis_artifact_id=str(link.artifact_id),
            validation_proof_id=str(link.proof_id),
            provider=link.provider,
            proof_class=proof_class,
            proof_source=eligibility.source,
            is_real_provider_proof=eligibility.is_real_provider_proof,
        ),
    )


__all__ = [
    "ELIGIBLE_PROOF_SOURCES",
    "FIXTURE_MOCK",
    "FixtureMockProofSource",
    "ProofEligibility",
    "RealProviderProofSource",
    "ReflectionProof",
    "ReflectionProofSource",
    "ReflectionReadiness",
    "decide_eligibility",
    "reflection_readiness",
]
