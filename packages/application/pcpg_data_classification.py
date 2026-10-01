"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — FBR-PCPG-3: deterministic data-class
classifier (Architecture 26, `00_FIELD.md` §12; GAP-11-006, governed by
HA-PCPG-4).

Source: `00_FIELD.md` §12, verbatim: "FBR-PCPG-3: PROMPT CONTENT → DATA
CLASS. No deterministic classifier exists for free text. GAP-11-006 is
OPEN; the default is restrictive." HA-PCPG-4 (`00_FIELD.md` §13,
`HUMAN_AUTHORITY_QUEUE.md`), verbatim fail-closed default, now the
STANDING, ALREADY-DECIDED governing rule this module implements (it does
not itself require a new Human Authority decision — HD-29 did not touch
HA-PCPG-4): "Deterministic, rule-based candidates. Ambiguous content
takes the most restrictive class. No override."

E1 re-derivation (2026-10-01, independent, against `checkpoint-PFC-PCPG-13`):
`grep` for `DataClass`/`DataClassification`/`classify_prompt_content`
outside the RED text itself: zero hits in `packages/`. FBR-PCPG-3 is
genuinely absent. HD-29 (recorded `checkpoint-PFC-PCPG-13`) conditionally
admits `PROVIDER_COMPUTATION` but names "Data Governance" as one of its
own "at minimum" eligibility prerequisites — FBR-PCPG-3/GAP-11-006 is
confirmed the active, tractable blocker (the companion "Source" status
prerequisite, I-12, has no owning GAP/HA-PCPG-* row and is explicitly
NOT built here, per this Work Unit's own authorization). **FBR-PCPG-3 is
the next First Broken Relation.**

THE DC-01..07 VOCABULARY (not invented here)
------------------------------------------------
`docs/architecture/11_SECURITY_PRIVACY_OBSERVABILITY.md` §25 (AC-11-009)
names the seven classes verbatim: DC-01 PUBLIC, DC-02 INTERNAL, DC-03
WORKSPACE_CONFIDENTIAL, DC-04 PERSONAL_DATA, DC-05 SENSITIVE_OPERATIONAL,
DC-06 SECURITY_SENSITIVE, DC-07 AUDIT_SENSITIVE. §26's own Data Class
Handling Matrix runs, in this exact numeric order, from least to most
restrictive storage/AI-eligibility/logging/export language. `[IMPLEMENTATION
CHOICE]`, disclosed: 11 does not spell "DC-07 is more restrictive than
DC-06" as a single sentence, but no other ordering is given anywhere in
11, and this one is the only reading consistent with both the numbering
and the Matrix's own monotonically-stricter prose — this module encodes
it as the `DataClass` Enum's own ordinal values, so "most restrictive"
is a real, falsifiable `max()` over the vocabulary, not a guess.

WHY EXACTLY THESE THREE DETERMINISTIC SIGNALS, AND NO OTHERS
------------------------------------------------------------------
HA-PCPG-4 requires "deterministic, rule-based candidates" — never a
guess from free-text semantics. This module therefore classifies using
ONLY signals a real, earlier, already-closed relation already computed
deterministically — it invents no new free-text heuristic of its own:

- `workspace_scoped` (caller-supplied, from the real fact that R-02's
  own scope validation admits no observation without a Workspace):
  → DC-03 WORKSPACE_CONFIDENTIAL, §26's own exact words, "Workspace-
  scoped content." Always true for any real, successfully-ingressed
  observation today (R-01/R-02's own closed scope); kept as an explicit
  parameter, not a hardcoded assumption, so the `unknown` branch below
  remains directly, honestly testable rather than silently unreachable.
- `action.decision_substitution_requested` (R-05's own already-real,
  already-deterministic field — `operation_index()` lookup plus a plain
  conditional, no model): → DC-05 SENSITIVE_OPERATIONAL, §26's own exact
  words, "authority, recovery, operationally sensitive data" — a
  decision-substitution attempt is directly about authority.
- `action.possible_secret_content` (R-05's own already-real, already-
  deterministic regex-pattern detector): → DC-06 SECURITY_SENSITIVE,
  §26's own exact words, "secrets, security configuration, forensic
  sensitive material." `pcpg_simplix.py`'s own module docstring already
  named this exact relationship when `possible_secret_content` was first
  materialized: "informational flags only, consumed (not authoritatively
  decided) by a later relation" — this module is that later relation.

`action.possible_external_effect` and `action.target` are deliberately
NOT used: neither has a citable, non-speculative mapping to a specific
DC class in 11 §25–26 the way the three signals above do (using them
would mean inventing a new heuristic, which HA-PCPG-4 forbids). DC-01
PUBLIC and DC-02 INTERNAL are never produced by this module: no real,
deterministic signal anywhere in this codebase asserts "this content is
safe to treat as public" or "merely internal" — disclosed, not silently
assumed.

WHY `unknown` IS NEVER SILENTLY REWRITTEN INTO A GUESSED CLASS
--------------------------------------------------------------------
When none of the three signals fires, `candidate_classes` is empty —
`unknown=True`, the honest report that this instance genuinely knows
nothing (never reachable from today's real pipeline, since `workspace_
scoped` is always true in practice, but proven directly here all the
same, matching this Field's own standing discipline of testing a
not-yet-reachable branch rather than skipping it). `effective_handling_
class` still falls back to the ceiling (`AUDIT_SENSITIVE`) for
CONSERVATIVE DOWNSTREAM HANDLING purposes — GAP-11-006's own cited
"the default is restrictive" and HA-PCPG-4's own "UNKNOWN must remain
UNKNOWN... never guessed" — but `unknown=True`/`candidate_classes=()`
is what a consumer must read to know this is a conservative UPPER BOUND,
never an asserted fact about the content.

WHAT THIS WORK UNIT DOES NOT DO (the user's own explicit boundary)
------------------------------------------------------------------------
This module is not wired into `pcpg_delta_evaluation.py` (R-07),
`pcpg_composed_effect.py` (R-08) or any other relation in this
increment. Building the classifier does not, by itself, change any
existing relation's reachable output — R-07's own `OPERATION_CLASS_NOT_
ADMITTED` reason is now a stale justification (HA-PCPG-1 is no longer
simply undecided, per HD-29) but remains an accurate current VALUE
(wiring Data Governance into the per-delta decision is a separate,
later Work Unit this report does not begin). `CLASSIFICATION != AUTHORITY`,
`CLASSIFICATION != PROVIDER ELIGIBILITY`, `DATA CLASS != SEND PERMISSION`,
`UNKNOWN != PERMISSION` — this module computes a classification value
and nothing else; it grants nothing, and no caller may ever read it as
authority or permission.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from application.pcpg_simplix import SemanticAction


class DataClass(IntEnum):
    """Architecture 11 §25 (AC-11-009), DC-01..DC-07, verbatim names.
    Ordinal values ARE the restrictiveness order (module docstring's
    own disclosed `[IMPLEMENTATION CHOICE]`) — `max()` over a set of
    these values is therefore a real, falsifiable "most restrictive"
    computation, not a guess."""

    PUBLIC = 1
    INTERNAL = 2
    WORKSPACE_CONFIDENTIAL = 3
    PERSONAL_DATA = 4
    SENSITIVE_OPERATIONAL = 5
    SECURITY_SENSITIVE = 6
    AUDIT_SENSITIVE = 7


RESTRICTIVE_CEILING = DataClass.AUDIT_SENSITIVE
"""GAP-11-006's own cited default ("the default is restrictive") /
HA-PCPG-4's own rule ("ambiguous content takes the most restrictive
class... UNKNOWN must remain UNKNOWN... never guessed"): the
conservative HANDLING ceiling used when no real candidate fires —
never asserted as a known classification fact (see `DataClassification.
unknown`)."""

_WORKSPACE_SCOPED_PROVENANCE = (
    "WORKSPACE_SCOPED -> DC-03 WORKSPACE_CONFIDENTIAL (11 section 25-26: "
    '"Workspace-scoped content")'
)
_DECISION_SUBSTITUTION_PROVENANCE = (
    "DECISION_SUBSTITUTION_REQUESTED -> DC-05 SENSITIVE_OPERATIONAL (11 section 26: "
    '"authority, recovery, operationally sensitive data")'
)
_POSSIBLE_SECRET_CONTENT_PROVENANCE = (
    "POSSIBLE_SECRET_CONTENT -> DC-06 SECURITY_SENSITIVE (11 section 26: "
    '"secrets, security configuration, forensic sensitive material")'
)


@dataclass(frozen=True, slots=True)
class DataClassification:
    candidate_classes: frozenset[DataClass]
    """The real, rule-fired candidates. Empty exactly when nothing real
    is known about this content — UNKNOWN, never a guessed class."""
    unknown: bool
    """`True` exactly when `candidate_classes` is empty."""
    most_restrictive_candidate: DataClass | None
    """`max(candidate_classes)` when non-empty; `None` when `unknown`.
    HA-PCPG-4's own rule: "ambiguous content takes the most restrictive
    class.\""""
    effective_handling_class: DataClass
    """What a downstream consumer must treat this as for conservative
    handling: `most_restrictive_candidate` when known, else the ceiling
    `RESTRICTIVE_CEILING` — a conservative upper bound on unknown
    content's required handling, never an asserted fact about what the
    content actually is."""
    provenance: tuple[str, ...]
    """Which real signal(s) fired, cited by name. Empty exactly when
    `unknown` is `True`."""


def classify_prompt_content(
    action: SemanticAction, *, workspace_scoped: bool
) -> DataClassification:
    """FBR-PCPG-3's producer (this Work Unit's own disclosed scope).
    Pure, deterministic, no I/O, no model, no provider, no override
    parameter (HA-PCPG-4: "No override"). Every signal it reads is
    already real and already deterministic, computed by an earlier,
    already-closed relation — this function invents no new free-text
    heuristic of its own (module docstring)."""
    candidates: set[DataClass] = set()
    provenance: list[str] = []

    if workspace_scoped:
        candidates.add(DataClass.WORKSPACE_CONFIDENTIAL)
        provenance.append(_WORKSPACE_SCOPED_PROVENANCE)
    if action.decision_substitution_requested:
        candidates.add(DataClass.SENSITIVE_OPERATIONAL)
        provenance.append(_DECISION_SUBSTITUTION_PROVENANCE)
    if action.possible_secret_content:
        candidates.add(DataClass.SECURITY_SENSITIVE)
        provenance.append(_POSSIBLE_SECRET_CONTENT_PROVENANCE)

    frozen_candidates = frozenset(candidates)
    if not frozen_candidates:
        return DataClassification(
            candidate_classes=frozenset(),
            unknown=True,
            most_restrictive_candidate=None,
            effective_handling_class=RESTRICTIVE_CEILING,
            provenance=(),
        )

    most_restrictive = max(frozen_candidates)
    return DataClassification(
        candidate_classes=frozen_candidates,
        unknown=False,
        most_restrictive_candidate=most_restrictive,
        effective_handling_class=most_restrictive,
        provenance=tuple(provenance),
    )


__all__ = [
    "RESTRICTIVE_CEILING",
    "DataClass",
    "DataClassification",
    "classify_prompt_content",
]
