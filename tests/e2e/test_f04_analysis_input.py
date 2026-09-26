"""F04 WU-04.4: AIOP-001 contract + manifest bound to the verified frozen set.

MUST BECOME TRUE: the manifest is exactly the frozen members (ids + original
text digests), the fingerprint F and the Burst; the registered closed HD-18
schema is validated deterministically; the mock output conforms and carries
only manifest refs.

MUST REMAIN IMPOSSIBLE: a foreign / extra / missing Question; an unverified F;
a new-question field; a schema-invalid VALIDATED; prompt text changing the
structure; cross-Workspace refs; any write of `normalized_text`.

FALSIFIERS: D1-D8 (F04 reconstruction §15).
"""

from __future__ import annotations

import dataclasses
import json
import uuid
from typing import Any

import f02_support as f02
import f03_support as f03
import f04_support as f04
import pytest
import sqlalchemy as sa
from ai_contracts.aiop import AIOperationId
from ai_contracts.f04_operations import QUESTION_ANALYSIS, f04_operation_registry
from ai_contracts.generation import AIValidationResult
from ai_gateway.adapters.providers.mock import MockProviderAdapter
from ai_gateway.context import InputArtifactRef
from ai_gateway.validator import validate_output
from application.analysis_input import (
    ManifestBindingViolation,
    build_manifest,
    build_prompt,
    load_verified_frozen_input,
    question_ref,
    text_digest,
    verify_manifest_binding,
)
from persistence.tables import ai_context_manifests_table
from semantic_types.ids import GenerationId, WorkspaceId


def _frozen(db: sa.Connection, ctx: dict[str, Any]) -> Any:
    return load_verified_frozen_input(f02.ports(db), f03.session_of(db, ctx["session"]))


def _manifest(frozen: Any) -> Any:
    return build_manifest(
        frozen,
        contract=QUESTION_ANALYSIS,
        manifest_id=uuid.uuid4(),
        requesting_actor_ref="test",
        assembled_at=f02.NOW,
    )


def test_d1_manifest_is_exactly_the_frozen_set(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    f04.run(db_connection, ctx, ctx["oa1"])
    (row,) = f04.rows(
        db_connection,
        ai_context_manifests_table,
        session_id=ctx["session"].value,
        ai_operation_id="AIOP-001",
    )
    burst = f03.burst_of(db_connection, ctx)
    assert row["frozen_set_ref"] == f"burst:{ctx['burst'].value}"
    assert row["frozen_set_fingerprint"] == burst.frozen_membership_fingerprint
    questions = {q["id"]: q["original_text"] for q in f03.question_rows(db_connection, ctx)}
    inputs = {i["artifact_ref"]: i for i in row["input_artifact_refs_with_versions"]}
    expected = {f"question:{qid}": text_digest(text) for qid, text in questions.items()}
    assert {
        k: v["content_digest"] for k, v in inputs.items() if k.startswith("question:")
    } == expected
    # pinned by content, never by the mutable record_version (FBR-F04-6)
    assert all("version" not in v for v in inputs.values())
    assert set(row["excluded_context_classes"]) == {"AI_DERIVED_ARTIFACT", "NORMALIZED_TEXT"}


@pytest.mark.parametrize("attack", ["extra", "missing", "foreign_digest"])
def test_d2_extra_missing_or_foreign_question_is_refused(
    db_connection: sa.Connection, attack: str
) -> None:
    ctx = f04.capture_context(db_connection)
    frozen = _frozen(db_connection, ctx)
    manifest = _manifest(frozen)
    refs = list(manifest.input_artifact_refs_with_versions)
    if attack == "extra":
        refs.append(
            InputArtifactRef(artifact_ref=f"question:{uuid.uuid4()}", content_digest="0" * 64)
        )
    elif attack == "missing":
        refs = refs[1:]
    else:
        refs[0] = InputArtifactRef(artifact_ref=refs[0].artifact_ref, content_digest="f" * 64)
    tampered = dataclasses.replace(manifest, input_artifact_refs_with_versions=tuple(refs))
    with pytest.raises(ManifestBindingViolation):
        verify_manifest_binding(tampered, frozen)


def test_d2_run_refuses_before_the_provider_when_the_set_is_unverified(
    db_connection: sa.Connection,
) -> None:
    ctx = f04.analysis_context(db_connection)
    db_connection.execute(sa.text("ALTER TABLE question_bursts DISABLE TRIGGER USER"))
    db_connection.execute(
        sa.text("UPDATE question_bursts SET frozen_membership_fingerprint = 'x' WHERE id = :b"),
        {"b": ctx["burst"].value},
    )
    db_connection.execute(sa.text("ALTER TABLE question_bursts ENABLE TRIGGER USER"))
    outcome = f04.run(db_connection, ctx, ctx["oa1"])
    assert (outcome.status, outcome.reason_code) == ("NOT_EXECUTED", "FROZEN_SET_UNVERIFIED")
    assert f04.generations(db_connection, ctx) == []


def test_d3_fingerprint_mismatch_is_refused(db_connection: sa.Connection) -> None:
    ctx = f04.capture_context(db_connection)
    frozen = _frozen(db_connection, ctx)
    tampered = dataclasses.replace(_manifest(frozen), frozen_set_fingerprint="0" * 64)
    with pytest.raises(ManifestBindingViolation) as exc:
        verify_manifest_binding(tampered, frozen)
    assert exc.value.reason_code == "MANIFEST_FINGERPRINT_MISMATCH"


def _validate(content: object, refs: frozenset[str]) -> AIValidationResult:
    raw = content if isinstance(content, str) else json.dumps(content)
    return validate_output(
        raw_content=raw,
        contract=QUESTION_ANALYSIS,
        allowed_question_refs=refs,
        ai_generation_id=GenerationId(uuid.uuid4()),
        validated_at=f02.NOW,
    ).proof.validation_result


def _valid(refs: list[str]) -> dict[str, Any]:
    return {
        "operation": "AIOP-001",
        "contract_version": "1.0",
        "classification_proposals": [{"question_ref": refs[0], "proposed_class": "a"}],
        "question_families": [{"label": "f", "question_refs": refs[:2]}],
        "unusual_question_flags": [{"question_ref": refs[0], "reason": "r"}],
        "pattern_descriptions": [{"text": "t", "supporting_question_refs": refs[:1]}],
        "contradiction_proposals": [{"question_refs": refs[:2], "description": "d"}],
    }


def test_d4_d5_schema_is_closed_and_refs_are_manifest_only() -> None:
    refs = [f"question:{uuid.uuid4()}" for _ in range(3)]
    allowed = frozenset(refs)
    assert _validate(_valid(refs), allowed) is AIValidationResult.VALIDATED
    attacks: list[object] = [
        "{not json",
        json.dumps(_valid(refs))[:40],  # partial
        {**_valid(refs), "operation": "AIOP-014"},
        {**_valid(refs), "contract_version": "2.0"},
        {**_valid(refs), "additional_questions": ["new?"]},  # HD-18
        {**_valid(refs), "suggested_questions": []},
        {k: v for k, v in _valid(refs).items() if k != "question_families"},
        {
            **_valid(refs),
            "classification_proposals": [
                {"question_ref": f"question:{uuid.uuid4()}", "proposed_class": "x"}
            ],
        },
        {
            **_valid(refs),
            "question_families": [{"label": "f", "question_refs": refs, "new_question": "?"}],
        },
        {
            **_valid(refs),
            "contradiction_proposals": [{"question_refs": refs[:1], "description": "d"}],
        },
        {
            **_valid(refs),
            "pattern_descriptions": [{"text": "", "supporting_question_refs": refs[:1]}],
        },
        {
            **_valid(refs),
            "unusual_question_flags": [{"question_ref": refs[0], "reason": "x" * 1001}],
        },
        [1, 2, 3],
    ]
    for attack in attacks:
        assert _validate(attack, allowed) is AIValidationResult.REJECTED, attack


def test_d6_prompt_injection_changes_neither_structure_nor_output(
    db_connection: sa.Connection,
) -> None:
    ctx = f04.capture_context(db_connection)
    frozen = _frozen(db_connection, ctx)
    prompt = build_prompt(frozen, QUESTION_ANALYSIS)
    injected = [b for b in prompt.data_blocks if "Ignore all previous instructions" in b.content]
    assert len(injected) == 1  # the injection is a DATA block, not an instruction
    assert "Ignore all previous" not in prompt.system_instructions
    benign = dataclasses.replace(
        prompt,
        data_blocks=tuple(
            dataclasses.replace(b, content="A harmless question?") for b in prompt.data_blocks
        ),
    )
    mock = MockProviderAdapter()
    assert mock.invoke(prompt).raw_content == mock.invoke(benign).raw_content
    assert _validate(mock.invoke(prompt).raw_content, frozen.question_refs) is (
        AIValidationResult.VALIDATED
    )


def test_d7_no_cross_workspace_refs(db_connection: sa.Connection) -> None:
    ctx = f04.capture_context(db_connection)
    frozen = _frozen(db_connection, ctx)
    foreign = dataclasses.replace(_manifest(frozen), workspace_id=WorkspaceId(uuid.uuid4()))
    with pytest.raises(ManifestBindingViolation) as exc:
        verify_manifest_binding(foreign, frozen)
    assert exc.value.reason_code == "MANIFEST_FOREIGN_WORKSPACE"
    other = f04.capture_context(db_connection)
    other_refs = _frozen(db_connection, other).question_refs
    assert not (other_refs & frozen.question_refs)
    content = _valid(sorted(other_refs))
    assert _validate(content, frozen.question_refs) is AIValidationResult.REJECTED


def test_d8_normalized_text_unchanged_after_the_full_flow(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    before = {
        q["id"]: (q["normalized_text"], q["original_text"], q["record_version"])
        for q in f03.question_rows(db_connection, ctx)
    }
    outcome = f04.run(db_connection, ctx, ctx["oa1"])
    assert outcome.status == "ACCEPTED" and outcome.next is not None
    assert outcome.next.status == "ACCEPTED"
    after = {
        q["id"]: (q["normalized_text"], q["original_text"], q["record_version"])
        for q in f03.question_rows(db_connection, ctx)
    }
    assert after == before
    assert all(v[0] is None for v in after.values())


def test_contracts_are_registered_and_only_f04_operations() -> None:
    registry = f04_operation_registry()
    assert registry.get(AIOperationId.AIOP_001) == QUESTION_ANALYSIS
    assert registry.get(AIOperationId.AIOP_002) is not None
    for op in AIOperationId:
        if op not in (AIOperationId.AIOP_001, AIOperationId.AIOP_002):
            assert registry.get(op) is None


def test_mock_output_refs_come_only_from_the_manifest(db_connection: sa.Connection) -> None:
    ctx = f04.capture_context(db_connection)
    frozen = _frozen(db_connection, ctx)
    payload = json.loads(
        MockProviderAdapter().invoke(build_prompt(frozen, QUESTION_ANALYSIS)).raw_content
    )
    used = {p["question_ref"] for p in payload["classification_proposals"]}
    assert used == frozen.question_refs == {question_ref(q) for q in ctx["question_ids"]}
