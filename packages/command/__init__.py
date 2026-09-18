"""command: CommandEnvelope, registry, handler contracts.

Architectural ownership (14_IMPLEMENTATION_SEQUENCE.md §3.1):
    Responsibility     : CommandEnvelope, registry, handler contracts.
    May depend on      : domain contracts, semantic_types.
    Must not depend on : HTTP, provider SDK.
    Canonical write    : no direct write.

PKG-10 SCOPE (Build Phase 4, "Command envelope and attempts"):
    envelope.py  -- CommandEnvelope (09 section 9's exact field list),
                    CommandOutcome (14 section 6's closed vocabulary),
                    compute_payload_fingerprint.
    registry.py  -- CommandRegistry, CommandContract: the generic
                    command_type -> registered-contract catalogue, no
                    concrete named Command registered here.

No concrete Command (`CMD_CREATE_SESSION`, `CMD_BEGIN_SETUP`, ...) is
implemented in this package -- 14's PKG-10 manifest assigns only
`CommandEnvelope, CommandRegistry` as PUBLIC_INTERFACES. `commit/`
(BND-014, CommitUnit, transaction orchestration) remains PKG-13's
scope; nothing here dispatches, executes, or commits any Command.
`packages/persistence/command_repository.py` implements the storage
port for Command/attempt records, depending on this package's types the
same one-directional way `persistence` already depends on `domain`/
`governance` -- this package still performs no direct write of its own.
"""
