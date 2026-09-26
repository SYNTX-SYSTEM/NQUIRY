"""Composition root for governed runtime ports (F02 WU-02.6).

One place that constructs the real SQLAlchemy-backed ports every governed
Command/Query handler needs from a single request-scoped connection. Both
`application.http_dispatch` and the real-PostgreSQL tests use it, so the
runtime and the tests exercise the same wiring. Adds no semantics: every
member is an existing port implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from authority.resolver import AuthorityResolver
from boundaries.bnd_014_commit import Bnd014CommitEvaluator
from commit.idempotency import SqlAlchemyIdempotencyRepository
from persistence.ai_authorization_repository import SqlAlchemyOperationAuthorizationRepository
from persistence.ai_record_repository import SqlAlchemyAIRecordRepository
from persistence.audit_repository import SqlAlchemyAuditRepository
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository
from persistence.burst_repository import SqlAlchemyBurstRepository
from persistence.challenge_repository import SqlAlchemyChallengeRepository
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.commit_repository import SqlAlchemyCommitRepository
from persistence.decision_repository import SqlAlchemyDecisionRepository
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.outbox_repository import SqlAlchemyOutboxRepository
from persistence.question_cluster_repository import SqlAlchemyQuestionClusterRepository
from persistence.question_repository import SqlAlchemyQuestionRepository
from persistence.session_participation_repository import SqlAlchemySessionParticipationRepository
from persistence.session_repository import SqlAlchemySessionRepository
from persistence.system_operation_reader import SqlAlchemySystemOperationReader
from persistence.workspace_repository import SqlAlchemyWorkspaceRepository
from semantic_types.clock import Clock


class RealClock:
    """`semantic_types.clock.Clock` port, real wall clock."""

    def now(self) -> datetime:
        return datetime.now(timezone.utc)


@dataclass
class GovernedPorts:
    connection: Any
    """A SQLAlchemy connection, typed `Any`: `application` may not import sqlalchemy."""
    clock: Clock = field(default_factory=RealClock)

    def __post_init__(self) -> None:
        c = self.connection
        self.workspaces = SqlAlchemyWorkspaceRepository(c)
        self.memberships = SqlAlchemyMembershipRepository(c)
        self.bindings = SqlAlchemyAuthorityBindingRepository(c)
        self.challenges = SqlAlchemyChallengeRepository(c)
        self.sessions = SqlAlchemySessionRepository(c)
        self.participations = SqlAlchemySessionParticipationRepository(c)
        self.bursts = SqlAlchemyBurstRepository(c)
        self.questions = SqlAlchemyQuestionRepository(c)
        self.decisions = SqlAlchemyDecisionRepository(c)
        self.commands = SqlAlchemyCommandRepository(c)
        self.audit = SqlAlchemyAuditRepository(c)
        self.outbox = SqlAlchemyOutboxRepository(c)
        self.commits = SqlAlchemyCommitRepository(c)
        self.idempotency = SqlAlchemyIdempotencyRepository(c)
        self.resolver = AuthorityResolver(self.memberships, self.bindings, self.clock)
        # F04 WU-04.3: operational AI records and operation authorizations.
        self.ai_records = SqlAlchemyAIRecordRepository(c)
        self.ai_authorizations = SqlAlchemyOperationAuthorizationRepository(c)
        self.system_operations = SqlAlchemySystemOperationReader(c)
        self.question_clusters = SqlAlchemyQuestionClusterRepository(c)

    def bnd014(self) -> Bnd014CommitEvaluator:
        return Bnd014CommitEvaluator(
            self.resolver,
            membership_repository=self.memberships,
            participation_repository=self.participations,
            system_operation_reader=self.system_operations,
        )


__all__ = ["GovernedPorts", "RealClock"]
