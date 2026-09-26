"""F04 independent-review repairs FBR-F04-R1 and FBR-F04-R2 (PI-1; 09 §118;
06 §16 home note; reconstruction §11 items 2a/2b/4a/4b).

R1: the accepted effect must provably BE the VALIDATED candidate.
MUST BECOME TRUE: every accepted artifact's content is byte-identical to the
output its proof validated: sha256(content) = content_fingerprint =
proof.output_fingerprint. The persisted-only provenance chain includes the
VALIDATED proof.
MUST REMAIN IMPOSSIBLE: an accepted artifact whose content differs from the
validated bytes, or which has no VALIDATED proof of the same operation; a
provenance chain that resolves without a VALIDATED proof.

R2: a persisted VALIDATED proof exists if and only if its generation is
VALIDATED and has exactly one accepted artifact (all in one commit).
MUST BECOME TRUE: a denied / failed acceptance leaves the generation FAILED
(ACCEPTANCE_DENIED), the validated fingerprint in `failure_detail_ref`, NO
proof row, and RETRY legal.
MUST REMAIN IMPOSSIBLE: a VALIDATED proof on a FAILED (or any non-VALIDATED)
generation; a VALIDATED proof or VALIDATED generation without its accepted
artifact at commit.
"""

from __future__ import annotations

import dataclasses
import hashlib
import uuid
from typing import Any

import f02_support as f02
import f04_support as f04
import pytest
import sqlalchemy as sa
from ai_contracts.aiop import AIOperationId
from ai_contracts.authorization import RequestCase
from application.analysis_provenance import ProvenanceBroken, resolve_provenance
from commit.coordinator import CommitInjectionPoint
from persistence.provenance_reader import SqlAlchemyImmutableProvenanceReader
from persistence.tables import (
    ai_derived_artifacts_table,
    ai_generations_table,
    ai_validation_proofs_table,
)
from sqlalchemy.exc import DBAPIError
from test_support.failure_injector import ScriptedFailureInjector

A1 = AIOperationId.AIOP_001


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _proof(db: sa.Connection, generation_id: Any) -> list[Any]:
    return f04.rows(db, ai_validation_proofs_table, ai_generation_id=generation_id)


def _immediate(db: sa.Connection) -> None:
    """Fire the deferred PI-1 constraint triggers now (as COMMIT would)."""
    db.execute(sa.text("SET CONSTRAINTS ALL IMMEDIATE"))


# ------------------------------------------------------------------------ R1


def test_r1_every_accepted_artifact_is_the_validated_bytes(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    outcome = f04.run(db_connection, ctx, ctx["oa1"])
    assert outcome.status == "ACCEPTED" and outcome.next.status == "ACCEPTED"  # type: ignore[union-attr]
    artifacts = f04.artifacts(db_connection, ctx)
    assert {a["ai_operation_id"] for a in artifacts} == {"AIOP-001", "AIOP-002"}
    for artifact in artifacts:
        (proof,) = _proof(db_connection, artifact["ai_generation_id"])
        assert proof["validation_result"] == "VALIDATED"
        assert proof["ai_operation_id"] == artifact["ai_operation_id"]
        assert _sha(artifact["content"]) == artifact["content_fingerprint"]
        assert artifact["content_fingerprint"] == proof["output_fingerprint"]
    # the same invariant, evaluated by PostgreSQL itself over persisted state
    bad = db_connection.execute(
        sa.text(
            "SELECT count(*) FROM ai_derived_artifacts a "
            "LEFT JOIN ai_validation_proofs p ON p.ai_generation_id = a.ai_generation_id "
            "WHERE a.session_id = :s AND (p.id IS NULL OR p.validation_result <> 'VALIDATED' "
            "OR p.output_fingerprint <> a.content_fingerprint "
            "OR a.content_fingerprint <> encode(sha256(convert_to(a.content, 'UTF8')), 'hex'))"
        ),
        {"s": ctx["session"].value},
    ).scalar_one()
    assert bad == 0


def _insert_copy(db: sa.Connection, artifact: Any, **changes: Any) -> None:
    row = dict(artifact)
    row.update(id=uuid.uuid4(), **changes)
    db.execute(sa.insert(ai_derived_artifacts_table).values(**row))


def test_r1_db_refuses_an_accepted_artifact_that_is_not_the_validated_bytes(
    db_connection: sa.Connection,
) -> None:
    """The binding trigger fires BEFORE INSERT, so it refuses before uniqueness
    could: its message is what the attack meets."""
    import json

    ctx = f04.analysis_context(db_connection)
    f04.run(db_connection, ctx, ctx["oa1"], scripted={A1: f04_timeout()})  # FAILED generation
    retry = f04.request(db_connection, ctx, A1, RequestCase.RETRY)
    f04.run(db_connection, ctx, retry.authorization_id, follow_up=False)
    failed, validated = f04.generations(db_connection, ctx, "AIOP-001")
    (artifact,) = f04.artifacts(db_connection, ctx, "AIOP-001")
    assert artifact["ai_generation_id"] == validated["id"]
    reserialized = json.dumps(json.loads(artifact["content"]), separators=(",", ":"))
    assert reserialized != artifact["content"]
    attacks = [
        # the pre-repair defect: re-serialized content under the proof's fingerprint
        {"content": reserialized},
        # content and fingerprint agree with each other but not with the proof
        {"content": reserialized, "content_fingerprint": _sha(reserialized)},
        # an accepted artifact for a generation that has no VALIDATED proof
        {"ai_generation_id": failed["id"]},
    ]
    for changes in attacks:
        with pytest.raises(DBAPIError) as exc, db_connection.begin_nested():
            _insert_copy(db_connection, artifact, **changes)
        assert "accepted artifact must be the validated output" in str(exc.value), changes


class _Tampered:
    """A reader that returns persisted facts, except the proof, which is
    replaced by `proof` (None = missing). Proves the resolver's own guard."""

    def __init__(self, inner: SqlAlchemyImmutableProvenanceReader, proof: Any) -> None:
        self._inner, self._proof = inner, proof

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def validation_proof(self, generation_id: uuid.UUID) -> Any:
        real = self._inner.validation_proof(generation_id)
        return self._proof(real) if callable(self._proof) else self._proof


@pytest.mark.parametrize(
    "tamper",
    [
        None,
        lambda p: dataclasses.replace(p, validation_result="REJECTED"),
        lambda p: dataclasses.replace(p, output_fingerprint="0" * 64),
        lambda p: dataclasses.replace(p, ai_operation_id="AIOP-002"),
    ],
    ids=["missing", "rejected", "fingerprint", "operation"],
)
def test_r1_resolver_refuses_a_chain_without_the_validated_proof(
    db_connection: sa.Connection, tamper: Any
) -> None:
    ctx = f04.analysis_context(db_connection)
    f04.run(db_connection, ctx, ctx["oa1"], follow_up=False)
    (artifact,) = f04.artifacts(db_connection, ctx, "AIOP-001")
    reader = SqlAlchemyImmutableProvenanceReader(db_connection)
    chain = resolve_provenance(reader, artifact["id"])
    (proof,) = _proof(db_connection, artifact["ai_generation_id"])
    assert chain.links[0].proof_id == proof["id"]  # the chain visits the proof
    with pytest.raises(ProvenanceBroken):
        resolve_provenance(_Tampered(reader, tamper), artifact["id"])  # type: ignore[arg-type]


# ------------------------------------------------------------------------ R2


def test_r2_denied_acceptance_persists_no_validated_proof(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    outcome = f04.run(
        db_connection,
        ctx,
        ctx["oa1"],
        accept_failure_injector=ScriptedFailureInjector(
            fire_at=CommitInjectionPoint.BEFORE_AUDIT, exception=RuntimeError("boom")
        ),
    )
    assert outcome.status == "ACCEPTANCE_DENIED"
    (gen,) = f04.generations(db_connection, ctx)
    assert gen["status"] == "FAILED"
    assert gen["failure_code"].startswith("ACCEPTANCE_DENIED:")
    assert gen["failure_detail_ref"].startswith("validated_output_fingerprint:")
    assert len(gen["failure_detail_ref"].split(":", 1)[1]) == 64
    assert _proof(db_connection, gen["id"]) == []
    assert f04.artifacts(db_connection, ctx) == []
    _immediate(db_connection)  # the deferred PI-1 checks hold at "commit"
    assert f04.request(db_connection, ctx, A1, RequestCase.RETRY).case is RequestCase.RETRY


def test_r2_db_refuses_a_validated_proof_without_its_accepted_artifact(
    db_connection: sa.Connection,
) -> None:
    ctx = f04.analysis_context(db_connection)
    f04.run(db_connection, ctx, ctx["oa1"], stop_after_execute=True)  # generation RUNNING
    (gen,) = f04.generations(db_connection, ctx)
    with pytest.raises(DBAPIError) as exc, db_connection.begin_nested():
        db_connection.execute(
            sa.insert(ai_validation_proofs_table).values(
                id=uuid.uuid4(),
                workspace_id=ctx["ws"].value,
                ai_generation_id=gen["id"],
                ai_operation_id="AIOP-001",
                contract_version="1.0",
                validator_version="4.1",
                validation_result="VALIDATED",
                validated_at=f02.NOW,
                output_fingerprint="f" * 64,
            )
        )
        _immediate(db_connection)
    assert "PI-1" in str(exc.value)


def test_r2_db_refuses_a_validated_generation_without_proof_and_artifact(
    db_connection: sa.Connection,
) -> None:
    ctx = f04.analysis_context(db_connection)
    f04.run(db_connection, ctx, ctx["oa1"], stop_after_execute=True)  # RUNNING, version 2
    (gen,) = f04.generations(db_connection, ctx)
    with pytest.raises(DBAPIError) as exc, db_connection.begin_nested():
        for status, version in (("OUTPUT_RECEIVED", 3), ("VALIDATED", 4)):
            db_connection.execute(
                sa.update(ai_generations_table)
                .where(ai_generations_table.c.id == gen["id"])
                .values(status=status, record_version=version)
            )
        _immediate(db_connection)
    assert "PI-1" in str(exc.value)


def test_r2_rejected_and_indeterminate_proofs_are_unchanged(db_connection: sa.Connection) -> None:
    from ai_gateway.adapters.providers.mock import MockProviderOutcome

    ctx = f04.analysis_context(db_connection)
    f04.run(db_connection, ctx, ctx["oa1"], scripted={A1: MockProviderOutcome.PARTIAL_RESPONSE})
    (gen,) = f04.generations(db_connection, ctx)
    assert [p["validation_result"] for p in _proof(db_connection, gen["id"])] == ["REJECTED"]
    _immediate(db_connection)


def f04_timeout() -> Any:
    from ai_gateway.adapters.providers.mock import MockProviderOutcome

    return MockProviderOutcome.TIMEOUT
