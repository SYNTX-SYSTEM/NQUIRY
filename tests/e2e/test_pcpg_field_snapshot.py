"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — R-03: Current Field reconstruction
(Architecture 26).

Source: `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md`
R-03: "PRODUCER: the existing canonical producers of `00_FIELD.md` §7,
read-only." This module is a pure COMPOSITION of real, already-proven
producers into one `FieldSnapshot` -- it reads no fact it does not already
have a real, cited home for, and re-derives nothing.

E1 re-derivation (2026-09-30, against `checkpoint-PFC-PCPG-3`): R-04
(Pulse), R-06 through R-10 and R-12 all depend, directly or transitively,
on R-03 existing first; R-03 itself needs nothing but R-01/R-02's own
already-materialized output (a verified principal and a validated scope).
R-03 is therefore the next First Broken Relation -- not assumed, derived.

SCOPE OF THIS WORK UNIT (disclosed, not silently narrowed)
------------------------------------------------------------
R-03 ONLY: Actor context (role, governance-root fact, and the actor's own
raw, current authority bindings -- quoted, never filtered or re-derived),
Session context (state/version/fixture/proof-mode/actions, quoted
verbatim from `session_position`, present only when a Session is named),
and two Field-wide, static, cited facts this Field itself already states
elsewhere (the HD-21 admitted AI-contract scope; that no external
dependency exists in NQUIRY today), plus Provider context (environment
and whether a route is configured, from `analysis_runtime` -- config
only, never an invocation). Never re-derives authority, state or
capability: every field is a direct, traceable quote of a real producer's
value at the same basis (P-02, P-14, P-15).

`Data handling` (R-03's own "at minimum" bullet: "the data classes and
handling rules of in-scope sources") is deliberately NOT a field of
`FieldSnapshot`: `00_FIELD.md` §7 itself states no classifier is
materialized ("none materialized as a classifier; the classes are
architectural" -- GAP-11-006, FBR-PCPG-3, still OPEN). Fabricating a
placeholder value here would violate I-02 (no stratum-1 value without a
real source); omitting the field is the honest choice.
"""

from __future__ import annotations

import ast
import pathlib
from datetime import datetime, timezone

import f03_support as f03
import pytest
import sqlalchemy as sa
from application import inquiry_queries as queries
from application.inquiry_queries import QueryDenied
from application.pcpg_field_snapshot import (
    AI_CONTRACTS_ADMITTED,
    EXTERNAL_EFFECTS,
    FieldSnapshot,
    reconstruct_field,
)
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository


def _now() -> datetime:
    return datetime(2026, 9, 30, 12, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Actor context: role, governance-root, and raw authority bindings, quoted
# ---------------------------------------------------------------------------


def test_actor_context_role_matches_the_real_workspace_overview_exactly(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    ports = f03.f02.ports(db_connection)
    principal = f03.principal(ctx["fac"])
    overview = queries.workspace_overview(ports, principal, ctx["ws"])
    snapshot = reconstruct_field(
        ports, principal, workspace_id=ctx["ws"], session_id=None, now=_now()
    )
    assert snapshot.actor.role == overview["viewer"]["role"]
    assert snapshot.actor.is_governance_root == overview["viewer"]["isGovernanceRoot"]


@pytest.mark.parametrize("actor_key", ["owner", "fac"])
def test_actor_context_authority_bindings_equal_the_real_repository_output(
    db_connection: sa.Connection, actor_key: str
) -> None:
    """P-14: no parallel authority model -- the snapshot's own authority
    facts are the SAME rows `list_current_bindings` itself returns, never
    filtered, re-derived or re-interpreted. Parametrized over an actor
    whose only real binding is WORKSPACE-scoped (owner) and one whose
    only real binding is SESSION-scoped (fac) -- a test that used only
    the owner would never notice a scope-based filter, since the owner
    has no SESSION-scoped binding to filter away."""
    ctx = f03.generating_context(db_connection, participants=1)
    ports = f03.f02.ports(db_connection)
    actor = ctx[actor_key]
    principal = f03.principal(actor)
    real_bindings = SqlAlchemyAuthorityBindingRepository(db_connection).list_current_bindings(
        ctx["ws"], actor
    )
    assert real_bindings, actor_key  # the fixture must actually give this actor a binding
    snapshot = reconstruct_field(
        ports, principal, workspace_id=ctx["ws"], session_id=None, now=_now()
    )
    assert len(snapshot.actor.authority) == len(real_bindings)
    real_ids = {str(b.id.value) for b in real_bindings}
    snapshot_ids = {a.binding_id for a in snapshot.actor.authority}
    assert real_ids == snapshot_ids
    for fact in snapshot.actor.authority:
        matching = next(b for b in real_bindings if str(b.id.value) == fact.binding_id)
        assert fact.authority_class == matching.authority_class.value
        assert fact.scope_type == matching.scope_type
        assert fact.scope_id == str(matching.scope_id)
        assert fact.binding_version == matching.record_version.value


def test_a_non_member_is_denied_before_any_field_fact_is_read(db_connection: sa.Connection) -> None:
    """I-06: identity and scope before any fact. `ctx["outsider"]` from
    `generating_context` is a SAME-Workspace non-participant member, not a
    cross-Workspace outsider -- a genuine outsider comes from
    `new_workspace_with_member` (the same fix WU-PFC-PCPG-1 needed). The
    uniform denial propagates as `QueryDenied("WORKSPACE_NOT_ACCESSIBLE")`
    -- `inquiry_queries._context`'s own translation of `NotAWorkspaceMember
    Error`/`WorkspaceNotFoundError` into one uniform reason, never leaking
    which of the two actually happened (I-06's own uniform-denial shape)."""
    ctx = f03.generating_context(db_connection, participants=1)
    ports = f03.f02.ports(db_connection)
    _, real_outsider = f03.new_workspace_with_member(db_connection, "genuine-outsider")
    outsider_principal = f03.principal(real_outsider)
    with pytest.raises(QueryDenied):
        reconstruct_field(
            ports, outsider_principal, workspace_id=ctx["ws"], session_id=None, now=_now()
        )


# ---------------------------------------------------------------------------
# Session context: present only when named; quoted verbatim from
# session_position; UNRESOLVED (never a crash) when the id does not belong
# to the validated scope.
# ---------------------------------------------------------------------------


def test_session_context_is_absent_when_no_session_is_named(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    ports = f03.f02.ports(db_connection)
    principal = f03.principal(ctx["fac"])
    snapshot = reconstruct_field(
        ports, principal, workspace_id=ctx["ws"], session_id=None, now=_now()
    )
    assert snapshot.session is None
    assert "session" not in snapshot.unresolved


def test_session_context_matches_session_position_exactly(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    ports = f03.f02.ports(db_connection)
    principal = f03.principal(ctx["fac"])
    real = queries.session_position(ports, principal, ctx["ws"], ctx["session"])
    snapshot = reconstruct_field(
        ports, principal, workspace_id=ctx["ws"], session_id=ctx["session"], now=_now()
    )
    assert snapshot.session is not None
    assert snapshot.session.state == real["session"]["state"]
    assert snapshot.session.version == real["session"]["version"]
    assert snapshot.session.fixture == real["session"]["fixture"]
    assert snapshot.session.proof_mode == real["session"]["proofMode"]
    assert snapshot.session.actions == real["actions"]


def test_a_session_of_another_workspace_is_unresolved_never_a_crash(
    db_connection: sa.Connection,
) -> None:
    """R-03 FAILURE STATE: an unresolvable fact is UNRESOLVED, not an
    unhandled exception that takes down the whole reconstruction."""
    ctx = f03.generating_context(db_connection, participants=1)
    other_ws, other_owner = f03.new_workspace_with_member(db_connection, "other")
    other_ctx = f03.f02.inquiry_context(db_connection, fixture=False)
    ports = f03.f02.ports(db_connection)
    principal = f03.principal(ctx["fac"])
    snapshot = reconstruct_field(
        ports,
        principal,
        workspace_id=ctx["ws"],
        session_id=other_ctx["session"],
        now=_now(),
    )
    assert snapshot.session is None
    assert "session" in snapshot.unresolved


# ---------------------------------------------------------------------------
# Static, cited, Field-wide facts -- never re-derived, never guessed
# ---------------------------------------------------------------------------


def test_ai_contracts_admitted_is_the_real_hd21_scope() -> None:
    assert frozenset({"AIOP-001", "AIOP-002"}) == AI_CONTRACTS_ADMITTED


def test_external_effects_is_empty_matching_00_field_section_3() -> None:
    assert frozenset() == EXTERNAL_EFFECTS


def test_snapshot_carries_the_same_static_facts_every_time(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    ports = f03.f02.ports(db_connection)
    principal = f03.principal(ctx["fac"])
    snapshot = reconstruct_field(
        ports, principal, workspace_id=ctx["ws"], session_id=None, now=_now()
    )
    assert snapshot.ai_contracts_admitted == AI_CONTRACTS_ADMITTED
    assert snapshot.external_effects == EXTERNAL_EFFECTS


# ---------------------------------------------------------------------------
# Provider context: configuration only, never an invocation
# ---------------------------------------------------------------------------


def test_provider_context_reflects_a_real_test_environment(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    ports = f03.f02.ports(db_connection)
    principal = f03.principal(ctx["fac"])
    snapshot = reconstruct_field(
        ports,
        principal,
        workspace_id=ctx["ws"],
        session_id=None,
        now=_now(),
        environment={"NQUIRY_ENVIRONMENT": "TEST", "NQUIRY_AI_PROVIDER": "mock"},
    )
    assert snapshot.provider.environment == "TEST"
    assert snapshot.provider.provider_configured is True
    assert "provider" not in snapshot.unresolved


def test_provider_context_is_unresolved_on_a_forbidden_mock_configuration(
    db_connection: sa.Connection,
) -> None:
    """HD-19: MockProvider is dev-runtime only. A misconfigured environment
    never crashes the snapshot and never silently claims a route exists."""
    ctx = f03.generating_context(db_connection, participants=1)
    ports = f03.f02.ports(db_connection)
    principal = f03.principal(ctx["fac"])
    snapshot = reconstruct_field(
        ports,
        principal,
        workspace_id=ctx["ws"],
        session_id=None,
        now=_now(),
        environment={"NQUIRY_ENVIRONMENT": "PRODUCTION", "NQUIRY_AI_PROVIDER": "mock"},
    )
    assert snapshot.provider.provider_configured is False
    assert "provider" in snapshot.unresolved


def test_provider_context_with_no_provider_configured_is_resolved_and_false(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    ports = f03.f02.ports(db_connection)
    principal = f03.principal(ctx["fac"])
    snapshot = reconstruct_field(
        ports,
        principal,
        workspace_id=ctx["ws"],
        session_id=None,
        now=_now(),
        environment={"NQUIRY_ENVIRONMENT": "PRODUCTION"},
    )
    assert snapshot.provider.provider_configured is False
    assert snapshot.provider.environment == "PRODUCTION"
    assert "provider" not in snapshot.unresolved


# ---------------------------------------------------------------------------
# Determinism, basis-independence from any raw intent, purity
# ---------------------------------------------------------------------------


def test_the_snapshot_is_identical_for_two_calls_at_the_same_basis(
    db_connection: sa.Connection,
) -> None:
    """I-05/I-19: the reconstructed Field does not depend on a raw intent
    (this function never even takes one as a parameter) and is identical
    for any two calls at the same underlying state."""
    ctx = f03.generating_context(db_connection, participants=1)
    ports = f03.f02.ports(db_connection)
    principal = f03.principal(ctx["fac"])
    first = reconstruct_field(
        ports, principal, workspace_id=ctx["ws"], session_id=ctx["session"], now=_now()
    )
    second = reconstruct_field(
        ports, principal, workspace_id=ctx["ws"], session_id=ctx["session"], now=_now()
    )
    assert first == second


def test_reconstruct_field_takes_no_raw_intent_parameter() -> None:
    """Static shape proof: R-03's own INPUT list never includes the raw
    intent (00_FIELD.md §10: "Field reconstruction does not depend on the
    prompt. It is the canonical snapshot of the validated scope.")."""
    import inspect

    sig = inspect.signature(reconstruct_field)
    assert "raw_intent" not in sig.parameters
    assert "declared_purpose" not in sig.parameters


def test_the_module_never_invokes_a_provider_only_reads_configuration() -> None:
    """I-16/B-08: R-03 may read provider ROUTE CONFIGURATION (00_FIELD.md
    §7's own home for it, `application.analysis_runtime`) but must never
    CALL a gateway. Static check: no `.generate(`/`.invoke(`/`.send(` call
    exists anywhere in this module, and no import reaches an ai_gateway
    provider adapter directly."""
    root = pathlib.Path(__file__).resolve().parents[2] / "packages" / "application"
    source = (root / "pcpg_field_snapshot.py").read_text()
    tree = ast.parse(source)
    forbidden_calls = {"generate", "invoke", "send", "call"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            assert node.func.attr not in forbidden_calls, node.func.attr
    forbidden_imports = ("ai_gateway.adapters", "anthropic", "openai")
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            assert not any(mod.startswith(f) for f in forbidden_imports), mod


def test_field_snapshot_equality_is_structural_not_identity() -> None:
    """A frozen dataclass proof: two snapshots with the same content are
    equal even if constructed separately (needed for the determinism
    falsifier above to mean anything)."""
    import dataclasses

    assert dataclasses.is_dataclass(FieldSnapshot)
    assert FieldSnapshot.__dataclass_params__.frozen  # type: ignore[attr-defined]
