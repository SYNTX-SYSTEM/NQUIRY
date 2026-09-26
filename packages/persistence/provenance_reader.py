"""Immutable-records-only reader for F04 inverse provenance (§0.1 rule 8).

Every method reads ONLY write-once facts: accepted artifacts (append-only),
the IDENTITY columns of a generation (trigger-immutable; never `status`),
operation authorizations (immutable), Commands (immutable) and their COMMITTED
audit rows (append-only). It has no access to Session state, generation
status or "the currently accepted artifact" (falsifier E16).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

import sqlalchemy as sa

from persistence.tables import (
    ai_derived_artifacts_table,
    ai_generations_table,
    ai_operation_authorizations_table,
    ai_validation_proofs_table,
    audit_events_table,
    commands_table,
)


@dataclass(frozen=True, slots=True)
class ArtifactFact:
    artifact_id: uuid.UUID
    ai_operation_id: str
    ai_generation_id: uuid.UUID
    accepted_by_command_id: uuid.UUID | None
    content: str
    content_fingerprint: str


@dataclass(frozen=True, slots=True)
class ProofFact:
    """The immutable AI_VALIDATION_PROOF of a generation (09 §56; review R1)."""

    proof_id: uuid.UUID
    ai_generation_id: uuid.UUID
    ai_operation_id: str
    validation_result: str
    output_fingerprint: str


@dataclass(frozen=True, slots=True)
class GenerationIdentityFact:
    generation_id: uuid.UUID
    ai_operation_id: str
    operation_authorization_id: uuid.UUID | None
    authorizing_command_id: uuid.UUID | None
    retry_of_generation_id: uuid.UUID | None
    precondition_artifact_ref: uuid.UUID | None
    provider: str


@dataclass(frozen=True, slots=True)
class AuthorizationFact:
    authorization_id: uuid.UUID
    shape: str
    ai_operation_id: str
    authorizing_command_id: uuid.UUID
    chain_root_command_id: uuid.UUID
    request_case: str | None
    supersedes_authorization_id: uuid.UUID | None
    retry_of_generation_id: uuid.UUID | None
    precondition_artifact_ref: uuid.UUID | None


@dataclass(frozen=True, slots=True)
class CommittedAuditFact:
    command_id: uuid.UUID
    command_type: str
    actor_type: str
    actor_id: str
    authority_source_type: str | None
    authority_source_ref: uuid.UUID
    authority_scope_ref: str | None


class SqlAlchemyImmutableProvenanceReader:
    def __init__(self, connection: sa.Connection) -> None:
        self._c = connection

    def artifact(self, artifact_id: uuid.UUID) -> ArtifactFact | None:
        a = ai_derived_artifacts_table
        row = self._c.execute(
            sa.select(
                a.c.id,
                a.c.ai_operation_id,
                a.c.ai_generation_id,
                a.c.accepted_by_command_id,
                a.c.content,
                a.c.content_fingerprint,
            ).where(a.c.id == artifact_id)
        ).one_or_none()
        return None if row is None else ArtifactFact(*row)

    def validation_proof(self, generation_id: uuid.UUID) -> ProofFact | None:
        v = ai_validation_proofs_table
        row = self._c.execute(
            sa.select(
                v.c.id,
                v.c.ai_generation_id,
                v.c.ai_operation_id,
                v.c.validation_result,
                v.c.output_fingerprint,
            ).where(v.c.ai_generation_id == generation_id)
        ).one_or_none()
        return None if row is None else ProofFact(*row)

    def generation_identity(self, generation_id: uuid.UUID) -> GenerationIdentityFact | None:
        g = ai_generations_table
        row = self._c.execute(
            sa.select(
                g.c.id,
                g.c.ai_operation_id,
                g.c.operation_authorization_id,
                g.c.authorizing_command_id,
                g.c.retry_of_generation_id,
                g.c.precondition_artifact_ref,
                g.c.provider,
            ).where(g.c.id == generation_id)
        ).one_or_none()
        return None if row is None else GenerationIdentityFact(*row)

    def authorization(self, authorization_id: uuid.UUID) -> AuthorizationFact | None:
        t = ai_operation_authorizations_table
        row = self._c.execute(
            sa.select(
                t.c.id,
                t.c.shape,
                t.c.ai_operation_id,
                t.c.authorizing_command_id,
                t.c.chain_root_command_id,
                t.c.request_case,
                t.c.supersedes_authorization_id,
                t.c.retry_of_generation_id,
                t.c.precondition_artifact_ref,
            ).where(t.c.id == authorization_id)
        ).one_or_none()
        return None if row is None else AuthorizationFact(*row)

    def committed_audit(self, command_id: uuid.UUID) -> CommittedAuditFact | None:
        a, c = audit_events_table, commands_table
        row = self._c.execute(
            sa.select(
                a.c.command_id,
                c.c.command_type,
                a.c.actor_type,
                a.c.actor_id,
                a.c.authority_source_type,
                a.c.authority_source_ref,
                a.c.authority_scope_ref,
            )
            .join(c, sa.and_(c.c.id == a.c.command_id, c.c.workspace_id == a.c.workspace_id))
            .where(a.c.command_id == command_id, a.c.result == "COMMITTED")
        ).one_or_none()
        return None if row is None else CommittedAuditFact(*row)


__all__ = [
    "ArtifactFact",
    "AuthorizationFact",
    "CommittedAuditFact",
    "GenerationIdentityFact",
    "ProofFact",
    "SqlAlchemyImmutableProvenanceReader",
]
