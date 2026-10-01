"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — FBR-PCPG-3: deterministic data-class
classifier (Architecture 26; GAP-11-006; governed by HA-PCPG-4).

Source: `00_FIELD.md` §12 (FBR-PCPG-3), §13 (HA-PCPG-4, the already-
decided standing rule this module implements). `docs/architecture/
11_SECURITY_PRIVACY_OBSERVABILITY.md` §25-26 (DC-01..07, the Data Class
Handling Matrix).

E1 re-derivation (2026-10-01, independent, against `checkpoint-PFC-PCPG-13`):
`grep` for `DataClass`/`DataClassification`/`classify_prompt_content`:
zero hits outside this module. FBR-PCPG-3 is the next First Broken
Relation (full reasoning in `pcpg_data_classification.py`'s own module
docstring, not repeated here).

SCOPE (disclosed): three deterministic signals only — `workspace_scoped`,
`SemanticAction.decision_substitution_requested`,
`SemanticAction.possible_secret_content` — each already real and already
deterministic from an earlier, closed relation. DC-01 PUBLIC and DC-02
INTERNAL are never produced (no real signal exists for either). No model,
no provider, no override.
"""

from __future__ import annotations

import ast
import pathlib

from application.pcpg_data_classification import (
    RESTRICTIVE_CEILING,
    DataClass,
    classify_prompt_content,
)
from application.pcpg_simplix import Modality, RequestedExecutor, SemanticAction


def _action(
    *,
    decision_substitution_requested: bool = False,
    possible_secret_content: bool = False,
) -> SemanticAction:
    return SemanticAction(
        clause_index=0,
        span=(0, 1),
        clause_text="x",
        modality=Modality.REQUESTED,
        negated=False,
        requested_executor=RequestedExecutor.HUMAN,
        candidate_operation=None,
        target=None,
        possible_external_effect=False,
        possible_secret_content=possible_secret_content,
        decision_substitution_requested=decision_substitution_requested,
    )


# ---------------------------------------------------------------------------
# Restrictiveness ordering itself (required falsifier: mutation that
# weakens restrictive ordering must be caught)
# ---------------------------------------------------------------------------


def test_restrictive_ordering_is_exactly_dc01_through_dc07_ascending() -> None:
    assert [c.value for c in DataClass] == [1, 2, 3, 4, 5, 6, 7]
    assert DataClass.PUBLIC < DataClass.INTERNAL < DataClass.WORKSPACE_CONFIDENTIAL
    assert (
        DataClass.WORKSPACE_CONFIDENTIAL < DataClass.PERSONAL_DATA < DataClass.SENSITIVE_OPERATIONAL
    )
    assert DataClass.SENSITIVE_OPERATIONAL < DataClass.SECURITY_SENSITIVE
    assert DataClass.SECURITY_SENSITIVE < DataClass.AUDIT_SENSITIVE
    assert RESTRICTIVE_CEILING is DataClass.AUDIT_SENSITIVE


# ---------------------------------------------------------------------------
# One unambiguous low-restriction input
# ---------------------------------------------------------------------------


def test_workspace_scoped_alone_is_an_unambiguous_low_restriction_result() -> None:
    result = classify_prompt_content(_action(), workspace_scoped=True)
    assert result.candidate_classes == frozenset({DataClass.WORKSPACE_CONFIDENTIAL})
    assert result.unknown is False
    assert result.most_restrictive_candidate is DataClass.WORKSPACE_CONFIDENTIAL
    assert result.effective_handling_class is DataClass.WORKSPACE_CONFIDENTIAL


# ---------------------------------------------------------------------------
# One unambiguous high-restriction input
# ---------------------------------------------------------------------------


def test_possible_secret_content_alone_no_workspace_scope_is_unambiguous_high_restriction() -> None:
    action = _action(possible_secret_content=True)
    result = classify_prompt_content(action, workspace_scoped=False)
    assert result.candidate_classes == frozenset({DataClass.SECURITY_SENSITIVE})
    assert result.most_restrictive_candidate is DataClass.SECURITY_SENSITIVE
    assert result.effective_handling_class is DataClass.SECURITY_SENSITIVE


# ---------------------------------------------------------------------------
# Overlapping classifications (the candidate SET itself has >1 member)
# ---------------------------------------------------------------------------


def test_overlapping_signals_produce_multiple_real_candidates() -> None:
    action = _action(possible_secret_content=True, decision_substitution_requested=True)
    result = classify_prompt_content(action, workspace_scoped=True)
    assert result.candidate_classes == frozenset(
        {
            DataClass.WORKSPACE_CONFIDENTIAL,
            DataClass.SENSITIVE_OPERATIONAL,
            DataClass.SECURITY_SENSITIVE,
        }
    )


# ---------------------------------------------------------------------------
# Ambiguity resolving to the most restrictive class (the RESOLUTION, not
# just the set)
# ---------------------------------------------------------------------------


def test_ambiguity_resolves_to_the_most_restrictive_candidate() -> None:
    action = _action(possible_secret_content=True, decision_substitution_requested=True)
    result = classify_prompt_content(action, workspace_scoped=True)
    assert result.most_restrictive_candidate is DataClass.SECURITY_SENSITIVE
    assert result.effective_handling_class is DataClass.SECURITY_SENSITIVE


def test_decision_substitution_alone_resolves_to_sensitive_operational_not_escalated() -> None:
    """A narrower check that the resolution picks exactly the real
    maximum among what actually fired, never escalating beyond it."""
    action = _action(decision_substitution_requested=True)
    result = classify_prompt_content(action, workspace_scoped=True)
    assert result.most_restrictive_candidate is DataClass.SENSITIVE_OPERATIONAL
    assert DataClass.SECURITY_SENSITIVE not in result.candidate_classes
    assert DataClass.AUDIT_SENSITIVE not in result.candidate_classes


# ---------------------------------------------------------------------------
# Unknown / unclassifiable content, and empty content
# ---------------------------------------------------------------------------


def test_unknown_when_no_real_signal_fires_never_a_guessed_class() -> None:
    """Never reachable from today's real pipeline (R-01/R-02 always
    admit a Workspace-scoped observation), but proven directly, matching
    this Field's own standing discipline of testing a not-yet-reachable
    branch rather than skipping it."""
    result = classify_prompt_content(_action(), workspace_scoped=False)
    assert result.candidate_classes == frozenset()
    assert result.unknown is True
    assert result.most_restrictive_candidate is None
    assert result.provenance == ()


def test_unknown_content_still_gets_the_restrictive_ceiling_for_handling() -> None:
    """GAP-11-006's own cited default ("the default is restrictive") /
    HA-PCPG-4's own rule ("UNKNOWN must remain UNKNOWN... never
    guessed"): the ceiling is a conservative HANDLING bound, distinct
    from the honest `unknown=True` classification report."""
    result = classify_prompt_content(_action(), workspace_scoped=False)
    assert result.effective_handling_class is RESTRICTIVE_CEILING
    assert result.unknown is True


def test_empty_content_with_no_workspace_scope_is_also_unknown() -> None:
    """A distinct real-world scenario (content with nothing to classify
    at all) that happens to hit the same honest UNKNOWN path as a
    non-empty, still-unrecognized clause -- tested separately because
    it is a materially different situation, even though the code path
    and outcome are identical."""
    empty_action = SemanticAction(
        clause_index=0,
        span=(0, 0),
        clause_text="",
        modality=Modality.REQUESTED,
        negated=False,
        requested_executor=RequestedExecutor.HUMAN,
        candidate_operation=None,
        target=None,
        possible_external_effect=False,
        possible_secret_content=False,
        decision_substitution_requested=False,
    )
    result = classify_prompt_content(empty_action, workspace_scoped=False)
    assert result.unknown is True
    assert result.candidate_classes == frozenset()


# ---------------------------------------------------------------------------
# Classification provenance
# ---------------------------------------------------------------------------


def test_provenance_cites_exactly_the_signals_that_fired() -> None:
    action = _action(possible_secret_content=True)
    result = classify_prompt_content(action, workspace_scoped=True)
    assert len(result.provenance) == 2
    assert any("WORKSPACE_SCOPED" in p for p in result.provenance)
    assert any("POSSIBLE_SECRET_CONTENT" in p for p in result.provenance)
    assert not any("DECISION_SUBSTITUTION" in p for p in result.provenance)


def test_provenance_is_empty_exactly_when_unknown() -> None:
    result = classify_prompt_content(_action(), workspace_scoped=False)
    assert result.provenance == ()
    assert result.unknown is True


# ---------------------------------------------------------------------------
# No override path
# ---------------------------------------------------------------------------


def test_the_module_exposes_no_override_or_assignment_function() -> None:
    root = pathlib.Path(__file__).resolve().parents[2] / "packages" / "application"
    source = (root / "pcpg_data_classification.py").read_text()
    tree = ast.parse(source)
    forbidden_name_fragments = ("override", "assign_class", "set_class", "force_class")
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            lowered = node.name.lower()
            assert not any(f in lowered for f in forbidden_name_fragments), node.name
            for arg in node.args.args + node.args.kwonlyargs:
                lowered_arg = arg.arg.lower()
                assert not any(f in lowered_arg for f in forbidden_name_fragments), arg.arg


# ---------------------------------------------------------------------------
# No model, no provider, no I/O
# ---------------------------------------------------------------------------


def test_the_module_touches_no_database_no_provider_and_no_model() -> None:
    root = pathlib.Path(__file__).resolve().parents[2] / "packages" / "application"
    source = (root / "pcpg_data_classification.py").read_text()
    tree = ast.parse(source)
    forbidden = (
        "ai_gateway",
        "anthropic",
        "openai",
        "provider",
        "psycopg",
        "sqlalchemy",
        "model",
        "torch",
        "transformers",
    )
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


# ---------------------------------------------------------------------------
# Deterministic replay on identical input
# ---------------------------------------------------------------------------


def test_same_inputs_give_the_same_classification_every_time() -> None:
    action = _action(possible_secret_content=True, decision_substitution_requested=True)
    first = classify_prompt_content(action, workspace_scoped=True)
    second = classify_prompt_content(action, workspace_scoped=True)
    assert first == second
