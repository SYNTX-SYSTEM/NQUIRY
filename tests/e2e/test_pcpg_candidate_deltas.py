"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — R-06: candidate delta formation
(Architecture 26).

Source: `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md`
R-06: "PRODUCER: the governance evaluation (stratum 3), from R-05 and the
operation index... INPUT: the semantic observation and the Field
snapshot... OUTPUT: the ordered candidate deltas." (R-06's own prose, not
the header diagram's more compressed drawing — see `WU-PFC-PCPG-4.md` §0's
SFE correction: R-06 does not consume Pulse.)

E1 re-derivation (2026-09-30, independent, against `checkpoint-PFC-PCPG-5`):
R-03 and R-05 -- R-06's own two prerequisites -- are both real
(`pcpg_field_snapshot.py`, `pcpg_simplix.py`); R-06 itself is genuinely
absent (`grep` for `CandidateDelta`/`candidate_delta`/`form_candidate`:
zero hits). No sibling ambiguity: closing R-04 did not unblock anything
R-06 itself does not already gate. R-06 is the next First Broken Relation.

SCOPE OF THIS WORK UNIT (disclosed, not silently narrowed)
------------------------------------------------------------
This increment covers R-06 for DIRECT deltas only: one candidate delta
per REQUESTED-modality semantic action, formed straight from R-05's own
output plus the real, already-closed `pcpg_operation_index`. It does
NOT cover IMPLIED intermediate deltas -- R-06's own PRECONDITION example
("an order requires an approval... on a Session already in ANALYSIS no
BEGIN_ANALYSIS delta is implied") needs a canonical "operation X requires
canonical state/relation Y, satisfied or not" index that does not exist
anywhere in this codebase today. Building one now would be a second,
separate, large relation of its own -- not this increment's minimum
coherent delta. Every `CandidateDelta` below is DIRECT (never IMPLIED);
`dependency_edges` is always empty and `proposed_state` is always `None`
in this increment, both disclosed, neither fabricated.

Only REQUESTED-modality actions form a delta (R-05's own PROOF: "Negated,
hypothetical and prohibited actions never become requested actions" --
R-06's PRECONDITION "every requested action yields a delta" is read
literally: PROHIBITED/HYPOTHETICAL/CONDITIONAL/ASSERTED actions form no
delta at all, matching `fixtures/UNKNOWN_INTENT.txt` U5's own expectation
("ORDER is NOT a requested delta") exactly).
"""

from __future__ import annotations

import ast
import pathlib
from datetime import datetime, timezone

import f03_support as f03
import pytest
import sqlalchemy as sa
from application.pcpg_candidate_deltas import CandidateDelta, form_candidate_deltas
from application.pcpg_field_pulse import derive_pulse
from application.pcpg_field_snapshot import (
    ActorContext,
    FieldSnapshot,
    ProviderContext,
    SessionContext,
    reconstruct_field,
)
from application.pcpg_operation_index import ExecutionClass, operation_index
from application.pcpg_simplix import Modality, observe_semantics


def _now() -> datetime:
    return datetime(2026, 9, 30, 12, 0, tzinfo=timezone.utc)


def _bare_snapshot(session_state: str | None = None) -> FieldSnapshot:
    """A minimal, synthetic (not DB-backed) FieldSnapshot -- legitimate
    here because R-06 is a pure function of its two real inputs, neither
    of which requires a live database to construct for a unit-level
    falsifier (the DB-backed end-to-end case is covered separately)."""
    session = None
    if session_state is not None:
        session = SessionContext(
            session_id="11111111-1111-4111-8111-111111111111",
            state=session_state,
            version=1,
            fixture=False,
            proof_mode="GOVERNED",
            actions={},
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


# ---------------------------------------------------------------------------
# Basic formation: one REQUESTED action -> one delta, fields quoted
# ---------------------------------------------------------------------------


def test_a_single_requested_action_forms_one_delta() -> None:
    obs = observe_semantics("Begin the analysis.")
    snapshot = _bare_snapshot(session_state="QUESTION_CAPTURE")
    deltas = form_candidate_deltas(obs, snapshot)
    assert len(deltas) == 1
    delta = deltas[0]
    assert delta.operation == "BEGIN_ANALYSIS"
    assert delta.source_clause == "Begin the analysis"
    assert delta.span == obs.actions[0].span
    assert delta.current_state == "QUESTION_CAPTURE"
    assert delta.proposed_state is None
    assert delta.dependency_edges == ()


def test_multiple_requested_actions_form_one_delta_each_none_dropped() -> None:
    """P-04: the delta set is complete."""
    obs = observe_semantics(
        "Analyse the questions, pick the most important and start the investigation."
    )
    snapshot = _bare_snapshot(session_state="QUESTION_SELECTION")
    deltas = form_candidate_deltas(obs, snapshot)
    assert len(deltas) == 3
    assert [d.operation for d in deltas] == [
        "REQUEST_QUESTION_ANALYSIS",
        "SELECT_PRIMARY_QUESTION",
        "BEGIN_INVESTIGATION",
    ]


def test_delta_ids_are_stable_and_unique_within_one_observation() -> None:
    """A single-delta fixture cannot falsify uniqueness at all (any
    constant id would trivially pass) -- this uses a genuine 3-delta
    observation."""
    obs = observe_semantics(
        "Analyse the questions, pick the most important and start the investigation."
    )
    snapshot = _bare_snapshot(session_state="QUESTION_SELECTION")
    deltas = form_candidate_deltas(obs, snapshot)
    assert len(deltas) == 3
    ids = [d.delta_id for d in deltas]
    assert len(ids) == len(set(ids))


# ---------------------------------------------------------------------------
# Only REQUESTED modality forms a delta
# ---------------------------------------------------------------------------


def test_prohibited_action_forms_no_delta() -> None:
    """U5-equivalent: 'ORDER is NOT a requested delta.'"""
    obs = observe_semantics("Do not grant authority to Ravi.")
    assert obs.actions[0].modality is Modality.PROHIBITED
    deltas = form_candidate_deltas(obs, _bare_snapshot())
    assert deltas == ()


def test_hypothetical_premise_forms_no_delta() -> None:
    """The HYPOTHETICAL premise clause itself never forms a delta -- the
    second clause ("which one would you recommend") is a separate,
    genuinely REQUESTED action (an unrecognized verb in the real NQUIRY
    vocabulary, so it legitimately forms its own UNKNOWN delta; that is
    not this falsifier's own concern)."""
    obs = observe_semantics("If supplier B were approved, which one would you recommend?")
    assert obs.actions[0].modality is Modality.HYPOTHETICAL
    deltas = form_candidate_deltas(obs, _bare_snapshot())
    assert all(d.source_clause != obs.actions[0].clause_text for d in deltas)


def test_conditional_premise_forms_no_delta() -> None:
    obs = observe_semantics("If the burst completes, begin the analysis.")
    assert obs.actions[0].modality is Modality.CONDITIONAL
    deltas = form_candidate_deltas(obs, _bare_snapshot())
    # Only the (non-conditional) second clause, if any, could form a delta;
    # here there is no second clause, so no delta at all is formed.
    assert all(d.source_clause != obs.actions[0].clause_text for d in deltas)


def test_asserted_claim_forms_no_delta() -> None:
    obs = observe_semantics("Maya already approved it.")
    assert obs.actions[0].modality is Modality.ASSERTED
    deltas = form_candidate_deltas(obs, _bare_snapshot())
    assert deltas == ()


def test_a_negated_clause_among_others_still_leaves_the_others_intact() -> None:
    obs = observe_semantics("Begin the analysis, but do not start the investigation.")
    deltas = form_candidate_deltas(obs, _bare_snapshot(session_state="QUESTION_CAPTURE"))
    assert len(deltas) == 1
    assert deltas[0].operation == "BEGIN_ANALYSIS"


# ---------------------------------------------------------------------------
# UNKNOWN operation / target
# ---------------------------------------------------------------------------


def test_unrecognized_verb_forms_an_unknown_delta_never_a_guess() -> None:
    """U1: no catalog operation with certainty -> delta UNKNOWN."""
    obs = observe_semantics("Synergize the questions into a north-star.")
    deltas = form_candidate_deltas(obs, _bare_snapshot())
    assert len(deltas) == 1
    assert deltas[0].operation is None
    assert deltas[0].execution_class is ExecutionClass.UNKNOWN


def test_unresolved_target_is_carried_through_as_unknown() -> None:
    """U2: 'Analyse the second one more deeply.' -- no antecedent."""
    obs = observe_semantics("Analyse the second one more deeply.")
    deltas = form_candidate_deltas(obs, _bare_snapshot())
    assert len(deltas) == 1
    assert deltas[0].target is None


def test_out_of_scope_target_is_carried_through() -> None:
    obs = observe_semantics(
        "Compare our questions with the questions in the other workspace.",
        out_of_scope_references={"the other workspace": "workspace:other"},
    )
    deltas = form_candidate_deltas(obs, _bare_snapshot())
    assert any(d.target == "OUT_OF_SCOPE" for d in deltas)


# ---------------------------------------------------------------------------
# Execution class: quoted from the real, closed catalog -- never re-derived
# ---------------------------------------------------------------------------


_TRIGGER_FOR_OPERATION: dict[str, str] = {
    "BEGIN_SETUP": "Begin setup.",
    "BEGIN_CHALLENGE_CAPTURE": "Begin challenge capture.",
    "PREPARE_BURST": "Prepare the burst.",
    "ADMIT_PARTICIPANT": "Admit participant Ravi to the session.",
    "OPEN_QUESTION_GENERATION": "Open question generation.",
    "GRANT_SESSION_CONTROL": "Grant session control to Ravi.",
    "CAPTURE_QUESTION": "Capture the question.",
    "COMPLETE_BURST": "Complete the burst.",
    "BEGIN_ANALYSIS": "Begin the analysis.",
    "REQUEST_QUESTION_ANALYSIS": "Analyse the questions.",
    "REQUEST_QUESTION_CLUSTERING": "Cluster the questions.",
    "BEGIN_REFLECTION": "Begin reflection.",
    "BEGIN_QUESTION_SELECTION": "Begin question selection.",
    "SELECT_COMPELLING_QUESTION": "Select the compelling question.",
    "SELECT_PRIMARY_QUESTION": "Pick the most important.",
    "CREATE_IMPACT_CHAIN": "Create the impact chain.",
    "APPEND_IMPACT_CHAIN_NODE": "Append to the impact chain.",
    "BEGIN_INVESTIGATION": "Start the investigation.",
    "CREATE_WORKSPACE": "Create a workspace.",
    "CREATE_CHALLENGE": "Create a challenge.",
    "ADD_MEMBER": "Add a member.",
    "GRANT_AUTHORITY_BINDING": "Grant authority to Ravi.",
    "REVOKE_AUTHORITY_BINDING": "Revoke authority from Ravi.",
    "CREATE_SESSION": "Create a session.",
    "OPEN_DECISION_CONSIDERATION": "Open a decision.",
    "RECORD_HUMAN_DECISION": "Record the decision.",
}


def test_every_real_catalog_operation_has_a_trigger_case_in_this_suite() -> None:
    assert set(_TRIGGER_FOR_OPERATION.keys()) == set(operation_index().keys())


@pytest.mark.parametrize("operation_id", sorted(operation_index().keys()))
def test_execution_class_equals_the_real_catalogs_own_value(operation_id: str) -> None:
    """P-14-style equivalence: no parallel classification model (I-20)."""
    raw = _TRIGGER_FOR_OPERATION[operation_id]
    obs = observe_semantics(raw)
    deltas = form_candidate_deltas(obs, _bare_snapshot())
    delta = next(d for d in deltas if d.operation == operation_id)
    assert delta.execution_class == operation_index()[operation_id].execution_class


_MUST_NEVER_BE_PROVIDER_COMPUTATION = frozenset(
    op
    for op, entry in operation_index().items()
    if entry.execution_class is ExecutionClass.HUMAN_COMMAND
)


@pytest.mark.parametrize("operation_id", sorted(_MUST_NEVER_BE_PROVIDER_COMPUTATION))
def test_selection_approval_decision_and_authority_effects_are_never_provider_computation(
    operation_id: str,
) -> None:
    """P-05, exhaustive over the whole real catalog's HUMAN_COMMAND half."""
    raw = _TRIGGER_FOR_OPERATION[operation_id]
    obs = observe_semantics(raw)
    deltas = form_candidate_deltas(obs, _bare_snapshot())
    delta = next(d for d in deltas if d.operation == operation_id)
    assert delta.execution_class is not ExecutionClass.PROVIDER_COMPUTATION


# ---------------------------------------------------------------------------
# current_state / span / purity / determinism
# ---------------------------------------------------------------------------


def test_current_state_is_none_when_no_session_is_named() -> None:
    obs = observe_semantics("Create a session.")
    deltas = form_candidate_deltas(obs, _bare_snapshot(session_state=None))
    assert deltas[0].current_state is None


def test_every_delta_span_is_a_real_substring_of_the_raw_intent() -> None:
    raw = "Begin the analysis, but do not start the investigation."
    obs = observe_semantics(raw)
    deltas = form_candidate_deltas(obs, _bare_snapshot(session_state="QUESTION_CAPTURE"))
    for delta in deltas:
        start, end = delta.span
        assert raw[start:end] == delta.source_clause


def test_an_observation_with_no_requested_actions_forms_no_deltas() -> None:
    obs = observe_semantics("Maya already approved it.")
    assert form_candidate_deltas(obs, _bare_snapshot()) == ()


def test_same_inputs_give_the_same_deltas_every_time() -> None:
    obs = observe_semantics("Begin the analysis.")
    snapshot = _bare_snapshot(session_state="QUESTION_CAPTURE")
    first = form_candidate_deltas(obs, snapshot)
    second = form_candidate_deltas(obs, snapshot)
    assert first == second


def test_the_module_touches_no_database_and_no_provider() -> None:
    """P-01/I-16, static: this is a pure function of its two real inputs --
    no `ports`, `connection` or `db` parameter anywhere, no provider or
    ai_gateway import."""
    root = pathlib.Path(__file__).resolve().parents[2] / "packages" / "application"
    source = (root / "pcpg_candidate_deltas.py").read_text()
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


def test_candidate_delta_is_a_frozen_dataclass() -> None:
    import dataclasses

    assert dataclasses.is_dataclass(CandidateDelta)
    assert CandidateDelta.__dataclass_params__.frozen  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Real, DB-backed end-to-end integration: the NQUIRY_SESSION_AUTHORITY
# fixture's own direct (non-implied) deltas
# ---------------------------------------------------------------------------


def test_end_to_end_against_a_real_session_snapshot(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    ports = f03.f02.ports(db_connection)
    principal = f03.principal(ctx["fac"])
    snapshot = reconstruct_field(
        ports, principal, workspace_id=ctx["ws"], session_id=ctx["session"], now=_now()
    )
    obs = observe_semantics("Begin the analysis.")
    deltas = form_candidate_deltas(obs, snapshot)
    assert len(deltas) == 1
    assert deltas[0].operation == "BEGIN_ANALYSIS"
    assert deltas[0].execution_class is ExecutionClass.HUMAN_COMMAND
    assert deltas[0].current_state == snapshot.session.state
    # derive_pulse (R-04) still composes cleanly alongside R-06's output,
    # proving the two relations do not collide (R-06 does not consume
    # Pulse; R-04 does not consume deltas -- the SFE correction holds).
    pulse = derive_pulse(ports, snapshot, workspace_id=ctx["ws"], session_id=ctx["session"])
    assert pulse is not None
