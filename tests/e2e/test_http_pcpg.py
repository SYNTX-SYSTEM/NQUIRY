"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) over HTTP — FBR-PCPG-18: the real
`PCPG-R12/1` wire contract (Architecture 26).

Source: `packages/application/http_pcpg.py`'s own module docstring. This
file falsifies two separate things:

1. The real FastAPI route end-to-end (real cookies, real PostgreSQL,
   `nquiry_api.main.app`, the same harness `test_http_f04.py` already
   established: `http_f02.db_app` + `_client`) -- proving the composition
   this Work Unit added is actually reachable over HTTP, not merely
   callable in Python.
2. The pure wire-serialization helpers (`_governance_observation_wire`,
   `_result_body`, `_delta_wire`, ...) directly, against hand-built
   `ActorSafeProjection`/`GovernanceObservationUnavailable` objects -- no
   DB needed, the same "construct the dataclass by hand" convention
   `test_pcpg_actor_projection.py` already uses for R-12 itself.

B-10 is falsified by scanning the REAL, full JSON response (end-to-end
case) for every forbidden key/substring at once, rather than asserting a
finite "it has no X" list per field -- a response that somehow grew a new
field this Work Unit never named would still be caught.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import cast

import f03_support as f03
import sqlalchemy as sa
import test_http_f02 as http_f02
from application import pcpg_observation as pcpg
from application.http_pcpg import (
    _chain_result_wire,
    _delta_wire,
    _governance_observation_wire,
    _result_body,
    _semantic_observation_wire,
)
from application.pcpg_actor_projection import ActorSafeProjection
from application.pcpg_capability import Capability
from application.pcpg_chain_results import AuthorityRequirement, ChainResult, FirstBrokenRelation
from application.pcpg_delta_evaluation import DeltaRecord, Result
from application.pcpg_operation_index import ExecutionClass
from application.pcpg_runtime_composition import (
    FIELD_RECONSTRUCTION_UNAVAILABLE,  # noqa: F401 -- cited in a docstring below
    GovernanceObservationUnavailable,
)
from application.pcpg_simplix import (
    Modality,
    RequestedExecutor,
    SemanticAction,
    SemanticObservation,
)
from fastapi.testclient import TestClient
from semantic_types.ids import WorkspaceId
from test_http_f02 import _client

db_app = http_f02.db_app  # the F02 request-connection fixture (test_http_f04.py's own pattern)


def _d(value: object) -> dict[str, object]:
    """A nested wire value, cast back to the dict it always really is --
    `_governance_observation_wire`'s own nested dicts are typed
    `dict[str, object]` at every level, so a direct `wire["x"]["y"]` chain
    is `object` to mypy even though it is always a dict at runtime."""
    return cast("dict[str, object]", value)


def _l(value: object) -> list[object]:
    return cast("list[object]", value)


# ---------------------------------------------------------------------------
# Hand-built fixtures for the pure wire-serialization falsifiers
# ---------------------------------------------------------------------------

_NOW = datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc)


def _delta(
    delta_id: str = "D0",
    *,
    operation: str | None = "BEGIN_ANALYSIS",
    execution_class: ExecutionClass = ExecutionClass.HUMAN_COMMAND,
    result: Result = Result.HUMAN_ACTION_AVAILABLE,
    reason: str | None = None,
    flags: frozenset[str] = frozenset(),
    session_proof_ceiling: str | None = None,
) -> DeltaRecord:
    return DeltaRecord(
        delta_id=delta_id,
        operation=operation,
        execution_class=execution_class,
        target=None,
        source_clause="begin the analysis",
        span=(0, 18),
        current_state="QUESTION_GENERATION",
        result=result,
        reason=reason,
        flags=flags,
        session_proof_ceiling=session_proof_ceiling,
    )


def _semantic_observation() -> SemanticObservation:
    action = SemanticAction(
        clause_index=0,
        span=(0, 18),
        clause_text="begin the analysis",
        modality=Modality.REQUESTED,
        negated=False,
        requested_executor=RequestedExecutor.AI,
        candidate_operation="BEGIN_ANALYSIS",
        target=None,
        possible_external_effect=False,
        possible_secret_content=False,
        decision_substitution_requested=False,
    )
    return SemanticObservation(
        rule_set_version="SIMPLIX-1",
        raw_intent="begin the analysis",
        clauses=("begin the analysis",),
        actions=(action,),
        unknown_relations=(),
        relations_touched=frozenset({"BEGIN_ANALYSIS"}),
        declared_purpose=None,
        semantic_purpose="BEGIN_ANALYSIS",
        purpose_alignment=None,
        semantic_drift=False,
    )


def _chain_result(records: tuple[DeltaRecord, ...]) -> ChainResult:
    broken = records[0]
    return ChainResult(
        first_broken_relation=FirstBrokenRelation(predecessor=None, broken=broken),
        maximum_legitimate_transition=(),
        next_valid_transition=broken if broken.result is Result.HUMAN_ACTION_AVAILABLE else None,
        human_authority_required=(
            AuthorityRequirement(
                delta_id=broken.delta_id, result=broken.result, reason=broken.reason
            ),
        ),
        partial=True,
    )


def _capability() -> Capability:
    return Capability(
        governance_admissible=False,
        governance_admissible_reasons=frozenset({"MLT_EMPTY"}),
        provider_executable=False,
        provider_executable_reasons=frozenset({"NO_ELIGIBLE_PROVIDER_ROUTE"}),
        can_send=False,
    )


def _projection(*, composed_proof_ceiling: str | None = None) -> ActorSafeProjection:
    records = (_delta(),)
    return ActorSafeProjection(
        raw_intent="begin the analysis",
        raw_intent_digest_sha256="deadbeef" * 8,
        derivation_time=_NOW,
        semantic_observation=_semantic_observation(),
        delta_records=records,
        chain_result=_chain_result(records),
        capability=_capability(),
        composed_proof_ceiling=composed_proof_ceiling,
    )


# ---------------------------------------------------------------------------
# 1. Pure wire-serialization falsifiers (no DB)
# ---------------------------------------------------------------------------


def test_current_observation_has_the_exact_contract_tag() -> None:
    wire = _governance_observation_wire(_projection())
    assert wire["kind"] == "current"
    assert wire["contract"] == "PCPG-R12/1"


def test_unavailable_observation_carries_only_kind_and_reason_code() -> None:
    wire = _governance_observation_wire(
        GovernanceObservationUnavailable(FIELD_RECONSTRUCTION_UNAVAILABLE)
    )
    assert wire == {"kind": "unavailable", "reasonCode": FIELD_RECONSTRUCTION_UNAVAILABLE}


def test_basis_carries_exactly_the_digest_and_derivation_time() -> None:
    projection = _projection()
    wire = _governance_observation_wire(projection)
    assert wire["basis"] == {
        "rawIntentDigestSha256": projection.raw_intent_digest_sha256,
        "derivationTime": projection.derivation_time.isoformat(),
    }


def test_composed_proof_ceiling_is_projected_verbatim_including_none() -> None:
    assert (
        _governance_observation_wire(_projection(composed_proof_ceiling=None))[
            "composedProofCeiling"
        ]
        is None
    )
    assert (
        _governance_observation_wire(_projection(composed_proof_ceiling="GOVERNED"))[
            "composedProofCeiling"
        ]
        == "GOVERNED"
    )
    assert (
        _governance_observation_wire(_projection(composed_proof_ceiling="FIXTURE_NON_PROOF"))[
            "composedProofCeiling"
        ]
        == "FIXTURE_NON_PROOF"
    )


def test_delta_wire_has_exactly_the_named_field_set() -> None:
    wire = _delta_wire(_delta(flags=frozenset({"SOME_FLAG"})))
    assert set(wire) == {
        "deltaId",
        "operation",
        "executionClass",
        "target",
        "sourceClause",
        "span",
        "currentState",
        "result",
        "reasonCode",
        "flags",
        "sessionProofCeiling",
    }
    assert wire["result"] == "HUMAN_ACTION_AVAILABLE"
    assert wire["flags"] == ["SOME_FLAG"]


def test_chain_wire_carries_first_broken_relation_as_nested_deltas() -> None:
    records = (_delta(result=Result.GOVERNANCE_BOUNDARY, reason="OPERATION_CLASS_NOT_ADMITTED"),)
    chain = _chain_result(records)
    wire = _chain_result_wire(chain)
    first_broken = _d(wire["firstBrokenRelation"])
    assert _d(first_broken["broken"])["deltaId"] == records[0].delta_id
    assert first_broken["predecessor"] is None
    assert wire["partial"] is True
    assert wire["humanAuthorityRequired"] == [
        {
            "deltaId": records[0].delta_id,
            "result": "GOVERNANCE_BOUNDARY",
            "reasonCode": "OPERATION_CLASS_NOT_ADMITTED",
        }
    ]


def test_chain_wire_first_broken_relation_is_null_when_there_is_none() -> None:
    chain = ChainResult(
        first_broken_relation=None,
        maximum_legitimate_transition=(),
        next_valid_transition=None,
        human_authority_required=(),
        partial=False,
    )
    assert _chain_result_wire(chain)["firstBrokenRelation"] is None


def test_semantic_observation_wire_serializes_every_real_action_field() -> None:
    wire = _semantic_observation_wire(_semantic_observation())
    actions = _l(wire["actions"])
    assert len(actions) == 1
    action_wire = _d(actions[0])
    assert action_wire["modality"] == "REQUESTED"
    assert action_wire["requestedExecutor"] == "AI"
    assert action_wire["candidateOperation"] == "BEGIN_ANALYSIS"
    assert set(action_wire) == {
        "clauseIndex",
        "span",
        "clauseText",
        "modality",
        "negated",
        "requestedExecutor",
        "candidateOperation",
        "target",
        "possibleExternalEffect",
        "possibleSecretContent",
        "decisionSubstitutionRequested",
    }


def _fake_ingress() -> pcpg.ObservationIngressResult:
    return pcpg.ObservationIngressResult(
        workspace_id=WorkspaceId(f03.uid()),
        workspace_name="Inquiry",
        session_id=None,
        raw_intent="begin the analysis",
        raw_intent_length=18,
        raw_intent_digest_sha256="deadbeef" * 8,
        declared_purpose=None,
        observed_at=_NOW,
    )


def test_result_body_governance_observation_is_no_longer_hardcoded_none() -> None:
    body = _result_body(_fake_ingress(), _projection())
    assert _d(body["governanceObservation"])["kind"] == "current"
    assert body["kind"] == "ok"


# ---------------------------------------------------------------------------
# 2. B-10 negative disclosure: scan the full serialized wire for every
#    forbidden token at once
# ---------------------------------------------------------------------------

_B10_FORBIDDEN_TOKENS = (
    "bindingId",
    "bindingVersion",
    "eligibleInputs",
    "retainedInstructionSemantics",
    "excludedDeltaIds",
    "architectureRef",
    "httpRoute",
    "readinessProducer",
    "holderClass",
    "dataClassification",
    "providerContext",
    "pulse",
)


def test_b10_forbidden_tokens_never_appear_in_the_current_wire() -> None:
    blob = json.dumps(_governance_observation_wire(_projection()))
    for token in _B10_FORBIDDEN_TOKENS:
        assert token not in blob, token


def test_b10_forbidden_tokens_never_appear_in_the_unavailable_wire() -> None:
    blob = json.dumps(
        _governance_observation_wire(
            GovernanceObservationUnavailable(FIELD_RECONSTRUCTION_UNAVAILABLE)
        )
    )
    for token in _B10_FORBIDDEN_TOKENS:
        assert token not in blob, token


# ---------------------------------------------------------------------------
# 3. Real FastAPI route, real cookies, real PostgreSQL
# ---------------------------------------------------------------------------


def _post(client: TestClient, ws: str, **body: object) -> dict[str, object]:
    response = client.post(f"/workspaces/{ws}/prompt-observations", json=body)
    assert response.status_code == 200, response.text
    return cast("dict[str, object]", response.json())


def _go(body: dict[str, object]) -> dict[str, object]:
    return cast("dict[str, object]", body["governanceObservation"])


def test_a_real_request_over_http_returns_a_current_governance_observation(
    db_app: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_app, participants=1)
    client = _client(db_app, ctx["fac"])
    body = _post(
        client,
        str(ctx["ws"].value),
        rawIntent="begin the analysis",
        sessionId=str(ctx["session"].value),
    )
    assert body["kind"] == "ok"
    go = _go(body)
    assert go["kind"] == "current"
    assert go["contract"] == "PCPG-R12/1"
    assert _d(go["semanticObservation"])["clauses"] == ["begin the analysis"]
    assert isinstance(go["deltas"], list) and len(_l(go["deltas"])) >= 1
    assert _d(go["capability"])["canSend"] is False
    # Disclosed: always None today -- see test_pcpg_runtime_composition.py's
    # own test_composed_proof_ceiling_is_honestly_none_in_the_real_runtime_today.
    assert go["composedProofCeiling"] is None


def test_a_real_request_over_http_with_unparseable_intent_returns_unavailable(
    db_app: sa.Connection,
) -> None:
    """Non-blank for R-01's own `raw_intent.strip()` check (so R-01/R-02
    still succeed, reaching this Work Unit's own composition), but entirely
    non-ASCII so every clause R-05 forms is `_is_unparseable` -- the same
    real condition `pcpg_simplix.py`'s own `SemanticObservationUnavailable`
    branch requires, exercised here over the real HTTP route."""
    ctx = f03.generating_context(db_app, participants=1)
    client = _client(db_app, ctx["fac"])
    body = _post(client, str(ctx["ws"].value), rawIntent="日本語のテキストです")
    assert _go(body) == {"kind": "unavailable", "reasonCode": "SEMANTIC_OBSERVATION_UNAVAILABLE"}


def test_a_real_request_over_http_contains_no_b10_forbidden_token(db_app: sa.Connection) -> None:
    ctx = f03.generating_context(db_app, participants=1)
    client = _client(db_app, ctx["fac"])
    body = _post(
        client,
        str(ctx["ws"].value),
        rawIntent="begin the analysis",
        sessionId=str(ctx["session"].value),
    )
    blob = json.dumps(body)
    for token in _B10_FORBIDDEN_TOKENS:
        assert token not in blob, token


def test_existing_r01_r02_envelope_fields_are_unaffected_by_this_work_unit(
    db_app: sa.Connection,
) -> None:
    """Regression guard: everything R-01/R-02 already published at the top
    level is untouched by FBR-PCPG-18 -- only `governanceObservation`
    changed from a hardcoded `None`."""
    ctx = f03.generating_context(db_app, participants=1)
    client = _client(db_app, ctx["fac"])
    body = _post(
        client,
        str(ctx["ws"].value),
        rawIntent="begin the analysis",
        sessionId=str(ctx["session"].value),
        declaredPurpose="move the Session forward",
    )
    assert body["field"] == "PRE_CALL_PROMPT_GOVERNANCE"
    assert _d(body["workspace"])["workspaceId"] == str(ctx["ws"].value)
    assert body["rawIntent"] == "begin the analysis"
    assert body["rawIntentLength"] == len("begin the analysis")
    assert body["declaredPurpose"] == "move the Session forward"
    assert body["session"] == {"sessionId": str(ctx["session"].value)}
