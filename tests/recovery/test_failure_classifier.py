"""T8 FAILURE CLASSIFIER TEST: FailureClass/FailureSignals/classify_failure,
pure, no database.

14 section 48's own PKG-22 scope: `packages/recovery/failure_classifier.py`.
"""

from __future__ import annotations

import dataclasses

import pytest
from recovery.failure_classifier import FailureClass, FailureSignals, classify_failure

_ALL_SIGNAL_FIELDS = tuple(f.name for f in dataclasses.fields(FailureSignals))


def test_failure_class_is_exactly_the_19_named_values() -> None:
    """Regression guard on 10 section 9's own closed vocabulary."""
    assert {member.value for member in FailureClass} == {
        "F-VAL",
        "F-AUTH",
        "F-BND",
        "F-CONC",
        "F-PERS",
        "F-PCOM",
        "F-AUD",
        "F-OUT",
        "F-AIGEN",
        "F-AIVAL",
        "F-AITOOL",
        "F-EXT",
        "F-NET",
        "F-PROVDR",
        "F-EVID",
        "F-PROV",
        "F-GOV",
        "F-REC",
        "F-SEC",
    }


def test_no_signals_yields_an_empty_classification() -> None:
    assert classify_failure(FailureSignals()) == frozenset()


@pytest.mark.parametrize(
    ("field_name", "expected_class"),
    [
        ("validation_failed", FailureClass.F_VAL),
        ("authority_failed", FailureClass.F_AUTH),
        ("boundary_denied", FailureClass.F_BND),
        ("concurrency_conflict", FailureClass.F_CONC),
        ("persistence_error", FailureClass.F_PERS),
        ("partial_commit", FailureClass.F_PCOM),
        ("audit_failure", FailureClass.F_AUD),
        ("event_outbox_failure", FailureClass.F_OUT),
        ("ai_generation_failure", FailureClass.F_AIGEN),
        ("ai_validation_failure", FailureClass.F_AIVAL),
        ("ai_tool_failure", FailureClass.F_AITOOL),
        ("external_side_effect_failure", FailureClass.F_EXT),
        ("network_failure", FailureClass.F_NET),
        ("provider_failure", FailureClass.F_PROVDR),
        ("evidence_failure", FailureClass.F_EVID),
        ("provenance_failure", FailureClass.F_PROV),
        ("governance_mutation_failure", FailureClass.F_GOV),
        ("recovery_failure", FailureClass.F_REC),
        ("security_relevant_failure", FailureClass.F_SEC),
    ],
)
def test_each_signal_maps_to_exactly_its_own_class(
    field_name: str, expected_class: FailureClass
) -> None:
    signals = FailureSignals(**{field_name: True})
    assert classify_failure(signals) == frozenset({expected_class})


def test_multiple_concurrent_signals_are_not_collapsed() -> None:
    """10 section 9: "A single attempt may have multiple failure
    classifications. The system must not collapse them when
    consequence certainty differs."
    """
    signals = FailureSignals(persistence_error=True, audit_failure=True, event_outbox_failure=True)
    assert classify_failure(signals) == frozenset(
        {FailureClass.F_PERS, FailureClass.F_AUD, FailureClass.F_OUT}
    )


def test_failure_signals_has_no_raw_technical_event_field() -> None:
    """Mandatory adversarial attacks: timeout before/after commit; DB
    exception; client disconnect; ambiguous connection loss.
    ARCHITECTURAL_INVARIANTS for this package: "TIMEOUT != FAILED; DB
    EXCEPTION != FAILED." Structural proof: no field name on
    `FailureSignals` represents a raw technical event at all -- a
    caller cannot even construct one, let alone have it silently
    misclassified.
    """
    forbidden_substrings = ("timeout", "timed_out", "exception", "disconnect", "connection")
    for field_name in _ALL_SIGNAL_FIELDS:
        for forbidden in forbidden_substrings:
            assert forbidden not in field_name.lower(), field_name


def test_failure_signals_rejects_unknown_keyword_fields() -> None:
    """Positive control: `FailureSignals` is a real, closed dataclass --
    an attempt to sneak in an unrecognized signal fails immediately
    rather than being silently ignored.
    """
    with pytest.raises(TypeError):
        FailureSignals(timed_out=True)  # type: ignore[call-arg]
