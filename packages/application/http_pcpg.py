"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) HTTP dispatch — R-01/R-02 ingress plus
the FBR-PCPG-18 runtime composition of R-03 through R-12 (Architecture 26).

`apps/api/src/nquiry_api/http/pcpg.py` is a thin adapter, same discipline as
every other route file (14 §3.1). This module wires the real producers
(`application.pcpg_observation.observe` for R-01/R-02,
`application.pcpg_runtime_composition.derive_governance_observation` for
R-03 through R-12) to the existing session-cookie identity and the existing
common failure envelope — nothing here evaluates a boundary, resolves
authority or touches persistence directly; every governance value below is
read verbatim from a real producer, never computed here.

This is a QUERY, not a Command (09; `01_INVARIANTS.md` I-18): side-effect-free,
no Idempotency-Key, no canonical write, `kind: "ok"` on success — the SAME
envelope `inquiry_queries` already answers with, not a new top-level kind
(I-20: no parallel result vocabulary). The outer envelope's own `"kind": "ok"`
/ HTTP 200 is governed solely by R-01/R-02's own success (unchanged by this
Work Unit); `governanceObservation`'s own nested `"kind"` ("current" /
"unavailable") is the FBR-PCPG-18 composition's own, independent
discriminator — a query that honestly fails to derive today's governance
state is still a successful query about the real, current Field.

WIRE CONTRACT `PCPG-R12/1` (FBR-PCPG-18)
-----------------------------------------
`governanceObservation` is either:
  `{"kind": "unavailable", "reasonCode": <one of the three real codes>}`
or
  `{"kind": "current", "contract": "PCPG-R12/1", "basis": {...},
    "semanticObservation": {...}, "deltas": [...], "chain": {...},
    "capability": {...}, "composedProofCeiling": <str | None>}`

B-10 NEGATIVE DISCLOSURE — never serialized, by construction, never by a
filter bolted on here: `EligibleContentSet` (R-11 is never called, see
`pcpg_runtime_composition.py`'s own module docstring), `AuthorityFact.
binding_id`/`binding_version` (no field of `ActorSafeProjection` nests an
`AuthorityFact`), raw `Pulse` internals, `ProviderContext`, a
`DataClassification` structure, `pcpg_operation_index` internals beyond the
real `operation`/`executionClass` values already in `DeltaRecord`, and no
`readinessProducer`/`httpRoute`/`architectureRef` string — none of these
reach `ActorSafeProjection`'s own fields in the first place, so there is
nothing to redact; this function only ever reads what that object actually
carries.
"""

from __future__ import annotations

from typing import Any

from semantic_types.ids import SessionId, WorkspaceId

from application import pcpg_observation as pcpg
from application.composition import GovernedPorts
from application.http_f02 import Response, _denied, _rejected, _uuid, _with_actor
from application.inquiry_queries import QueryDenied, QueryNotFound
from application.pcpg_actor_projection import ActorSafeProjection
from application.pcpg_capability import Capability
from application.pcpg_chain_results import AuthorityRequirement, ChainResult, FirstBrokenRelation
from application.pcpg_delta_evaluation import DeltaRecord
from application.pcpg_runtime_composition import (
    GovernanceObservationUnavailable,
    derive_governance_observation,
)
from application.pcpg_simplix import SemanticAction, SemanticObservation

_WIRE_CONTRACT = "PCPG-R12/1"


def _delta_wire(record: DeltaRecord) -> dict[str, object]:
    return {
        "deltaId": record.delta_id,
        "operation": record.operation,
        "executionClass": record.execution_class.value,
        "target": record.target,
        "sourceClause": record.source_clause,
        "span": list(record.span),
        "currentState": record.current_state,
        "result": record.result.value,
        "reasonCode": record.reason,
        "flags": sorted(record.flags),
        "sessionProofCeiling": record.session_proof_ceiling,
    }


def _action_wire(action: SemanticAction) -> dict[str, object]:
    return {
        "clauseIndex": action.clause_index,
        "span": list(action.span),
        "clauseText": action.clause_text,
        "modality": action.modality.value,
        "negated": action.negated,
        "requestedExecutor": action.requested_executor.value,
        "candidateOperation": action.candidate_operation,
        "target": action.target,
        "possibleExternalEffect": action.possible_external_effect,
        "possibleSecretContent": action.possible_secret_content,
        "decisionSubstitutionRequested": action.decision_substitution_requested,
    }


def _semantic_observation_wire(observation: SemanticObservation) -> dict[str, object]:
    return {
        "ruleSetVersion": observation.rule_set_version,
        "clauses": list(observation.clauses),
        "actions": [_action_wire(a) for a in observation.actions],
        "unknownRelations": list(observation.unknown_relations),
        "relationsTouched": sorted(observation.relations_touched),
        "declaredPurpose": observation.declared_purpose,
        "semanticPurpose": observation.semantic_purpose,
        "purposeAlignment": observation.purpose_alignment,
        "semanticDrift": observation.semantic_drift,
    }


def _first_broken_relation_wire(fbr: FirstBrokenRelation | None) -> dict[str, object] | None:
    if fbr is None:
        return None
    return {
        "predecessor": None if fbr.predecessor is None else _delta_wire(fbr.predecessor),
        "broken": _delta_wire(fbr.broken),
    }


def _authority_requirement_wire(requirement: AuthorityRequirement) -> dict[str, object]:
    return {
        "deltaId": requirement.delta_id,
        "result": requirement.result.value,
        "reasonCode": requirement.reason,
    }


def _chain_result_wire(chain: ChainResult) -> dict[str, object]:
    return {
        "firstBrokenRelation": _first_broken_relation_wire(chain.first_broken_relation),
        "maximumLegitimateTransition": [
            _delta_wire(r) for r in chain.maximum_legitimate_transition
        ],
        "nextValidTransition": (
            None
            if chain.next_valid_transition is None
            else _delta_wire(chain.next_valid_transition)
        ),
        "humanAuthorityRequired": [
            _authority_requirement_wire(r) for r in chain.human_authority_required
        ],
        "partial": chain.partial,
    }


def _capability_wire(capability: Capability) -> dict[str, object]:
    return {
        "governanceAdmissible": capability.governance_admissible,
        "governanceAdmissibleReasons": sorted(capability.governance_admissible_reasons),
        "providerExecutable": capability.provider_executable,
        "providerExecutableReasons": sorted(capability.provider_executable_reasons),
        "canSend": capability.can_send,
    }


def _governance_observation_wire(
    observation: ActorSafeProjection | GovernanceObservationUnavailable,
) -> dict[str, object]:
    if isinstance(observation, GovernanceObservationUnavailable):
        return {"kind": "unavailable", "reasonCode": observation.reason_code}
    return {
        "kind": "current",
        "contract": _WIRE_CONTRACT,
        "basis": {
            "rawIntentDigestSha256": observation.raw_intent_digest_sha256,
            "derivationTime": observation.derivation_time.isoformat(),
        },
        "semanticObservation": _semantic_observation_wire(observation.semantic_observation),
        "deltas": [_delta_wire(r) for r in observation.delta_records],
        "chain": _chain_result_wire(observation.chain_result),
        "capability": _capability_wire(observation.capability),
        "composedProofCeiling": observation.composed_proof_ceiling,
    }


def _result_body(
    result: pcpg.ObservationIngressResult,
    governance_observation: ActorSafeProjection | GovernanceObservationUnavailable,
) -> dict[str, object]:
    return {
        "kind": "ok",
        "field": "PRE_CALL_PROMPT_GOVERNANCE",
        "workspace": {
            "workspaceId": str(result.workspace_id.value),
            "name": result.workspace_name,
        },
        "session": (
            None if result.session_id is None else {"sessionId": str(result.session_id.value)}
        ),
        "rawIntent": result.raw_intent,
        "rawIntentLength": result.raw_intent_length,
        "rawIntentDigestSha256": result.raw_intent_digest_sha256,
        "declaredPurpose": result.declared_purpose,
        "observedAt": result.observed_at.isoformat(),
        # FBR-PCPG-18: the real R-03..R-12 runtime composition (R-11, R-13
        # and every provider/SEND path excluded, see
        # `pcpg_runtime_composition.py`'s own module docstring).
        "governanceObservation": _governance_observation_wire(governance_observation),
    }


def dispatch_submit_observation(
    *,
    session_token: str | None,
    workspace_id: str,
    raw_intent: object,
    session_id: str | None,
    declared_purpose: object,
) -> Response:
    def work(ports: GovernedPorts, principal: Any) -> Response:
        ws = WorkspaceId(_uuid(workspace_id, "workspace_id"))
        sid = SessionId(_uuid(session_id, "session_id")) if session_id else None
        if not isinstance(raw_intent, str):
            return _rejected("RAW_INTENT_REQUIRED")
        if declared_purpose is not None and not isinstance(declared_purpose, str):
            return _rejected("DECLARED_PURPOSE_INVALID")

        try:
            result = pcpg.observe(
                ports,
                principal,
                workspace_id=ws,
                raw_intent=raw_intent,
                session_id=sid,
                declared_purpose=declared_purpose,
                now=ports.clock.now(),
            )
        except pcpg.ObservationInputRejected as exc:
            return _rejected(exc.reason_code)
        except QueryDenied as exc:
            return _denied(exc.reason_code)
        except QueryNotFound as exc:
            return 404, {"kind": "not_found", "reasonCode": exc.reason_code}

        governance_observation = derive_governance_observation(ports, principal, result)
        return 200, _result_body(result, governance_observation)

    return _with_actor(session_token, work)


__all__ = ["dispatch_submit_observation"]
