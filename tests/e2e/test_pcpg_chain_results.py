"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — R-09: chain results: FBR, MLT, NVT,
HAR, PARTIAL (Architecture 26).

Source: `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md`
R-09: "INPUT: the delta records, their dependency order, the composition
result and the Pulse ... OUTPUT: FIRST_BROKEN_RELATION ...
MAXIMUM_LEGITIMATE_TRANSITION ... NEXT_VALID_TRANSITION ...
HUMAN_AUTHORITY_REQUIRED ... PARTIAL."

E1 re-derivation (2026-10-01, independent, against `checkpoint-PFC-PCPG-8`):
R-06 (deltas), R-07 (records), R-08 (composition), R-04 (Pulse) are all
real; `grep` for `FirstBrokenRelation`/`ChainResult`/`derive_chain_result`:
zero hits outside this module. R-09 is the next First Broken Relation.

SCOPE (disclosed; full reasoning in `pcpg_chain_results.py`'s own module
docstring, not repeated here): FBR and MLT are fully covered against
§7.2/§7.3's own definitions. NVT covers only rule 1 of §7.4 (rule 2 has
no producer; disclosed, not guessed). HAR covers only AUTHORITY_BOUNDARY
and GOVERNANCE_BOUNDARY (the two RESULT classes this Field can already
answer honestly); STATE_BOUNDARY/DATA_BOUNDARY/DENIED/INDETERMINATE get
no HAR entry (disclosed). PARTIAL is fully covered. Dependency order is
the given tuple order (R-06's own disclosed DIRECT-delta scope makes
`dependency_edges` always `()`, so no real cycle can occur today).
"""

from __future__ import annotations

import ast
import pathlib

from application.pcpg_chain_results import (
    GOVERNANCE_QUESTION_HA_PCPG_1,
    AuthorityRequirement,
    FirstBrokenRelation,
    derive_chain_result,
)
from application.pcpg_composed_effect import CompositionResult, compose_effect
from application.pcpg_delta_evaluation import DeltaRecord, Result
from application.pcpg_field_pulse import GOVERNANCE_BLOCKER_HA23, Pulse
from application.pcpg_operation_index import ExecutionClass

_EMPTY_PULSE = Pulse(
    active_transitions={},
    pending_authority_requirements=(),
    in_flight_operations=False,
    stale_sources=(),
    external_dependencies=frozenset(),
    unresolved_eligibility=True,
    unresolved_eligibility_reasons=frozenset(),
    governance_blockers=(),
    unresolved=(),
)

_BLOCKED_PULSE = Pulse(
    active_transitions={},
    pending_authority_requirements=(),
    in_flight_operations=False,
    stale_sources=(),
    external_dependencies=frozenset(),
    unresolved_eligibility=True,
    unresolved_eligibility_reasons=frozenset(),
    governance_blockers=(GOVERNANCE_BLOCKER_HA23,),
    unresolved=(),
)


def _record(
    delta_id: str,
    result: Result,
    *,
    reason: str | None = None,
    execution_class: ExecutionClass = ExecutionClass.HUMAN_COMMAND,
    operation: str | None = "BEGIN_ANALYSIS",
) -> DeltaRecord:
    return DeltaRecord(
        delta_id=delta_id,
        operation=operation,
        execution_class=execution_class,
        target=None,
        source_clause="x",
        span=(0, 1),
        current_state=None,
        result=result,
        reason=reason,
        flags=frozenset(),
    )


def _chain(records: tuple[DeltaRecord, ...], pulse: Pulse = _EMPTY_PULSE) -> object:
    effect = compose_effect(records)
    return derive_chain_result(records, effect, pulse)


# ---------------------------------------------------------------------------
# FIRST_BROKEN_RELATION (§7.2)
# ---------------------------------------------------------------------------


def test_no_records_gives_no_broken_relation() -> None:
    result = _chain(())
    assert result.first_broken_relation is None


def test_all_legitimate_records_give_no_broken_relation() -> None:
    records = (
        _record("D0", Result.HUMAN_ACTION_AVAILABLE),
        _record("D1", Result.HUMAN_ACTION_AVAILABLE),
    )
    result = _chain(records)
    assert result.first_broken_relation is None


def test_the_first_non_legitimate_record_is_the_broken_one_with_no_predecessor() -> None:
    broken = _record(
        "D0", Result.GOVERNANCE_BOUNDARY, execution_class=ExecutionClass.PROVIDER_COMPUTATION
    )
    result = _chain((broken,))
    assert result.first_broken_relation == FirstBrokenRelation(predecessor=None, broken=broken)


def test_the_broken_records_predecessor_is_the_immediately_preceding_legitimate_record() -> None:
    legit = _record("D0", Result.HUMAN_ACTION_AVAILABLE)
    broken = _record("D1", Result.AUTHORITY_BOUNDARY, reason="NO_SESSION_CONTROL")
    trailing = _record("D2", Result.STATE_BOUNDARY, reason="ANALYSIS_NOT_READY")
    result = _chain((legit, broken, trailing))
    assert result.first_broken_relation == FirstBrokenRelation(predecessor=legit, broken=broken)


def test_only_the_first_broken_record_is_reported_never_a_later_one() -> None:
    """A second, independently-broken record downstream of the first must
    never surface as the FBR -- FBR is always the FIRST break."""
    first_break = _record("D0", Result.STATE_BOUNDARY, reason="X")
    second_break = _record("D1", Result.AUTHORITY_BOUNDARY, reason="NOT_A_PARTICIPANT")
    result = _chain((first_break, second_break))
    assert result.first_broken_relation.broken is first_break


# ---------------------------------------------------------------------------
# MAXIMUM_LEGITIMATE_TRANSITION (§7.3)
# ---------------------------------------------------------------------------


def test_mlt_is_exactly_the_composed_effects_retained_set() -> None:
    records = (_record("D0", Result.GOVERNANCE_BOUNDARY),)
    effect = compose_effect(records)
    result = derive_chain_result(records, effect, _EMPTY_PULSE)
    assert result.maximum_legitimate_transition == effect.retained


def test_mlt_never_contains_a_human_command_delta_even_when_human_action_available() -> None:
    """§7.3, verbatim: HUMAN_COMMAND deltas never enter the MLT, even
    when HUMAN_ACTION_AVAILABLE. True by construction (R-07 never emits
    ALLOWED for a HUMAN_COMMAND delta) -- proven here, not assumed."""
    records = (
        _record("D0", Result.HUMAN_ACTION_AVAILABLE, execution_class=ExecutionClass.HUMAN_COMMAND),
    )
    result = _chain(records)
    assert result.maximum_legitimate_transition == ()


def test_mlt_retains_a_hand_built_allowed_provider_computation_delta() -> None:
    allowed = _record(
        "D0",
        Result.ALLOWED,
        execution_class=ExecutionClass.PROVIDER_COMPUTATION,
        operation="REQUEST_QUESTION_ANALYSIS",
    )
    result = _chain((allowed,))
    assert result.maximum_legitimate_transition == (allowed,)


# ---------------------------------------------------------------------------
# NEXT_VALID_TRANSITION (§7.4, rule 1 only; disclosed)
# ---------------------------------------------------------------------------


def test_nvt_is_the_first_human_action_available_record_at_or_before_the_fbr() -> None:
    unrelated_later = _record("D0", Result.HUMAN_ACTION_AVAILABLE)
    earliest_available = _record("D1", Result.HUMAN_ACTION_AVAILABLE)
    broken = _record("D2", Result.STATE_BOUNDARY, reason="X")
    trailing_available = _record("D3", Result.HUMAN_ACTION_AVAILABLE)
    result = _chain((unrelated_later, earliest_available, broken, trailing_available))
    assert result.next_valid_transition is unrelated_later


def test_nvt_is_none_when_no_human_action_available_record_precedes_the_fbr() -> None:
    broken = _record("D0", Result.GOVERNANCE_BOUNDARY)
    result = _chain((broken,))
    assert result.next_valid_transition is None


def test_nvt_searches_the_whole_list_when_there_is_no_broken_relation() -> None:
    """No FBR at all -- 'at or before the FBR' places no ceiling."""
    legit_provider = _record(
        "D0", Result.ALLOWED, execution_class=ExecutionClass.PROVIDER_COMPUTATION
    )
    available = _record("D1", Result.HUMAN_ACTION_AVAILABLE)
    result = _chain((legit_provider, available))
    assert result.next_valid_transition is available


def test_nvt_a_record_strictly_after_the_fbr_is_never_selected() -> None:
    broken = _record("D0", Result.STATE_BOUNDARY, reason="X")
    later_available = _record("D1", Result.HUMAN_ACTION_AVAILABLE)
    result = _chain((broken, later_available))
    assert result.next_valid_transition is None


# ---------------------------------------------------------------------------
# HUMAN_AUTHORITY_REQUIRED (§7.5, disclosed subset)
# ---------------------------------------------------------------------------


def test_har_covers_an_authority_boundary_delta_with_its_own_real_reason_code() -> None:
    record = _record("D0", Result.AUTHORITY_BOUNDARY, reason="NO_SESSION_CONTROL")
    result = _chain((record,))
    assert result.human_authority_required == (
        AuthorityRequirement(
            delta_id="D0", result=Result.AUTHORITY_BOUNDARY, reason="NO_SESSION_CONTROL"
        ),
    )


def test_har_covers_a_governance_boundary_delta_with_the_cited_open_ha_question() -> None:
    record = _record(
        "D0",
        Result.GOVERNANCE_BOUNDARY,
        reason="OPERATION_CLASS_NOT_ADMITTED",
        execution_class=ExecutionClass.PROVIDER_COMPUTATION,
    )
    result = _chain((record,))
    assert GOVERNANCE_QUESTION_HA_PCPG_1 == "HA-PCPG-1"
    assert result.human_authority_required == (
        AuthorityRequirement(
            delta_id="D0",
            result=Result.GOVERNANCE_BOUNDARY,
            reason="OPERATION_CLASS_NOT_ADMITTED",
        ),
    )


def test_har_never_covers_a_state_boundary_delta() -> None:
    """Disclosed scope: a state-legality wall names no authority holder."""
    record = _record("D0", Result.STATE_BOUNDARY, reason="ANALYSIS_NOT_READY")
    result = _chain((record,))
    assert result.human_authority_required == ()


def test_har_never_covers_an_indeterminate_delta() -> None:
    record = _record("D0", Result.INDETERMINATE, reason="SEMANTIC_UNKNOWN")
    result = _chain((record,))
    assert result.human_authority_required == ()


def test_har_never_covers_a_human_action_available_delta() -> None:
    record = _record("D0", Result.HUMAN_ACTION_AVAILABLE)
    result = _chain((record,))
    assert result.human_authority_required == ()


def test_har_lists_every_qualifying_delta_in_order_not_only_the_first() -> None:
    a = _record("D0", Result.AUTHORITY_BOUNDARY, reason="NOT_A_PARTICIPANT")
    b = _record("D1", Result.GOVERNANCE_BOUNDARY, reason="OPERATION_CLASS_NOT_ADMITTED")
    result = _chain((a, b))
    assert [r.delta_id for r in result.human_authority_required] == ["D0", "D1"]


# ---------------------------------------------------------------------------
# PARTIAL (§7.6)
# ---------------------------------------------------------------------------


def test_partial_is_false_when_there_are_no_requested_deltas_at_all() -> None:
    result = _chain(())
    assert result.partial is False


def test_partial_is_true_when_any_requested_delta_is_outside_the_retained_set() -> None:
    """Today's own architectural fact (WU-PFC-PCPG-7/8): every real
    observation with at least one delta is PARTIAL, because the retained
    set is always empty."""
    record = _record("D0", Result.HUMAN_ACTION_AVAILABLE)
    result = _chain((record,))
    assert result.partial is True


def test_partial_is_false_when_the_retained_set_equals_the_full_requested_set() -> None:
    allowed = _record("D0", Result.ALLOWED, execution_class=ExecutionClass.PROVIDER_COMPUTATION)
    result = _chain((allowed,))
    assert result.partial is False


# ---------------------------------------------------------------------------
# Pulse: accepted, not consumed (disclosed; matches R-07's own precedent)
# ---------------------------------------------------------------------------


def test_a_governance_blocking_pulse_does_not_change_the_chain_result() -> None:
    """No producer exists to translate a bare Pulse blocker into a
    delta-shaped FBR/HAR entry (module docstring). Proven by direct
    comparison against the identical call with an unblocked Pulse."""
    records = (_record("D0", Result.HUMAN_ACTION_AVAILABLE),)
    blocked = _chain(records, _BLOCKED_PULSE)
    unblocked = _chain(records, _EMPTY_PULSE)
    assert blocked == unblocked


# ---------------------------------------------------------------------------
# Determinism, purity, no I/O, no provider (mirrors R-08's own discipline)
# ---------------------------------------------------------------------------


def test_same_inputs_give_the_same_chain_result_every_time() -> None:
    records = (_record("D0", Result.AUTHORITY_BOUNDARY, reason="NOT_FACILITATOR"),)
    effect = compose_effect(records)
    first = derive_chain_result(records, effect, _EMPTY_PULSE)
    second = derive_chain_result(records, effect, _EMPTY_PULSE)
    assert first == second


def test_the_module_touches_no_database_and_no_provider() -> None:
    root = pathlib.Path(__file__).resolve().parents[2] / "packages" / "application"
    source = (root / "pcpg_chain_results.py").read_text()
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


def test_composition_result_import_is_not_unused() -> None:
    """A static sanity check mirroring the same import discipline used
    throughout: this test module's own use of CompositionResult stays
    honest (via `compose_effect`'s own return value)."""
    effect = compose_effect(())
    assert effect.composition_result is CompositionResult.COMPOSABLE
