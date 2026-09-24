"""The frozen human question set: reconstruction and verification (F03).

03 TRN-SESS-005: "frozen-set identity must be reconstructable". The frozen raw
set is the Burst's membership at completion. Its fingerprint is a pure function
of immutable birth facts (`domain.burst_membership.compute_frozen_membership_
fingerprint`, FBR-F03-4), so it is recomputable at any time from canonical
persistence, including after later normalization or derived work on the
Questions. F04 (BEGIN_ANALYSIS / AIOP-001) must verify a frozen set through
`verify_frozen_set` before using it.

Read-only: nothing here writes.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.burst import QuestionBurst
from domain.burst_membership import (
    QuestionBurstMembership,
    compute_frozen_membership_fingerprint,
)
from semantic_types.ids import BurstId, QuestionId

from application.composition import GovernedPorts


@dataclass(frozen=True, slots=True)
class FrozenSetVerification:
    stored: str | None
    recomputed: str | None
    member_count: int

    @property
    def matches(self) -> bool:
        return self.stored is not None and self.stored == self.recomputed


def load_members(
    ports: GovernedPorts, burst_id: BurstId
) -> tuple[tuple[QuestionBurstMembership, ...], dict[QuestionId, str]]:
    members = ports.bursts.list_members(burst_id)
    texts: dict[QuestionId, str] = {}
    for member in members:
        question = ports.questions.get(member.question_id)
        if question is not None:
            texts[member.question_id] = question.original_text
    return members, texts


def recompute_frozen_fingerprint(ports: GovernedPorts, burst_id: BurstId) -> str | None:
    """The fingerprint of the Burst's CURRENT membership, or `None` if empty."""
    members, texts = load_members(ports, burst_id)
    if not members:
        return None
    return compute_frozen_membership_fingerprint(members, texts)


def verify_frozen_set(ports: GovernedPorts, burst: QuestionBurst) -> FrozenSetVerification:
    members, _ = load_members(ports, burst.burst_id)
    recomputed = recompute_frozen_fingerprint(ports, burst.burst_id)
    return FrozenSetVerification(
        stored=burst.frozen_membership_fingerprint,
        recomputed=recomputed,
        member_count=len(members),
    )


__all__ = [
    "FrozenSetVerification",
    "load_members",
    "recompute_frozen_fingerprint",
    "verify_frozen_set",
]
