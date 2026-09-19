"""FailureClassifier: 10 section 9's exact 19-value Failure Taxonomy.

Source: 10_FAILURE_RECOVERY_ROLLBACK.md section 9 ("10 defines these
explicit failure classes" -- definitive-closure language, the same
"is there an 'exact'/'defines' word" test already used to formalize
every other closed vocabulary in this codebase; "A single attempt may
have multiple failure classifications. The system must not collapse
them when consequence certainty differs."), section 29/section 1176's
own Failure Taxonomy Matrix (each class's own detection point/known
state/canonical consequence/retry eligibility columns);
14_IMPLEMENTATION_SEQUENCE.md ARCHITECTURAL_INVARIANTS for this package
("TIMEOUT != FAILED; DB EXCEPTION != FAILED").

WHY `FailureSignals` HAS NO `timed_out`/`db_exception`/`client_disconnected`
FIELD
--------------------------------------------------------------------
This package's own ARCHITECTURAL_INVARIANTS state it explicitly:
"TIMEOUT != FAILED; DB EXCEPTION != FAILED" (mirrored by
`10_FAILURE_RECOVERY_ROLLBACK.md` section 5's "timeout != proven
failure", "local error != external non-occurrence"). A raw technical
event (a socket timeout, a driver exception, a dropped connection) is
NOT itself a failure classification -- it is evidence a CALLER must
first interpret against actual system state before deciding whether
any of the 19 named classes legitimately applies. `FailureClassifier`
therefore accepts only ALREADY-INTERPRETED boolean signals ("this
attempt's own boundary evaluation returned DENY", not "the boundary
call timed out") -- classifying only after authoritative consequence
analysis, per this package's own OBJECTIVE line. Mandatory adversarial
attacks "timeout before/after commit", "DB exception", "client
disconnect" are proven by `FailureSignals`' own field list structurally
excluding any such raw technical event as an input at all.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FailureClass(Enum):
    """10 section 9's exact 19-value closed taxonomy."""

    F_VAL = "F-VAL"
    F_AUTH = "F-AUTH"
    F_BND = "F-BND"
    F_CONC = "F-CONC"
    F_PERS = "F-PERS"
    F_PCOM = "F-PCOM"
    F_AUD = "F-AUD"
    F_OUT = "F-OUT"
    F_AIGEN = "F-AIGEN"
    F_AIVAL = "F-AIVAL"
    F_AITOOL = "F-AITOOL"
    F_EXT = "F-EXT"
    F_NET = "F-NET"
    F_PROVDR = "F-PROVDR"
    F_EVID = "F-EVID"
    F_PROV = "F-PROV"
    F_GOV = "F-GOV"
    F_REC = "F-REC"
    F_SEC = "F-SEC"


@dataclass(frozen=True, slots=True)
class FailureSignals:
    """Already-interpreted facts about one attempt -- never a raw
    technical event (see this module's own docstring). Every field
    defaults to `False`; a caller sets only the signals it has actually
    confirmed apply.
    """

    validation_failed: bool = False
    authority_failed: bool = False
    boundary_denied: bool = False
    concurrency_conflict: bool = False
    persistence_error: bool = False
    partial_commit: bool = False
    audit_failure: bool = False
    event_outbox_failure: bool = False
    ai_generation_failure: bool = False
    ai_validation_failure: bool = False
    ai_tool_failure: bool = False
    external_side_effect_failure: bool = False
    network_failure: bool = False
    provider_failure: bool = False
    evidence_failure: bool = False
    provenance_failure: bool = False
    governance_mutation_failure: bool = False
    recovery_failure: bool = False
    security_relevant_failure: bool = False


_SIGNAL_TO_CLASS: tuple[tuple[str, FailureClass], ...] = (
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
)


def classify_failure(signals: FailureSignals) -> frozenset[FailureClass]:
    """Pure mapping, no I/O. 10 section 9: "A single attempt may have
    multiple failure classifications" -- returns every applicable
    class, never collapses to one, and every class not signalled is
    simply absent, never guessed.
    """

    return frozenset(
        failure_class
        for field_name, failure_class in _SIGNAL_TO_CLASS
        if getattr(signals, field_name)
    )


__all__ = ["FailureClass", "FailureSignals", "classify_failure"]
