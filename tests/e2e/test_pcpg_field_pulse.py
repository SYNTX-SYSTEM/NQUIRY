"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — R-04: Field Pulse (Architecture 26).

Source: `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md`
R-04: "PRODUCER: a derived view over existing records... INPUT: the Field
snapshot... OUTPUT: Pulse elements, each citing its canonical source."
`04_OBSERVATION_RESULT.md` §3 lists 10 elements. I-07 (`01_INVARIANTS.md`):
"Pulse introduces no status, lifecycle, flag or counter of its own" --
every element below is a direct read of a real, already-proven producer.

SCOPE OF THIS WORK UNIT (disclosed, not silently narrowed; "do not
redesign R-04" honored by building only what a REAL producer already
supports, inventing no new persistence surface)
------------------------------------------------------------------------
Covered, each with a real, cited, already-existing producer:
- ACTIVE_TRANSITIONS / PENDING_AUTHORITY_REQUIREMENTS: `session_position.
  actions`'s own `relevant`/`available`/`reasonCode` fields (R-04's own
  citation, verbatim) -- already carried by R-03's `SessionContext`.
- IN_FLIGHT_OPERATIONS: `application.reflection_proof._unresolved` --
  00_FIELD.md §7's own named home for this exact Pulse element.
- STALE_SOURCES: `application.frozen_set.verify_frozen_set` (F03) --
  the same function `session_position` itself already calls.
- EXTERNAL_DEPENDENCIES: the same static, cited fact R-03 already
  materializes (`00_FIELD.md` §3: "none exist in NQUIRY today").
- UNRESOLVED_ELIGIBILITY: a static, cited fact -- GAP-11-006 (data-class
  classifier) and HARD-DEP-002/GAP-08-008 (provider route) are ALL
  unconditionally OPEN today, so eligibility is unconditionally
  unresolved for every observation, not something to compute per call.
- GOVERNANCE_BLOCKERS: HA-23 (`HUMAN_AUTHORITY_QUEUE.md`, confirmed
  OPEN), the RED text's own worked example ("HA-23 for leaving
  INVESTIGATION"), cited when the named Session is currently in
  INVESTIGATION -- the one concrete case this Field's own text names,
  not a general Case-3 scanner invented here.

Explicitly NOT covered (no real listing producer exists in this
codebase today; inventing one would be redesigning R-04's own scope,
not deriving its minimum coherent implementation from what exists):
PENDING_HUMAN_DECISIONS (no `DecisionRepository.list_*` method exists),
INDETERMINATE_CONSEQUENCES beyond what `_unresolved` already covers (no
`recovery_repository` listing method exists), RECENT_AUTHORITY_CHANGE
(no generic "source produced at version X" comparison exists outside a
specific delta's own context, which R-04 does not have -- R-06's job).
Each is a real name in `Pulse.unresolved`, never silently dropped.
"""

from __future__ import annotations

import ast
import pathlib
from datetime import datetime, timezone

import f03_support as f03
import sqlalchemy as sa
import test_http_f02 as http_f02
import test_pfc_b4_impact_chain as b4
from application.pcpg_field_pulse import (
    GOVERNANCE_BLOCKER_HA23,
    UNRESOLVED_ELIGIBILITY_REASONS,
    derive_pulse,
)
from application.pcpg_field_snapshot import reconstruct_field

db_app = http_f02.db_app


def _now() -> datetime:
    return datetime(2026, 9, 30, 12, 0, tzinfo=timezone.utc)


def _pulse_for(db: sa.Connection, ctx: dict, actor_key: str = "fac"):
    ports = f03.f02.ports(db)
    principal = f03.principal(ctx[actor_key])
    snapshot = reconstruct_field(
        ports, principal, workspace_id=ctx["ws"], session_id=ctx["session"], now=_now()
    )
    pulse = derive_pulse(ports, snapshot, workspace_id=ctx["ws"], session_id=ctx["session"])
    return snapshot, pulse


# ---------------------------------------------------------------------------
# ACTIVE_TRANSITIONS / PENDING_AUTHORITY_REQUIREMENTS
# ---------------------------------------------------------------------------


def test_active_transitions_equals_the_relevant_subset_of_session_actions(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    snapshot, pulse = _pulse_for(db_connection, ctx)
    assert snapshot.session is not None
    real_relevant = {k: v for k, v in snapshot.session.actions.items() if v["relevant"]}
    assert dict(pulse.active_transitions) == real_relevant
    assert real_relevant  # the fixture must genuinely exercise a non-empty case


def test_pending_authority_requirements_equals_unavailable_relevant_reason_codes(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    # Ravi is a participant with no SESSION_CONTROL_RIGHT -- his relevant
    # actions are mostly unavailable, giving real reason codes to compare.
    snapshot, pulse = _pulse_for(db_connection, ctx, actor_key="outsider")
    assert snapshot.session is not None
    expected = tuple(
        sorted(
            v["reasonCode"]
            for v in snapshot.session.actions.values()
            if v["relevant"] and not v["available"] and v["reasonCode"]
        )
    )
    assert tuple(sorted(pulse.pending_authority_requirements)) == expected
    assert expected  # the fixture must genuinely exercise a non-empty case


def test_no_session_named_gives_no_active_transitions_or_requirements(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    ports = f03.f02.ports(db_connection)
    principal = f03.principal(ctx["fac"])
    snapshot = reconstruct_field(
        ports, principal, workspace_id=ctx["ws"], session_id=None, now=_now()
    )
    pulse = derive_pulse(ports, snapshot, workspace_id=ctx["ws"], session_id=None)
    assert pulse.active_transitions == {}
    assert pulse.pending_authority_requirements == ()


# ---------------------------------------------------------------------------
# IN_FLIGHT_OPERATIONS
# ---------------------------------------------------------------------------


def test_in_flight_operations_is_false_with_no_analysis_yet_requested(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    _, pulse = _pulse_for(db_connection, ctx)
    assert pulse.in_flight_operations is False


def test_in_flight_operations_equals_the_real_unresolved_function(
    db_connection: sa.Connection,
) -> None:
    """P-15: no element exists the producer would not report -- proven by
    direct equality against `reflection_proof._unresolved` itself."""
    from application.reflection_proof import _unresolved

    ctx = f03.generating_context(db_connection, participants=1)
    ports = f03.f02.ports(db_connection)
    session = ports.sessions.get(ctx["session"])
    real = _unresolved(ports, session)
    _, pulse = _pulse_for(db_connection, ctx)
    assert pulse.in_flight_operations == real


def test_in_flight_operations_is_true_for_an_authorized_not_yet_executed_analysis(
    db_connection: sa.Connection,
) -> None:
    """The genuinely non-trivial case (mirrors `fixtures/NQUIRY_SESSION_
    AUTHORITY.txt`'s own 'Session C' variant: 'an AIOP-001 authorization
    exists without an executed generation'). Without this case, a mutation
    that hardcodes `in_flight_operations = False` would never be caught,
    since every other fixture in this suite happens to also be False."""
    import f04_support as f04

    ctx = f04.analysis_context(db_connection)  # oa1 authorized, never run
    ports = f04.f02.ports(db_connection)
    principal = f04.f03.principal(ctx["fac"])
    snapshot = reconstruct_field(
        ports, principal, workspace_id=ctx["ws"], session_id=ctx["session"], now=_now()
    )
    pulse = derive_pulse(ports, snapshot, workspace_id=ctx["ws"], session_id=ctx["session"])
    assert pulse.in_flight_operations is True


# ---------------------------------------------------------------------------
# STALE_SOURCES
# ---------------------------------------------------------------------------


def test_stale_sources_is_empty_with_no_completed_burst(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    _, pulse = _pulse_for(db_connection, ctx)
    assert pulse.stale_sources == ()


# ---------------------------------------------------------------------------
# Static, cited, Field-wide facts
# ---------------------------------------------------------------------------


def test_external_dependencies_is_empty_matching_00_field_section_3(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    _, pulse = _pulse_for(db_connection, ctx)
    assert pulse.external_dependencies == frozenset()


def test_unresolved_eligibility_is_always_true_today_citing_the_real_open_gaps(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    _, pulse = _pulse_for(db_connection, ctx)
    assert pulse.unresolved_eligibility is True
    assert pulse.unresolved_eligibility_reasons == UNRESOLVED_ELIGIBILITY_REASONS
    assert "GAP-11-006" in UNRESOLVED_ELIGIBILITY_REASONS


# ---------------------------------------------------------------------------
# GOVERNANCE_BLOCKERS (HA-23)
# ---------------------------------------------------------------------------


def test_governance_blockers_is_empty_outside_investigation(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    _, pulse = _pulse_for(db_connection, ctx)
    assert pulse.governance_blockers == ()


def test_governance_blockers_cites_ha23_while_in_investigation(
    db_app: sa.Connection,
) -> None:
    """Drives a real Fixture Session to INVESTIGATION via the already-
    proven WU-PFC-B4/B5 product path (selection -> complete ImpactChain ->
    BEGIN_INVESTIGATION), then reads Pulse over the SAME connection with
    `reconstruct_field`/`derive_pulse` directly (both real `sa.Connection`
    -backed, not HTTP)."""
    ctx = b4._reach(db_app)
    b4._create(db_app, ctx)
    for level in range(1, 6):
        assert b4._append(db_app, ctx, level).json()["kind"] == "committed"
    body = {"expectedVersion": b4._version(db_app, ctx)}
    assert b4._post(db_app, ctx, "transitions/begin-investigation", body).json()["kind"] == (
        "committed"
    )

    ports = f03.f02.ports(db_app)
    principal = f03.principal(ctx["fac"])
    snapshot = reconstruct_field(
        ports, principal, workspace_id=ctx["ws"], session_id=ctx["session"], now=_now()
    )
    pulse = derive_pulse(ports, snapshot, workspace_id=ctx["ws"], session_id=ctx["session"])
    assert snapshot.session is not None
    assert snapshot.session.state == "INVESTIGATION"
    assert pulse.governance_blockers == (GOVERNANCE_BLOCKER_HA23,)


# ---------------------------------------------------------------------------
# Disclosed, not-yet-covered elements
# ---------------------------------------------------------------------------


def test_unresolved_names_the_three_not_yet_covered_elements(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    _, pulse = _pulse_for(db_connection, ctx)
    assert set(pulse.unresolved) == {
        "PENDING_HUMAN_DECISIONS",
        "INDETERMINATE_CONSEQUENCES",
        "RECENT_AUTHORITY_CHANGE",
    }


# ---------------------------------------------------------------------------
# I-07: Pulse is a view, never a new state
# ---------------------------------------------------------------------------


def test_pulse_introduces_no_status_or_counter_of_its_own() -> None:
    """Static shape proof: `Pulse` carries no field that is not a direct
    reading of a real producer or a disclosed absence -- no id, no
    timestamp, no version counter of its own (I-07)."""
    import dataclasses

    from application.pcpg_field_pulse import Pulse

    field_names = {f.name for f in dataclasses.fields(Pulse)}
    forbidden = {"id", "created_at", "updated_at", "version", "sequence"}
    assert not (field_names & forbidden)


def test_the_module_touches_no_provider_and_makes_no_egress() -> None:
    root = pathlib.Path(__file__).resolve().parents[2] / "packages" / "application"
    source = (root / "pcpg_field_pulse.py").read_text()
    tree = ast.parse(source)
    forbidden_imports = ("ai_gateway.adapters", "anthropic", "openai")
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            assert not any(mod.startswith(f) for f in forbidden_imports), mod
    forbidden_calls = {"generate", "invoke", "send"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            assert node.func.attr not in forbidden_calls, node.func.attr


def test_pulse_is_identical_for_two_calls_at_the_same_basis(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    ports = f03.f02.ports(db_connection)
    principal = f03.principal(ctx["fac"])
    snapshot = reconstruct_field(
        ports, principal, workspace_id=ctx["ws"], session_id=ctx["session"], now=_now()
    )
    first = derive_pulse(ports, snapshot, workspace_id=ctx["ws"], session_id=ctx["session"])
    second = derive_pulse(ports, snapshot, workspace_id=ctx["ws"], session_id=ctx["session"])
    assert first == second
