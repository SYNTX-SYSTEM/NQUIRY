"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — R-10: current capability, stratum 4
(Architecture 26).

Source: `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md`
R-10: "OUTPUT: GOVERNANCE_ADMISSIBLE, PROVIDER_EXECUTABLE and CAN_SEND,
each with its reasons." `04_OBSERVATION_RESULT.md` §8 is the AUTHORITATIVE
HOME for the exact bullets and the already-published current values.

E1 re-derivation (2026-10-01, independent, against `checkpoint-PFC-PCPG-9`):
R-08 (composition), R-09 (chain results), R-04 (Pulse), R-03
(`ProviderContext`) are all real; `grep` for `GOVERNANCE_ADMISSIBLE`/
`PROVIDER_EXECUTABLE`/`CAN_SEND`/`derive_capability`: zero hits outside
this module. R-10 is the next First Broken Relation.

SCOPE (disclosed; full reasoning in `pcpg_capability.py`'s own module
docstring, not repeated here): GOVERNANCE_ADMISSIBLE covers bullets 1
(MLT non-empty), 2 (composition COMPOSABLE) and 4 (admitted operation
class, via a small closed/grepped operation->contract table); bullets 3
and 5 have no producer and are never checked (never silently assumed
true either — they are simply absent from the reasons set, same as
every prior relation's own disclosed-narrowing pattern). PROVIDER_
EXECUTABLE reuses §8's own already-published, cited, unconditional
`NO_ELIGIBLE_PROVIDER_ROUTE` value (no route-table producer exists
anywhere in this codebase), plus the one real, additionally-checkable
`NO_ENVIRONMENT_DECLARED` reason. CAN_SEND is the plain boolean AND.

A further architectural fact this Work Unit's own testing found (full
reasoning in `pcpg_capability.py`'s module docstring): GOVERNANCE_
ADMISSIBLE can never be true today, not even hypothetically — R-08's own
design makes bullets 1 (MLT non-empty) and 2 (COMPOSABLE) mutually
exclusive by construction.
"""

from __future__ import annotations

import ast
import pathlib

from application.pcpg_capability import (
    MLT_EMPTY,
    NO_ELIGIBLE_PROVIDER_ROUTE,
    NO_ENVIRONMENT_DECLARED,
    OPERATION_NOT_ADMITTED_FOR_RETAINED_DELTA,
    Capability,
    derive_capability,
)
from application.pcpg_chain_results import ChainResult, derive_chain_result
from application.pcpg_composed_effect import ComposedEffect, CompositionResult, compose_effect
from application.pcpg_delta_evaluation import DeltaRecord, Result
from application.pcpg_field_pulse import Pulse
from application.pcpg_field_snapshot import AI_CONTRACTS_ADMITTED, ProviderContext
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
    governance_blockers=("HA-23",),
    unresolved=(),
)

_DECLARED_PROVIDER = ProviderContext(environment="test", provider_configured=False)
_UNDECLARED_PROVIDER = ProviderContext(environment=None, provider_configured=False)

_PROVIDER_DELTA = "REQUEST_QUESTION_ANALYSIS"


def _record(
    delta_id: str,
    result: Result,
    *,
    operation: str | None = "BEGIN_ANALYSIS",
    execution_class: ExecutionClass = ExecutionClass.HUMAN_COMMAND,
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
        reason=None,
        flags=frozenset(),
    )


def _allowed_provider_delta(operation: str = _PROVIDER_DELTA) -> DeltaRecord:
    return _record(
        "D0",
        Result.ALLOWED,
        operation=operation,
        execution_class=ExecutionClass.PROVIDER_COMPUTATION,
    )


def _chain(records: tuple[DeltaRecord, ...]) -> tuple[ChainResult, ComposedEffect]:
    effect = compose_effect(records)
    chain = derive_chain_result(records, effect, _EMPTY_PULSE)
    return chain, effect


def _derive(
    records: tuple[DeltaRecord, ...],
    *,
    pulse: Pulse = _EMPTY_PULSE,
    admitted: frozenset[str] = AI_CONTRACTS_ADMITTED,
    provider: ProviderContext = _DECLARED_PROVIDER,
) -> Capability:
    chain, effect = _chain(records)
    return derive_capability(chain, effect, pulse, admitted, provider)


# ---------------------------------------------------------------------------
# GOVERNANCE_ADMISSIBLE bullet 1: MLT non-empty
# ---------------------------------------------------------------------------


def test_an_empty_mlt_makes_governance_admissible_false_with_mlt_empty() -> None:
    capability = _derive(())
    assert capability.governance_admissible is False
    assert MLT_EMPTY in capability.governance_admissible_reasons


def test_todays_real_field_has_no_delta_ever_resolve_allowed_so_mlt_is_always_empty() -> None:
    """Cross-checks WU-7/8/9's own already-proven architectural fact from
    this relation's own vantage point: any realistic record set (no
    hand-built ALLOWED record) always yields MLT_EMPTY."""
    records = (
        _record("D0", Result.HUMAN_ACTION_AVAILABLE),
        _record(
            "D1",
            Result.GOVERNANCE_BOUNDARY,
            operation=_PROVIDER_DELTA,
            execution_class=ExecutionClass.PROVIDER_COMPUTATION,
        ),
    )
    capability = _derive(records)
    assert MLT_EMPTY in capability.governance_admissible_reasons


# ---------------------------------------------------------------------------
# GOVERNANCE_ADMISSIBLE bullet 2: composition COMPOSABLE
# ---------------------------------------------------------------------------


def test_a_composable_empty_mlt_still_fails_on_mlt_empty_alone() -> None:
    """An empty retained set is COMPOSABLE (R-08) but still MLT_EMPTY
    (R-10 bullet 1) -- the two bullets are independent."""
    chain, effect = _chain(())
    assert effect.composition_result is CompositionResult.COMPOSABLE
    capability = _derive(())
    assert capability.governance_admissible_reasons == frozenset({MLT_EMPTY})


def test_a_non_composable_composition_result_is_reported_by_its_own_real_reason() -> None:
    allowed = _allowed_provider_delta()
    _, effect = _chain((allowed,))
    assert effect.composition_result is CompositionResult.INDETERMINATE
    assert effect.reason == "COMPOSITION_CHECKS_NOT_MATERIALIZED"
    capability = _derive((allowed,))
    assert "COMPOSITION_CHECKS_NOT_MATERIALIZED" in capability.governance_admissible_reasons
    assert MLT_EMPTY not in capability.governance_admissible_reasons


# ---------------------------------------------------------------------------
# GOVERNANCE_ADMISSIBLE bullet 4: admitted operation class
# ---------------------------------------------------------------------------


def test_a_retained_delta_mapping_to_an_admitted_contract_passes_bullet_four() -> None:
    capability = _derive((_allowed_provider_delta(),))
    assert OPERATION_NOT_ADMITTED_FOR_RETAINED_DELTA not in capability.governance_admissible_reasons


def test_a_retained_delta_mapping_to_a_contract_outside_admitted_fails_bullet_four() -> None:
    capability = _derive((_allowed_provider_delta(),), admitted=frozenset())
    assert OPERATION_NOT_ADMITTED_FOR_RETAINED_DELTA in capability.governance_admissible_reasons


def test_a_retained_delta_with_an_unmapped_operation_fails_bullet_four() -> None:
    """An operation not in the closed PROVIDER_COMPUTATION contract table
    (hypothetically retained, never reachable today) must never be
    silently waved through."""
    capability = _derive((_allowed_provider_delta("SOME_FUTURE_OPERATION"),))
    assert OPERATION_NOT_ADMITTED_FOR_RETAINED_DELTA in capability.governance_admissible_reasons


# ---------------------------------------------------------------------------
# GOVERNANCE_ADMISSIBLE overall: never true today, by construction
# ---------------------------------------------------------------------------


def test_governance_admissible_can_never_be_true_bullets_one_two_mutually_exclusive() -> None:
    """A genuine, disclosed architectural fact this falsifier proves
    directly rather than merely asserting in prose: R-08's own already-
    proven design makes a non-empty retained set always `INDETERMINATE`
    (never `COMPOSABLE`), while an empty one is always `COMPOSABLE` but
    then fails bullet 1 (`MLT_EMPTY`). Bullets 1 and 2 can therefore never
    both hold at once in this Field as currently composed -- not merely
    "in practice today", but by logical construction of R-08's own
    design. `governance_admissible` is checked here for both the empty
    and the (hypothetical, never-reachable) non-empty case, and is false
    in both."""
    _, empty_effect = _chain(())
    assert empty_effect.composition_result is CompositionResult.COMPOSABLE
    assert _derive(()).governance_admissible is False

    allowed = _allowed_provider_delta()
    _, non_empty_effect = _chain((allowed,))
    assert non_empty_effect.composition_result is CompositionResult.INDETERMINATE
    assert _derive((allowed,)).governance_admissible is False


def test_governance_admissible_reasons_contain_only_whats_actually_wrong() -> None:
    """A narrower, positive-direction check: bullet 4 (operation
    admitted) is NOT reported as a reason when the retained delta's own
    contract is genuinely admitted -- the overall value is still false
    (bullet 2), but the reasons set must not fabricate a bullet-4
    failure that did not occur."""
    capability = _derive((_allowed_provider_delta(),))
    assert capability.governance_admissible_reasons == frozenset(
        {"COMPOSITION_CHECKS_NOT_MATERIALIZED"}
    )


# ---------------------------------------------------------------------------
# PROVIDER_EXECUTABLE: §8's own already-published, cited current value
# ---------------------------------------------------------------------------


def test_provider_executable_is_unconditionally_false_with_the_cited_reason() -> None:
    capability = _derive(())
    assert capability.provider_executable is False
    assert NO_ELIGIBLE_PROVIDER_ROUTE in capability.provider_executable_reasons


def test_provider_executable_stays_false_even_with_a_declared_environment() -> None:
    capability = _derive((), provider=_DECLARED_PROVIDER)
    assert capability.provider_executable is False
    assert NO_ENVIRONMENT_DECLARED not in capability.provider_executable_reasons


def test_an_undeclared_environment_adds_its_own_honest_reason() -> None:
    capability = _derive((), provider=_UNDECLARED_PROVIDER)
    assert NO_ENVIRONMENT_DECLARED in capability.provider_executable_reasons
    assert NO_ELIGIBLE_PROVIDER_ROUTE in capability.provider_executable_reasons
    assert capability.provider_executable is False


# ---------------------------------------------------------------------------
# CAN_SEND: the plain boolean AND
# ---------------------------------------------------------------------------


def test_can_send_is_false_whenever_governance_admissible_is_false() -> None:
    assert _derive(()).can_send is False


def test_can_send_is_false_in_the_hypothetical_mlt_non_empty_case_too() -> None:
    """Doubly false today: PROVIDER_EXECUTABLE is unconditionally false
    (no route producer exists at all), and -- per the mutual-exclusivity
    fact proven above -- GOVERNANCE_ADMISSIBLE can never be true either.
    CAN_SEND is false both ways, never by coincidence."""
    capability = _derive((_allowed_provider_delta(),))
    assert capability.governance_admissible is False
    assert capability.provider_executable is False
    assert capability.can_send is False


# ---------------------------------------------------------------------------
# Pulse: accepted, not consumed (disclosed; matches R-07's/R-09's own precedent)
# ---------------------------------------------------------------------------


def test_a_governance_blocking_pulse_does_not_change_the_capability() -> None:
    blocked = _derive((), pulse=_BLOCKED_PULSE)
    unblocked = _derive((), pulse=_EMPTY_PULSE)
    assert blocked == unblocked


# ---------------------------------------------------------------------------
# Determinism, purity, no I/O, no provider
# ---------------------------------------------------------------------------


def test_same_inputs_give_the_same_capability_every_time() -> None:
    assert _derive(()) == _derive(())


def test_the_module_touches_no_database_and_no_provider() -> None:
    root = pathlib.Path(__file__).resolve().parents[2] / "packages" / "application"
    source = (root / "pcpg_capability.py").read_text()
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
