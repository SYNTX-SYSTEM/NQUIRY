"""The account creation policy vocabulary (24 §11.14; WU-AUTH-09).

Which policy applies in production is HUMAN_AUTHORITY_REQUIRED (24 §36 #3–#5).
Until decided, `DENIED` is in force: an unknown provider subject creates no
identity. HD-28 / NQ-DEC-056 decided the local-password case (host-operator
creation only, no self-service) and left the external-provider policy
fail-closed.

`SELF_REGISTRATION_ALLOWED` is the open policy. HD-AUTH-08 (2026-10-04)
admitted it in every declared environment for an unknown, verified
external-provider subject (PROVIDER_BOOTSTRAP); HD-AUTH-13 (2026-10-07)
admitted it for a person with a local e-mail address and password
(SELF_REGISTERED: identity only, no authority of any kind, the address
verified through the existing verified-email relation before the identity is
established for normal use). The three relation-bearing
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

# PROVIDER_BOOTSTRAP provenance (generic provider-driven identity; 24 §11.14
# SELF_REGISTRATION_ALLOWED): what an identity created from a verified provider
# credential is, and where each of its two human-facing attributes came from.
# Recorded in the IDENTITY_CREATED SecurityEvent so the system can answer
# "why is this person called this" and "where did this email come from".
IDENTITY_CLASS_PROVIDER_BOOTSTRAP = "PROVIDER_BOOTSTRAP_IDENTITY"
NAME_SOURCE_PROVIDER_DISPLAY_NAME_CLAIM = "PROVIDER_DISPLAY_NAME_CLAIM"
EMAIL_SOURCE_PROVIDER_VERIFIED_CLAIM = "PROVIDER_VERIFIED_EMAIL_CLAIM"

# SELF_REGISTERED provenance (HD-AUTH-13; WU-AUTH-22): the person asserted both
# attributes themselves; the address is unverified at creation and the identity
# is not established until the verified-email relation exists for it.
IDENTITY_CLASS_SELF_REGISTERED = "SELF_REGISTERED_IDENTITY"
NAME_SOURCE_SELF_ASSERTED = "SELF_ASSERTED"
EMAIL_SOURCE_SELF_ASSERTED_UNVERIFIED = "SELF_ASSERTED_UNVERIFIED"
ESTABLISHMENT_ESTABLISHED = "ESTABLISHED"
ESTABLISHMENT_PENDING = "PENDING_EMAIL_VERIFICATION"

__all__ = [
    "EMAIL_SOURCE_PROVIDER_VERIFIED_CLAIM",
    "EMAIL_SOURCE_SELF_ASSERTED_UNVERIFIED",
    "ESTABLISHMENT_ESTABLISHED",
    "ESTABLISHMENT_PENDING",
    "IDENTITY_CLASS_SELF_REGISTERED",
    "NAME_SOURCE_SELF_ASSERTED",
    "IDENTITY_CLASS_PROVIDER_BOOTSTRAP",
    "MATERIALIZED_POLICIES",
    "NAME_SOURCE_PROVIDER_DISPLAY_NAME_CLAIM",
    "AccountCreationPolicy",
]
