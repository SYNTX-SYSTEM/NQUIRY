"""Human-facing identity presentation of the authenticated self
(PURPLE_IDENTITY_PRESENTATION_01; 24 §13.1 canonical identity; §20.1
AUTHENTICATION != AUTHORIZATION; HD-28 identity creation).

SOURCE AUTHORITY, reconstructed before this module existed:
- `users.name` and `users.email` are NOT NULL attributes of the canonical
  identity row. Their only producers are the identity creation authorities
  (HD-28 host-operator command: name required, email normalized and unique;
  DEV / TEST policy creation, WU-AUTH-09). No authentication relation writes
  them: login, link, unlink, rotation, recovery and disable leave both
  columns untouched (disable writes only `disabled_*`).
- They are already projected to other humans by the governed product (member
  rosters, participants, admit / grant candidates), so showing them to the
  identity itself adds no exposure.
- The local login identifier is not a credential attribute: `local_auth_
  credentials` carries no email; the login resolves the typed address through
  `users.email`. The provider email and display name live on
  `external_provider_identities` only and never reach this module.

LAWS: the presentation is a function of the identity row alone — the same
for a LOCAL_PASSWORD and a GOOGLE_OIDC session of one identity, before and
after a link, after a rotation, after an unlink. Nothing is derived (no
local-part, no initials, no provider profile), nothing is defaulted, and no
role, membership, authority or capability can appear here: the dataclass has
no such field. Readable only by the live session's own identity.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from persistence.identity_repository import SqlAlchemyIdentityRepository
from persistence.local_auth_repository import SqlAlchemyLocalSessionRepository
from semantic_types.ids import UserId

from application.auth_handler import SessionRequired, _require_live


@dataclass(frozen=True, slots=True)
class IdentityPresentation:
    user_id: UserId
    display_name: str
    canonical_email: str


def own_identity_presentation(
    connection: Any, raw_token: str | None, *, now: datetime
) -> IdentityPresentation:
    """The presentation of the identity that owns the live session `raw_token`.
    Raises `SessionRequired` without a live session, and also when the
    identity row behind the principal cannot be read (fail closed: no
    partial or synthesized presentation)."""
    sessions = SqlAlchemyLocalSessionRepository(connection)
    current = _require_live(raw_token, session_repository=sessions, now=now)
    found = SqlAlchemyIdentityRepository(connection).presentation(current.user_id)
    if found is None:
        raise SessionRequired("no identity behind the session")
    name, email = found
    return IdentityPresentation(user_id=current.user_id, display_name=name, canonical_email=email)


__all__ = ["IdentityPresentation", "SessionRequired", "own_identity_presentation"]
