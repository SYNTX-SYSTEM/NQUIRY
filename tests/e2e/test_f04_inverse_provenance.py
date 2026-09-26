"""F04 inverse DeepSweep, materialized: every accepted artifact and cluster run
resolves to BEGIN_ANALYSIS and the controller BINDING through PERSISTED,
write-once records only (§0.1 rule 8; §11 items 2a/2b, 4a/4b; §11.6 P1-P6).

FALSIFIERS: E16, K17, K19. The reader has no access to Session state,
generation status or a "current accepted artifact" (proven statically below).
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import f04_support as f04
import pytest
import sqlalchemy as sa
from ai_contracts.aiop import AIOperationId
from ai_contracts.authorization import RequestCase
from ai_gateway.adapters.providers.mock import MockProviderOutcome
from application.analysis_provenance import resolve_provenance
from application.analysis_runtime import UNAVAILABLE
from persistence.provenance_reader import SqlAlchemyImmutableProvenanceReader

ROOT = Path(__file__).resolve().parents[2]
A1, A2 = AIOperationId.AIOP_001, AIOperationId.AIOP_002
T = MockProviderOutcome.TIMEOUT


def _chain(db: sa.Connection, ctx: dict[str, Any], op: str) -> Any:
    (artifact,) = f04.artifacts(db, ctx, op)
    return resolve_provenance(SqlAlchemyImmutableProvenanceReader(db), artifact["id"])


def _assert_root(chain: Any, ctx: dict[str, Any]) -> None:
    assert chain.root.command_id == ctx["begin_command"].value
    assert chain.root.command_type == "CMD_BEGIN_ANALYSIS"
    assert chain.root.authority_source_type == "BINDING"
    assert chain.root.authority_scope_ref == f"SESSION:{ctx['session'].value}"
    assert chain.root.actor_id == str(ctx["fac"].value)


def test_p1_branch_2a_and_4a_original(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    f04.run(db_connection, ctx, ctx["oa1"])
    analysis = _chain(db_connection, ctx, "AIOP-001")
    assert [(link.authorization.shape, link.branch) for link in analysis.links] == [
        ("OA-1", "ORIGINAL")
    ]
    _assert_root(analysis, ctx)
    clusters = _chain(db_connection, ctx, "AIOP-002")
    assert [(link.authorization.shape, link.branch) for link in clusters.links] == [
        ("OA-3", "ORIGINAL"),
        ("OA-1", "ORIGINAL"),
    ]
    _assert_root(clusters, ctx)
    assert all(link.provider == "mock" for link in clusters.links)


def test_p2_e16_branch_2b_retry(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    f04.run(db_connection, ctx, ctx["oa1"], scripted={A1: T})
    request = f04.request(db_connection, ctx, A1, RequestCase.RETRY)
    f04.run(db_connection, ctx, request.authorization_id)
    chain = _chain(db_connection, ctx, "AIOP-001")
    (link,) = chain.links
    assert (link.authorization.shape, link.branch) == ("OA-2", "RETRY")
    assert link.retry_of_generation_id is not None
    assert link.authorizing_audit.command_type == "CMD_REQUEST_QUESTION_ANALYSIS"
    assert link.authorizing_audit.authority_source_type == "BINDING"
    _assert_root(chain, ctx)
    # K9 via 4a: OA-3 authorized by the request, X from branch 2b
    clusters = _chain(db_connection, ctx, "AIOP-002")
    assert [link.authorization.shape for link in clusters.links] == ["OA-3", "OA-2"]
    assert (
        clusters.links[0].authorization.authorizing_command_id
        == request.commit_unit.command_id.value
    )


def test_p3_branch_2b_recovery(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    f04.run(db_connection, ctx, ctx["oa1"], runtime=UNAVAILABLE)
    request = f04.request(db_connection, ctx, A1, RequestCase.RECOVERY)
    f04.run(db_connection, ctx, request.authorization_id)
    (link,) = _chain(db_connection, ctx, "AIOP-001").links
    assert link.branch == "RECOVERY"
    assert link.retry_of_generation_id is None
    assert link.superseded_authorization_id == ctx["oa1"]


def test_p5_k17_branch_4b_clustering_retry(db_connection: sa.Connection) -> None:
    ctx = f04.analysis_context(db_connection)
    f04.run(db_connection, ctx, ctx["oa1"], scripted={A2: T})
    f04.run(
        db_connection, ctx, f04.request(db_connection, ctx, A2, RequestCase.RETRY).authorization_id
    )
    chain = _chain(db_connection, ctx, "AIOP-002")
    assert [(link.authorization.shape, link.branch) for link in chain.links] == [
        ("OA-4", "RETRY"),
        ("OA-1", "ORIGINAL"),
    ]
    _assert_root(chain, ctx)


def test_p6_k19_branch_4b_clustering_recovery_from_an_oa2_artifact(
    db_connection: sa.Connection,
) -> None:
    ctx = f04.analysis_context(db_connection)
    f04.run(db_connection, ctx, ctx["oa1"], scripted={A1: T})
    retry = f04.request(db_connection, ctx, A1, RequestCase.RETRY)
    f04.run(db_connection, ctx, retry.authorization_id, follow_up=False)
    f04.run(
        db_connection,
        ctx,
        f04.request(db_connection, ctx, A2, RequestCase.RECOVERY).authorization_id,
    )
    chain = _chain(db_connection, ctx, "AIOP-002")
    assert [(link.authorization.shape, link.branch) for link in chain.links] == [
        ("OA-4", "RECOVERY"),
        ("OA-2", "RETRY"),
    ]
    assert chain.links[0].superseded_authorization_id is not None
    _assert_root(chain, ctx)


def test_the_resolver_reads_no_mutable_state() -> None:
    source = (ROOT / "packages/persistence/provenance_reader.py").read_text()
    tree = ast.parse(source)
    names = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    for forbidden in (
        "status",
        "state",
        "record_version",
        "sessions_table",
        "get_accepted_artifact",
    ):
        assert forbidden not in names, forbidden
    assert "sessions" not in source.split('"""', 2)[2]


def test_persisted_links_cannot_be_rewritten(db_connection: sa.Connection) -> None:
    from sqlalchemy.exc import DBAPIError

    ctx = f04.analysis_context(db_connection)
    f04.run(db_connection, ctx, ctx["oa1"])
    for stmt in (
        "UPDATE ai_operation_authorizations SET chain_root_command_id = authorizing_command_id",
        "UPDATE ai_operation_authorizations SET precondition_artifact_ref = NULL",
        "UPDATE ai_generations SET precondition_artifact_ref = NULL WHERE session_id = :s",
        "UPDATE ai_derived_artifacts SET accepted_by_command_id = NULL WHERE session_id = :s",
    ):
        with pytest.raises(DBAPIError), db_connection.begin_nested():
            db_connection.execute(sa.text(stmt), {"s": ctx["session"].value})
