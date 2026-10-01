"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — R-12: actor-safe projection → CYAN
(Architecture 26).

Source: `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md`
R-12: "OUTPUT: only what the actor may already read: the actor's own raw
intent; the semantic observation; the delta results with reason codes;
FBR, MLT, NVT and HAR (as holder classes, not other people's binding
internals); the capability values with reasons; the proof ceiling; the
basis identity and its derivation time."

E1 re-derivation (2026-10-01, independent, against `checkpoint-PFC-PCPG-10`):
R-01 (`ObservationIngressResult`), R-05 (`SemanticObservation`), R-07
(`DeltaRecord`), R-09 (`ChainResult`), R-10 (`Capability`) are all real;
`grep` for `ActorSafeProjection`/`derive_actor_safe_projection`: zero
hits outside this module. R-12 is the next First Broken Relation.

SCOPE (disclosed; full reasoning in `pcpg_actor_projection.py`'s own
module docstring, not repeated here): 6 of 7 named OUTPUT items are
covered by direct re-packaging of already-real producers (WU-PFC-PCPG-17
adds "the proof ceiling", projected directly from R-08's own
`ComposedEffect.composed_proof_ceiling`, never routed through R-09, R-10
or R-11 — neither owns the proof-ceiling semantic); the richer "basis
identity" composite beyond the raw-intent fingerprint and derivation
time is disclosed absent. The FAILURE STATE is not modeled as a separate
branch: the function's own non-optional signature already enforces "no
projection without a complete result" structurally.
"""

from __future__ import annotations

import dataclasses
from datetime import datetime, timezone

from application.pcpg_actor_projection import ActorSafeProjection, derive_actor_safe_projection
from application.pcpg_capability import Capability
from application.pcpg_chain_results import AuthorityRequirement, ChainResult, FirstBrokenRelation
from application.pcpg_composed_effect import ComposedEffect, CompositionResult
from application.pcpg_delta_evaluation import DeltaRecord, Result
from application.pcpg_observation import ObservationIngressResult
from application.pcpg_operation_index import ExecutionClass
from application.pcpg_simplix import (
    Modality,
    RequestedExecutor,
    SemanticAction,
    SemanticObservation,
)
from semantic_types.ids import WorkspaceId

_OBSERVED_AT = datetime(2026, 10, 1, 12, 0, 0, tzinfo=timezone.utc)

_INGRESS = ObservationIngressResult(
    workspace_id=WorkspaceId.from_str("11111111-1111-1111-1111-111111111111"),
    workspace_name="Acme",
    session_id=None,
    raw_intent="Begin the analysis.",
    raw_intent_length=len("Begin the analysis."),
    raw_intent_digest_sha256="a" * 64,
    declared_purpose=None,
    observed_at=_OBSERVED_AT,
)

_ACTION = SemanticAction(
    clause_index=0,
    span=(0, 19),
    clause_text="Begin the analysis.",
    modality=Modality.REQUESTED,
    negated=False,
    requested_executor=RequestedExecutor.HUMAN,
    candidate_operation="BEGIN_ANALYSIS",
    target=None,
    possible_external_effect=False,
    possible_secret_content=False,
    decision_substitution_requested=False,
)

_OBSERVATION = SemanticObservation(
    rule_set_version="SIMPLIX-1",
    raw_intent="Begin the analysis.",
    clauses=("Begin the analysis.",),
    actions=(_ACTION,),
    unknown_relations=(),
    relations_touched=frozenset(),
    declared_purpose=None,
    semantic_purpose=None,
    purpose_alignment=None,
    semantic_drift=False,
)


def _record(delta_id: str = "D0", result: Result = Result.HUMAN_ACTION_AVAILABLE) -> DeltaRecord:
    return DeltaRecord(
        delta_id=delta_id,
        operation="BEGIN_ANALYSIS",
        execution_class=ExecutionClass.HUMAN_COMMAND,
        target=None,
        source_clause="x",
        span=(0, 1),
        current_state=None,
        result=result,
        reason=None,
        flags=frozenset(),
    )


_RECORDS = (_record(),)

_CHAIN_RESULT = ChainResult(
    first_broken_relation=None,
    maximum_legitimate_transition=(),
    next_valid_transition=_RECORDS[0],
    human_authority_required=(),
    partial=False,
)

_CAPABILITY = Capability(
    governance_admissible=False,
    governance_admissible_reasons=frozenset({"MLT_EMPTY"}),
    provider_executable=False,
    provider_executable_reasons=frozenset({"NO_ELIGIBLE_PROVIDER_ROUTE"}),
    can_send=False,
)


def _composed_effect(ceiling: str | None) -> ComposedEffect:
    return ComposedEffect(
        retained=(),
        composition_result=CompositionResult.COMPOSABLE,
        reason=None,
        composed_proof_ceiling=ceiling,
    )


_COMPOSED_EFFECT_GOVERNED = _composed_effect("GOVERNED")


def _project(composed_effect: ComposedEffect = _COMPOSED_EFFECT_GOVERNED) -> ActorSafeProjection:
    return derive_actor_safe_projection(
        _INGRESS, _OBSERVATION, _RECORDS, _CHAIN_RESULT, _CAPABILITY, composed_effect
    )


# ---------------------------------------------------------------------------
# Each real OUTPUT item is carried through verbatim, not re-derived
# ---------------------------------------------------------------------------


def test_raw_intent_is_carried_through_verbatim() -> None:
    assert _project().raw_intent == "Begin the analysis."


def test_raw_intent_digest_is_the_real_ingress_producers_own_value() -> None:
    assert _project().raw_intent_digest_sha256 == _INGRESS.raw_intent_digest_sha256


def test_derivation_time_is_the_real_ingress_observed_at() -> None:
    assert _project().derivation_time == _OBSERVED_AT


def test_semantic_observation_is_carried_through_verbatim() -> None:
    assert _project().semantic_observation is _OBSERVATION


def test_delta_records_are_carried_through_verbatim() -> None:
    assert _project().delta_records == _RECORDS


def test_chain_result_is_carried_through_verbatim() -> None:
    assert _project().chain_result is _CHAIN_RESULT


def test_capability_is_carried_through_verbatim() -> None:
    assert _project().capability is _CAPABILITY


# ---------------------------------------------------------------------------
# No fabrication: this producer invents no new value
# ---------------------------------------------------------------------------


def test_projection_adds_no_field_beyond_the_seven_named_items() -> None:
    """I-19/E6 BYPASSED-type check mirrored for FABRICATED: the dataclass
    shape must contain exactly the real, cited OUTPUT items (6 of R-12's
    own 7 named items are covered -- `composed_proof_ceiling` is the
    7th, WU-PFC-PCPG-17; "the basis identity" composite remains
    disclosed-absent), nothing extra invented."""
    fields = {f.name for f in dataclasses.fields(ActorSafeProjection)}
    assert fields == {
        "raw_intent",
        "raw_intent_digest_sha256",
        "derivation_time",
        "semantic_observation",
        "delta_records",
        "chain_result",
        "capability",
        "composed_proof_ceiling",
    }


def test_two_different_observations_project_independently_no_shared_mutable_state() -> None:
    other_ingress = dataclasses.replace(_INGRESS, raw_intent="Compare the suppliers.")
    first = _project()
    second = derive_actor_safe_projection(
        other_ingress, _OBSERVATION, _RECORDS, _CHAIN_RESULT, _CAPABILITY, _COMPOSED_EFFECT_GOVERNED
    )
    assert first.raw_intent == "Begin the analysis."
    assert second.raw_intent == "Compare the suppliers."


# ---------------------------------------------------------------------------
# "as holder classes, not other people's binding internals" -- proven by
# construction against the real dataclass shapes, not merely asserted
# ---------------------------------------------------------------------------

_FORBIDDEN_FIELD_SUBSTRINGS = ("binding_id", "binding_version", "holder_user_id", "other_user_id")


def test_no_field_in_the_projection_carries_another_actors_identity() -> None:
    for cls in (DeltaRecord, FirstBrokenRelation, AuthorityRequirement, ChainResult, Capability):
        for field in dataclasses.fields(cls):
            lowered = field.name.lower()
            assert not any(forbidden in lowered for forbidden in _FORBIDDEN_FIELD_SUBSTRINGS), (
                cls.__name__,
                field.name,
            )


def test_authority_requirement_carries_only_delta_id_result_and_reason() -> None:
    """HAR's own disclosed shape (R-09) is already holder-class-safe: no
    binding reference, no other actor's identity -- verified directly."""
    fields = {f.name for f in dataclasses.fields(AuthorityRequirement)}
    assert fields == {"delta_id", "result", "reason"}


# ---------------------------------------------------------------------------
# Determinism, purity, no I/O, no provider
# ---------------------------------------------------------------------------


def test_same_inputs_give_the_same_projection_every_time() -> None:
    assert _project() == _project()


def test_the_module_touches_no_database_and_no_provider() -> None:
    import ast
    import pathlib

    root = pathlib.Path(__file__).resolve().parents[2] / "packages" / "application"
    source = (root / "pcpg_actor_projection.py").read_text()
    tree = ast.parse(source)
    forbidden = ("ai_gateway", "anthropic", "openai", "provider", "psycopg", "sqlalchemy")
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            mods = [node.module or ""]
        else:
            continue
        for mod in mods:
            assert not any(mod.split(".")[0].startswith(f) for f in forbidden), mod
    for fn in ast.walk(tree):
        if isinstance(fn, ast.FunctionDef):
            arg_names = {a.arg for a in fn.args.args}
            assert not ({"ports", "connection", "db"} & arg_names), fn.name


# ---------------------------------------------------------------------------
# WU-PFC-PCPG-17: I-12's own composed proof ceiling, projected directly
# from R-08 -- never routed through R-09, R-10 or R-11
# ---------------------------------------------------------------------------


def test_fixture_non_proof_from_r08_reaches_r12_unchanged() -> None:
    """Required falsifier 1."""
    result = _project(_composed_effect("FIXTURE_NON_PROOF"))
    assert result.composed_proof_ceiling == "FIXTURE_NON_PROOF"


def test_governed_from_r08_reaches_r12_unchanged() -> None:
    """Required falsifier 2."""
    result = _project(_composed_effect("GOVERNED"))
    assert result.composed_proof_ceiling == "GOVERNED"


def test_none_from_r08_remains_none_in_r12() -> None:
    """Required falsifiers 3 and 5: an unknown ceiling is projected as
    `None`, never silently defaulted to `"GOVERNED"`."""
    result = _project(_composed_effect(None))
    assert result.composed_proof_ceiling is None
    assert result.composed_proof_ceiling != "GOVERNED"


def test_r12_reads_the_ceiling_only_from_composed_effect_never_elsewhere() -> None:
    """Required falsifiers 4, 6, 7: "R-12 does not recompute the ceiling
    from delta_records"; "does not derive it from ChainResult"; "does not
    derive it from Capability." Proven directly by static AST inspection:
    the `composed_proof_ceiling=` keyword argument to `ActorSafeProjection`
    must be exactly the attribute access `composed_effect.
    composed_proof_ceiling`, nothing else."""
    import ast
    import pathlib

    root = pathlib.Path(__file__).resolve().parents[2] / "packages" / "application"
    source = (root / "pcpg_actor_projection.py").read_text()
    tree = ast.parse(source)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "ActorSafeProjection":
            for kw in node.keywords:
                if kw.arg == "composed_proof_ceiling":
                    found = True
                    assert isinstance(kw.value, ast.Attribute)
                    assert kw.value.attr == "composed_proof_ceiling"
                    assert isinstance(kw.value.value, ast.Name)
                    assert kw.value.value.id == "composed_effect"
    assert found, "composed_proof_ceiling keyword not found in ActorSafeProjection(...) call"


def test_per_delta_session_proof_ceiling_remains_independently_present() -> None:
    """Required falsifier 8: the per-delta ceiling (already real since
    `checkpoint-PFC-PCPG-16`, carried through `delta_records`) is wholly
    independent of the composed/aggregate one -- different values on
    purpose, both present at once."""
    per_delta_record = dataclasses.replace(_RECORDS[0], session_proof_ceiling="FIXTURE_NON_PROOF")
    result = derive_actor_safe_projection(
        _INGRESS,
        _OBSERVATION,
        (per_delta_record,),
        _CHAIN_RESULT,
        _CAPABILITY,
        _composed_effect("GOVERNED"),
    )
    assert result.delta_records[0].session_proof_ceiling == "FIXTURE_NON_PROOF"
    assert result.composed_proof_ceiling == "GOVERNED"


def test_changing_only_composed_effect_changes_only_the_projected_ceiling() -> None:
    """Required falsifier 9."""
    governed = _project(_composed_effect("GOVERNED"))
    fixture = _project(_composed_effect("FIXTURE_NON_PROOF"))
    assert governed.composed_proof_ceiling != fixture.composed_proof_ceiling
    assert governed.raw_intent == fixture.raw_intent
    assert governed.raw_intent_digest_sha256 == fixture.raw_intent_digest_sha256
    assert governed.derivation_time == fixture.derivation_time
    assert governed.semantic_observation is fixture.semantic_observation
    assert governed.delta_records == fixture.delta_records
    assert governed.chain_result is fixture.chain_result
    assert governed.capability is fixture.capability


def test_no_source_provenance_or_provider_output_proof_class_is_invented() -> None:
    """Required falsifiers 10-11: "no source provenance is added"; "no
    provider-output proof class is invented." This module cites only the
    two real `inquiry_queries.proof_mode` values, passed through -- never
    the richer I-12 vocabulary."""
    import pathlib

    root = pathlib.Path(__file__).resolve().parents[2] / "packages" / "application"
    source = (root / "pcpg_actor_projection.py").read_text()
    for forbidden in (
        "source_authority",
        "evidence_status",
        "AI_VALIDATION_PROOF",
        "DOMAIN_EVIDENCE",
        "SYSTEM_PROOF",
        "MOCK_NON_PROOF",
        "ProvenanceEnvelope",
    ):
        assert forbidden not in source
