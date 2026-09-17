"""Actor Identity Model.

Source: 04_AUTHORITY_AND_DECISION_RIGHTS.md §3 (Actor Identity Model):
HUMAN_USER, SYSTEM_SERVICE, AI_PROCESSOR, EXTERNAL_SYSTEM. Closed —
these are the only 4 actor classes the architecture defines.

Non-collapse rule (04 §3.3, §3.2, 05 AC-05-007): only `HUMAN_USER` can
ever hold a `HumanAuthorityBinding`. `SYSTEM_SERVICE` gets
`SYSTEM_DERIVED` authority through an entirely different mechanism
(04 §8, not modeled here — PKG-03 does not implement SYSTEM_DERIVED
resolution, only rejects it as a route to a *human* right). `AI_PROCESSOR`
"may not receive human decision rights" (04 §3.3) — never, structurally,
regardless of any other input.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from semantic_types.ids import UserId


class ActorClass(str, Enum):
    """The 4 actor classes 04 §3 defines."""

    HUMAN_USER = "HUMAN_USER"
    SYSTEM_SERVICE = "SYSTEM_SERVICE"
    AI_PROCESSOR = "AI_PROCESSOR"
    EXTERNAL_SYSTEM = "EXTERNAL_SYSTEM"


@dataclass(frozen=True, slots=True)
class ActorIdentity:
    """The requesting actor, as `AuthorityResolver` receives it.

    `user_id` is present for every actor class (a `SYSTEM_SERVICE`,
    `AI_PROCESSOR`, or `EXTERNAL_SYSTEM` still needs *some* identifier
    for audit/correlation, 11 §8), but `AuthorityResolver` only ever
    consults it when `actor_class == HUMAN_USER` — see
    `resolver.py`'s docstring for why this is a structural guarantee,
    not a runtime convention a caller could accidentally bypass.
    """

    actor_class: ActorClass
    user_id: UserId


__all__ = ["ActorClass", "ActorIdentity"]
