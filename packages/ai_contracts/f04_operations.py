"""The two F04 AI Operation Contracts and their closed output schemas.

Source: 08 §23 AIOP-001 QUESTION_ANALYSIS and §24 AIOP-002 QUESTION_CLUSTERING;
F04 HD-18 (16 §41 REC-020 / NQ-DEC-046) narrows the AIOP-001 OUTPUT CONTRACT;
HD-21 (REC-023) puts AIOP-002 in scope; 09 §34/§35 name the cluster contract.
FBR-F04-8: before F04 no contract was registered and the validator accepted
one hard-coded mock shape. The exact field names and limits below are the
Case-2 materialization choice the architecture delegated to WU-04.4.

AIOP-001 output (closed; no other key at any level):

    {"operation": "AIOP-001", "contract_version": "1.0",
     "classification_proposals": [{"question_ref": R, "proposed_class": S}],
     "question_families":        [{"label": S, "question_refs": [R, ...]}],
     "unusual_question_flags":   [{"question_ref": R, "reason": S}],
     "pattern_descriptions":     [{"text": S, "supporting_question_refs": [R, ...]}],
     "contradiction_proposals":  [{"question_refs": [R, R, ...], "description": S}]}

There is deliberately NO field for additional or new Questions (HD-18), and
nothing that could name a selection, a priority, a Decision, Evidence, an
Assumption or a Session transition.

AIOP-002 output (closed):

    {"operation": "AIOP-002", "contract_version": "1.0",
     "clusters": [{"label": S | null, "description": S | null,
                   "question_refs": [R, ...]}]}

A Question belongs to at most one cluster of a run. There is no priority,
rank or selection field (08 §24 FORBIDDEN: "grant selection priority").

R is a question reference `question:<uuid>` that MUST be in the manifest. S is
a non-empty string within the stated limit.
"""

from __future__ import annotations

from semantic_types.versions import ContractVersion

from ai_contracts.aiop import AIOperationContract, AIOperationId, AIOperationRegistry

F04_CONTRACT_VERSION = ContractVersion("1.0")

QUESTION_ANALYSIS = AIOperationContract(AIOperationId.AIOP_001, F04_CONTRACT_VERSION)
QUESTION_CLUSTERING = AIOperationContract(AIOperationId.AIOP_002, F04_CONTRACT_VERSION)

MAX_LABEL = 120
MAX_TEXT = 1000
MAX_ITEMS = 200

AIOP_001_TOP_LEVEL = frozenset(
    {
        "operation",
        "contract_version",
        "classification_proposals",
        "question_families",
        "unusual_question_flags",
        "pattern_descriptions",
        "contradiction_proposals",
    }
)
AIOP_001_SECTIONS: dict[str, dict[str, str]] = {
    # section -> {field: kind}; kind: "ref" | "refs" | "refs2" | "label" | "text"
    "classification_proposals": {"question_ref": "ref", "proposed_class": "label"},
    "question_families": {"label": "label", "question_refs": "refs"},
    "unusual_question_flags": {"question_ref": "ref", "reason": "text"},
    "pattern_descriptions": {"text": "text", "supporting_question_refs": "refs"},
    "contradiction_proposals": {"question_refs": "refs2", "description": "text"},
}
AIOP_002_TOP_LEVEL = frozenset({"operation", "contract_version", "clusters"})
AIOP_002_CLUSTER = {
    "label": "optional_label",
    "description": "optional_text",
    "question_refs": "refs",
}


def f04_operation_registry() -> AIOperationRegistry:
    """The approved contracts F04 may invoke. Any other AIOP is unregistered and
    BND-009 REQUIREs an approved contract for it."""
    registry = AIOperationRegistry()
    registry.register(QUESTION_ANALYSIS)
    registry.register(QUESTION_CLUSTERING)
    return registry


__all__ = [
    "AIOP_001_SECTIONS",
    "AIOP_001_TOP_LEVEL",
    "AIOP_002_CLUSTER",
    "AIOP_002_TOP_LEVEL",
    "F04_CONTRACT_VERSION",
    "MAX_ITEMS",
    "MAX_LABEL",
    "MAX_TEXT",
    "QUESTION_ANALYSIS",
    "QUESTION_CLUSTERING",
    "f04_operation_registry",
]
