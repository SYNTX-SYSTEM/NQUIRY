"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — R-05: the local SIMPLIX semantic sweep
(Architecture 26).

Source: `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md`
R-05: "PRODUCER: SIMPLIX, inside the trusted backend boundary. Mechanism is
open (HA-PCPG-2); the default is reproducible, rule-based derivation."
`00_FIELD.md` §13 HA-PCPG-2's fail-closed default: "Only derivations that
are reproducible from (rule-set version, inputs) are admitted. Uncertainty
becomes UNKNOWN, never a guess." This module honors that default as its
PERMANENT shape, not a placeholder: no model, no LLM, no embeddings, no
external provider, ever -- a closed-vocabulary, deterministic text
classifier only.

WHAT THIS MODULE IS
--------------------
A pure function of (raw_intent, declared_purpose, in_scope_references,
out_of_scope_references) -> SemanticObservation. It reads the real,
already-materialized `pcpg_operation_index` (read-only: `execution_class`
is the Field's own catalog vocabulary, 04_OBSERVATION_RESULT.md §4,
already real and non-authority) to resolve candidate operations and the
DECISION_SUBSTITUTION_REQUESTED flag. It derives NOTHING about authority,
state, membership, role, evidence, capability or provider eligibility --
that is R-06 through R-10, later Work Units, explicitly out of scope here.

WHY CLAUSE SPLITTING DELIBERATELY OVER-SEGMENTS ON "AND"/"BUT"
------------------------------------------------------------------
A real syntactic parser would distinguish a coordinating conjunction
joining two clauses ("begin the analysis and start the investigation")
from one joining a noun phrase ("salt and pepper"). This module does not
attempt that distinction -- HA-PCPG-2 admits only reproducible, rule-based
derivation, and a genuine parser is out of reach without a model. It
always splits on top-level " and "/" but " (and their comma-joined forms)
alongside sentence punctuation. This over-segments compound noun phrases
into spurious extra "clauses", but that is SAFE by construction: a
spurious clause either matches no real operation (UNKNOWN, ignored
downstream) or, in the adversarial case, keeps each clause's own
modality strictly local -- negation in one clause never crosses into
another (`test_negation_does_not_suppress_the_other_clause_in_a_
compound_intent`, `test_over_splitting_on_and_never_reclassifies_a_
prohibited_action_as_requested`). Under-segmentation -- merging a
PROHIBITED clause into an adjacent REQUESTED one -- would be unsafe;
over-segmentation is not.

WHY `semantic_purpose`/`purpose_alignment` ARE MINIMAL, NOT SYNTHESIZED
------------------------------------------------------------------------
Free-text purpose summarization ("move the Session to INVESTIGATION with
an AI-chosen primary", the prose in `fixtures/NQUIRY_SESSION_AUTHORITY.
txt`) is itself a model-shaped computation. This module never attempts
it. `purpose_alignment` is a closed, deterministic bag-of-words overlap
check between `declared_purpose` and the REQUESTED-clause text, never a
generated sentence; `None` (not computable) is the fail-closed default,
never a guess.

WHY THE SECRET-PATTERN AND EXTERNAL-EFFECT DETECTORS ARE NARROW
------------------------------------------------------------------
`possible_secret_content` and `possible_external_effect` are closed
pattern/verb detectors, not the FBR-PCPG-3 data-class classifier
("No deterministic classifier exists for free text. GAP-11-006 is OPEN";
`00_FIELD.md` §12 -- a separate, later, still-open relation). They are
informational flags only, consumed (not authoritatively decided) by a
later relation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from application.pcpg_operation_index import ExecutionClass, operation_index

RULE_SET_VERSION = "SIMPLIX-1"
"""This module's own derivation version (I-19, HA-PCPG-2: reproducible
from (rule-set version, inputs)). Bump whenever the vocabulary or any
detection rule below changes in a way that could change an output."""


class Modality(Enum):
    """R-05's own OUTPUT vocabulary, verbatim from 02_RELATIONS.md."""

    ASSERTED = "ASSERTED"
    REQUESTED = "REQUESTED"
    CONDITIONAL = "CONDITIONAL"
    PROHIBITED = "PROHIBITED"
    HYPOTHETICAL = "HYPOTHETICAL"


class RequestedExecutor(Enum):
    """04_OBSERVATION_RESULT.md §5 delta-record field REQUESTED_EXECUTOR,
    stratum 2 -- "human, AI or unspecified, as the prompt asks". This is a
    purely textual reading, never an authority computation."""

    HUMAN = "HUMAN"
    AI = "AI"
    NONE = "NONE"


class SemanticObservationUnavailable(Exception):
    """R-05 FAILURE STATE, verbatim: "A SIMPLIX failure leaves the whole
    observation INDETERMINATE with reason SEMANTIC_OBSERVATION_UNAVAILABLE.
    Never a partial guess." Raised when not even one clause of the raw
    intent can be parsed."""


@dataclass(frozen=True, slots=True)
class SemanticAction:
    clause_index: int
    span: tuple[int, int]
    """Character offsets into the raw intent (P-02: every item cites its
    span)."""
    clause_text: str
    modality: Modality
    negated: bool
    requested_executor: RequestedExecutor
    candidate_operation: str | None
    """A real `pcpg_operation_index` operation_id, or `None` for UNKNOWN
    (I-04: never a closest-match guess)."""
    target: str | None
    """The resolved in-scope reference, the literal string "OUT_OF_SCOPE",
    or `None` for UNKNOWN (an unresolved referring expression, I-04)."""
    possible_external_effect: bool
    possible_secret_content: bool
    decision_substitution_requested: bool
    """True exactly when `requested_executor is AI` and the candidate
    operation's own real `execution_class` (pcpg_operation_index, read-
    only) is HUMAN_COMMAND -- 04_OBSERVATION_RESULT.md §4's own rule,
    computed from the Field's own catalog, never guessed."""


@dataclass(frozen=True, slots=True)
class SemanticObservation:
    rule_set_version: str
    raw_intent: str
    clauses: tuple[str, ...]
    actions: tuple[SemanticAction, ...]
    unknown_relations: tuple[str, ...]
    """Clause texts that could not be parsed at all (U4), excluded from
    `actions`."""
    relations_touched: frozenset[str]
    """The set of distinct real operation_ids any action names, regardless
    of modality."""
    declared_purpose: str | None
    """Echoed verbatim (I-01: the claim is DATA, never rewritten)."""
    semantic_purpose: str | None
    """A minimal, closed-vocabulary label -- never synthesized text. `None`
    when the requested/conditional actions do not share exactly one
    candidate operation."""
    purpose_alignment: str | None
    """"ALIGNED" or "DRIFTED" from a closed bag-of-words overlap check
    against `declared_purpose`; `None` when there is no declared purpose
    to compare against."""
    semantic_drift: bool
    """True when the requested/conditional actions' candidate operations
    span more than one distinct real `execution_class`."""


# ---------------------------------------------------------------------------
# Closed vocabulary: natural-language trigger phrase -> real operation_id.
# Every operation_id referenced here is validated, at import time, to be a
# real, already-materialized entry of `pcpg_operation_index` (I-20: no
# parallel operation vocabulary).
# ---------------------------------------------------------------------------

_OPERATION_TRIGGERS: tuple[tuple[str, str], ...] = (
    ("begin setup", "BEGIN_SETUP"),
    ("begin challenge capture", "BEGIN_CHALLENGE_CAPTURE"),
    ("prepare the burst", "PREPARE_BURST"),
    ("admit participant", "ADMIT_PARTICIPANT"),
    ("open question generation", "OPEN_QUESTION_GENERATION"),
    ("grant session control", "GRANT_SESSION_CONTROL"),
    ("capture the question", "CAPTURE_QUESTION"),
    ("complete the burst", "COMPLETE_BURST"),
    ("begin the analysis", "BEGIN_ANALYSIS"),
    ("analyse the questions", "REQUEST_QUESTION_ANALYSIS"),
    ("analyze the questions", "REQUEST_QUESTION_ANALYSIS"),
    ("cluster the questions", "REQUEST_QUESTION_CLUSTERING"),
    ("begin reflection", "BEGIN_REFLECTION"),
    ("begin question selection", "BEGIN_QUESTION_SELECTION"),
    ("select the compelling question", "SELECT_COMPELLING_QUESTION"),
    ("pick the most important", "SELECT_PRIMARY_QUESTION"),
    ("pick the primary question", "SELECT_PRIMARY_QUESTION"),
    ("create the impact chain", "CREATE_IMPACT_CHAIN"),
    ("append to the impact chain", "APPEND_IMPACT_CHAIN_NODE"),
    ("start the investigation", "BEGIN_INVESTIGATION"),
    ("create a workspace", "CREATE_WORKSPACE"),
    ("create a challenge", "CREATE_CHALLENGE"),
    ("add a member", "ADD_MEMBER"),
    ("grant authority", "GRANT_AUTHORITY_BINDING"),
    ("revoke authority", "REVOKE_AUTHORITY_BINDING"),
    ("create a session", "CREATE_SESSION"),
    ("open a decision", "OPEN_DECISION_CONSIDERATION"),
    ("record the decision", "RECORD_HUMAN_DECISION"),
)
# Longer triggers first, so a more specific phrase is never shadowed by a
# shorter substring of it (e.g. "pick the primary question" before any
# shorter, looser variant).
_OPERATION_TRIGGERS = tuple(sorted(_OPERATION_TRIGGERS, key=lambda pair: -len(pair[0])))

for _trigger, _operation_id in _OPERATION_TRIGGERS:
    if _operation_id not in operation_index():
        raise ValueError(
            f"pcpg_simplix vocabulary names {_operation_id!r}, which is not a real "
            f"pcpg_operation_index entry (I-20: no parallel operation vocabulary)"
        )

_NEGATION_MARKERS = ("do not", "don't", "never", "without")
_HYPOTHETICAL_MARKERS = ("if ",)
_HYPOTHETICAL_VERBS = ("were", "would")
_CONDITIONAL_MARKERS = ("if ",)
_FIRST_PERSON_VERB = re.compile(
    r"^i\s+(select|choose|pick|authorize|approve|decide|grant|revoke|create|mark)\b", re.IGNORECASE
)
_UNRESOLVED_REFERENT = re.compile(
    r"\b(it|that|this|them|those|the second one|the first one|the one)\b", re.IGNORECASE
)
_EXTERNAL_EFFECT_VERBS = (
    "delete",
    "remove",
    "destroy",
    "purge",
    "order",
    "pay",
    "send",
    "publish",
    "submit",
    "transmit",
    "email",
    "fetch",
    "subscribe",
    "charge",
)
_SECRET_PATTERN = re.compile(
    r"\b(?:sk|pk|api|key|token|secret|password|pwd)[-_][A-Za-z0-9-]{6,}\b", re.IGNORECASE
)
_ASCII_LETTER = re.compile(r"[A-Za-z]")

_CLAUSE_SPLIT = re.compile(
    r"(?:,\s+|\s+(?:and|but)\s+|[.!?;]+(?!['\"])\s*)",
    re.IGNORECASE,
)
"""Deliberately conservative (over-segmenting, never under-segmenting; see
the module docstring): a comma, a coordinating " and "/" but ", or a run
of sentence punctuation not immediately closing a quoted span (so a
quoted title's own internal "?" is never mistaken for a clause
boundary)."""

_STOPWORDS = frozenset(
    {
        "the",
        "a",
        "an",
        "to",
        "of",
        "for",
        "and",
        "but",
        "is",
        "it",
        "on",
        "in",
        "our",
        "we",
        "i",
        "you",
        "this",
        "that",
    }
)


def _split_clauses(raw_intent: str) -> list[tuple[int, int]]:
    """Returns (start, end) spans of non-empty clauses, in order."""
    spans: list[tuple[int, int]] = []
    pos = 0
    for match in _CLAUSE_SPLIT.finditer(raw_intent):
        end = match.start()
        if end > pos and raw_intent[pos:end].strip():
            stripped = raw_intent[pos:end]
            lead = len(stripped) - len(stripped.lstrip())
            trail = len(stripped) - len(stripped.rstrip())
            spans.append((pos + lead, end - trail))
        pos = match.end()
    if pos < len(raw_intent) and raw_intent[pos:].strip():
        stripped = raw_intent[pos:]
        lead = len(stripped) - len(stripped.lstrip())
        trail = len(stripped) - len(stripped.rstrip())
        spans.append((pos + lead, len(raw_intent) - trail))
    return spans


def _is_unparseable(clause: str) -> bool:
    letters = sum(1 for ch in clause if ch.isalpha())
    ascii_letters = len(_ASCII_LETTER.findall(clause))
    if letters == 0:
        return True
    return ascii_letters / max(letters, 1) < 0.5


def _match_operation(clause_lower: str) -> str | None:
    for trigger, operation_id in _OPERATION_TRIGGERS:
        if re.search(rf"\b{re.escape(trigger)}\b", clause_lower):
            return operation_id
    return None


def _resolve_target(
    clause: str,
    clause_lower: str,
    in_scope_references: dict[str, str],
    out_of_scope_references: dict[str, str],
) -> str | None:
    for reference_text in out_of_scope_references:
        if reference_text.lower() in clause_lower:
            return "OUT_OF_SCOPE"
    for reference_text, canonical_ref in in_scope_references.items():
        if reference_text.lower() in clause_lower:
            return canonical_ref
    if _UNRESOLVED_REFERENT.search(clause):
        return None
    return None


def _detect_modality(clause_lower: str, negated: bool, matched_operation: str | None) -> Modality:
    is_hypothetical = clause_lower.startswith(_HYPOTHETICAL_MARKERS) and any(
        v in clause_lower for v in _HYPOTHETICAL_VERBS
    )
    if is_hypothetical:
        return Modality.HYPOTHETICAL
    if clause_lower.startswith(_CONDITIONAL_MARKERS):
        return Modality.CONDITIONAL
    if negated:
        return Modality.PROHIBITED
    if matched_operation is not None:
        return Modality.REQUESTED
    # No known operation matched and no imperative/negation/conditional
    # shape detected: a bare declarative clause is a claim, not a request.
    if _looks_like_bare_imperative(clause_lower):
        return Modality.REQUESTED
    return Modality.ASSERTED


_ASSERTION_MARKERS = ("already", "has", "have", "is", "are", "was", "were", "we have")
_ASSERTION_MARKER_PATTERN = re.compile(
    r"\b(?:" + "|".join(re.escape(m) for m in _ASSERTION_MARKERS) + r")\b"
)
"""Word-boundary matching, not plain substring containment: a naive `in`
check on "are " previously misread "comp**are** our questions..." as
containing the claim marker "are " (the space-terminated form matched
inside the verb "compare" itself), misclassifying a real REQUESTED
imperative as ASSERTED. Found during R-06's own adversarial testing
(`test_pcpg_candidate_deltas.py::test_out_of_scope_target_is_carried_
through`), fixed here at SIMPLIX's own root rather than worked around in
a later relation -- the same "repair the root" discipline this Field has
followed throughout (WU-PFC-PCPG-1's coverage-guard repair, WU-PFC-PCPG-2's
stale-test-scope repair). A falsifier for this exact case now lives in
`test_pcpg_simplix.py` itself."""


def _looks_like_bare_imperative(clause_lower: str) -> bool:
    """A clause with no recognized claim marker and no explicit subject at
    all is read as an imperative directed at the product/assistant (the
    raw-intent box is, by this Field's own definition, a prompt to an
    AI). Clauses that assert a fact about the world ("Maya already
    approved it", "We have enough budget") are excluded by their own
    claim markers -- a closed, disclosed set, never a full grammar."""
    if _ASSERTION_MARKER_PATTERN.search(clause_lower):
        return False
    return not clause_lower.startswith(("i ", "we ", "maya ", "ravi "))


def _detect_negation(clause_lower: str) -> bool:
    return any(m in clause_lower for m in _NEGATION_MARKERS)


def _detect_executor(clause: str, clause_lower: str, modality: Modality) -> RequestedExecutor:
    if modality is Modality.ASSERTED:
        return RequestedExecutor.NONE
    if _FIRST_PERSON_VERB.match(clause.strip()):
        return RequestedExecutor.HUMAN
    return RequestedExecutor.AI


def observe_semantics(
    raw_intent: str,
    declared_purpose: str | None = None,
    *,
    in_scope_references: dict[str, str] | None = None,
    out_of_scope_references: dict[str, str] | None = None,
) -> SemanticObservation:
    """The R-05 producer. Pure, deterministic, no I/O of any kind."""
    in_scope = dict(in_scope_references or {})
    out_of_scope = dict(out_of_scope_references or {})

    spans = _split_clauses(raw_intent)
    actions: list[SemanticAction] = []
    unknown_relations: list[str] = []

    for index, (start, end) in enumerate(spans):
        clause = raw_intent[start:end]
        if _is_unparseable(clause):
            unknown_relations.append(clause)
            continue
        clause_lower = clause.lower()
        negated = _detect_negation(clause_lower)
        matched_operation = _match_operation(clause_lower)
        modality = _detect_modality(clause_lower, negated, matched_operation)
        executor = _detect_executor(clause, clause_lower, modality)
        target = _resolve_target(clause, clause_lower, in_scope, out_of_scope)
        possible_external_effect = any(
            re.search(rf"\b{re.escape(v)}\b", clause_lower) for v in _EXTERNAL_EFFECT_VERBS
        )
        possible_secret_content = bool(_SECRET_PATTERN.search(clause))

        decision_substitution_requested = False
        if matched_operation is not None and executor is RequestedExecutor.AI:
            entry = operation_index()[matched_operation]
            if entry.execution_class is ExecutionClass.HUMAN_COMMAND:
                decision_substitution_requested = True

        actions.append(
            SemanticAction(
                clause_index=index,
                span=(start, end),
                clause_text=clause,
                modality=modality,
                negated=negated,
                requested_executor=executor,
                candidate_operation=matched_operation,
                target=target,
                possible_external_effect=possible_external_effect,
                possible_secret_content=possible_secret_content,
                decision_substitution_requested=decision_substitution_requested,
            )
        )

    if not actions and not spans:
        raise SemanticObservationUnavailable(
            "SEMANTIC_OBSERVATION_UNAVAILABLE: no clause could be segmented"
        )
    if not actions and unknown_relations:
        raise SemanticObservationUnavailable(
            "SEMANTIC_OBSERVATION_UNAVAILABLE: no clause could be parsed"
        )

    relations_touched = frozenset(
        a.candidate_operation for a in actions if a.candidate_operation is not None
    )

    live_operations = [
        a.candidate_operation
        for a in actions
        if a.candidate_operation is not None
        and a.modality in (Modality.REQUESTED, Modality.CONDITIONAL)
    ]
    distinct_live = set(live_operations)
    semantic_purpose = next(iter(distinct_live)) if len(distinct_live) == 1 else None

    live_classes = {operation_index()[op].execution_class for op in distinct_live}
    semantic_drift = len(live_classes) > 1

    purpose_alignment: str | None = None
    if declared_purpose:
        declared_tokens = {
            t for t in re.findall(r"[a-z]+", declared_purpose.lower()) if t not in _STOPWORDS
        }
        action_tokens: set[str] = set()
        for a in actions:
            if a.modality in (Modality.REQUESTED, Modality.CONDITIONAL):
                action_tokens |= {
                    t for t in re.findall(r"[a-z]+", a.clause_text.lower()) if t not in _STOPWORDS
                }
        purpose_alignment = "ALIGNED" if declared_tokens & action_tokens else "DRIFTED"

    return SemanticObservation(
        rule_set_version=RULE_SET_VERSION,
        raw_intent=raw_intent,
        clauses=tuple(raw_intent[s:e] for s, e in spans),
        actions=tuple(actions),
        unknown_relations=tuple(unknown_relations),
        relations_touched=relations_touched,
        declared_purpose=declared_purpose,
        semantic_purpose=semantic_purpose,
        purpose_alignment=purpose_alignment,
        semantic_drift=semantic_drift,
    )


__all__ = [
    "RULE_SET_VERSION",
    "Modality",
    "RequestedExecutor",
    "SemanticAction",
    "SemanticObservation",
    "SemanticObservationUnavailable",
    "observe_semantics",
]
