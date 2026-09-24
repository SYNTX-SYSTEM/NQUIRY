"""CommandEnvelope: the typed transport contract every consequential
write request uses.

Source: 09_DATA_EVENT_API_CONTRACTS.md §9 (CommandEnvelope's exact
field list), §9.1 (authority_context_ref is a reference, never a
reusable authorization token), §9.2 (expected_versions are concurrency
predicates, not a substitute for fresh authority checks), §12 (retry
semantics: same command_id/new attempt_id iff payload unchanged;
changed payload is a new logical Command), §139 (payload fingerprint
immutable per attempt), AC-09-001 (every mutable record a command
targets must expose a freshness predicate);
12_MINIMUM_PROTOTYPE_ARCHITECTURE.md §15 (Governed Command Proof,
minimum fields exercised); 14_IMPLEMENTATION_SEQUENCE.md §6 (Command
outcome closed vocabulary).

WHY `requesting_actor_type`/`requesting_actor_id` ARE PLAIN STRINGS
--------------------------------------------------------------------
14 §3.1 gives `command` exactly one allowed internal dependency:
`domain` contracts plus `semantic_types` -- not `authority`. The real,
strongly-typed `authority.actor.ActorClass`/`ActorIdentity` therefore
cannot be imported here without violating the directory ownership
contract (and 14's own file-level map, §48, confirms
`packages/command/envelope.py`'s only allowed import is
`semantic_types`). This mirrors the precedent PKG-05 already
established for `domain.session_transitions`'s `AuthorityDependency`/
`BoundaryDependency` enums: hold the identifier as inert *data* at this
layer, never the real authority-bearing type. BND-001 (Identity,
PKG-09) is what actually resolves a real `ActorIdentity` later in the
canonical request path; this envelope only carries an unverified claim
about who is asking, exactly as 09 §9.1 frames `authority_context_ref`
("a reference to authority inputs... not a reusable authorization
token") -- the same non-authority-carrying treatment extends naturally
to the actor fields themselves at this transport-contract layer.

WHY `authority_context_ref` IS A BARE `uuid.UUID`, NOT A STRUCTURED
`AuthorityContextReference`
--------------------------------------------------------------------
09 §10 defines `AuthorityContextReference` as its own full DATA
CONTRACT (actor_ref, required_authority_class, binding_ref, ...). This
package's PUBLIC_INTERFACES are exactly `CommandEnvelope,
CommandRegistry` (14 §46) -- constructing that full record here would
be implementing a public interface 14 does not assign to PKG-10, i.e.
"successor package implementation" (14 §11, excluded scope). A bare
`uuid.UUID` reference is the same generic-scope-reference precedent
`boundaries.bnd_005_human_authority.Bnd005Input.scope_id` already used
(PKG-09) for a polymorphic identifier with no single closed semantic
type of its own.

WHY `human_decision_ref`/`evidence_set_ref`/`method_version_ref` USE
EXISTING STRONG TYPES
--------------------------------------------------------------------
Unlike `authority_context_ref`, these three already have closed,
existing semantic types in `semantic_types` (`DecisionId`,
`EvidenceSetId`, `MethodVersion` -- 14 §5's closed identity/version
list) -- using them directly costs nothing extra and avoids
regressing to an untyped placeholder where a real type already exists.

WHY `payload` IS `object`, NOT A `CommandPayload` PROTOCOL
--------------------------------------------------------------------
09: "Consequential payloads use versioned typed contracts. Raw
dictionaries are rejected at public consequential boundaries." No
concrete Command payload contract is assigned to this package (14
PKG-10 COMMANDS: "If none are assigned, NOT_APPLICABLE" -- and none
are). An empty structural `Protocol` here would constrain nothing
(unlike `boundaries.BoundaryInput`, which meaningfully requires
`boundary_id`/`context`) and would falsely suggest a payload contract
this package does not define. The one concrete, enforceable rule 09
actually states -- "raw dictionaries are rejected" -- is checked
directly in `__post_init__` instead.

WHY `expected_versions` MUST COVER EXACTLY `target_refs`
--------------------------------------------------------------------
AC-09-001: "Every mutable record whose current value can affect
consequential commit must expose a freshness mechanism." Operationalized
here as the one generic, non-domain-specific rule this package can
enforce without guessing at any concrete Command's semantics: a ref
named as a mutation target must carry a stated expected version, and an
expected version must name an actual target -- neither a naked target
nor an orphaned expected-version entry is legitimate. This is also the
package's defense against the mandatory adversarial attack "missing
required expected version".
"""

from __future__ import annotations

import hashlib
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from semantic_types.ids import (
    AttemptId,
    CausationId,
    CommandId,
    CorrelationId,
    DecisionId,
    EvidenceSetId,
    WorkspaceId,
)
from semantic_types.versions import ContractVersion, MethodVersion, RecordVersion


class CommandOutcome(Enum):
    """14 §6's exact 4-value closed vocabulary for Command outcome.
    These are all terminal dispositions of one attempt; there is no
    fifth value and none may be reinterpreted as another (18 FAILURE
    SEMANTICS: "Do not reinterpret INDETERMINATE as failure or
    success.").
    """

    DENIED = "DENIED"
    FAILED_PRECOMMIT = "FAILED_PRECOMMIT"
    COMMITTED = "COMMITTED"
    INDETERMINATE = "INDETERMINATE"


@dataclass(frozen=True, slots=True)
class CommandEnvelope:
    """09 §9's exact field list. Every consequential write request uses
    one of these; this package does not yet dispatch or execute any of
    them (no CommitUnit exists until PKG-13) -- it only proves the
    contract is well-formed and reconstructable.
    """

    command_id: CommandId
    command_type: str
    command_contract_version: ContractVersion
    attempt_id: AttemptId
    correlation_id: CorrelationId
    requested_at: datetime
    requesting_actor_type: str
    requesting_actor_id: str
    workspace_scope_ref: WorkspaceId
    target_refs: tuple[str, ...]
    expected_versions: Mapping[str, RecordVersion]
    payload: object
    causation_id: CausationId | None = None
    authority_context_ref: uuid.UUID | None = None
    human_decision_ref: DecisionId | None = None
    evidence_set_ref: EvidenceSetId | None = None
    method_version_ref: MethodVersion | None = None
    idempotency_key: str | None = None
    created_refs: tuple[str, ...] = ()
    """F02 WU-02.6: refs of records this Command CREATES (e.g. a new
    Challenge). Not version-checked -- a new record has no prior version;
    its identity uniqueness is enforced by the database inside the
    CommitUnit. Recorded, with `target_refs`, on the CommitUnit and audit
    event so "what effect occurred" is reconstructable."""

    def __post_init__(self) -> None:
        # Mandatory adversarial attack: Event submitted as Command. An
        # EventId (or any other strong identity, or a bare string/UUID)
        # is a structurally different type than CommandId -- this is
        # the type system rejecting the substitution PKG-00's own
        # semantic_types docstring promises ("mixing them is a semantic
        # error the type system must reject"), enforced here at
        # *runtime* since CommandEnvelope is a public consequential
        # boundary a caller could otherwise miswire.
        if not isinstance(self.command_id, CommandId):
            raise TypeError(f"command_id must be a CommandId, got {type(self.command_id)!r}")
        if not self.command_type:
            raise ValueError("CommandEnvelope.command_type must be non-empty")
        if not isinstance(self.command_contract_version, ContractVersion):
            raise TypeError(
                "command_contract_version must be a ContractVersion, "
                f"got {type(self.command_contract_version)!r}"
            )
        if not isinstance(self.attempt_id, AttemptId):
            raise TypeError(f"attempt_id must be an AttemptId, got {type(self.attempt_id)!r}")
        if not isinstance(self.correlation_id, CorrelationId):
            raise TypeError(
                f"correlation_id must be a CorrelationId, got {type(self.correlation_id)!r}"
            )
        if self.causation_id is not None and not isinstance(self.causation_id, CausationId):
            raise TypeError(
                f"causation_id must be a CausationId or None, got {type(self.causation_id)!r}"
            )
        if not self.requesting_actor_type:
            raise ValueError("CommandEnvelope.requesting_actor_type must be non-empty")
        if not self.requesting_actor_id:
            raise ValueError("CommandEnvelope.requesting_actor_id must be non-empty")
        if not isinstance(self.workspace_scope_ref, WorkspaceId):
            raise TypeError(
                f"workspace_scope_ref must be a WorkspaceId, got {type(self.workspace_scope_ref)!r}"
            )
        if any(not isinstance(v, RecordVersion) for v in self.expected_versions.values()):
            raise TypeError("every expected_versions value must be a RecordVersion")
        if set(self.created_refs) & set(self.target_refs):
            raise ValueError("CommandEnvelope.created_refs must be disjoint from target_refs")
        if any(not isinstance(ref, str) or not ref for ref in self.created_refs):
            raise ValueError("CommandEnvelope.created_refs must be non-empty strings")
        # Mandatory adversarial attack: missing required expected version.
        target_set = set(self.target_refs)
        expected_set = set(self.expected_versions.keys())
        if target_set != expected_set:
            missing = target_set - expected_set
            orphaned = expected_set - target_set
            raise ValueError(
                "CommandEnvelope.expected_versions must cover exactly target_refs "
                f"(missing={sorted(missing)}, orphaned={sorted(orphaned)})"
            )
        if isinstance(self.payload, Mapping):
            raise TypeError(
                "CommandEnvelope.payload must not be a raw mapping; "
                "construct a typed payload contract instead (09 section 9)"
            )
        if self.human_decision_ref is not None and not isinstance(
            self.human_decision_ref, DecisionId
        ):
            raise TypeError("human_decision_ref must be a DecisionId or None")
        if self.evidence_set_ref is not None and not isinstance(
            self.evidence_set_ref, EvidenceSetId
        ):
            raise TypeError("evidence_set_ref must be an EvidenceSetId or None")
        if self.method_version_ref is not None and not isinstance(
            self.method_version_ref, MethodVersion
        ):
            raise TypeError("method_version_ref must be a MethodVersion or None")
        if self.authority_context_ref is not None and not isinstance(
            self.authority_context_ref, uuid.UUID
        ):
            raise TypeError("authority_context_ref must be a uuid.UUID or None")


def compute_payload_fingerprint(payload: object) -> str:
    """09 section 139/AC-09-013: the identity a payload is compared
    against under a reused `command_id`/idempotency key.

    `[IMPLEMENTATION CHOICE]`: SHA-256 over `repr(payload)`. No concrete
    Command payload contract exists yet (this package assigns none --
    14 PKG-10 COMMANDS: NOT_APPLICABLE), so there is no canonical
    field-serialization order to hash beyond what a payload's own
    `__repr__` already provides. A frozen dataclass's `__repr__` is
    deterministic for equal field values in declaration order, which is
    sufficient to prove "same payload -> same fingerprint, different
    payload -> different fingerprint" for this package's own tests. A
    future package introducing a concrete Command payload contract
    should give that contract its own canonical serialization if
    `repr()` proves insufficient for its shape (e.g. containing
    unordered collections) -- this function does not claim to be the
    final word for every future payload type.
    """
    return hashlib.sha256(repr(payload).encode("utf-8")).hexdigest()


__all__ = ["CommandOutcome", "CommandEnvelope", "compute_payload_fingerprint"]
