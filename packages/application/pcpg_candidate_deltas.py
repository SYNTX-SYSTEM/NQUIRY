"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — R-06: candidate delta formation
(Architecture 26).

Source: `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md`
R-06: "PRODUCER: the governance evaluation (stratum 3), from R-05 and the
operation index... INPUT: the semantic observation and the Field
snapshot." (R-06's own prose is the authority here, not the header
diagram's more compressed drawing — `WU-PFC-PCPG-4.md` §0's SFE
correction: R-06 does not consume Pulse.)

WHAT THIS MODULE IS
--------------------
A pure function of (SemanticObservation, FieldSnapshot) -> candidate
deltas. It invents nothing: `operation` and `execution_class` are read
straight from the real, already-closed `pcpg_operation_index`; `target`
and `source_clause`/`span` are read straight from the real R-05 output;
`current_state` is read straight from the real R-03 snapshot.

SCOPE OF THIS WORK UNIT (disclosed, not silently narrowed)
------------------------------------------------------------
DIRECT deltas only — one per REQUESTED-modality semantic action. NOT
covered: IMPLIED intermediate deltas. R-06's own PRECONDITION gives the
worked example: "an order requires an approval... on a Session already
in ANALYSIS no BEGIN_ANALYSIS delta is implied" — this needs a canonical
"operation X requires canonical relation/state Y, already-satisfied or
not" index, which exists nowhere in this codebase today. Building one now
would be a second, separate, large relation of its own (its own
completeness proof, its own adversarial fixtures), not this increment's
minimum coherent delta. Every `CandidateDelta.dependency_edges` here is
therefore always `()`, and `proposed_state` is always `None` — both
disclosed, neither fabricated. A future Work Unit that materializes the
canonical-chain index closes this gap; nothing here forecloses it.

WHY ONLY REQUESTED-MODALITY ACTIONS FORM A DELTA
----------------------------------------------------
R-06's own PRECONDITION: "every requested action yields a delta; none is
dropped" — read literally. `02_RELATIONS.md` R-05's own PROOF already
established "Negated, hypothetical and prohibited actions never become
requested actions"; `fixtures/UNKNOWN_INTENT.txt` U5 states the
consequence directly: "ORDER is NOT a requested delta" for a negated
clause. PROHIBITED, HYPOTHETICAL, CONDITIONAL and ASSERTED actions
therefore form no delta at all in this module — not a weaker delta, no
delta.

WU-PFC-PCPG-16 UPDATE: SESSION-LEVEL I-12 PROOF CEILING CARRIED HERE
--------------------------------------------------------------------------
`01_INVARIANTS.md` I-12: "The source authority, mutability, evidence
status and proof class of every input are quoted canonically... Fixture
scopes stay FIXTURE_NON_PROOF." I-12's own CONSUMERS are named verbatim
as "R-03, R-06, R-08" — R-06 is explicitly one of them. The already-real,
already-authoritative fact is `snapshot.session.proof_mode` (R-03,
`checkpoint-PFC-PCPG-4`; itself produced by `inquiry_queries.proof_mode`,
HD-24 rule 5: `"FIXTURE_NON_PROOF" if fixture else "GOVERNED"`) — this
Work Unit does not create a second producer for it, only quotes it
canonically onto each `CandidateDelta`, exactly as I-12's own LAW
requires ("quoted canonically", never re-derived).

Disclosed, narrow scope: `session_proof_ceiling` carries ONLY the
Session-level fact (`"FIXTURE_NON_PROOF"` / `"GOVERNED"`, or `None` when
no Session is named — never guessed). It does NOT carry source
authority, mutability status, evidence status, or the proof class of any
individual input beyond the Session itself, and it is never inferred
from `target` (a free-form, already-resolved reference string, never
treated as a lookup key into any canonical object — I-12's own richer
per-input scope remains genuinely open, `WU-PFC-PCPG-13.md`/`WU-PFC-
PCPG-16.md` §1). `PARTIAL I-12 != I-12 COMPLETE`.
"""

from __future__ import annotations

from dataclasses import dataclass

from application.pcpg_field_snapshot import FieldSnapshot
from application.pcpg_operation_index import ExecutionClass, resolve_operation
from application.pcpg_simplix import Modality, SemanticObservation


@dataclass(frozen=True, slots=True)
class CandidateDelta:
    delta_id: str
    """Stable within one observation (R-06's own OUTPUT: "an identity")."""
    source_clause: str
    span: tuple[int, int]
    """P-02: traces to its span in the raw intent."""
    target: str | None
    """The real, already-resolved R-05 target: a canonical reference, the
    literal "OUT_OF_SCOPE", or `None` for UNKNOWN."""
    operation: str | None
    """A real `pcpg_operation_index` operation_id, or `None` for UNKNOWN
    (I-04: never a closest-match guess)."""
    execution_class: ExecutionClass
    """Read from the real catalog when `operation` is known;
    `ExecutionClass.UNKNOWN` otherwise — never re-derived (I-20)."""
    current_state: str | None
    """The real Session state from the Field snapshot, or `None` when no
    Session is named."""
    proposed_state: str | None
    """Always `None` in this increment — see the module docstring."""
    dependency_edges: tuple[str, ...]
    """Always `()` in this increment — see the module docstring
    (IMPLIED-delta formation is out of scope)."""
    session_proof_ceiling: str | None = None
    """I-12's own Session-level proof ceiling, quoted canonically from
    `snapshot.session.proof_mode` — `None` when no Session is named
    (never guessed). WU-PFC-PCPG-16 update, module docstring."""


def form_candidate_deltas(
    observation: SemanticObservation, snapshot: FieldSnapshot
) -> tuple[CandidateDelta, ...]:
    """The R-06 producer (DIRECT deltas only). Pure, deterministic, no I/O."""
    current_state = snapshot.session.state if snapshot.session is not None else None
    session_proof_ceiling = snapshot.session.proof_mode if snapshot.session is not None else None

    deltas: list[CandidateDelta] = []
    for index, action in enumerate(observation.actions):
        if action.modality is not Modality.REQUESTED:
            continue
        execution_class = ExecutionClass.UNKNOWN
        if action.candidate_operation is not None:
            entry = resolve_operation(action.candidate_operation)
            if entry is not None:
                execution_class = entry.execution_class
        deltas.append(
            CandidateDelta(
                delta_id=f"D{index}",
                source_clause=action.clause_text,
                span=action.span,
                target=action.target,
                operation=action.candidate_operation,
                execution_class=execution_class,
                current_state=current_state,
                proposed_state=None,
                dependency_edges=(),
                session_proof_ceiling=session_proof_ceiling,
            )
        )
    return tuple(deltas)


__all__ = ["CandidateDelta", "form_candidate_deltas"]
