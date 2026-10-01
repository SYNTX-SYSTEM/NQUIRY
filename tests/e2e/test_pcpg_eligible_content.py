"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — R-11: provider-safe projection
eligibility, constraints only (Architecture 26).

Source: `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md`
R-11: "OUTPUT: the eligible content set ... PROOF: no blocked delta,
forbidden instruction, secret, cross-Workspace datum, DC-07 datum or
governance internal is ever in the eligible set (P-13)."

E1 re-derivation (2026-10-01, independent, against `checkpoint-PFC-PCPG-11`):
R-09 (`ChainResult.maximum_legitimate_transition`) is real; `grep` for
`EligibleContentSet`/`derive_eligible_content`: zero hits outside this
module. R-11 is the one remaining ordinary relation (R-13/R-14 are
explicitly not materialized / cross-cutting). R-11 is the next First
Broken Relation.

SCOPE (disclosed; full reasoning in `pcpg_eligible_content.py`'s own
module docstring, not repeated here): the eligible content set is proven
empty today for BOTH of R-11's own FAILURE STATE clauses — an empty MLT
(MLT_EMPTY) and a hypothetical non-empty MLT (CONTENT_NOT_CLASSIFIABLE,
since no data-class classifier producer exists anywhere). P-13's own
proof (nothing blocked/forbidden/secret/cross-Workspace/DC-07/governance-
internal is ever eligible) is therefore trivially, provably true: nothing
is ever eligible, full stop.
"""

from __future__ import annotations

from application.pcpg_delta_evaluation import DeltaRecord, Result
from application.pcpg_eligible_content import (
    CONTENT_NOT_CLASSIFIABLE,
    MLT_EMPTY,
    EligibilityResult,
    derive_eligible_content,
)
from application.pcpg_operation_index import ExecutionClass


def _allowed_delta(
    delta_id: str = "D0", operation: str = "REQUEST_QUESTION_ANALYSIS"
) -> DeltaRecord:
    return DeltaRecord(
        delta_id=delta_id,
        operation=operation,
        execution_class=ExecutionClass.PROVIDER_COMPUTATION,
        target=None,
        source_clause="x",
        span=(0, 1),
        current_state=None,
        result=Result.ALLOWED,
        reason=None,
        flags=frozenset(),
    )


# ---------------------------------------------------------------------------
# An empty MLT: FAILURE STATE's first clause, verbatim
# ---------------------------------------------------------------------------


def test_an_empty_mlt_gives_an_empty_eligible_set_with_mlt_empty_reason() -> None:
    eligible = derive_eligible_content(())
    assert eligible.eligible_inputs == ()
    assert eligible.retained_instruction_semantics == ()
    assert eligible.result is EligibilityResult.NO_ELIGIBLE_CONTENT
    assert eligible.reasons == frozenset({MLT_EMPTY})


def test_an_empty_mlt_excludes_no_delta_ids_there_are_none() -> None:
    assert derive_eligible_content(()).excluded_delta_ids == ()


# ---------------------------------------------------------------------------
# A hypothetical non-empty MLT: FAILURE STATE's second clause, proven
# directly rather than assumed unreachable
# ---------------------------------------------------------------------------


def test_a_non_empty_mlt_still_gives_an_empty_eligible_set_not_classifiable() -> None:
    allowed = _allowed_delta()
    eligible = derive_eligible_content((allowed,))
    assert eligible.eligible_inputs == ()
    assert eligible.retained_instruction_semantics == ()
    assert eligible.result is EligibilityResult.NO_ELIGIBLE_CONTENT
    assert eligible.reasons == frozenset({CONTENT_NOT_CLASSIFIABLE})


def test_a_non_empty_mlt_excludes_every_one_of_its_own_delta_ids() -> None:
    first = _allowed_delta("D0", "REQUEST_QUESTION_ANALYSIS")
    second = _allowed_delta("D1", "REQUEST_QUESTION_CLUSTERING")
    eligible = derive_eligible_content((first, second))
    assert eligible.excluded_delta_ids == ("D0", "D1")


def test_mlt_empty_and_not_classifiable_are_reported_as_distinct_reasons() -> None:
    """The two FAILURE STATE clauses are honored separately for
    diagnostic honesty, even though both yield the identical empty
    result today (module docstring's own disclosed simplification)."""
    empty = derive_eligible_content(())
    non_empty = derive_eligible_content((_allowed_delta(),))
    assert empty.reasons != non_empty.reasons
    assert empty.eligible_inputs == non_empty.eligible_inputs == ()


# ---------------------------------------------------------------------------
# P-13: nothing is ever in the eligible set, proven directly
# ---------------------------------------------------------------------------


def test_p13_nothing_is_ever_eligible_regardless_of_how_many_deltas_are_retained() -> None:
    """A genuine, direct proof of P-13 rather than an assertion in prose:
    construct a larger retained set and show the eligible set is still
    empty -- there is no size or shape of MLT that produces a non-empty
    eligible set today."""
    deltas = tuple(_allowed_delta(f"D{i}") for i in range(5))
    eligible = derive_eligible_content(deltas)
    assert eligible.eligible_inputs == ()
    assert eligible.retained_instruction_semantics == ()


# ---------------------------------------------------------------------------
# Determinism, purity, no I/O, no provider
# ---------------------------------------------------------------------------


def test_same_inputs_give_the_same_eligible_set_every_time() -> None:
    deltas = (_allowed_delta(),)
    assert derive_eligible_content(deltas) == derive_eligible_content(deltas)


def test_the_module_touches_no_database_and_no_provider() -> None:
    import ast
    import pathlib

    root = pathlib.Path(__file__).resolve().parents[2] / "packages" / "application"
    source = (root / "pcpg_eligible_content.py").read_text()
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
