"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — R-01 Observation ingress, R-02 Scope
validation (Architecture 26, FBR-PCPG-1).

Source: `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/00_FIELD.md` §3,
§10 (timeline), §12 (FBR-PCPG-1); `02_RELATIONS.md` R-01, R-02; `01_INVARIANTS.md`
I-01, I-06, I-18; `03_BOUNDARIES.md` B-02, B-10.

WHAT THIS MODULE IS
--------------------
The smallest coherent delta closing FBR-PCPG-1: "no relation exists that takes
a raw user intent into the backend as an authenticated, scope-validated,
side-effect-free observation." This module IS that relation, and nothing more.

It materializes R-01 (ingress) and R-02 (scope validation) only. It does
**not** build R-03 (Field reconstruction), R-04 (Pulse), R-05 (SIMPLIX semantic
sweep), R-06..R-12 (deltas, governance, composition, chain, capability,
projection) — those are FBR-PCPG-2 and later, each its own Work Unit. Emitting
any of their outputs here (a delta, a capability value, a semantic
interpretation) would be FABRICATED (E6): there is no producer for them yet.

REUSE (never re-implemented, 00_FIELD.md §7)
----------------------------------------------
- Identity (BND-001): the caller already resolved a real
  `security.identity.AuthenticatedPrincipal` (`application.auth_handler.
  resolve_session`) before this module runs at all.
- Workspace + membership (BND-002/BND-003): `application.workspace_context.
  resolve_workspace_context` — the exact existing producer `inquiry_queries`
  itself consumes for every query. Not re-implemented here.
- Session ownership: the same `session.workspace_id != context.workspace.id`
  check `inquiry_queries` already uses for every Session-scoped read (e.g.
  `challenge_detail`, `session_position`) — a foreign or unknown Session for a
  member is `not_found`, never a fact leak.
- Failure vocabulary: `application.inquiry_queries.QueryDenied` /
  `QueryNotFound` — the EXISTING denial/not-found vocabulary this Field's own
  law (I-20: "no parallel... policy") forbids inventing a second copy of.

WHAT THIS MODULE DELIBERATELY DOES NOT DO (I-18, I-06, B-10)
--------------------------------------------------------------
- No Command, no CommitUnit, no canonical write of any kind: every read here
  goes through `GovernedPorts`' read-only repositories, and nothing in this
  module calls a mutating method.
- No persistence of the raw intent or of this result (HA-PCPG-3 default:
  ephemeral, derived on read). The raw intent is held only in this call's
  local variables and returned once, to the actor who supplied it.
- No logging of raw-intent content, here or in a caller: this module never
  writes to a log, a tracer span or an operational-observation sink (the
  `_observation_sink` pattern `http_f02._observe` uses for Commands, "identities
  and outcome only", is not reused here because it is not required by R-01/R-02
  and adding it would risk a future contributor attaching content to it — see
  `01_INVARIANTS.md` I-18).
- No network egress of any kind (I-16 is not even in scope for this ingress-only
  relation, since nothing here reaches SIMPLIX, let alone a provider).

WHY A DIGEST, NOT JUST THE ECHOED TEXT
------------------------------------------
`04_OBSERVATION_RESULT.md` §9 names "the raw-intent fingerprint (a one-way
digest; the raw intent itself is not kept, I-18)" as part of the future basis.
This module does not build the basis (that is R-03/R-14 territory), but it
computes the digest now, at the one point the raw intent exists in memory, so
a future Work Unit can reuse it without ever needing to re-derive from stored
text. `[IMPLEMENTATION CHOICE]`, disclosed: SHA-256 over the UTF-8 bytes of
the raw intent exactly as submitted (no trim, no normalization — the digest of
an altered string would misrepresent I-01's "verbatim" input).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime

from security.identity import AuthenticatedPrincipal
from semantic_types.ids import SessionId, WorkspaceId

from application.composition import GovernedPorts
from application.inquiry_queries import QueryDenied, QueryNotFound
from application.workspace_context import (
    NotAWorkspaceMemberError,
    WorkspaceContext,
    WorkspaceNotFoundError,
    resolve_workspace_context,
)

RAW_INTENT_MAX_CHARS = 8000
"""`[IMPLEMENTATION CHOICE]`, disclosed: R-01's own precondition only says
"within a bounded size"; RED leaves the exact number to BLUE (00_FIELD.md §7:
"implementation structure ... BLUE derives"). Generous enough for a real
drafted prompt, small enough that this ingress cannot become a free-text
dumping ground (aligned, in spirit, with `domain.burst_input.
BURST_INPUT_MAX_CHARS = 2000` being the smallest fixed-contract text field in
this codebase; a draft prompt is naturally longer than one captured Question)."""

DECLARED_PURPOSE_MAX_CHARS = 2000
"""`[IMPLEMENTATION CHOICE]`, disclosed: bounded for the same reason. The
declared purpose is a claim (R-01 input), never trusted (00_FIELD.md §3)."""


class ObservationInputRejected(Exception):
    """The submitted wire shape is invalid: INPUT, never an authority
    statement (R-01 FAILURE STATE: "Malformed or oversized input: rejected.
    Nothing is read."). Raised before any Field fact is read."""

    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(reason_code)


@dataclass(frozen=True, slots=True)
class ObservationIngressResult:
    """R-01 + R-02's OUTPUT: "an observation request bound to a verified
    principal" (R-01) plus "a validated scope: the Workspace the actor is a
    member of, and the named Session ... only if it belongs to that Workspace"
    (R-02). Nothing beyond that — see the module docstring for what is
    deliberately absent (no semantic observation, no delta, no capability)."""

    workspace_id: WorkspaceId
    workspace_name: str
    session_id: SessionId | None
    raw_intent: str
    """Carried through exactly as submitted (R-01 OUTPUT: "opaque DATA").
    Never trimmed, normalized or interpreted by this module."""
    raw_intent_length: int
    raw_intent_digest_sha256: str
    declared_purpose: str | None
    observed_at: datetime


def observe(
    ports: GovernedPorts,
    principal: AuthenticatedPrincipal,
    *,
    workspace_id: WorkspaceId,
    raw_intent: str,
    session_id: SessionId | None,
    declared_purpose: str | None,
    now: datetime,
) -> ObservationIngressResult:
    """R-01 (ingress) then R-02 (scope validation), in that order (I-06:
    "identity, Workspace and membership ... before any Field fact is read").

    Identity (BND-001) is already proven by the caller (the connection was
    opened only after `resolve_session` succeeded); this function proves
    Workspace membership (BND-002/BND-003) via the EXISTING producer before
    it reads or returns anything about the named Session (I-06, I-05: "the
    prompt cannot manufacture or widen the Field" — a Session id the actor
    merely claims is validated, never trusted).

    Raises:
        ObservationInputRejected: malformed or oversized `raw_intent` /
            `declared_purpose` (R-01 FAILURE STATE). Nothing is read.
        QueryDenied: unknown Workspace or non-member (R-02 FAILURE STATE,
            I-06: the uniform denial, before any Session fact).
        QueryNotFound: `session_id` given but the Session does not exist, or
            belongs to another Workspace (R-02 OUTPUT: "only if it belongs to
            that Workspace" — a foreign Session is never disclosed as
            foreign; it is indistinguishable from unknown, same as every
            other Session-scoped query in this codebase).
    """
    if not isinstance(raw_intent, str) or not raw_intent.strip():
        raise ObservationInputRejected("RAW_INTENT_REQUIRED")
    if len(raw_intent) > RAW_INTENT_MAX_CHARS:
        raise ObservationInputRejected("RAW_INTENT_TOO_LONG")
    if declared_purpose is not None:
        if not isinstance(declared_purpose, str):
            raise ObservationInputRejected("DECLARED_PURPOSE_INVALID")
        if len(declared_purpose) > DECLARED_PURPOSE_MAX_CHARS:
            raise ObservationInputRejected("DECLARED_PURPOSE_TOO_LONG")

    # R-02 (BND-002/BND-003), via the EXISTING producer -- the same one every
    # `inquiry_queries` read consumes. Not re-implemented; only the
    # translation into the existing `QueryDenied` vocabulary is repeated here
    # (`inquiry_queries._context`'s own two lines), because that translation
    # is glue, not a rule: both call sites raise the identical existing
    # reason code for the identical existing exception pair.
    try:
        context: WorkspaceContext = resolve_workspace_context(
            principal, workspace_id, ports.workspaces, ports.memberships
        )
    except (WorkspaceNotFoundError, NotAWorkspaceMemberError) as exc:
        raise QueryDenied("WORKSPACE_NOT_ACCESSIBLE") from exc

    validated_session_id: SessionId | None = None
    if session_id is not None:
        session = ports.sessions.get(session_id)
        if session is None or session.workspace_id != context.workspace.id:
            # R-02: "the named Session ... only if it belongs to that
            # Workspace" — an unknown or foreign Session is not_found, never
            # a disclosed cross-Workspace fact (same vocabulary as every
            # other Session-scoped query, e.g. `inquiry_queries.session_position`).
            raise QueryNotFound("SESSION_NOT_FOUND")
        validated_session_id = session_id

    digest = hashlib.sha256(raw_intent.encode("utf-8")).hexdigest()

    return ObservationIngressResult(
        workspace_id=context.workspace.id,
        workspace_name=context.workspace.name,
        session_id=validated_session_id,
        raw_intent=raw_intent,
        raw_intent_length=len(raw_intent),
        raw_intent_digest_sha256=digest,
        declared_purpose=declared_purpose,
        observed_at=now,
    )


__all__ = [
    "DECLARED_PURPOSE_MAX_CHARS",
    "RAW_INTENT_MAX_CHARS",
    "ObservationIngressResult",
    "ObservationInputRejected",
    "observe",
]
