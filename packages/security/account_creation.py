"""The account creation policy vocabulary (24 §11.14; WU-AUTH-09).

Which policy applies in production is HUMAN_AUTHORITY_REQUIRED (24 §36 #3–#5).
Until decided, `DENIED` is in force: an unknown provider subject creates no
identity. HD-28 / NQ-DEC-056 decided the local-password case (host-operator
creation only, no self-service) and left the external-provider policy
fail-closed.

`SELF_REGISTRATION_ALLOWED` is materialized so the approved branch can be
proven; the runtime admits it in DEVELOPMENT / TEST only (24 §25.3 "explicit
test account creation policy for test only"). The three relation-bearing
policies name relations that do not exist yet (invitations, pre-provisioned
identities, governance-mediated creation); the runtime refuses them rather
than behaving as if they were decided.
"""

from __future__ import annotations

from enum import Enum


class AccountCreationPolicy(Enum):
    DENIED = "DENIED"
    SELF_REGISTRATION_ALLOWED = "SELF_REGISTRATION_ALLOWED"
    INVITATION_REQUIRED = "INVITATION_REQUIRED"
    PRE_PROVISIONED_IDENTITY_REQUIRED = "PRE_PROVISIONED_IDENTITY_REQUIRED"
    GOVERNANCE_MEDIATED_CREATION = "GOVERNANCE_MEDIATED_CREATION"


MATERIALIZED_POLICIES: frozenset[AccountCreationPolicy] = frozenset(
    {AccountCreationPolicy.DENIED, AccountCreationPolicy.SELF_REGISTRATION_ALLOWED}
)

__all__ = ["MATERIALIZED_POLICIES", "AccountCreationPolicy"]
