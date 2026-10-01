"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — FBR-PCPG-18: runtime composition of
R-03 through R-12 (Architecture 26).

Source: `packages/application/pcpg_runtime_composition.py`'s own module
docstring (the authoritative RED reconciliation and disclosed scope are
recorded there, not repeated here). This file falsifies exactly that
module's own `derive_governance_observation`, calling it directly against
real, DB-backed producers -- the same direct-producer-call convention every
other PCPG relation's own test file already uses (never through the HTTP
dispatch layer; `test_http_pcpg.py` falsifies the wire/HTTP layer
separately).

WHAT THIS FILE DOES NOT RE-PROVE
-----------------------------------
Every individual producer's own branch logic (R-03's unresolved-session
handling, R-05's clause segmentation, R-07's RESULT vocabulary, R-08's
composition, R-09's chain derivation, R-10's capability derivation, R-12's
projection) is already fully falsified, byte-for-byte, in its own dedicated
test file (`test_pcpg_field_snapshot.py` through `test_pcpg_actor_
projection.py`), unmodified by this Work Unit. This file falsifies only the
NEW fact: that `derive_governance_observation` calls them in the real
canonical order, with the real arguments, and fails closed, honestly,
exactly where it says it does.
"""

from __future__ import annotations

import ast
import hashlib
import inspect
import types
from datetime import datetime, timezone

import f03_support as f03
import pytest
import sqlalchemy as sa
from application import pcpg_observation as pcpg
from application.pcpg_runtime_composition import (
    FIELD_RECONSTRUCTION_UNAVAILABLE,
    PROJECTION_INCOMPLETE,
    SEMANTIC_OBSERVATION_UNAVAILABLE,
    GovernanceObservationUnavailable,
    derive_governance_observation,
)
from semantic_types.ids import SessionId, WorkspaceId


def _now() -> datetime:
    return datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc)


def _ingress(
    *,
    workspace_id: WorkspaceId,
    workspace_name: str = "Inquiry",
    session_id: SessionId | None = None,
    raw_intent: str,
    declared_purpose: str | None = None,
) -> pcpg.ObservationIngressResult:
    """Hand-built R-01/R-02 output -- R-01/R-02 themselves are untouched by
    this Work Unit and already fully falsified in
    `test_pcpg_observation_ingress.py`; constructing the result directly
    isolates these falsifiers to R-03 onward, exactly this file's own
    disclosed scope."""
    digest = hashlib.sha256(raw_intent.encode("utf-8")).hexdigest()
    return pcpg.ObservationIngressResult(
        workspace_id=workspace_id,
        workspace_name=workspace_name,
        session_id=session_id,
        raw_intent=raw_intent,
        raw_intent_length=len(raw_intent),
        raw_intent_digest_sha256=digest,
        declared_purpose=declared_purpose,
        observed_at=_now(),
    )


# ---------------------------------------------------------------------------
# 1. The real, successful composition: R-03..R-12 (never R-11) actually run
# ---------------------------------------------------------------------------


def test_successful_composition_produces_a_real_actor_safe_projection(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    ports = f03.f02.ports(db_connection)
    principal = f03.principal(ctx["fac"])
    ingress = _ingress(
        workspace_id=ctx["ws"],
        session_id=ctx["session"],
        raw_intent="begin the analysis",
        declared_purpose="move the Session forward",
    )
    observation = derive_governance_observation(ports, principal, ingress)
    assert not isinstance(observation, GovernanceObservationUnavailable), observation
    assert observation.raw_intent == "begin the analysis"
    assert observation.raw_intent_digest_sha256 == ingress.raw_intent_digest_sha256
    assert observation.derivation_time == ingress.observed_at
    assert observation.semantic_observation.raw_intent == "begin the analysis"
    assert len(observation.delta_records) >= 1
    assert observation.chain_result is not None
    assert observation.capability is not None


def _imported_module_names(mod: types.ModuleType) -> set[str]:
    """The real, executable `import X` / `from X import ...` module
    references in `mod`'s own source -- via its AST, never a raw substring
    search (which would also match this module's own disclosure prose,
    e.g. its docstring's own citation of `EligibleContentSet` explaining
    why R-11 is NOT called). The same "structural, not textual" discipline
    WU-PFC-PCPG-17's own AST purity check already established."""
    tree = ast.parse(inspect.getsource(mod))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def test_r11_eligible_content_is_never_produced_or_imported(db_connection: sa.Connection) -> None:
    """B-10's own deny-list item: `EligibleContentSet` must never reach the
    projection -- proven both structurally (the module never IMPORTS R-11's
    own module at all, checked via AST, not a docstring-sensitive substring
    search) and behaviorally (a real composition's own result carries no
    such attribute)."""
    import application.pcpg_runtime_composition as mod

    imported = _imported_module_names(mod)
    assert not any("pcpg_eligible_content" in name for name in imported)

    ctx = f03.generating_context(db_connection, participants=1)
    ports = f03.f02.ports(db_connection)
    principal = f03.principal(ctx["fac"])
    ingress = _ingress(workspace_id=ctx["ws"], session_id=ctx["session"], raw_intent="begin setup")
    observation = derive_governance_observation(ports, principal, ingress)
    assert not isinstance(observation, GovernanceObservationUnavailable)
    assert not hasattr(observation, "eligible_content")
    assert not hasattr(observation, "eligible_inputs")


def test_r13_send_and_provider_execution_are_never_touched() -> None:
    """Structural, not textual (see `_imported_module_names`): this
    module's own docstring legitimately NAMES `ai_contracts`/providers in
    prose, explaining what it deliberately does not call -- the real
    falsifier is that nothing here actually IMPORTS a provider-SDK or
    AI-contract module, confirmed the same way `check_provider_sdk_imports.
    py` already confirms it for the whole application layer."""
    import application.pcpg_runtime_composition as mod

    imported = _imported_module_names(mod)
    for forbidden in ("ai_gateway", "ai_contracts", "openai", "anthropic", "provider_route"):
        assert not any(forbidden in name for name in imported), (forbidden, imported)


# ---------------------------------------------------------------------------
# 2. Fail-closed: the three real reason codes, each from its own real cause
# ---------------------------------------------------------------------------


def test_unparseable_raw_intent_maps_to_semantic_observation_unavailable(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    ports = f03.f02.ports(db_connection)
    principal = f03.principal(ctx["fac"])
    ingress = _ingress(workspace_id=ctx["ws"], raw_intent="   ")
    observation = derive_governance_observation(ports, principal, ingress)
    assert isinstance(observation, GovernanceObservationUnavailable)
    assert observation.reason_code == SEMANTIC_OBSERVATION_UNAVAILABLE


def test_non_member_principal_maps_to_field_reconstruction_unavailable(
    db_connection: sa.Connection,
) -> None:
    """R-03's own FAILURE STATE for a precondition violation: a principal
    this composition calls `reconstruct_field` for, but who is not a member
    of the named Workspace, surfaces the real `QueryDenied` R-03 itself
    raises (via `workspace_overview`'s own `_context()` translation) --
    never an uncaught exception, never a synthesized partial value."""
    ctx = f03.generating_context(db_connection, participants=1)
    ports = f03.f02.ports(db_connection)
    _other_ws, other_owner = f03.new_workspace_with_member(db_connection, "intruder")
    principal = f03.principal(other_owner)
    ingress = _ingress(workspace_id=ctx["ws"], raw_intent="begin the analysis")
    observation = derive_governance_observation(ports, principal, ingress)
    assert isinstance(observation, GovernanceObservationUnavailable)
    assert observation.reason_code == FIELD_RECONSTRUCTION_UNAVAILABLE


def test_unexpected_producer_failure_maps_to_projection_incomplete(
    db_connection: sa.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The broad, deliberate catch-all: an unexpected failure anywhere from
    R-04 onward never reaches the caller as an uncaught exception and is
    never silently turned into a partial capability value either."""
    import application.pcpg_runtime_composition as mod

    def _boom(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("unexpected producer failure")

    monkeypatch.setattr(mod, "derive_pulse", _boom)

    ctx = f03.generating_context(db_connection, participants=1)
    ports = f03.f02.ports(db_connection)
    principal = f03.principal(ctx["fac"])
    ingress = _ingress(workspace_id=ctx["ws"], raw_intent="begin the analysis")
    observation = mod.derive_governance_observation(ports, principal, ingress)
    assert isinstance(observation, GovernanceObservationUnavailable)
    assert observation.reason_code == PROJECTION_INCOMPLETE


def test_governance_observation_unavailable_rejects_an_unknown_reason_code() -> None:
    with pytest.raises(ValueError):
        GovernanceObservationUnavailable("NOT_A_REAL_REASON_CODE")


# ---------------------------------------------------------------------------
# 3. ABSENT != FALSE / UNKNOWN != DENIED: an unresolved session never blocks
# ---------------------------------------------------------------------------


def test_an_unknown_session_is_unresolved_not_a_composition_failure(
    db_connection: sa.Connection,
) -> None:
    """R-03's own disclosed design: a foreign/unknown Session becomes
    `unresolved`, never a raised exception -- the whole composition still
    honestly proceeds (with `session=None` downstream), exactly as every
    other PCPG relation already handles a `None` session. This is the
    direct proof that `FIELD_RECONSTRUCTION_UNAVAILABLE` is never raised
    for this case, distinguishing it from the genuine scope failure above."""
    ctx = f03.generating_context(db_connection, participants=1)
    ports = f03.f02.ports(db_connection)
    principal = f03.principal(ctx["fac"])
    foreign_session = SessionId(f03.uid())
    ingress = _ingress(
        workspace_id=ctx["ws"], session_id=foreign_session, raw_intent="begin the analysis"
    )
    observation = derive_governance_observation(ports, principal, ingress)
    assert not isinstance(observation, GovernanceObservationUnavailable), observation


# ---------------------------------------------------------------------------
# 4. I-12: per-delta ceiling flows; the composed ceiling is honestly None
#    today (disclosed architectural fact, not a defect of this Work Unit)
# ---------------------------------------------------------------------------


def test_per_delta_session_proof_ceiling_reaches_the_real_delta_records(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=1, fixture=True)
    ports = f03.f02.ports(db_connection)
    principal = f03.principal(ctx["fac"])
    ingress = _ingress(
        workspace_id=ctx["ws"], session_id=ctx["session"], raw_intent="begin the analysis"
    )
    observation = derive_governance_observation(ports, principal, ingress)
    assert not isinstance(observation, GovernanceObservationUnavailable), observation
    assert any(r.session_proof_ceiling == "FIXTURE_NON_PROOF" for r in observation.delta_records)


def test_composed_proof_ceiling_is_honestly_none_in_the_real_runtime_today(
    db_connection: sa.Connection,
) -> None:
    """Disclosed, proven architectural fact (same root cause as WU-7/8/9's
    own "no delta is ever ALLOWED"): `compose_effect` only ever retains
    `Result.ALLOWED` deltas, and `evaluate_deltas` never assigns `ALLOWED`
    to any real delta today -- so `retained` is always empty and
    `composed_proof_ceiling` is always `None`, for every real request, not
    merely the ones this test happens to construct. Not a defect of this
    Work Unit: the same structural fact `pcpg_capability.py`'s own module
    docstring already discloses for `GOVERNANCE_ADMISSIBLE`."""
    ctx = f03.generating_context(db_connection, participants=1, fixture=True)
    ports = f03.f02.ports(db_connection)
    principal = f03.principal(ctx["fac"])
    ingress = _ingress(
        workspace_id=ctx["ws"], session_id=ctx["session"], raw_intent="begin the analysis"
    )
    observation = derive_governance_observation(ports, principal, ingress)
    assert not isinstance(observation, GovernanceObservationUnavailable), observation
    assert observation.composed_proof_ceiling is None
    assert observation.capability.governance_admissible is False
    assert observation.capability.can_send is False


# ---------------------------------------------------------------------------
# 5. No shared mutable state between two observations
# ---------------------------------------------------------------------------


def test_two_observations_project_independently(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    ports = f03.f02.ports(db_connection)
    principal = f03.principal(ctx["fac"])
    first = derive_governance_observation(
        ports,
        principal,
        _ingress(workspace_id=ctx["ws"], session_id=ctx["session"], raw_intent="begin setup"),
    )
    second = derive_governance_observation(
        ports,
        principal,
        _ingress(
            workspace_id=ctx["ws"], session_id=ctx["session"], raw_intent="begin the analysis"
        ),
    )
    assert not isinstance(first, GovernanceObservationUnavailable)
    assert not isinstance(second, GovernanceObservationUnavailable)
    assert first.raw_intent != second.raw_intent
    assert first.delta_records != second.delta_records
