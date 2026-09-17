"""security: identity/service identity, Workspace security, SecurityEvent.

Architectural ownership (14_IMPLEMENTATION_SEQUENCE.md §3.1):
    Responsibility     : identity/service identity, Workspace security, SecurityEvent.
    May depend on      : semantic_types.
    Must not depend on : domain authority invention.
    Canonical write    : no domain write.

PKG-01 SCOPE NOTE: `identity.py` materializes the human-identity port
(`AuthenticatedPrincipal`, `IdentityPort`) per 14 §32 and PKG-01's
manifest. Service identity, Workspace security enforcement, and
SecurityEvent land in later phases (14 §46: PKG-25/PKG-26, Phase 10).
"""
