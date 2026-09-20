"""Human identity (PKG-01) and runtime service identity / DB-principal
capability map (PKG-25).

Source: 14_IMPLEMENTATION_SEQUENCE.md §32 (AUTHENTICATION AND SERVICE
IDENTITY) — the `AuthenticatedPrincipal` shape is taken verbatim from
there. 11_SECURITY_PRIVACY_OBSERVABILITY.md §5–§7 (Human Identity,
Authentication Session Contract, Identity to Workspace Resolution) and
06_BOUNDARY_ARCHITECTURE.md §7 (BND-001 IDENTITY BOUNDARY) ground the
non-collapse rule below.

PKG-01 SCOPE NOTE: this module defines the identity *port* only — the
shape authentication resolves to, and the Protocol a caller uses to
resolve it. It does not implement a production OIDC adapter.
`GAP-14-001` (Reference Authentication Provider Selection, 15 §0)
remains open; a concrete production adapter is future work, gated by
that gap being resolved. The deterministic test adapter lives in
`packages/test_support/identity.py` (14 §32: "Test adapter is
deterministic").

Non-collapse rule (11 §1 AC-11-001, 06 §7 BND-001): IDENTITY != AUTHORITY.
`AuthenticatedPrincipal` proves WHO IS CALLING only — it structurally
cannot carry a role, permission, or any other authority-shaped field.
A claims payload containing e.g. `role: "admin"` must have no effect on
and no representation in the resolved principal (11 §6 AC-11-002 item 7:
"session material is never accepted as a client-supplied
HumanAuthorityBinding").

PKG-25 ADDITION: `ServicePrincipal`/`TableOperation`/`TableCapability`/
`SECURITY_CAPABILITY_MAP` below materialize this package's own PUBLIC
INTERFACE ("security capability map") and its OBJECTIVE ("Runtime
technical identities and privilege separation... migration_owner,
api_reader, governed_commit_writer, ai_gateway_writer,
projection_writer, recovery_reader, security_event_writer,
audit_reader, test_principal. No runtime superuser."). This module's
own `AuthenticatedPrincipal`/`IdentityPort` above (PKG-01) resolve WHO
a human is; `ServicePrincipal` below names WHICH technical/DB identity
a service-to-service or worker call runs as (11 §8 AC-11-003: "Service
identity proves which technical principal called. It does not prove
that the requested domain consequence is authorized"). The two are
deliberately unrelated types — a human's `AuthenticatedPrincipal` never
becomes a `ServicePrincipal` and vice versa.

WHY THIS CAPABILITY MAP IS CODE-GROUNDED, NOT INVENTED
--------------------------------------------------------------------
Every table -> principal assignment below was derived by TRACING
which real, already-merged repository class in `packages/persistence/`
and `packages/commit/idempotency.py` actually issues an
INSERT/UPDATE/DELETE against that table today (verified via
`grep -oE 'sa\\.(insert|update|delete)\\(' packages/persistence/*.py
packages/commit/idempotency.py`), not by guessing at a plausible-looking
future architecture. A table with NO real production writer anywhere in
this codebase yet (`users`, `workspaces`, `workspace_memberships`,
`role_assignments`, `human_authority_bindings`, `challenges`,
`sessions` -- all read-only repositories today, per PKG-01/02/03's own
scope: no governed Command has been assigned to mutate them anywhere in
the 32-package DAG as of PKG-25) receives NO write grant to ANY of the
9 principals here -- only `api_reader` (read) and `test_principal`
(NON_PROOF fixture power) may touch them at all. 11 §15's own words
apply literally: "Database-level permission is a necessary
infrastructure capability for the approved path. It is never sufficient
legitimacy" -- granting write capability for a path that does not exist
yet would be exactly the kind of speculative invention this codebase's
own DIFF_AUDIT discipline forbids. When a future package builds a real
governed writer for one of these tables, THAT package must extend this
map, not this one.

WHY `recovery_reader` GETS FULL CRUD ON `recovery_records` DESPITE ITS
NAME
--------------------------------------------------------------------
14's own PKG-25 OBJECTIVE names this principal literally
`recovery_reader`; `migrations/versions/b7ec21429b53_recovery_command_fields.py`'s
own docstring (written at PKG-24, before this package existed) already
disclosed "No `recovery_reader`/any `RecoveryRepository` DB-principal
GRANT is created here... deferred to `012_security_events_rls`" —
naming `recovery_reader` as the ONE principal covering ALL of
`RecoveryRepository`'s own DB access, not merely its read methods.
`RecoveryService.resolve_recovery` (PKG-24) deliberately does NOT route
through `CommitCoordinator`/`governed_commit_writer` (see
`application.recovery_handler`'s own module docstring) -- it is its own,
separate governed write path, and therefore needs its own, separate DB
principal. The name is this package's own literal label, not a
constraint that the principal must be read-only.

WHY `security_event_writer` HAS A ROLE BUT NO GRANT YET
--------------------------------------------------------------------
`security_events` (the table this principal writes) does not exist
until PKG-26's own migration creates it — the identical "role/entry
exists now, its one grant is deferred to the package that creates the
target" pattern `recovery_reader` itself just followed one package
earlier. The role is still created here (roles are cluster-wide
objects, independent of any one table's existence) so PKG-26 only has
to `GRANT`, not also `CREATE ROLE`.

WHY `migration_owner` HAS NO ROW IN `SECURITY_CAPABILITY_MAP`
--------------------------------------------------------------------
`migration_owner` is a DDL identity (11 §15: "MIGRATION_PRINCIPAL:
schema migration capability, not domain mutation authority"), not a
row-level DML identity — its own one capability is
`CREATE ON SCHEMA public` (see `migrate_role_grants`'s own migration),
which this table-keyed map has no way to represent. It is still a
`ServicePrincipal` member (14's own literal 9-name list), just outside
this particular map's own shape.

WHY THE EXISTING 5 "no governed writer yet" TABLES ARE NOT SILENTLY
GRANTED TO `governed_commit_writer` "JUST IN CASE"
--------------------------------------------------------------------
See the "code-grounded" note above — the same discipline applies in
both directions: neither inventing a narrower boundary the architecture
never drew, nor inventing a broader grant no real caller needs yet.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol, runtime_checkable

from semantic_types.ids import UserId


@dataclass(frozen=True, slots=True)
class AuthenticatedPrincipal:
    """Exactly the shape from 14 §32: `AuthenticatedPrincipal(UserId,
    authentication_session_ref, authentication_time, issuer_ref)`.

    No role, permission, or authority-shaped field exists here by
    construction — that is the non-collapse proof, not a runtime check.
    """

    user_id: UserId
    authentication_session_ref: str
    authentication_time: datetime
    issuer_ref: str

    def __post_init__(self) -> None:
        if not self.authentication_session_ref:
            raise ValueError(
                "AuthenticatedPrincipal requires a non-empty authentication_session_ref"
            )
        if self.authentication_time.tzinfo is None:
            raise ValueError("AuthenticatedPrincipal.authentication_time must be timezone-aware")
        if not self.issuer_ref:
            raise ValueError("AuthenticatedPrincipal requires a non-empty issuer_ref")


@dataclass(frozen=True, slots=True)
class ExternalCredential:
    """Already-verified external identity claims, presented to the
    identity port for mapping to a canonical `UserId`.

    Cryptographic verification of the underlying credential (signature,
    audience, expiry, revocation — 11 §6 AC-11-002 item 1: "credential
    verification occurs at an authenticated boundary") happens upstream
    of this port, in the concrete production adapter `GAP-14-001` will
    introduce. This type carries only what identity *resolution* needs
    once that verification has already occurred; it is not a JWT/OIDC
    token parser.

    `extra_claims` exists so a concrete adapter can pass through
    provider-specific claims for logging/observability, but
    `IdentityPort.resolve` must never read an authority-shaped key out
    of it (e.g. "role", "is_admin") — see the mandatory adversarial
    test in `tests/security/test_identity.py`.
    """

    subject: str
    issuer_ref: str
    session_ref: str
    authentication_time: datetime
    extra_claims: tuple[tuple[str, str], ...] = ()


@runtime_checkable
class IdentityPort(Protocol):
    """Port: map an already-authenticated external credential to a
    canonical `AuthenticatedPrincipal`.

    How a concrete adapter performs that mapping (a users-table lookup,
    just-in-time provisioning, ...) is an implementation detail of the
    adapter, not of this port.
    """

    def resolve(self, credential: ExternalCredential) -> AuthenticatedPrincipal: ...


class ServicePrincipal(Enum):
    """14's own PKG-25 OBJECTIVE names these 9 DB principals verbatim.
    Each is a real, LOGIN-capable local PostgreSQL role (see
    `infra/local/db_roles.sql`), none a superuser (14's own "No runtime
    superuser" requirement, proven by
    `tests/security/test_db_principals.py`).
    """

    MIGRATION_OWNER = "migration_owner"
    API_READER = "api_reader"
    GOVERNED_COMMIT_WRITER = "governed_commit_writer"
    AI_GATEWAY_WRITER = "ai_gateway_writer"
    PROJECTION_WRITER = "projection_writer"
    RECOVERY_READER = "recovery_reader"
    SECURITY_EVENT_WRITER = "security_event_writer"
    AUDIT_READER = "audit_reader"
    TEST_PRINCIPAL = "test_principal"


class TableOperation(Enum):
    """The 4 DML verbs `information_schema.role_table_grants` reports.
    DDL (`CREATE`/`ALTER`/`DROP`) is deliberately not a member — only
    `migration_owner` needs DDL, and it is schema-scoped, not
    table-keyed (see this module's own "WHY `migration_owner` HAS NO
    ROW" docstring section)."""

    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


@dataclass(frozen=True, slots=True)
class TableCapability:
    table: str
    operations: frozenset[TableOperation]


_READ_ONLY = frozenset({TableOperation.SELECT})
_READ_WRITE = frozenset({TableOperation.SELECT, TableOperation.INSERT, TableOperation.UPDATE})
_READ_WRITE_DELETE = frozenset(
    {TableOperation.SELECT, TableOperation.INSERT, TableOperation.UPDATE, TableOperation.DELETE}
)

# Every protected/canonical/operational table this codebase has created
# through PKG-24's own migrations (`persistence.tables`), in creation
# order -- used both to build `SECURITY_CAPABILITY_MAP` below (every
# table gets an `api_reader`/`test_principal` row) and by
# `tests/security/test_service_identity.py` to assert this list itself
# stays exhaustive as future packages add tables.
ALL_PROTECTED_TABLES: tuple[str, ...] = (
    "users",
    "workspaces",
    "workspace_memberships",
    "role_assignments",
    "human_authority_bindings",
    "challenges",
    "sessions",
    "questions",
    "question_lineage",
    "question_bursts",
    "burst_question_memberships",
    "commands",
    "command_attempts",
    "idempotency_records",
    "audit_events",
    "outbox_events",
    "commit_units",
    "question_selections",
    "decisions",
    "source_references",
    "evidence",
    "claim_anchors",
    "evidence_relations",
    "evidence_set_references",
    "ai_generations",
    "ai_derived_artifacts",
    "ai_context_manifests",
    "projection_checkpoints",
    "session_read_model",
    "inquiry_read_model",
    "recovery_records",
)

# Tables with a real, already-merged governed writer (traced by
# `grep`, see this module's own "WHY THIS CAPABILITY MAP IS
# CODE-GROUNDED" docstring section) -- everything else in
# `ALL_PROTECTED_TABLES` currently has NO production writer at all.
_GOVERNED_COMMIT_WRITER_TABLES: tuple[str, ...] = (
    "questions",
    "question_lineage",
    "question_bursts",
    "burst_question_memberships",
    "commands",
    "command_attempts",
    "idempotency_records",
    "audit_events",
    "outbox_events",
    "commit_units",
    "question_selections",
    "decisions",
    "source_references",
    "evidence",
    "claim_anchors",
    "evidence_relations",
    "evidence_set_references",
)
_AI_GATEWAY_WRITER_TABLES: tuple[str, ...] = (
    "ai_generations",
    "ai_derived_artifacts",
    "ai_context_manifests",
)
_PROJECTION_WRITER_TABLES: tuple[str, ...] = (
    "projection_checkpoints",
    "session_read_model",
    "inquiry_read_model",
)
_RECOVERY_READER_TABLES: tuple[str, ...] = ("recovery_records",)
_AUDIT_READER_TABLES: tuple[str, ...] = ("audit_events",)
# `security_events` does not exist until PKG-26's own migration -- see
# this module's own "WHY `security_event_writer` HAS A ROLE BUT NO
# GRANT YET" docstring section. Not listed in `ALL_PROTECTED_TABLES`
# (which only names tables that already exist) or in this package's own
# `SECURITY_CAPABILITY_MAP`/migration GRANT statements.

SECURITY_CAPABILITY_MAP: dict[ServicePrincipal, tuple[TableCapability, ...]] = {
    ServicePrincipal.API_READER: tuple(
        TableCapability(table, _READ_ONLY) for table in ALL_PROTECTED_TABLES
    ),
    ServicePrincipal.GOVERNED_COMMIT_WRITER: tuple(
        TableCapability(table, _READ_WRITE) for table in _GOVERNED_COMMIT_WRITER_TABLES
    ),
    ServicePrincipal.AI_GATEWAY_WRITER: tuple(
        TableCapability(table, _READ_WRITE) for table in _AI_GATEWAY_WRITER_TABLES
    ),
    ServicePrincipal.PROJECTION_WRITER: tuple(
        TableCapability(table, _READ_WRITE_DELETE) for table in _PROJECTION_WRITER_TABLES
    ),
    ServicePrincipal.RECOVERY_READER: tuple(
        TableCapability(table, _READ_WRITE) for table in _RECOVERY_READER_TABLES
    ),
    ServicePrincipal.AUDIT_READER: tuple(
        TableCapability(table, _READ_ONLY) for table in _AUDIT_READER_TABLES
    ),
    ServicePrincipal.SECURITY_EVENT_WRITER: (),
    ServicePrincipal.TEST_PRINCIPAL: tuple(
        TableCapability(table, _READ_WRITE_DELETE) for table in ALL_PROTECTED_TABLES
    ),
    ServicePrincipal.MIGRATION_OWNER: (),
}


def capability_tables(principal: ServicePrincipal) -> frozenset[str]:
    """Every table `principal` may touch at all, per
    `SECURITY_CAPABILITY_MAP`."""
    return frozenset(c.table for c in SECURITY_CAPABILITY_MAP.get(principal, ()))


def capability_operations(principal: ServicePrincipal, table: str) -> frozenset[TableOperation]:
    """The exact operations `principal` may perform on `table`. Empty
    if `principal` has no capability on `table` at all."""
    for capability in SECURITY_CAPABILITY_MAP.get(principal, ()):
        if capability.table == table:
            return capability.operations
    return frozenset()


__all__ = [
    "AuthenticatedPrincipal",
    "ExternalCredential",
    "IdentityPort",
    "ServicePrincipal",
    "TableOperation",
    "TableCapability",
    "ALL_PROTECTED_TABLES",
    "SECURITY_CAPABILITY_MAP",
    "capability_tables",
    "capability_operations",
]
