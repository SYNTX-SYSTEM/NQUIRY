"""ImpactChain and its answer nodes (09 §48; WU-PFC-B4 under HD-26).

Create, append and read, nothing else. The tables reject every other write:
nodes are append-only (S1(i)), a chain's anchor columns are immutable, and its
`record_version` advances by exactly one per appended node.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

import sqlalchemy as sa
from semantic_types.ids import QuestionId, SessionId, UserId, WorkspaceId
from semantic_types.versions import RecordVersion

from persistence.tables import impact_chain_nodes_table as n
from persistence.tables import impact_chains_table as c


@dataclass(frozen=True, slots=True)
class ImpactChainNode:
    node_id: uuid.UUID
    level: int
    answer_content: str
    author_user_id: UserId
    captured_at: datetime


@dataclass(frozen=True, slots=True)
class ImpactChain:
    impact_chain_id: uuid.UUID
    workspace_id: WorkspaceId
    session_id: SessionId
    selected_question_id: QuestionId
    created_by_user_id: UserId
    created_at: datetime
    record_version: RecordVersion
    nodes: tuple[ImpactChainNode, ...] = ()

    @property
    def next_level(self) -> int:
        return len(self.nodes) + 1


def impact_chain_target_ref(impact_chain_id: uuid.UUID) -> str:
    return f"impact_chain:{impact_chain_id}"


class SqlAlchemyImpactChainRepository:
    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def create(self, chain: ImpactChain) -> None:
        self._connection.execute(
            sa.insert(c).values(
                id=chain.impact_chain_id,
                workspace_id=chain.workspace_id.value,
                session_id=chain.session_id.value,
                selected_question_id=chain.selected_question_id.value,
                created_by_user_id=chain.created_by_user_id.value,
                created_at=chain.created_at,
                record_version=chain.record_version.value,
            )
        )

    def append(self, chain: ImpactChain, node: ImpactChainNode) -> RecordVersion:
        """Inserts `node` and advances the chain's version by one. Returns the
        new version. The DB triggers re-check successive level and author."""
        self._connection.execute(
            sa.insert(n).values(
                id=node.node_id,
                workspace_id=chain.workspace_id.value,
                impact_chain_id=chain.impact_chain_id,
                session_id=chain.session_id.value,
                selected_question_id=chain.selected_question_id.value,
                level=node.level,
                answer_content=node.answer_content,
                author_user_id=node.author_user_id.value,
                captured_at=node.captured_at,
            )
        )
        after = chain.record_version.value + 1
        self._connection.execute(
            sa.update(c)
            .where(
                c.c.id == chain.impact_chain_id, c.c.record_version == chain.record_version.value
            )
            .values(record_version=after)
        )
        return RecordVersion(after)

    def get(self, impact_chain_id: uuid.UUID) -> ImpactChain | None:
        row = (
            self._connection.execute(sa.select(c).where(c.c.id == impact_chain_id))
            .mappings()
            .one_or_none()
        )
        return None if row is None else self._with_nodes(row)

    def get_for_anchor(
        self, session_id: SessionId, selected_question_id: QuestionId
    ) -> ImpactChain | None:
        row = (
            self._connection.execute(
                sa.select(c).where(
                    c.c.session_id == session_id.value,
                    c.c.selected_question_id == selected_question_id.value,
                )
            )
            .mappings()
            .one_or_none()
        )
        return None if row is None else self._with_nodes(row)

    def _with_nodes(self, row: sa.RowMapping) -> ImpactChain:
        nodes = self._connection.execute(
            sa.select(n).where(n.c.impact_chain_id == row["id"]).order_by(n.c.level)
        ).mappings()
        return ImpactChain(
            impact_chain_id=row["id"],
            workspace_id=WorkspaceId(row["workspace_id"]),
            session_id=SessionId(row["session_id"]),
            selected_question_id=QuestionId(row["selected_question_id"]),
            created_by_user_id=UserId(row["created_by_user_id"]),
            created_at=row["created_at"],
            record_version=RecordVersion(row["record_version"]),
            nodes=tuple(
                ImpactChainNode(
                    node_id=r["id"],
                    level=int(r["level"]),
                    answer_content=r["answer_content"],
                    author_user_id=UserId(r["author_user_id"]),
                    captured_at=r["captured_at"],
                )
                for r in nodes
            ),
        )


class SqlAlchemyImpactChainVersionReader:
    """`commit.coordinator.CurrentVersionReader` for one ImpactChain."""

    def __init__(self, connection: sa.Connection, *, impact_chain_id: uuid.UUID) -> None:
        self._connection = connection
        self._id = impact_chain_id

    def read(self, target_ref: str) -> RecordVersion | None:
        if target_ref != impact_chain_target_ref(self._id):
            return None
        row = self._connection.execute(
            sa.select(c.c.record_version).where(c.c.id == self._id)
        ).one_or_none()
        return None if row is None else RecordVersion(row[0])


__all__ = [
    "ImpactChain",
    "ImpactChainNode",
    "SqlAlchemyImpactChainRepository",
    "SqlAlchemyImpactChainVersionReader",
    "impact_chain_target_ref",
]
