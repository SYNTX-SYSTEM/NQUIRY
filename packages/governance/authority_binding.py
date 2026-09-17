"""HumanAuthorityBinding closed vocabularies.

Source: 04_AUTHORITY_AND_DECISION_RIGHTS.md §6 (Human Authority
Binding definition), §9 (Decision Right Classes — the closed
`AuthorityClass` list), 05_GOVERNANCE_INSIDE_SYSTEM.md §8 (HABB
Lifecycle — the closed `AuthorityBindingState` list: "ACTIVE, REVOKED
... REVOKED is terminal for that binding record").

Non-collapse rule (05 §8.3): "A HumanAuthorityBinding does not contain
arbitrary strings such as can_do_anything, admin, superuser, *. It
binds one approved authority class to one bounded scope." This is
exactly why `AuthorityClass` is a closed enum, not a free-text column
at the Python level (the database CHECK constraint in migration
`01a37c093cd6_membership_governance.py` enforces the same closure
independently, at the schema level).
"""

from __future__ import annotations

from enum import Enum


class AuthorityClass(str, Enum):
    """The 7 Decision Right classes 04 §9 defines. Closed — a class not
    listed here does not exist architecturally; do not add one without
    tracing it to 04.
    """

    SESSION_CONTROL_RIGHT = "SESSION_CONTROL_RIGHT"
    QUESTION_SELECTION_RIGHT = "QUESTION_SELECTION_RIGHT"
    ASSUMPTION_INTERPRETATION_RIGHT = "ASSUMPTION_INTERPRETATION_RIGHT"
    EXPERIMENT_DECISION_RIGHT = "EXPERIMENT_DECISION_RIGHT"
    DECISION_RIGHT = "DECISION_RIGHT"
    ACTION_DECISION_RIGHT = "ACTION_DECISION_RIGHT"
    WORKSPACE_GOVERNANCE_RIGHT = "WORKSPACE_GOVERNANCE_RIGHT"


class AuthorityBindingState(str, Enum):
    """05 §8.1: "REVOKED is terminal for that binding record." A changed
    authority assignment creates a new binding rather than mutating
    historical authority semantics in place (05 AC-05-003).
    """

    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


__all__ = ["AuthorityClass", "AuthorityBindingState"]
