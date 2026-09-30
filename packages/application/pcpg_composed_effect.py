"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — R-08: composed effect (Architecture 26).

Source: `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md`
R-08: "OUTPUT: the retained set: deltas that are ALLOWED as
PROVIDER_COMPUTATION and whose dependencies are all retained ... the
composition result: COMPOSABLE, or the boundary class with a reason."

WHY THE RETAINED SET IS ALWAYS EMPTY IN THE CURRENT REAL FIELD
--------------------------------------------------------------
WU-PFC-PCPG-7 proved, as an architectural fact: every `PROVIDER_
COMPUTATION` delta is unconditionally `Result.GOVERNANCE_BOUNDARY`
today (HA-PCPG-1's own fail-closed default). Since the retained set is
defined as exactly "deltas that are ALLOWED", it is always empty for
every real observation today — not a limitation of this module, a
cross-checked fact now observed from a third independent direction.

WHY "WHOSE DEPENDENCIES ARE ALL RETAINED" NEEDS NO GRAPH TRAVERSAL HERE
-------------------------------------------------------------------------
`pcpg_candidate_deltas.py`'s own disclosed scope (R-06, DIRECT deltas
only) makes `dependency_edges` always `()`. "All of zero dependencies
are retained" is vacuously true for every delta today, so the retained-
set filter is exactly `result is Result.ALLOWED` — a real simplification
that follows from an already-disclosed upstream fact, not a new one
invented here.

WHY A NON-EMPTY RETAINED SET IS `INDETERMINATE`, NEVER A GUESSED
`COMPOSABLE`
------------------------------------------------------------------
R-08's own OUTPUT also names: the union of inputs and data classes; that
external effects must be none; that canonical effects stay within each
contract's maximum; the composed proof ceiling; purpose coherence; the
instrumental-to-blocked analysis. None of these has a producer anywhere
in this codebase (no data-class classifier, FBR-PCPG-3/GAP-11-006 still
OPEN; no AI-contract output-class registry; no proof-ceiling producer;
no purpose-coherence rule beyond SIMPLIX's own minimal bag-of-words
check). A non-empty retained set — which cannot occur today, given the
fact above, but which this code must still handle honestly if
`ALLOWED`/`dependency_edges` ever become real — is therefore
`CompositionResult.INDETERMINATE`, reason
`COMPOSITION_CHECKS_NOT_MATERIALIZED`: never waved through as
`COMPOSABLE` without actually performing the checks that name requires.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from application.pcpg_delta_evaluation import DeltaRecord, Result

COMPOSITION_CHECKS_NOT_MATERIALIZED = "COMPOSITION_CHECKS_NOT_MATERIALIZED"
"""The reason a non-empty retained set is INDETERMINATE in this
increment: the real sub-checks R-08's own OUTPUT names have no producer
in this codebase (see the module docstring)."""


class CompositionResult(Enum):
    """`04_OBSERVATION_RESULT.md` §7.1, this Field's own vocabulary,
    first materialized here (I-20). `COMPOSABLE` and the three named
    `COMPOSITION_<CLASS>` boundary reasons are the real, cited values;
    `INDETERMINATE` is this increment's own honest disclosure for a case
    it cannot yet check (never a guessed `COMPOSABLE`)."""

    COMPOSABLE = "COMPOSABLE"
    COMPOSITION_DATA_BOUNDARY = "COMPOSITION_DATA_BOUNDARY"
    COMPOSITION_EXTERNAL_EFFECT = "COMPOSITION_EXTERNAL_EFFECT"
    COMPOSITION_GOVERNANCE_BOUNDARY = "COMPOSITION_GOVERNANCE_BOUNDARY"
    INDETERMINATE = "INDETERMINATE"


@dataclass(frozen=True, slots=True)
class ComposedEffect:
    retained: tuple[DeltaRecord, ...]
    composition_result: CompositionResult
    reason: str | None


def compose_effect(records: tuple[DeltaRecord, ...]) -> ComposedEffect:
    """The R-08 producer (this increment's own disclosed scope). Pure,
    deterministic, no I/O. Order-preserving over `records`."""
    retained = tuple(r for r in records if r.result is Result.ALLOWED)

    if not retained:
        return ComposedEffect(
            retained=(), composition_result=CompositionResult.COMPOSABLE, reason=None
        )

    return ComposedEffect(
        retained=retained,
        composition_result=CompositionResult.INDETERMINATE,
        reason=COMPOSITION_CHECKS_NOT_MATERIALIZED,
    )


__all__ = [
    "COMPOSITION_CHECKS_NOT_MATERIALIZED",
    "ComposedEffect",
    "CompositionResult",
    "compose_effect",
]
