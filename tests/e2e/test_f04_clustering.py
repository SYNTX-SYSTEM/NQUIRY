"""F04 WU-04.9: AIOP-002 clustering (HD-21 + HD-23; 09 §34 / §35).

MUST BECOME TRUE: at most one automatic clustering run per OA-3, which exists
only after an AIOP-001 artifact was accepted; it is never blocked by the AIOP-001
generation of the same root Command (C9); clusters reference only frozen
Questions of this Session; at most one accepted cluster run per Session; every
branch (original, RETRY, RECOVERY) resolves to BEGIN_ANALYSIS through persisted
records only.

MUST REMAIN IMPOSSIBLE: clustering without an accepted AIOP-001 artifact; the
AIOP-001 artifact as model input; a second run per OA; a run after an accepted
cluster run; a Question / membership mutation; a priority grant.

FALSIFIERS: C9, K1-K20 (F04 reconstruction §15).
"""

from __future__ import annotations

import uuid
from typing import Any

import f02_support as f02
import f03_support as f03
import f04_support as f04
import pytest
import sqlalchemy as sa
from ai_contracts.aiop import AIOperationId
from ai_contracts.authorization import RequestCase
from ai_gateway.adapters.providers.mock import MockProviderOutcome
from application.analysis_runtime import UNAVAILABLE
from application.session_control_handler import SessionCommandDenied, SessionPreconditionUnmet
from persistence.tables import (
    ai_context_manifests_table,
    question_cluster_memberships_table,
    question_clusters_table,
)
from sqlalchemy.exc import DBAPIError

A1, A2 = AIOperationId.AIOP_001, AIOperationId.AIOP_002


def _clusters(db: sa.Connection, ctx: dict[str, Any]) -> list[Any]:
    return f04.rows(db, question_clusters_table, session_id=ctx["session"].value)


def _members(db: sa.Connection, ctx: dict[str, Any]) -> list[Any]:
    return f04.rows(db, question_cluster_memberships_table, session_id=ctx["session"].value)


def test_c9_k8_original_run_then_automatic_clustering(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    before = f04.snapshot(db_connection, ctx)
    outcome = f04.run(db_connection, ctx, ctx["oa1"])
    assert outcome.status == "ACCEPTED" and outcome.next is not None
    assert outcome.next.status == "ACCEPTED"

    (g1,) = f04.generations(db_connection, ctx, "AIOP-001")
    (g2,) = f04.generations(db_connection, ctx, "AIOP-002")
    # C9: same root Command, different operation: both persist.
    assert (
        g1["authorizing_command_id"] == g2["authorizing_command_id"] == ctx["begin_command"].value
    )
    (analysis,) = f04.artifacts(db_connection, ctx, "AIOP-001")
    assert g2["precondition_artifact_ref"] == analysis["id"]
    (audit,) = f03.audit_rows(db_connection, ctx, "CMD_ACCEPT_CLUSTERING_OUTPUT")
    assert audit["authority_source_type"] == "SYSTEM_OPERATION"
    assert audit["authority_source_ref"] == ctx["begin_command"].value

    # K1 / K3: one run, frozen Questions only, each at most once
    (run,) = f04.artifacts(db_connection, ctx, "AIOP-002")
    clusters = _clusters(db_connection, ctx)
    assert clusters and {c["cluster_run_id"] for c in clusters} == {run["id"]}
    member_ids = [m["question_id"] for m in _members(db_connection, ctx)]
    assert len(member_ids) == len(set(member_ids))
    assert set(member_ids) <= {q.value for q in ctx["question_ids"]}
    # K2: nothing human changed
    assert f04.snapshot(db_connection, ctx) == before


def test_k5_no_priority_or_selection_field() -> None:
    columns = {c.name for c in question_clusters_table.columns} | {
        c.name for c in question_cluster_memberships_table.columns
    }
    assert not {
        c for c in columns if any(w in c for w in ("priority", "rank", "select", "primary"))
    }


def test_k10_model_input_is_the_frozen_human_set_only(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    f04.run(db_connection, ctx, ctx["oa1"])
    (manifest,) = f04.rows(
        db_connection,
        ai_context_manifests_table,
        session_id=ctx["session"].value,
        ai_operation_id="AIOP-002",
    )
    refs = {
        i["artifact_ref"].split(":", 1)[0] for i in manifest["input_artifact_refs_with_versions"]
    }
    assert refs == {"question", "challenge"}
    assert "AI_DERIVED_ARTIFACT" in manifest["excluded_context_classes"]


@pytest.mark.parametrize("scripted", [MockProviderOutcome.TIMEOUT, MockProviderOutcome.FOREIGN_REF])
def test_k7_no_clustering_when_analysis_fails_or_is_rejected(
    db_connection: sa.Connection, scripted: MockProviderOutcome
) -> None:
    ctx = f04.analysis_context(db_connection)
    outcome = f04.run(db_connection, ctx, ctx["oa1"], scripted={A1: scripted})
    assert outcome.next is None
    assert f04.generations(db_connection, ctx, "AIOP-002") == []
    assert f04.authorizations(db_connection, ctx, "AIOP-002") == []
    assert _clusters(db_connection, ctx) == []
    with pytest.raises(SessionPreconditionUnmet) as exc:
        f04.request(db_connection, ctx, A2, RequestCase.RECOVERY)
    assert exc.value.reason_code == "NO_ACCEPTED_ANALYSIS"


def test_k4_k6_rejected_clustering_output_leaves_no_clusters(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    outcome = f04.run(
        db_connection, ctx, ctx["oa1"], scripted={A2: MockProviderOutcome.FOREIGN_REF}
    )
    assert outcome.next is not None and outcome.next.status == "REJECTED"
    (g2,) = f04.generations(db_connection, ctx, "AIOP-002")
    assert g2["status"] == "REJECTED"
    assert (
        _clusters(db_connection, ctx) == [] and f04.artifacts(db_connection, ctx, "AIOP-002") == []
    )


def test_k9_k11_k16_clustering_retry_after_analysis_retry(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    f04.run(db_connection, ctx, ctx["oa1"], scripted={A1: MockProviderOutcome.TIMEOUT})
    retry = f04.request(db_connection, ctx, A1, RequestCase.RETRY)
    outcome = f04.run(
        db_connection, ctx, retry.authorization_id, scripted={A2: MockProviderOutcome.TIMEOUT}
    )
    assert outcome.status == "ACCEPTED" and outcome.next.status == "FAILED"  # type: ignore[union-attr]
    (oa3,) = f04.authorizations(db_connection, ctx, "AIOP-002")
    # K9: OA-3 authorized by C = the analysis request
    assert oa3["authorizing_command_id"] == retry.commit_unit.command_id.value
    (failed,) = f04.generations(db_connection, ctx, "AIOP-002")
    assert failed["authorizing_command_id"] == retry.commit_unit.command_id.value

    # K11: no automatic retry; the controller RETRY creates OA-4
    cluster_retry = f04.request(db_connection, ctx, A2, RequestCase.RETRY)
    oa4 = f04.authorizations(db_connection, ctx, "AIOP-002")[-1]
    (x,) = f04.artifacts(db_connection, ctx, "AIOP-001")
    assert (oa4["shape"], oa4["request_case"]) == ("OA-4", "RETRY")
    assert oa4["precondition_artifact_ref"] == x["id"]  # K17: X persisted
    assert oa4["retry_of_generation_id"] == failed["id"]
    assert oa4["chain_root_command_id"] == ctx["begin_command"].value
    done = f04.run(db_connection, ctx, cluster_retry.authorization_id)
    assert done.status == "ACCEPTED"
    gens = f04.generations(db_connection, ctx, "AIOP-002")
    assert [g["status"] for g in gens] == ["FAILED", "VALIDATED"]
    assert gens[1]["retry_of_generation_id"] == failed["id"]
    assert gens[1]["precondition_artifact_ref"] == x["id"]
    # K13 / K16: one accepted cluster run; nothing more after it
    assert len(f04.artifacts(db_connection, ctx, "AIOP-002")) == 1
    for case in RequestCase:
        with pytest.raises(SessionPreconditionUnmet) as exc:
            f04.request(db_connection, ctx, A2, case)
        assert exc.value.reason_code == "RESULT_ALREADY_ACCEPTED"
    assert f04.run(db_connection, ctx, cluster_retry.authorization_id).status == "NOT_EXECUTED"


def test_k14_k19_recovery_of_an_unconsumed_oa3(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    # AIOP-001 accepted; the process stops before the clustering run (P6).
    assert f04.run(db_connection, ctx, ctx["oa1"], follow_up=False).status == "ACCEPTED"
    (oa3,) = f04.authorizations(db_connection, ctx, "AIOP-002")
    assert f04.generations(db_connection, ctx, "AIOP-002") == []
    with pytest.raises(SessionPreconditionUnmet):  # RETRY names the wrong case
        f04.request(db_connection, ctx, A2, RequestCase.RETRY)
    recovery = f04.request(db_connection, ctx, A2, RequestCase.RECOVERY)
    oa4 = f04.authorizations(db_connection, ctx, "AIOP-002")[-1]
    assert (oa4["request_case"], oa4["supersedes_authorization_id"]) == ("RECOVERY", oa3["id"])
    assert oa4["retry_of_generation_id"] is None
    # OA-3 is superseded and can never execute
    late = f04.run(db_connection, ctx, oa3["id"])
    assert late.reason_code == "SYSTEM_OPERATION_SUPERSEDED"
    assert f04.run(db_connection, ctx, recovery.authorization_id).status == "ACCEPTED"
    (gen,) = f04.generations(db_connection, ctx, "AIOP-002")
    assert gen["retry_of_generation_id"] is None
    assert gen["operation_authorization_id"] == recovery.authorization_id
    (x,) = f04.artifacts(db_connection, ctx, "AIOP-001")
    assert gen["precondition_artifact_ref"] == x["id"]


def test_k12_non_controller_request_is_denied(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    f04.run(db_connection, ctx, ctx["oa1"], scripted={A2: MockProviderOutcome.TIMEOUT})
    for actor in (ctx["participants"][0], ctx["owner"], ctx["outsider"]):
        with pytest.raises(SessionCommandDenied):
            f04.request(db_connection, ctx, A2, RequestCase.RETRY, actor)


def test_k20_request_while_clustering_non_terminal_is_blocked(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    f04.run(db_connection, ctx, ctx["oa1"], follow_up=False)
    (oa3,) = f04.authorizations(db_connection, ctx, "AIOP-002")
    stuck = f04.run(db_connection, ctx, oa3["id"], stop_after_execute=True)
    assert stuck.status == "INDETERMINATE"
    for case in RequestCase:
        with pytest.raises(SessionPreconditionUnmet) as exc:
            f04.request(db_connection, ctx, A2, case)
        assert exc.value.reason_code == "GENERATION_IN_PROGRESS"


def test_k18_forged_precondition_artifact_is_refused(db_connection: sa.Connection) -> None:
    """X must be an accepted AIOP-001 artifact of this Session (DB + gate)."""
    ctx = f04.analysis_context(db_connection)
    other = f04.analysis_context(db_connection)
    f04.run(db_connection, other, other["oa1"])
    (foreign_x,) = f04.artifacts(db_connection, other, "AIOP-001")
    with pytest.raises(DBAPIError), db_connection.begin_nested():
        db_connection.execute(
            sa.text(
                "INSERT INTO ai_operation_authorizations (id, workspace_id, session_id, "
                "ai_operation_id, shape, authorizing_command_id, sequence_no, "
                "chain_root_command_id, precondition_artifact_ref, created_at) VALUES "
                "(:i, :w, :s, 'AIOP-002', 'OA-3', :c, 1, :c, :x, now())"
            ),
            {
                "i": uuid.uuid4(),
                "w": ctx["ws"].value,
                "s": ctx["session"].value,
                "c": ctx["begin_command"].value,
                "x": foreign_x["id"],
            },
        )


def test_cluster_membership_of_a_non_frozen_question_is_refused(
    db_connection: sa.Connection,
) -> None:
    ctx = f04.analysis_context(db_connection)
    f04.run(db_connection, ctx, ctx["oa1"])
    (cluster, *_) = _clusters(db_connection, ctx)
    other = f04.capture_context(db_connection)
    foreign_q = other["question_ids"][0]
    with pytest.raises(DBAPIError) as exc, db_connection.begin_nested():
        db_connection.execute(
            sa.insert(question_cluster_memberships_table).values(
                id=uuid.uuid4(),
                workspace_id=ctx["ws"].value,
                session_id=ctx["session"].value,
                question_cluster_id=cluster["id"],
                question_id=foreign_q.value,
                cluster_run_id=cluster["cluster_run_id"],
                created_at=f02.NOW,
            )
        )
    # the Question is of another Workspace: refused by the composite FK / frozen-set trigger
    assert "frozen set" in str(exc.value) or "fk_question_cluster_memberships" in str(exc.value)
    for stmt in (
        "UPDATE question_clusters SET label = 'x' WHERE id = :i",
        "DELETE FROM question_clusters WHERE id = :i",
    ):
        with pytest.raises(DBAPIError), db_connection.begin_nested():
            db_connection.execute(sa.text(stmt), {"i": cluster["id"]})


def test_unavailable_provider_leaves_oa_unconsumed_for_recovery(
    db_connection: sa.Connection,
) -> None:
    ctx = f04.analysis_context(db_connection)
    assert f04.run(db_connection, ctx, ctx["oa1"], runtime=UNAVAILABLE).status == "NOT_EXECUTED"
    assert f04.generations(db_connection, ctx) == []


def test_k15_oa3_not_authorized_by_xs_command_is_denied_at_the_gate(
    db_connection: sa.Connection,
) -> None:
    """Defence in depth: even with the insert trigger bypassed (test superuser),
    the SYSTEM_OPERATION check refuses an OA-3 whose C is not X's authorizer."""
    from ai_contracts.authorization import AuthorizationShape, OperationAuthorization
    from authority.actor import ActorClass, ActorIdentity
    from authority.system_service import F04_ANALYSIS_SERVICE_ID
    from boundaries.authority_source import SystemOperationAuthority, SystemOperationPurpose
    from boundaries.system_operation import resolve_system_operation
    from semantic_types.ids import CommandId

    ctx = f04.analysis_context(db_connection)
    f04.run(db_connection, ctx, ctx["oa1"], scripted={A1: MockProviderOutcome.TIMEOUT})
    retry = f04.request(db_connection, ctx, A1, RequestCase.RETRY)
    f04.run(db_connection, ctx, retry.authorization_id, follow_up=False)
    (x,) = f04.artifacts(db_connection, ctx, "AIOP-001")  # authorized by the request
    real_oa3 = f04.authorizations(db_connection, ctx, "AIOP-002")[0]
    db_connection.execute(sa.text("ALTER TABLE ai_operation_authorizations DISABLE TRIGGER USER"))
    db_connection.execute(
        sa.text("DELETE FROM ai_operation_authorizations WHERE id = :i"), {"i": real_oa3["id"]}
    )
    forged = OperationAuthorization(
        authorization_id=uuid.uuid4(),
        workspace_id=ctx["ws"],
        session_id=ctx["session"],
        ai_operation_id=A2,
        shape=AuthorizationShape.OA_3,
        authorizing_command_id=CommandId(ctx["begin_command"].value),  # not X's authorizer
        sequence_no=1,
        chain_root_command_id=CommandId(ctx["begin_command"].value),
        created_at=f02.NOW,
        precondition_artifact_ref=x["id"],
    )
    f02.ports(db_connection).ai_authorizations.create(forged)
    db_connection.execute(sa.text("ALTER TABLE ai_operation_authorizations ENABLE TRIGGER USER"))
    resolution = resolve_system_operation(
        reader=f02.ports(db_connection).system_operations,
        actor=ActorIdentity(ActorClass.SYSTEM_SERVICE, F04_ANALYSIS_SERVICE_ID),
        workspace_id=ctx["ws"],
        authority=SystemOperationAuthority(
            session_id=ctx["session"].value,
            operation_authorization_id=forged.authorization_id,
            purpose=SystemOperationPurpose.EXECUTE,
        ),
    )
    assert resolution.reason_code == "SYSTEM_OPERATION_PRECONDITION_AUTHORIZER_MISMATCH"
