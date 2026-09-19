"""AIOP registry: the closed AI Operation identity vocabulary plus the
generic contract-registration/validation engine.

Source: 08_AI_ARCHITECTURE_AND_CONTRACTS.md section 4 (AI Operation
Identity -- "Every AI invocation must name one approved operation
contract"; the 16 example IDs), section 5 (AI Operation Contract
Envelope -- the fields every concrete AIOP contract must define),
sections 23-38 (AIOP-001 through AIOP-016, each given its own full
contract -- confirming section 4's list is exhaustive, not merely
illustrative); 09_DATA_EVENT_API_CONTRACTS.md AC-09-028 ("AI Commands
reference exact AIOP and contract version").

WHY `AIOperationId` IS A CLOSED 16-VALUE ENUM
--------------------------------------------------------------------
Section 4 introduces its list as "Example IDs", but sections 23-38
then give every one of those 16 identifiers its own complete,
numbered contract section -- the identical shape `BoundaryId`'s own
docstring already reasons about for 06's 18 named boundaries (PKG-08):
the identity vocabulary is exhaustively enumerated by the source
document even though not every member has a concrete implementation
yet. Materializing the identity list is pure vocabulary; materializing
what any one AIOP's Gateway path actually DOES is not this package's
scope (14 PKG-18 BOUNDARIES: "No provider call yet; contract
validation proof only").

WHY THIS MODULE HOLDS NO PER-OPERATION BUSINESS RULES
--------------------------------------------------------------------
Section 5's own envelope (PURPOSE, INPUT CONTRACT, OUTPUT CONTRACT,
ALLOWED/FORBIDDEN CANONICAL EFFECT, ...) is a documentation-level
completeness checklist each AIOP's own Gateway implementation must
satisfy -- 12 section 12.1 names only AIOP-001 as required for the
minimum prototype (AIOP-002 optional), and building either operation's
real Gateway path is PKG-19's own scope ("AI Gateway and MockProvider").
What THIS package proves is narrower and structural: that an AIOP
reference is a real, versioned, checkable fact -- not free text a
caller could misstate -- via `AIOperationRegistry`/
`validate_aiop_reference`. This mirrors `boundaries.registry.
BoundaryRegistry`'s own split from PKG-08: the generic registration/
lookup engine now, concrete per-operation implementations later.

WHY `AIOperationContract` CARRIES ONLY `ai_operation_id`/`contract_version`
--------------------------------------------------------------------
14 PKG-18 PUBLIC_INTERFACES: "Create only the typed public interfaces
needed by this package. Generic Repository<T>, generic status setters,
generic authority booleans and unversioned consequential dict payloads
are forbidden where they erase semantics." Section 5's full envelope
is fixed prose per operation (PURPOSE etc. do not vary at runtime), not
data a caller supplies per invocation -- there is nothing for this
type to carry beyond the one runtime fact AC-09-028 actually requires
checking: which operation, at which contract version.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from semantic_types.versions import ContractVersion


class AIOperationId(Enum):
    """08 section 4's own 16 named AI Operation Contract identities,
    each materialized as its own full contract in 08 sections 23-38.
    Closed -- an operation ID not listed here does not exist
    architecturally (AC-09-028: "AI Commands reference exact AIOP").
    """

    AIOP_001 = "AIOP-001"  # QUESTION_ANALYSIS
    AIOP_002 = "AIOP-002"  # QUESTION_CLUSTERING
    AIOP_003 = "AIOP-003"  # QUESTION_REFRAMING
    AIOP_004 = "AIOP-004"  # ASSUMPTION_INFERENCE
    AIOP_005 = "AIOP-005"  # INSIGHT_SYNTHESIS
    AIOP_006 = "AIOP-006"  # EVIDENCE_EXTRACTION
    AIOP_007 = "AIOP-007"  # EVIDENCE_SUMMARIZATION
    AIOP_008 = "AIOP-008"  # EVIDENCE_RELATION_PROPOSAL
    AIOP_009 = "AIOP-009"  # CONTRADICTION_DETECTION
    AIOP_010 = "AIOP-010"  # RESEARCH_SOURCE_DISCOVERY
    AIOP_011 = "AIOP-011"  # EXPERIMENT_PROPOSAL
    AIOP_012 = "AIOP-012"  # RECOMMENDATION_GENERATION
    AIOP_013 = "AIOP-013"  # DECISION_PREPARATION
    AIOP_014 = "AIOP-014"  # AI_QUESTION_GENERATION
    AIOP_015 = "AIOP-015"  # PERSPECTIVE_GENERATION
    AIOP_016 = "AIOP-016"  # REFLECTION_PROMPTING


@dataclass(frozen=True, slots=True)
class AIOperationContract:
    """One approved (operation, contract_version) pair. An operation ID
    alone is not authority (08 section 4) and not a legitimacy proof by
    itself -- it identifies which AIOP is being evaluated, at which
    version of that AIOP's own contract text.
    """

    ai_operation_id: AIOperationId
    contract_version: ContractVersion

    def __post_init__(self) -> None:
        if not isinstance(self.ai_operation_id, AIOperationId):
            raise TypeError(
                f"ai_operation_id must be an AIOperationId, got {type(self.ai_operation_id)!r}"
            )
        if not isinstance(self.contract_version, ContractVersion):
            raise TypeError(
                f"contract_version must be a ContractVersion, got {type(self.contract_version)!r}"
            )


class AIOperationRegistrationError(Exception):
    """Raised when a second contract attempts to register for an
    `AIOperationId` that already has one. No silent overwrite -- the
    same default-deny posture `boundaries.registry.BoundaryRegistry`
    already established (14 section 45).
    """


class AIOperationRegistry:
    """Maps `AIOperationId` to the one currently-approved
    `AIOperationContract` for it. Holds no invocation state -- looking
    a contract up does not invoke anything and is never itself a
    cached authorization.
    """

    def __init__(self) -> None:
        self._contracts: dict[AIOperationId, AIOperationContract] = {}

    def register(self, contract: AIOperationContract) -> None:
        if contract.ai_operation_id in self._contracts:
            raise AIOperationRegistrationError(
                f"an AIOperationContract is already registered for {contract.ai_operation_id!r}"
            )
        self._contracts[contract.ai_operation_id] = contract

    def get(self, ai_operation_id: AIOperationId) -> AIOperationContract | None:
        return self._contracts.get(ai_operation_id)


def validate_aiop_reference(
    *,
    ai_operation_id: AIOperationId,
    contract_version: ContractVersion,
    registry: AIOperationRegistry,
) -> bool:
    """Contract validation proof (14 PKG-18 BOUNDARIES: "contract
    validation proof only") -- true iff `ai_operation_id` is currently
    registered at exactly `contract_version`. Mandatory package-specific
    attacks this proves: "invalid contract" (unregistered operation
    ID -> False) and "wrong version" (registered operation ID at a
    DIFFERENT version -> False, never silently accepted as current).
    """
    registered = registry.get(ai_operation_id)
    return registered is not None and registered.contract_version == contract_version


__all__ = [
    "AIOperationId",
    "AIOperationContract",
    "AIOperationRegistrationError",
    "AIOperationRegistry",
    "validate_aiop_reference",
]
