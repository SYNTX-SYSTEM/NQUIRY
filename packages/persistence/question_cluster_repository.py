"""QuestionCluster / QuestionClusterMembership (09 §34 / §35; F04 WU-04.9).

Append-only: create and read, nothing else (the tables reject UPDATE / DELETE).
A cluster run is identified by `cluster_run_id` = the accepted AIOP-002
artifact. No method here can touch a Question, a Burst membership or a
fingerprint.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

import sqlalchemy as sa
from semantic_types.ids import ChallengeId, GenerationId, QuestionId, SessionId, WorkspaceId

from persistence.tables import question_cluster_memberships_table as m
from persistence.tables import question_clusters_table as c


@dataclass(frozen=True, slots=True)
class QuestionCluster:
    cluster_id: uuid.UUID
    workspace_id: WorkspaceId
    session_id: SessionId
    challenge_id: ChallengeId
    analysis_generation_id: GenerationId
    cluster_run_id: uuid.UUID
    label: str | None
    description: str | None
    created_at: datetime
    question_ids: tuple[QuestionId, ...] = ()


class SqlAlchemyQuestionClusterRepository:
    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def create_run(self, clusters: tuple[QuestionCluster, ...]) -> None:
        for cluster in clusters:
            self._connection.execute(
                sa.insert(c).values(
                    id=cluster.cluster_id,
                    workspace_id=cluster.workspace_id.value,
                    session_id=cluster.session_id.value,
                    challenge_id=cluster.challenge_id.value,
                    analysis_generation_id=cluster.analysis_generation_id.value,
                    cluster_run_id=cluster.cluster_run_id,
                    label=cluster.label,
                    description=cluster.description,
                    created_at=cluster.created_at,
                    record_version=1,
                )
            )
            for question_id in cluster.question_ids:
                self._connection.execute(
                    sa.insert(m).values(
                        id=uuid.uuid4(),
                        workspace_id=cluster.workspace_id.value,
                        session_id=cluster.session_id.value,
                        question_cluster_id=cluster.cluster_id,
                        question_id=question_id.value,
                        cluster_run_id=cluster.cluster_run_id,
                        created_at=cluster.created_at,
                    )
                )

    def list_run(self, session_id: SessionId) -> tuple[QuestionCluster, ...]:
        rows = list(
            self._connection.execute(
                sa.select(c).where(c.c.session_id == session_id.value).order_by(c.c.label, c.c.id)
            ).mappings()
        )
        members: dict[uuid.UUID, list[QuestionId]] = {}
        for row in self._connection.execute(
            sa.select(m.c.question_cluster_id, m.c.question_id).where(
                m.c.session_id == session_id.value
            )
        ):
            members.setdefault(row[0], []).append(QuestionId(row[1]))
        return tuple(
            QuestionCluster(
                cluster_id=r["id"],
                workspace_id=WorkspaceId(r["workspace_id"]),
                session_id=SessionId(r["session_id"]),
                challenge_id=ChallengeId(r["challenge_id"]),
                analysis_generation_id=GenerationId(r["analysis_generation_id"]),
                cluster_run_id=r["cluster_run_id"],
                label=r["label"],
                description=r["description"],
                created_at=r["created_at"],
                question_ids=tuple(members.get(r["id"], ())),
            )
            for r in rows
        )


__all__ = ["QuestionCluster", "SqlAlchemyQuestionClusterRepository"]
