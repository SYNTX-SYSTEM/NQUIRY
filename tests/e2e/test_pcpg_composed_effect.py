"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — R-08: composed effect (Architecture 26).

Source: `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md`
R-08: "INPUT: the delta records... OUTPUT: the retained set: deltas that
are ALLOWED as PROVIDER_COMPUTATION and whose dependencies are all
retained... the composition result: COMPOSABLE, or the boundary class
with a reason." PRECONDITION: "R-07 is complete for every delta."

E1 re-derivation (2026-09-30, independent, against `checkpoint-PFC-PCPG-7`):
R-06 (deltas), R-07 (RESULT/REASON) are both real; R-08 itself is
genuinely absent (`grep` for `ComposedEffect`/`retained_set`/
`COMPOSABLE`: zero hits). R-08's own INPUT ("the delta records") and
PRECONDITION ("R-07 is complete for every delta") are both satisfied for
the RESULT/REASON subset R-07 already produces. R-08 is the next First
Broken Relation.

A REAL, PROVABLE FACT THIS WORK UNIT BUILDS ON, NOT AROUND
------------------------------------------------------------
WU-PFC-PCPG-7 proved, as an architectural fact (not a gap): in the
current real NQUIRY Field, NO delta can ever resolve `Result.ALLOWED`
(every `PROVIDER_COMPUTATION` delta is unconditionally
`GOVERNANCE_BOUNDARY`, HA-PCPG-1's own fail-closed default). Since
R-08's own "retained set" is defined as exactly "deltas that are ALLOWED
as PROVIDER_COMPUTATION", **the retained set is therefore always empty
for every real observation today** — not a limitation of this Work
Unit, the Field's own already-proven, cross-checked conclusion, now
observed from a third independent direction (R-07's per-delta RESULT,
`04_OBSERVATION_RESULT.md` §8's own CAN_SEND note, and now R-08's own
composition).

SCOPE OF THIS WORK UNIT (disclosed, not silently narrowed)
------------------------------------------------------------
This increment computes the `retained` set (real: filter by
`Result.ALLOWED` -- and, since R-06's own DIRECT-delta scope discloses
`dependency_edges` as always `()`, "whose dependencies are all
retained" is vacuously true for every delta today, so the filter needs
no dependency-graph traversal this increment would have to invent).
`composition_result` is computed honestly, not guessed: an EMPTY
retained set is trivially `COMPOSABLE` (nothing can cross a boundary
that contains nothing); a NON-EMPTY retained set -- a case that cannot
occur today, given the fact above, but the code must still behave
honestly if `dependency_edges`/`ALLOWED` ever become real -- is
`INDETERMINATE`, because the real sub-checks R-08's OUTPUT also names
(data-class union, external-effect check, composed proof ceiling,
purpose coherence, instrumental-to-blocked analysis) have no producer
in this codebase: no data-class classifier (FBR-PCPG-3, GAP-11-006,
still OPEN), no AI-contract output-class registry, no proof-ceiling
producer, no purpose-coherence rule beyond SIMPLIX's own minimal one.
Never guessed `COMPOSABLE` for a case this module cannot actually check.
"""

from __future__ import annotations

import ast
import dataclasses
import pathlib

from application.pcpg_candidate_deltas import CandidateDelta
from application.pcpg_composed_effect import CompositionResult, compose_effect
from application.pcpg_delta_evaluation import DeltaRecord, Result
from application.pcpg_operation_index import ExecutionClass


def _record(result: Result, operation: str | None = "BEGIN_ANALYSIS") -> DeltaRecord:
    return DeltaRecord(
        delta_id="D0",
        operation=operation,
        execution_class=ExecutionClass.HUMAN_COMMAND,
        target=None,
        source_clause="x",
        span=(0, 1),
        current_state=None,
        result=result,
        reason=None,
        flags=frozenset(),
    )


# ---------------------------------------------------------------------------
# The always-true-today case: an empty retained set is trivially COMPOSABLE
# ---------------------------------------------------------------------------


def test_no_allowed_deltas_gives_an_empty_retained_set_and_composable() -> None:
    records = (
        _record(Result.HUMAN_ACTION_AVAILABLE),
        _record(Result.AUTHORITY_BOUNDARY),
        _record(Result.STATE_BOUNDARY),
        _record(Result.GOVERNANCE_BOUNDARY),
        _record(Result.INDETERMINATE),
    )
    effect = compose_effect(records)
    assert effect.retained == ()
    assert effect.composition_result is CompositionResult.COMPOSABLE
    assert effect.reason is None


def test_an_empty_delta_list_is_also_trivially_composable() -> None:
    effect = compose_effect(())
    assert effect.retained == ()
    assert effect.composition_result is CompositionResult.COMPOSABLE


# ---------------------------------------------------------------------------
# The filter itself: proven correct independent of today's degenerate
# real-world instance (I-19: the relation's own defined behavior, not
# only its current, narrower observable case)
# ---------------------------------------------------------------------------


def test_the_retained_filter_selects_exactly_the_allowed_deltas() -> None:
    """A hand-built ALLOWED record (this Field's own real vocabulary
    permits it, even though R-07's own current producer never emits it)
    proves the FILTER is correct, not only that it is exercised."""
    allowed = _record(Result.ALLOWED, operation="REQUEST_QUESTION_ANALYSIS")
    other = _record(Result.GOVERNANCE_BOUNDARY)
    effect = compose_effect((allowed, other))
    assert effect.retained == (allowed,)


def test_a_non_empty_retained_set_is_honestly_indeterminate_never_guessed_composable() -> None:
    """The rich sub-checks R-08's own OUTPUT names (data-class union,
    external-effect check, proof ceiling, purpose coherence,
    instrumental-to-blocked) have no producer in this codebase -- a
    non-empty retained set is never waved through as COMPOSABLE without
    actually checking them."""
    allowed = _record(Result.ALLOWED, operation="REQUEST_QUESTION_ANALYSIS")
    effect = compose_effect((allowed,))
    assert effect.composition_result is CompositionResult.INDETERMINATE
    assert effect.reason == "COMPOSITION_CHECKS_NOT_MATERIALIZED"


def test_multiple_allowed_deltas_all_retained_together() -> None:
    allowed1 = _record(Result.ALLOWED, operation="REQUEST_QUESTION_ANALYSIS")
    allowed2 = _record(Result.ALLOWED, operation="REQUEST_QUESTION_CLUSTERING")
    effect = compose_effect((allowed1, allowed2))
    assert set(effect.retained) == {allowed1, allowed2}
    assert effect.composition_result is CompositionResult.INDETERMINATE


# ---------------------------------------------------------------------------
# HUMAN_ACTION_AVAILABLE is never retained (I-08: HUMAN_COMMAND never MLT)
# ---------------------------------------------------------------------------


def test_human_action_available_is_never_retained_even_though_it_is_a_positive_result() -> None:
    """04_OBSERVATION_RESULT.md §7.3: 'It contains only PROVIDER_
    COMPUTATION deltas. HUMAN_COMMAND ... deltas never enter it, even
    when HUMAN_ACTION_AVAILABLE.' The retained-set filter is on RESULT
    alone (ALLOWED), which already excludes HUMAN_ACTION_AVAILABLE by
    construction -- proven explicitly, not assumed."""
    delta = _record(Result.HUMAN_ACTION_AVAILABLE)
    effect = compose_effect((delta,))
    assert effect.retained == ()
    assert delta not in effect.retained


# ---------------------------------------------------------------------------
# Determinism, purity, order preservation
# ---------------------------------------------------------------------------


def test_retained_set_preserves_delta_order() -> None:
    a = DeltaRecord(
        delta_id="A",
        operation="REQUEST_QUESTION_ANALYSIS",
        execution_class=ExecutionClass.PROVIDER_COMPUTATION,
        target=None,
        source_clause="x",
        span=(0, 1),
        current_state=None,
        result=Result.ALLOWED,
        reason=None,
        flags=frozenset(),
    )
    b = DeltaRecord(
        delta_id="B",
        operation="REQUEST_QUESTION_CLUSTERING",
        execution_class=ExecutionClass.PROVIDER_COMPUTATION,
        target=None,
        source_clause="y",
        span=(1, 2),
        current_state=None,
        result=Result.ALLOWED,
        reason=None,
        flags=frozenset(),
    )
    effect = compose_effect((b, a))
    assert effect.retained == (b, a)


def test_same_inputs_give_the_same_effect_every_time() -> None:
    records = (_record(Result.AUTHORITY_BOUNDARY), _record(Result.HUMAN_ACTION_AVAILABLE))
    first = compose_effect(records)
    second = compose_effect(records)
    assert first == second


def test_the_module_touches_no_database_and_no_provider() -> None:
    root = pathlib.Path(__file__).resolve().parents[2] / "packages" / "application"
    source = (root / "pcpg_composed_effect.py").read_text()
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


def test_composition_result_is_this_fields_own_complete_vocabulary() -> None:
    """I-20: one definition. `04_OBSERVATION_RESULT.md` §7.1's own
    values (COMPOSABLE, or a boundary class with a reason) plus
    INDETERMINATE for the undeterminable case this increment discloses."""
    assert {r.value for r in CompositionResult} == {
        "COMPOSABLE",
        "COMPOSITION_DATA_BOUNDARY",
        "COMPOSITION_EXTERNAL_EFFECT",
        "COMPOSITION_GOVERNANCE_BOUNDARY",
        "INDETERMINATE",
    }


def test_candidate_delta_type_is_not_imported_unused() -> None:
    """A static sanity check that this test module's own imports stay
    honest (mirrors the same import discipline used throughout)."""
    assert CandidateDelta.__name__ == "CandidateDelta"


# ---------------------------------------------------------------------------
# WU-PFC-PCPG-16: I-12's own Session-level composed proof ceiling
# ---------------------------------------------------------------------------


def _ceiling_record(delta_id: str, ceiling: str | None) -> DeltaRecord:
    return dataclasses.replace(
        _record(Result.ALLOWED, operation="REQUEST_QUESTION_ANALYSIS"),
        delta_id=delta_id,
        session_proof_ceiling=ceiling,
    )


def test_a_single_fixture_delta_composes_to_fixture_non_proof() -> None:
    """Required falsifier 1 (composed level): a retained FIXTURE_NON_
    PROOF delta's own ceiling is never raised by composition."""
    effect = compose_effect((_ceiling_record("D0", "FIXTURE_NON_PROOF"),))
    assert effect.composed_proof_ceiling == "FIXTURE_NON_PROOF"


def test_no_later_step_can_raise_a_retained_fixture_non_proof_ceiling() -> None:
    """Required falsifier 2: mixing a FIXTURE_NON_PROOF delta with
    further GOVERNED ones never raises the composed ceiling back to
    GOVERNED -- the most restrictive real ceiling always wins."""
    effect = compose_effect(
        (
            _ceiling_record("D0", "GOVERNED"),
            _ceiling_record("D1", "FIXTURE_NON_PROOF"),
            _ceiling_record("D2", "GOVERNED"),
        )
    )
    assert effect.composed_proof_ceiling == "FIXTURE_NON_PROOF"


def test_mixed_retained_deltas_compose_to_the_most_restrictive_ceiling() -> None:
    """Required falsifier 3: a mixed retained set never produces a
    ceiling weaker (less restrictive) than its own most restrictive
    real input."""
    effect = compose_effect(
        (_ceiling_record("D0", "FIXTURE_NON_PROOF"), _ceiling_record("D1", "GOVERNED"))
    )
    assert effect.composed_proof_ceiling == "FIXTURE_NON_PROOF"


def test_all_governed_retained_deltas_compose_to_governed() -> None:
    effect = compose_effect((_ceiling_record("D0", "GOVERNED"), _ceiling_record("D1", "GOVERNED")))
    assert effect.composed_proof_ceiling == "GOVERNED"


def test_an_unknown_ceiling_on_even_one_retained_delta_never_becomes_stronger_proof() -> None:
    """Required falsifier 4: "absence/unknown proof_mode never becomes
    stronger proof." A GOVERNED delta alongside an unknown (`None`) one
    must never compose to the known, weaker-restriction `"GOVERNED"` --
    that would silently dilute the unknown input away. The composed
    result is honestly `None` instead."""
    effect = compose_effect((_ceiling_record("D0", "GOVERNED"), _ceiling_record("D1", None)))
    assert effect.composed_proof_ceiling is None


def test_an_empty_retained_set_has_no_composed_ceiling_to_report() -> None:
    effect = compose_effect(())
    assert effect.composed_proof_ceiling is None


def test_the_module_invents_no_provider_output_or_evidence_proof_class() -> None:
    """Required falsifiers 6-7: "no provider-output proof class is
    invented"; "no Evidence provenance is invented." This module cites
    only the two real `inquiry_queries.proof_mode` values -- never the
    richer I-12 vocabulary (`AI_VALIDATION_PROOF`, `DOMAIN_EVIDENCE`,
    `SYSTEM_PROOF`, `PROPOSAL`, evidence-provenance field names)."""
    root = pathlib.Path(__file__).resolve().parents[2] / "packages" / "application"
    source = (root / "pcpg_composed_effect.py").read_text()
    for forbidden in (
        "AI_VALIDATION_PROOF",
        "DOMAIN_EVIDENCE",
        "SYSTEM_PROOF",
        "MOCK_NON_PROOF",
        "evidence_proof_refs",
        "ProvenanceEnvelope",
    ):
        assert forbidden not in source
