"""CommandRegistry: the semantic Command catalogue.

Source: 14_IMPLEMENTATION_SEQUENCE.md §3.1 ("command | CommandEnvelope,
registry, handler contracts"), §42 (CONTRACT VERSIONING: "No silent
semantic contract change"); 09_DATA_EVENT_API_CONTRACTS.md §61 (Command
Taxonomy -- category is a closed vocabulary, not free text).

WHAT THIS MODULE IS
--------------------
The generic catalogue every concrete named Command (`CMD_CREATE_SESSION`,
`CMD_BEGIN_SETUP`, ... -- 09 section 62's own Process Transition Command
Registry) will register into. 14's file-level map (section 48) assigns
exactly `packages/command/registry.py` to this package, described only
as "semantic Command catalogue" -- no concrete named Command is part of
PKG-10's own PUBLIC_INTERFACES (`CommandEnvelope, CommandRegistry`
only). Registering `CMD_CREATE_SESSION` etc. is deferred to whichever
future package first needs to submit that specific Command; building it
here would be implementing successor behavior.

WHY THIS MIRRORS `boundaries.registry.BoundaryRegistry`
--------------------------------------------------------
Same generic-engine-now/concrete-registrations-later split PKG-08 (this
package's structural sibling in the Coding Package DAG) already
established for BND-001..018: a registry that holds *no* evaluation or
dispatch logic of its own, only a default-deny (14 section 45) mapping
from a closed key to a caller-registered contract, with no silent
overwrite.

WHAT `validate_envelope` PROVES, AND WHAT IT DOES NOT
--------------------------------------------------------
`validate_envelope` proves two purely structural facts: the envelope's
`command_type` is a Command this system has ever declared to exist, and
its `command_contract_version` is the *exact* version currently
registered for that type (14 section 42's own rule -- no fuzzy/semver
compatibility logic is invented here, since 14 defines none). It proves
nothing about authority, boundaries, or whether the operation is
currently activatable (09 section 170's ACTIVE/BLOCKED_BY_OPEN_AUTHORITY/
BLOCKED_BY_OPEN_POLICY/DEFERRED_BY_SCOPE axis is a *separate*,
successor-owned concern -- AC-09-016: "A defined API/Command contract
may exist while execution remains blocked by unresolved authority/
policy").
"""

from __future__ import annotations

from dataclasses import dataclass

from semantic_types.versions import ContractVersion

from command.envelope import CommandEnvelope


@dataclass(frozen=True, slots=True)
class CommandContract:
    """The one fact this package can state about a registered Command
    without inventing its semantics: which type name is claimed, and at
    which contract version. A future package owning the concrete
    Command adds its own handler/authority/boundary wiring elsewhere;
    it registers here only to make its `command_type` and current
    version discoverable and enforceable.
    """

    command_type: str
    contract_version: ContractVersion

    def __post_init__(self) -> None:
        if not self.command_type:
            raise ValueError("CommandContract.command_type must be non-empty")
        if not isinstance(self.contract_version, ContractVersion):
            raise TypeError(
                f"contract_version must be a ContractVersion, got {type(self.contract_version)!r}"
            )


class CommandRegistrationError(Exception):
    """Raised when a second contract attempts to register for a
    `command_type` that already has one. No silent overwrite -- exactly
    one contract may claim a given command_type at a time (14 section
    45's default-deny posture, same as `BoundaryRegistrationError`).
    """


class UnregisteredCommandTypeError(Exception):
    """Raised by `validate_envelope` when `command_type` has never been
    registered. A Command this system has never declared to exist is
    not a legitimate target for anything downstream, including a
    dispatch attempt this package itself does not perform.
    """


class CommandContractVersionMismatch(Exception):
    """Raised by `validate_envelope` when the envelope's
    `command_contract_version` does not exactly match the currently
    registered version for its `command_type` (14 section 42: "No
    silent semantic contract change").
    """


class CommandRegistry:
    """Maps `command_type` to the one `CommandContract` currently
    registered for it. Holds no dispatch, handler, or execution logic
    of its own -- looking a contract up does not invoke anything.
    """

    def __init__(self) -> None:
        self._contracts: dict[str, CommandContract] = {}

    def register(self, contract: CommandContract) -> None:
        if contract.command_type in self._contracts:
            raise CommandRegistrationError(
                f"a CommandContract is already registered for {contract.command_type!r}"
            )
        self._contracts[contract.command_type] = contract

    def get(self, command_type: str) -> CommandContract | None:
        return self._contracts.get(command_type)

    def validate_envelope(self, envelope: CommandEnvelope) -> None:
        contract = self._contracts.get(envelope.command_type)
        if contract is None:
            raise UnregisteredCommandTypeError(
                f"command_type {envelope.command_type!r} is not registered"
            )
        if contract.contract_version != envelope.command_contract_version:
            raise CommandContractVersionMismatch(
                f"command_type {envelope.command_type!r} is registered at "
                f"contract_version {contract.contract_version!r}, envelope carries "
                f"{envelope.command_contract_version!r}"
            )


__all__ = [
    "CommandContract",
    "CommandRegistrationError",
    "UnregisteredCommandTypeError",
    "CommandContractVersionMismatch",
    "CommandRegistry",
]
