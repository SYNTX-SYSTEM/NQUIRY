"""The source-explicit participation right (F03 HD-15, 04 AUTH-DEP-Q-001).

One definition, used by BOTH the precommit boundary (BND-005 participation
evaluator) and the effect gate (BND-014, PARTICIPATION source), so the two can
never disagree about who holds the right.

The right is held by an authenticated HUMAN actor with a CURRENT
`SessionParticipation` (left_at NULL) in the named Session, in the same
Workspace, whose Workspace membership is still ACTIVE. It is re-read live on
every call (never cached). It is not a role, not a binding and not a client
claim; the Workspace role label is "not sufficient or necessary" (04 §40).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from authority.actor import ActorClass, ActorIdentity
from persistence.membership_repository import MembershipRepository
from persistence.session_participation_repository import SessionParticipationRepository
from semantic_types.ids import SessionId, WorkspaceId


@dataclass(frozen=True, slots=True)
class ParticipationResolution:
    granted: bool
    reason_code: str
    participation_id: uuid.UUID | None = None


def resolve_participation_right(
    *,
    participation_repository: SessionParticipationRepository | None,
    membership_repository: MembershipRepository | None,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session_id: uuid.UUID,
) -> ParticipationResolution:
    if participation_repository is None or membership_repository is None:
        return ParticipationResolution(False, "PARTICIPATION_READER_NOT_CONFIGURED")
    if actor.actor_class is not ActorClass.HUMAN_USER:
        return ParticipationResolution(False, "PARTICIPATION_ACTOR_NOT_HUMAN")
    participation = participation_repository.get_current(SessionId(session_id), actor.user_id)
    if participation is None or participation.workspace_id != workspace_id:
        return ParticipationResolution(False, "PARTICIPATION_NOT_CURRENT")
    if membership_repository.get_current_membership(workspace_id, actor.user_id) is None:
        return ParticipationResolution(False, "PARTICIPATION_NO_ACTIVE_MEMBERSHIP")
    return ParticipationResolution(True, "PARTICIPATION_CURRENT", participation.participation_id)


__all__ = ["ParticipationResolution", "resolve_participation_right"]
