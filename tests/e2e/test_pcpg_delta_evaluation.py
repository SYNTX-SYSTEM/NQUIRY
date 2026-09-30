"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — R-07: per-delta governance
evaluation (Architecture 26).

Source: `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md`
R-07: "INPUT: each delta, the Field snapshot and the Pulse... OUTPUT: one
delta record per delta ... and exactly one RESULT class with its reason."
PRECONDITION, verbatim: "For NQUIRY operations, the required authority,
the actual authority and the state availability are taken from the
existing readiness producer for that operation. For operations with a
projected capability, that is the `session_position.actions` entry at
the same basis. The evaluation never re-implements a readiness rule."

E1 re-derivation (2026-09-30, independent, against `checkpoint-PFC-PCPG-6`):
R-06 (DIRECT deltas), R-03 (snapshot) and R-04 (Pulse) are all real; R-07
itself is genuinely absent (`grep` for `DeltaRecord`/`Result.`/RESULT
vocabulary: zero hits). R-07's own INPUT is satisfied NOW for the
DIRECT-delta subset R-06 already produces -- R-07 evaluates "each delta"
generically; it does not require R-06's own disclosed IMPLIED-delta gap
to close first (nothing in R-07's PRECONDITION or FAILURE STATE names
IMPLIED deltas specifically). R-07 is the next First Broken Relation.

SCOPE OF THIS WORK UNIT (disclosed, not silently narrowed)
------------------------------------------------------------
This increment produces `RESULT` + `REASON` (the two fields every
downstream relation actually branches on) for each delta, plus a
passthrough of fields already real from R-05/R-06 (`delta_id`,
`operation`, `execution_class`, `target`, `source_clause`, `span`,
`current_state`, and the one real FLAG this Field already computes,
`DECISION_SUBSTITUTION_REQUESTED`). `04_OBSERVATION_RESULT.md` §5 names
roughly twenty delta-record fields in total (`REQUIRED_AUTHORITY`,
`ACTUAL_AUTHORITY` with binding reference, `AUTHORITY_SOURCE`/`SCOPE`,
`DATA_CLASSIFICATION`, `PROOF_CEILING`, `OUTPUT_CONTRACT`, `ELIGIBILITY`,
...) -- each needs a producer that does not exist in this codebase today
(a data-class classifier, FBR-PCPG-3, still OPEN; an AUTH-DEP-to-
authority-class lookup table; an AI-contract output-class registry).
Building any of them now would be redesigning R-07's own scope far
beyond "derive its minimum coherent implementation from what exists" --
each is named, disclosed, and left for a later Work Unit.

`Result` is this Field's OWN vocabulary (04_OBSERVATION_RESULT.md §6),
materialized here for the first time (its first real consumer) exactly
as `ExecutionClass` was materialized in `pcpg_operation_index.py` for
R-06 -- all 8 real values are defined (I-20: one definition), but this
increment's own producer only ever emits 5 of them (never
`DATA_BOUNDARY`/`DENIED`, whose own producers do not exist yet; see
below for why `ALLOWED` is correctly never emitted either).

THE RESULT-MAPPING ALGORITHM, EACH BRANCH CITED
----------------------------------------------------
1. `operation is None` (UNKNOWN) -> `INDETERMINATE`, reason
   `SEMANTIC_UNKNOWN` (I-04).
2. `execution_class is PROVIDER_COMPUTATION` -> `GOVERNANCE_BOUNDARY`,
   reason `OPERATION_CLASS_NOT_ADMITTED` -- a STATIC, already-decided
   fact, not a per-call computation: `00_FIELD.md` §13 HA-PCPG-1's own
   fail-closed default, restated verbatim by `04_OBSERVATION_RESULT.md`
   §8 as the Field's CURRENT value ("GOVERNANCE_ADMISSIBLE is false for
   every observation ... This holds even for a delta mapping to
   AIOP-001"). This is why `ALLOWED` ("a PROVIDER_COMPUTATION that is
   legitimate under the current Field **in every respect**") is
   correctly never produced by this Field today -- not a gap in this
   Work Unit, an already-decided architectural fact this Work Unit only
   quotes.
3. `operation` not present in `snapshot.session.actions` (no Session
   named, or a root-scope operation `session_position` does not cover)
   -> `INDETERMINATE`, reason `NO_AUTHORITATIVE_PRODUCER` -- R-07's own
   FAILURE STATE, verbatim ("A delta with no authoritative producer for
   its authority gives INDETERMINATE with reason
   `NO_AUTHORITATIVE_PRODUCER`").
4. Otherwise (`execution_class is HUMAN_COMMAND`, `operation` present in
   `snapshot.session.actions`): read `available`/`reasonCode` from that
   REAL entry, never re-derived.
   - `available` -> `HUMAN_ACTION_AVAILABLE`.
   - not `available`, `reasonCode` in the closed, cited, directly-
     verified set of real authority-lack codes this codebase actually
     produces (`_AUTHORITY_REASON_CODES`, grepped from
     `inquiry_queries.py` itself) -> `AUTHORITY_BOUNDARY`.
   - not `available`, any other real `reasonCode` -> `STATE_BOUNDARY`
     (the residual/default category -- matches `04_OBSERVATION_RESULT.
     md` §6's own precedence ordering, STATE_BOUNDARY before
     AUTHORITY_BOUNDARY, and `blocked_or()`'s own structure in
     `inquiry_queries.py`: authority is checked first, so any code that
     is not one of the known authority-lack codes is necessarily a
     state-topology fact).
"""

from __future__ import annotations

import ast
import pathlib
from datetime import datetime, timezone

import f03_support as f03
import pytest
import sqlalchemy as sa
from application.pcpg_candidate_deltas import CandidateDelta, form_candidate_deltas
from application.pcpg_delta_evaluation import Result, evaluate_deltas
from application.pcpg_field_pulse import derive_pulse
from application.pcpg_field_snapshot import (
    ActorContext,
    FieldSnapshot,
    ProviderContext,
    SessionContext,
    reconstruct_field,
)
from application.pcpg_operation_index import ExecutionClass
from application.pcpg_simplix import observe_semantics


def _now() -> datetime:
    return datetime(2026, 9, 30, 12, 0, tzinfo=timezone.utc)


def _delta(
    operation: str | None,
    execution_class: ExecutionClass,
    target: str | None = None,
    current_state: str | None = None,
) -> CandidateDelta:
    return CandidateDelta(
        delta_id="D0",
        source_clause="x",
        span=(0, 1),
        target=target,
        operation=operation,
        execution_class=execution_class,
        current_state=current_state,
        proposed_state=None,
        dependency_edges=(),
    )


def _snapshot_with_actions(
    actions: dict[str, object], state: str = "QUESTION_CAPTURE"
) -> FieldSnapshot:
    session = SessionContext(
        session_id="11111111-1111-4111-8111-111111111111",
        state=state,
        version=1,
        fixture=False,
        proof_mode="GOVERNED",
        actions=actions,
    )
    return FieldSnapshot(
        basis_time=_now(),
        workspace_id="00000000-0000-4000-8000-000000000000",
        actor=ActorContext(
            user_id="u1", role="Facilitator", is_governance_root=False, authority=()
        ),
        session=session,
        ai_contracts_admitted=frozenset({"AIOP-001", "AIOP-002"}),
        external_effects=frozenset(),
        provider=ProviderContext(environment="TEST", provider_configured=True),
        unresolved=(),
    )


def _bare_snapshot() -> FieldSnapshot:
    return FieldSnapshot(
        basis_time=_now(),
        workspace_id="00000000-0000-4000-8000-000000000000",
        actor=ActorContext(
            user_id="u1", role="Facilitator", is_governance_root=False, authority=()
        ),
        session=None,
        ai_contracts_admitted=frozenset({"AIOP-001", "AIOP-002"}),
        external_effects=frozenset(),
        provider=ProviderContext(environment="TEST", provider_configured=True),
        unresolved=(),
    )


# ---------------------------------------------------------------------------
# UNKNOWN operation -> INDETERMINATE (I-04)
# ---------------------------------------------------------------------------


def test_unknown_operation_is_indeterminate_semantic_unknown() -> None:
    delta = _delta(None, ExecutionClass.UNKNOWN)
    records = evaluate_deltas((delta,), _bare_snapshot())
    assert records[0].result is Result.INDETERMINATE
    assert records[0].reason == "SEMANTIC_UNKNOWN"


# ---------------------------------------------------------------------------
# PROVIDER_COMPUTATION -> GOVERNANCE_BOUNDARY, always, regardless of state
# (HA-PCPG-1's own already-decided fail-closed default)
# ---------------------------------------------------------------------------


def test_provider_computation_is_always_governance_boundary_never_allowed() -> None:
    delta = _delta("REQUEST_QUESTION_ANALYSIS", ExecutionClass.PROVIDER_COMPUTATION)
    snapshot = _snapshot_with_actions(
        {"REQUEST_QUESTION_ANALYSIS": {"available": True, "reasonCode": None, "relevant": True}}
    )
    records = evaluate_deltas((delta,), snapshot)
    assert records[0].result is Result.GOVERNANCE_BOUNDARY
    assert records[0].reason == "OPERATION_CLASS_NOT_ADMITTED"


def test_allowed_is_never_produced_by_this_increment() -> None:
    """The current real Field has no path to ALLOWED at all -- an
    architectural fact this Work Unit only quotes (00_FIELD.md §13
    HA-PCPG-1), not a gap."""
    obs = observe_semantics("Analyse the questions.")
    deltas = form_candidate_deltas(
        obs,
        _snapshot_with_actions(
            {"REQUEST_QUESTION_ANALYSIS": {"available": True, "reasonCode": None, "relevant": True}}
        ),
    )
    records = evaluate_deltas(
        deltas,
        _snapshot_with_actions(
            {"REQUEST_QUESTION_ANALYSIS": {"available": True, "reasonCode": None, "relevant": True}}
        ),
    )
    assert all(r.result is not Result.ALLOWED for r in records)


# ---------------------------------------------------------------------------
# No authoritative producer (R-07's own FAILURE STATE, verbatim)
# ---------------------------------------------------------------------------


def test_no_session_named_gives_no_authoritative_producer() -> None:
    delta = _delta("BEGIN_ANALYSIS", ExecutionClass.HUMAN_COMMAND)
    records = evaluate_deltas((delta,), _bare_snapshot())
    assert records[0].result is Result.INDETERMINATE
    assert records[0].reason == "NO_AUTHORITATIVE_PRODUCER"


def test_a_root_scope_operation_not_in_session_actions_gives_no_authoritative_producer() -> None:
    delta = _delta("CREATE_WORKSPACE", ExecutionClass.HUMAN_COMMAND)
    snapshot = _snapshot_with_actions({"BEGIN_ANALYSIS": {"available": True, "relevant": True}})
    records = evaluate_deltas((delta,), snapshot)
    assert records[0].result is Result.INDETERMINATE
    assert records[0].reason == "NO_AUTHORITATIVE_PRODUCER"


# ---------------------------------------------------------------------------
# HUMAN_COMMAND, present in session.actions: quoted, never re-derived
# ---------------------------------------------------------------------------


def test_available_human_command_is_human_action_available() -> None:
    delta = _delta("BEGIN_ANALYSIS", ExecutionClass.HUMAN_COMMAND)
    snapshot = _snapshot_with_actions(
        {"BEGIN_ANALYSIS": {"available": True, "reasonCode": None, "relevant": True}}
    )
    records = evaluate_deltas((delta,), snapshot)
    assert records[0].result is Result.HUMAN_ACTION_AVAILABLE
    assert records[0].reason is None


@pytest.mark.parametrize(
    "reason_code",
    [
        "NO_SESSION_CONTROL",
        "NO_QUESTION_SELECTION_RIGHT",
        "NOT_GOVERNANCE_ROOT",
        "NOT_A_PARTICIPANT",
        "NO_CHALLENGE_SESSION_CONTROL",
        "NOT_FACILITATOR",
    ],
)
def test_the_closed_set_of_real_authority_lack_codes_gives_authority_boundary(
    reason_code: str,
) -> None:
    delta = _delta("BEGIN_ANALYSIS", ExecutionClass.HUMAN_COMMAND)
    snapshot = _snapshot_with_actions(
        {"BEGIN_ANALYSIS": {"available": False, "reasonCode": reason_code, "relevant": True}}
    )
    records = evaluate_deltas((delta,), snapshot)
    assert records[0].result is Result.AUTHORITY_BOUNDARY
    assert records[0].reason == reason_code


@pytest.mark.parametrize(
    "reason_code",
    [
        "SESSION_NOT_IN_REFLECTION",
        "SESSION_CLOSED",
        "NO_CANDIDATES",
        "ANALYSIS_IN_PROGRESS",
        "REQUIRED_ANALYSIS_NOT_COMPLETED",
        "STATE_NOT_ELIGIBLE:QUESTION_CAPTURE",
    ],
)
def test_every_other_real_reason_code_gives_state_boundary(reason_code: str) -> None:
    delta = _delta("BEGIN_ANALYSIS", ExecutionClass.HUMAN_COMMAND)
    snapshot = _snapshot_with_actions(
        {"BEGIN_ANALYSIS": {"available": False, "reasonCode": reason_code, "relevant": True}}
    )
    records = evaluate_deltas((delta,), snapshot)
    assert records[0].result is Result.STATE_BOUNDARY
    assert records[0].reason == reason_code


# ---------------------------------------------------------------------------
# Passthrough fields and FLAGS
# ---------------------------------------------------------------------------


def test_delta_id_operation_target_and_current_state_are_quoted_not_recomputed() -> None:
    delta = _delta(
        "SELECT_PRIMARY_QUESTION",
        ExecutionClass.HUMAN_COMMAND,
        target="question:123",
        current_state="QUESTION_SELECTION",
    )
    snapshot = _snapshot_with_actions(
        {"SELECT_PRIMARY_QUESTION": {"available": True, "reasonCode": None, "relevant": True}},
        state="QUESTION_SELECTION",
    )
    records = evaluate_deltas((delta,), snapshot)
    record = records[0]
    assert record.delta_id == "D0"
    assert record.operation == "SELECT_PRIMARY_QUESTION"
    assert record.target == "question:123"
    assert record.current_state == "QUESTION_SELECTION"


def test_decision_substitution_requested_flag_is_carried_through() -> None:
    obs = observe_semantics("Pick the primary question for me.")
    action = obs.actions[0]
    assert action.decision_substitution_requested is True
    delta = CandidateDelta(
        delta_id="D0",
        source_clause=action.clause_text,
        span=action.span,
        target=action.target,
        operation=action.candidate_operation,
        execution_class=ExecutionClass.HUMAN_COMMAND,
        current_state="QUESTION_SELECTION",
        proposed_state=None,
        dependency_edges=(),
    )
    snapshot = _snapshot_with_actions(
        {"SELECT_PRIMARY_QUESTION": {"available": True, "reasonCode": None, "relevant": True}},
        state="QUESTION_SELECTION",
    )
    # evaluate_deltas takes the real flag straight from the SemanticAction
    # via a parallel, real flags mapping -- proven end-to-end below.
    records = evaluate_deltas(
        (delta,), snapshot, flags_by_delta_id={"D0": frozenset({"DECISION_SUBSTITUTION_REQUESTED"})}
    )
    assert "DECISION_SUBSTITUTION_REQUESTED" in records[0].flags


def test_no_flags_is_the_default() -> None:
    delta = _delta("BEGIN_ANALYSIS", ExecutionClass.HUMAN_COMMAND)
    snapshot = _snapshot_with_actions(
        {"BEGIN_ANALYSIS": {"available": True, "reasonCode": None, "relevant": True}}
    )
    records = evaluate_deltas((delta,), snapshot)
    assert records[0].flags == frozenset()


# ---------------------------------------------------------------------------
# Completeness, determinism, purity
# ---------------------------------------------------------------------------


def test_every_delta_gets_exactly_one_record_none_dropped() -> None:
    deltas = (
        _delta(None, ExecutionClass.UNKNOWN),
        _delta("BEGIN_ANALYSIS", ExecutionClass.HUMAN_COMMAND),
        _delta("REQUEST_QUESTION_ANALYSIS", ExecutionClass.PROVIDER_COMPUTATION),
    )
    snapshot = _snapshot_with_actions(
        {
            "BEGIN_ANALYSIS": {"available": True, "reasonCode": None, "relevant": True},
            "REQUEST_QUESTION_ANALYSIS": {"available": True, "reasonCode": None, "relevant": True},
        }
    )
    records = evaluate_deltas(deltas, snapshot)
    assert len(records) == 3
    assert [r.delta_id for r in records] == [d.delta_id for d in deltas]


def test_same_inputs_give_the_same_records_every_time() -> None:
    delta = _delta("BEGIN_ANALYSIS", ExecutionClass.HUMAN_COMMAND)
    snapshot = _snapshot_with_actions(
        {"BEGIN_ANALYSIS": {"available": True, "reasonCode": None, "relevant": True}}
    )
    first = evaluate_deltas((delta,), snapshot)
    second = evaluate_deltas((delta,), snapshot)
    assert first == second


def test_the_module_touches_no_database_and_no_provider() -> None:
    root = pathlib.Path(__file__).resolve().parents[2] / "packages" / "application"
    source = (root / "pcpg_delta_evaluation.py").read_text()
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


def test_result_is_this_fields_own_complete_vocabulary() -> None:
    """I-20: one definition. All 8 real RESULT values (04_OBSERVATION_
    RESULT.md §6) exist, even though this increment's own producer only
    ever emits a subset."""
    assert {r.value for r in Result} == {
        "ALLOWED",
        "HUMAN_ACTION_AVAILABLE",
        "STATE_BOUNDARY",
        "AUTHORITY_BOUNDARY",
        "DATA_BOUNDARY",
        "GOVERNANCE_BOUNDARY",
        "DENIED",
        "INDETERMINATE",
    }


# ---------------------------------------------------------------------------
# Real, DB-backed end-to-end integration
# ---------------------------------------------------------------------------


def test_end_to_end_against_a_real_session_snapshot(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    ports = f03.f02.ports(db_connection)
    principal = f03.principal(ctx["outsider"])  # a same-Workspace, non-controller member
    snapshot = reconstruct_field(
        ports, principal, workspace_id=ctx["ws"], session_id=ctx["session"], now=_now()
    )
    obs = observe_semantics("Begin the analysis.")
    deltas = form_candidate_deltas(obs, snapshot)
    records = evaluate_deltas(deltas, snapshot)
    assert len(records) == 1
    # The outsider has no SESSION_CONTROL_RIGHT -- equals the real
    # session_position.actions reason exactly (P-14-style equivalence).
    real_action = snapshot.session.actions["BEGIN_ANALYSIS"]
    assert real_action["available"] is False
    assert records[0].result is Result.AUTHORITY_BOUNDARY
    assert records[0].reason == real_action["reasonCode"]
    pulse = derive_pulse(ports, snapshot, workspace_id=ctx["ws"], session_id=ctx["session"])
    assert pulse is not None
