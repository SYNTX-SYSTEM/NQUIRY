"""Typed authority sources for the effect gate (F02 WU-02.6, HD-6).

Source: 16 §41 REC-004 / NQ-DEC-034 (human decision, 2026-09-24):
"CommitCoordinator / BND-014 carry typed authority sources, at minimum
BINDING, ROLE and FOUNDING. No fabricated UUID provenance. No fake
HumanAuthorityBinding. Audit provenance references actual, reconstructable
authority provenance." 20_SYSTEM_FIELD_ENGINEERING.md §7.

Four requirement shapes (three from F02 HD-6, PARTICIPATION from F03 HD-15), each named
by the architecture that authorizes it, never by convenience:

- `BindingAuthority`: 04's operation-specific `HumanAuthorityBinding`
  (every AUTH-DEP whose OPERATION AUTHORITY is an `AuthorityClass`).
  Provenance: the resolved binding id at the exact scope.
- `RoleAuthority`: an operation whose 04 OPERATION AUTHORITY is a
  source-explicit ROLE right, not a binding. Today exactly
  AUTH-DEP-CH-001 ("Facilitator may create Challenge", LEVEL_1_EXPLICIT;
  06 BND-004 "Facilitator in Workspace: may create Challenge").
  Provenance: the current `role_assignments` row id.
- `FoundingAuthority`: HARD-DEP-001 Option A (16 §41 REC-001): a
  verified human founding a Workspace. There is no pre-existing record
  to point at. Provenance: the founding Command's own id (a persisted
  `commands` row), plus the eligibility policy's reason code.

`AuthoritySourceProof` is what BND-014 hands back on ALLOW and what the
coordinator writes to `audit_events.authority_source_type/_ref/
authority_scope_ref`. There is deliberately no fallback constructor:
an ALLOW without a proof cannot be built.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum

from governance.authority_binding import AuthorityClass
from governance.membership import WorkspaceRole


class AuthoritySourceType(str, Enum):
    BINDING = "BINDING"
    ROLE = "ROLE"
    FOUNDING = "FOUNDING"
    PARTICIPATION = "PARTICIPATION"
    """F03 HD-15 (16 §41 REC-016 / NQ-DEC-043)."""


@dataclass(frozen=True, slots=True)
class BindingAuthority:
    authority_class: AuthorityClass
    scope_type: str
    scope_id: uuid.UUID

    def __post_init__(self) -> None:
        if not self.scope_type:
            raise ValueError("BindingAuthority.scope_type must be non-empty")


@dataclass(frozen=True, slots=True)
class RoleAuthority:
    """Role-sourced operation authority, scoped to the envelope's Workspace."""

    accepted_roles: frozenset[WorkspaceRole]
    operation_authority_ref: str
    """The architecture clause that makes this a role-sourced operation, e.g. "AUTH-DEP-CH-001"."""

    def __post_init__(self) -> None:
        if not self.accepted_roles:
            raise ValueError("RoleAuthority.accepted_roles must be non-empty")
        if not self.operation_authority_ref:
            raise ValueError("RoleAuthority.operation_authority_ref must be non-empty")


@dataclass(frozen=True, slots=True)
class FoundingAuthority:
    """HARD-DEP-001 Option A founding act. The Workspace is created by the same commit."""

    eligibility_reason_code: str
    operation_authority_ref: str = "HARD-DEP-001:OPTION_A"

    def __post_init__(self) -> None:
        if not self.eligibility_reason_code:
            raise ValueError("FoundingAuthority.eligibility_reason_code must be non-empty")


@dataclass(frozen=True, slots=True)
class ParticipationAuthority:
    """F03 HD-15: the source-explicit question-submission right of a CURRENT
    SessionParticipation (04 AUTH-DEP-Q-001: "Direct source participation
    right ... Valid SessionParticipation"). It is neither a role nor a
    binding: the Workspace role label is "not sufficient or necessary", and no
    `HumanAuthorityBinding` exists for it. Provenance: the participation id."""

    session_id: uuid.UUID
    operation_authority_ref: str = "AUTH-DEP-Q-001"

    def __post_init__(self) -> None:
        if not isinstance(self.session_id, uuid.UUID):
            raise TypeError("ParticipationAuthority.session_id must be a uuid.UUID")
        if not self.operation_authority_ref:
            raise ValueError("ParticipationAuthority.operation_authority_ref must be non-empty")


AuthorityRequirement = BindingAuthority | RoleAuthority | FoundingAuthority | ParticipationAuthority


@dataclass(frozen=True, slots=True)
class AuthoritySourceProof:
    source_type: AuthoritySourceType
    source_ref: uuid.UUID
    """BINDING: human_authority_bindings.id. ROLE: role_assignments.id. FOUNDING: commands.id.
    PARTICIPATION: session_participations.id."""
    scope_ref: str
    """e.g. "SESSION:<uuid>", "WORKSPACE:<uuid>"."""
    detail: str
    """Authority class, role, or founding policy reason: human-readable and structured."""

    def __post_init__(self) -> None:
        if not isinstance(self.source_type, AuthoritySourceType):
            raise TypeError("source_type must be an AuthoritySourceType")
        if not isinstance(self.source_ref, uuid.UUID):
            raise TypeError("source_ref must be a uuid.UUID")
        if not self.scope_ref or ":" not in self.scope_ref:
            raise ValueError("scope_ref must be '<SCOPE_TYPE>:<id>'")


__all__ = [
    "AuthorityRequirement",
    "AuthoritySourceProof",
    "AuthoritySourceType",
    "BindingAuthority",
    "FoundingAuthority",
    "ParticipationAuthority",
    "RoleAuthority",
]
