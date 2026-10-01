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
instrumental-to-blocked analysis. Of these, the data-class union
(FBR-PCPG-3, `pcpg_data_classification.py`, CLOSED `checkpoint-PFC-
PCPG-14`) and the composed proof ceiling's own Session-level slice
(WU-PFC-PCPG-16, below) now have real, narrow producers; an AI-contract
output-class registry, the full per-input proof ceiling (I-12), and a
purpose-coherence rule beyond SIMPLIX's own minimal bag-of-words check
still have none. A non-empty retained set — which cannot occur today,
given the fact above, but which this code must still handle honestly if
`ALLOWED`/`dependency_edges` ever become real — is therefore still
`CompositionResult.INDETERMINATE`, reason
`COMPOSITION_CHECKS_NOT_MATERIALIZED`: never waved through as
`COMPOSABLE` without actually performing the checks that name requires.

WU-PFC-PCPG-16 UPDATE: SESSION-LEVEL I-12 COMPOSED PROOF CEILING
------------------------------------------------------------------
`01_INVARIANTS.md` I-12 names R-08 as one of its own CONSUMERS
("R-03, R-06, R-08"). `composed_proof_ceiling` composes the real,
already-passed-through `DeltaRecord.session_proof_ceiling` values across
`retained` — the most restrictive known value, or honestly `None` when
`retained` is empty or any contributing ceiling is unknown (never
silently diluted toward a weaker value — see `_compose_proof_ceiling`).
This is the narrow Session-level slice only: `SESSION PROOF MODE !=
FULL SOURCE PROVENANCE`; `PARTIAL I-12 != I-12 COMPLETE`. It does not
claim source authority, mutability, evidence status, per-input proof
class, or AI-provider output class — all remain exactly as disclosed
above, genuinely open.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from application.pcpg_delta_evaluation import DeltaRecord, Result

COMPOSITION_CHECKS_NOT_MATERIALIZED = "COMPOSITION_CHECKS_NOT_MATERIALIZED"
"""The reason a non-empty retained set is INDETERMINATE in this
increment: the real sub-checks R-08's own OUTPUT names have no producer
in this codebase (see the module docstring). WU-PFC-PCPG-16 update: the
"composed proof ceiling" sub-check is now PARTIALLY covered (see
`_compose_proof_ceiling` below) for the narrow Session-level slice only
— the richer per-input scope remains exactly as disclosed here."""

_PROOF_CEILING_RESTRICTIVENESS: dict[str, int] = {
    "GOVERNED": 0,
    "FIXTURE_NON_PROOF": 1,
}
"""HD-24 rule 5's own two real values (`inquiry_queries.proof_mode`),
ranked least to most restrictive — the only two values this Field's own
Session-level proof mode producer ever returns. An unrecognized string
is treated the same as unknown (never silently assumed `GOVERNED`)."""


def _compose_proof_ceiling(retained: tuple[DeltaRecord, ...]) -> str | None:
    """`01_INVARIANTS.md` I-12's own LAW: "a delta's output inherits the
    most restrictive ceiling of its inputs... no delta may raise a
    ceiling." Composing across the retained set picks the single most
    restrictive real ceiling among them — but only when EVERY retained
    delta's own ceiling is actually known: an unknown ceiling on even one
    retained delta is never silently diluted away by other, known-but-
    weaker ceilings (I-12's own "no delta may raise a ceiling", read
    conservatively — reporting a known composed ceiling when one input is
    genuinely unknown would itself be a kind of unwarranted raise). The
    composed result is honestly `None` instead. `None` when `retained` is
    empty: nothing to compose."""
    if not retained:
        return None
    ceilings = [r.session_proof_ceiling for r in retained]
    if any(c not in _PROOF_CEILING_RESTRICTIVENESS for c in ceilings):
        return None
    known_ceilings = [c for c in ceilings if c is not None]
    return max(known_ceilings, key=lambda c: _PROOF_CEILING_RESTRICTIVENESS[c])


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
    composed_proof_ceiling: str | None = None
    """I-12's own Session-level composed ceiling (WU-PFC-PCPG-16 update)
    — the most restrictive `session_proof_ceiling` among `retained`, or
    `None` when `retained` is empty or any contributing ceiling is
    unknown (see `_compose_proof_ceiling`)."""


def compose_effect(records: tuple[DeltaRecord, ...]) -> ComposedEffect:
    """The R-08 producer (this increment's own disclosed scope). Pure,
    deterministic, no I/O. Order-preserving over `records`."""
    retained = tuple(r for r in records if r.result is Result.ALLOWED)
    composed_proof_ceiling = _compose_proof_ceiling(retained)

    if not retained:
        return ComposedEffect(
            retained=(),
            composition_result=CompositionResult.COMPOSABLE,
            reason=None,
            composed_proof_ceiling=composed_proof_ceiling,
        )

    return ComposedEffect(
        retained=retained,
        composition_result=CompositionResult.INDETERMINATE,
        reason=COMPOSITION_CHECKS_NOT_MATERIALIZED,
        composed_proof_ceiling=composed_proof_ceiling,
    )


__all__ = [
    "COMPOSITION_CHECKS_NOT_MATERIALIZED",
    "ComposedEffect",
    "CompositionResult",
    "compose_effect",
]
