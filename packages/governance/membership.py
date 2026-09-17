"""WorkspaceMembership and RoleAssignment closed vocabularies.

Source: 02_DOMAIN_AND_RELATION_MODEL.md §7 (WorkspaceMembership),
09_DATA_EVENT_API_CONTRACTS.md §23-24 (WorkspaceMembership,
RoleAssignment data contracts).

Non-collapse rule (02 §7.4, 04 AC-04-001, 05 AC-05-005): a role label is
governance *context* only. It never grants authority by itself — see
`AuthorityClass` in `authority_binding.py` for the closed vocabulary
that actually carries authority, and 05 AC-05-004 ("Membership Is
Authority Precondition, Not Authority").

`class X(str, Enum)` rather than `enum.StrEnum` deliberately: `StrEnum`
is Python 3.11+ only, and this repository's sandbox verification
interpreter is 3.10 (see docs/implementation/proof-reports/PKG-00.md,
KNOWN_LIMITATIONS) even though the declared target is 3.13.
"""

from __future__ import annotations

from enum import Enum


class WorkspaceRole(str, Enum):
    """The closed Workspace role vocabulary (02 §7.4, 05 GOV-004).

    Values match the literal source casing ("Owner", not "OWNER") —
    14 §6's CLOSED VOCABULARIES section does not cover Workspace roles,
    so there is no competing ALL_CAPS convention to follow here.
    """

    OWNER = "Owner"
    FACILITATOR = "Facilitator"
    CONTRIBUTOR = "Contributor"
    OBSERVER = "Observer"
    VIEWER = "Viewer"


class MembershipStatus(str, Enum):
    """WorkspaceMembership's "active/effective status representation" (09 §23)."""

    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


__all__ = ["WorkspaceRole", "MembershipStatus"]
