"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — R-03: Current Field reconstruction
(Architecture 26).

Source: `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/02_RELATIONS.md`
R-03: "PRODUCER: the existing canonical producers of `00_FIELD.md` §7,
read-only." "OUTPUT: the Field snapshot: canonical facts, each with its
source reference and version." This module composes REAL, already-proven
producers into one `FieldSnapshot` -- it invents no fact, re-derives no
authority, state or capability, and never touches the raw intent (I-05:
"Field reconstruction does not depend on the prompt").

WHY THIS IS A COMPOSITION, NOT A NEW PRODUCER
------------------------------------------------
Every field below is a direct quote of a call this codebase already makes
elsewhere, proven correct there:
- Actor role / governance-root: `application.inquiry_queries.
  workspace_overview`'s own `viewer` block (unchanged, re-read here).
- The actor's raw, current authority bindings: `persistence.
  authority_binding_repository.AuthorityBindingRepository.
  list_current_bindings` (the same port `GovernedPorts.bindings` already
  wraps) -- returned here as a flat, quoted list, never filtered,
  ranked or reinterpreted (P-14: no parallel authority model).
- Session context: `session_position`'s own `session`/`actions` blocks,
  quoted verbatim (state, version, fixture, proof mode, every relevant
  transition's availability and reason code).
- Provider context: `application.analysis_runtime.runtime_from_
  environment` -- read for its CONFIGURATION only (environment, whether a
  route exists); `.gateway` is never dereferenced to invoke anything
  (I-16/B-08, proven statically in the test suite).
- AI contracts admitted / external effects: two Field-wide, static facts
  this Field's own architecture text already states (HD-21's admitted
  AIOP scope; `00_FIELD.md` §3's own Pulse note that no external
  dependency exists in NQUIRY today) -- cited constants, not a producer
  call, because no producer for either exists as code.

WHY "DATA HANDLING" IS NOT A FIELD HERE
------------------------------------------
R-03's own "at minimum" OUTPUT list includes "Data handling: the data
classes and handling rules of in-scope sources." `00_FIELD.md` §7 itself
states, for that concern: "none materialized as a classifier; the classes
are architectural" (GAP-11-006, FBR-PCPG-3, still OPEN). Inventing a
placeholder value would violate I-02 (no stratum-1 value without a real
source, quoted and versioned); this module omits the field rather than
fabricate one. A future Work Unit that materializes FBR-PCPG-3 adds it.

WHY AN UNKNOWN/FOREIGN SESSION BECOMES UNRESOLVED, NOT AN EXCEPTION
----------------------------------------------------------------------
R-03's own FAILURE STATE: "A canonical producer is unavailable, or a fact
is unresolvable: that fact is UNRESOLVED, which propagates to
INDETERMINATE (I-04)." A named Session that does not belong to the
validated Workspace is exactly this case -- the snapshot still returns
(Actor context, the static facts and Provider context remain real and
useful), with `"session"` listed in `unresolved`, never a stack trace
that takes down the whole reconstruction. A non-member actor, by
contrast, is I-06's own scope-validation failure (identity/scope BEFORE
any fact is read) -- `workspace_overview`'s own `_context()` helper
already translates `WorkspaceNotFoundError`/`NotAWorkspaceMemberError`
into the uniform `QueryDenied("WORKSPACE_NOT_ACCESSIBLE")` (never leaking
which of the two occurred), and this module leaves that translation
unchanged: R-03's own PRECONDITION is "R-02 succeeded", and a caller that
invokes R-03 without a validated scope has violated that precondition,
not discovered a new UNRESOLVED case.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import cast

from security.identity import AuthenticatedPrincipal
from semantic_types.ids import SessionId, WorkspaceId

from application import inquiry_queries as queries
from application.analysis_runtime import (
    MockProviderForbidden,
    UnknownAIProvider,
    runtime_from_environment,
)
from application.composition import GovernedPorts

AI_CONTRACTS_ADMITTED = frozenset({"AIOP-001", "AIOP-002"})
"""HD-21's own admitted AIOP scope (08 §4-§5, §23-§38) -- a static,
cited fact of this codebase's architecture, not a producer call (no
callable "admitted contracts" listing exists; the scope is a decision
record, quoted here verbatim)."""

EXTERNAL_EFFECTS: frozenset[str] = frozenset()
"""`00_FIELD.md` §3's own Pulse note, verbatim: "EXTERNAL_DEPENDENCIES:
... none exist in NQUIRY today." A static, cited fact, re-read fresh by
any future caller rather than cached as permanently true."""


@dataclass(frozen=True, slots=True)
class AuthorityFact:
    authority_class: str
    scope_type: str
    scope_id: str
    binding_id: str
    binding_version: int


@dataclass(frozen=True, slots=True)
class ActorContext:
    user_id: str
    role: str | None
    is_governance_root: bool
    authority: tuple[AuthorityFact, ...]
    """Every row `AuthorityBindingRepository.list_current_bindings` returns
    for this actor in this Workspace, quoted -- not filtered to "relevant"
    classes, not re-derived (P-14: no parallel authority model)."""


@dataclass(frozen=True, slots=True)
class SessionContext:
    session_id: str
    state: str
    version: int
    fixture: bool
    proof_mode: str
    actions: Mapping[str, object]
    """`session_position`'s own `actions` dict, quoted verbatim -- the
    existing capability projection this Field consumes, never
    re-implements (00_FIELD.md §7)."""


@dataclass(frozen=True, slots=True)
class ProviderContext:
    environment: str | None
    provider_configured: bool
    """True exactly when `runtime_from_environment` resolved a real
    gateway CONFIGURATION for this environment -- never dereferenced to
    invoke anything (I-16)."""


@dataclass(frozen=True, slots=True)
class FieldSnapshot:
    basis_time: datetime
    workspace_id: str
    actor: ActorContext
    session: SessionContext | None
    ai_contracts_admitted: frozenset[str]
    external_effects: frozenset[str]
    provider: ProviderContext
    unresolved: tuple[str, ...]
    """Names of the "at minimum" facts that could not be read at this
    basis (I-04) -- never silently dropped, never defaulted."""


def reconstruct_field(
    ports: GovernedPorts,
    principal: AuthenticatedPrincipal,
    *,
    workspace_id: WorkspaceId,
    session_id: SessionId | None,
    now: datetime,
    environment: Mapping[str, str] | None = None,
) -> FieldSnapshot:
    """The R-03 producer. Raises `WorkspaceNotFoundError`/
    `NotAWorkspaceMemberError` (from `workspace_overview`, unchanged) when
    the scope itself is invalid -- R-03's own PRECONDITION is that R-02
    already succeeded; this is not a new failure mode, it is that
    precondition's own violation propagating unchanged (I-06)."""
    overview = queries.workspace_overview(ports, principal, workspace_id)
    real_bindings = ports.bindings.list_current_bindings(workspace_id, principal.user_id)
    authority = tuple(
        AuthorityFact(
            authority_class=b.authority_class.value,
            scope_type=b.scope_type,
            scope_id=str(b.scope_id),
            binding_id=str(b.id.value),
            binding_version=b.record_version.value,
        )
        for b in real_bindings
    )
    viewer = cast("dict[str, object]", overview["viewer"])
    actor = ActorContext(
        user_id=str(principal.user_id.value),
        role=cast("str | None", viewer["role"]),
        is_governance_root=bool(viewer["isGovernanceRoot"]),
        authority=authority,
    )

    unresolved: list[str] = []
    session: SessionContext | None = None
    if session_id is not None:
        try:
            real = queries.session_position(ports, principal, workspace_id, session_id)
        except queries.QueryNotFound:
            unresolved.append("session")
        else:
            real_session = cast("dict[str, object]", real["session"])
            session = SessionContext(
                session_id=str(session_id.value),
                state=cast(str, real_session["state"]),
                version=cast(int, real_session["version"]),
                fixture=cast(bool, real_session["fixture"]),
                proof_mode=cast(str, real_session["proofMode"]),
                actions=cast("Mapping[str, object]", real["actions"]),
            )

    provider = ProviderContext(environment=None, provider_configured=False)
    try:
        runtime = runtime_from_environment(environment)
    except (MockProviderForbidden, UnknownAIProvider):
        unresolved.append("provider")
    else:
        provider = ProviderContext(
            environment=None if runtime.environment is None else runtime.environment.value,
            provider_configured=runtime.available,
        )

    return FieldSnapshot(
        basis_time=now,
        workspace_id=str(workspace_id.value),
        actor=actor,
        session=session,
        ai_contracts_admitted=AI_CONTRACTS_ADMITTED,
        external_effects=EXTERNAL_EFFECTS,
        provider=provider,
        unresolved=tuple(unresolved),
    )


__all__ = [
    "AI_CONTRACTS_ADMITTED",
    "EXTERNAL_EFFECTS",
    "ActorContext",
    "AuthorityFact",
    "FieldSnapshot",
    "ProviderContext",
    "SessionContext",
    "reconstruct_field",
]
