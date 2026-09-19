#!/usr/bin/env python3
"""Architecture dependency checker.

Enforces the directory ownership contract (14_IMPLEMENTATION_SEQUENCE.md
§3.1) and the forbidden dependency matrix (§4) at the level of actual
Python imports. Two independent rules are checked per file:

1. INTERNAL_ALLOWED: a cross-package import (one of this repository's
   own flat top-level packages) is only legitimate if it appears on
   the importing package's "May depend on" list. Anything else is
   default-DENY — no allow-all boundary (14 §45).
2. EXTERNAL_FORBIDDEN: an import of a named external framework/driver/
   provider-SDK group that 14 §3.1/§4 explicitly forbids for that
   package, regardless of whether it is "internal" to this repo.

This script does not know about JavaScript/TypeScript imports
(`apps/web`); frontend/backend isolation is enforced by the frontend
build only depending on the typed HTTP client, never on a backend
package (14 §3.1: "frontend | ... | Must not depend on: DB,
governance repository, authority resolver").

Known scope limitation (disclosed, not silently accepted): this is the
*checkable subset* of §3.1/§4 expressible as Python top-level import
names. It does not yet distinguish "governance mutation port" from
"governance read port", or "restricted" vs "unrestricted" persistence
access, because those distinctions do not yet exist as separate
importable modules at Phase 0. Extend the tables below as later
packages introduce the concrete module split.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from _repo_scan import (
    API_SRC_ROOT,
    KNOWN_INTERNAL_PACKAGES,
    PACKAGES_ROOT,
    PROVIDER_SDK_MODULES,
    WORKER_SRC_ROOT,
    scan_owned_packages,
)

# "May depend on" (14 §3.1), translated to flat internal package names.
# A package name not present as a key defaults to "no internal deps".
INTERNAL_ALLOWED: dict[str, frozenset[str]] = {
    "semantic_types": frozenset(),
    "domain": frozenset({"semantic_types"}),
    "governance": frozenset({"domain", "semantic_types"}),
    "authority": frozenset(
        {
            "governance",
            "domain",
            "semantic_types",
            # PKG-03: `persistence` added so `AuthorityResolver` can be
            # constructed against the PKG-02 `MembershipRepository`/
            # `AuthorityBindingRepository` Protocol types (14 §16:
            # "Commit-time resolver reloads current authoritative
            # state" -- it must read through the real repositories, not
            # a copy). Read-only use: `authority` never imports `commit`
            # and has no write method to call.
            "persistence",
        }
    ),
    "boundaries": frozenset(
        {
            "domain",
            "authority",
            "governance",
            "evidence",
            "semantic_types",
            # PKG-19: `ai_contracts` added so `bnd_009_ai_invocation.py`/
            # `bnd_010_ai_output.py` can type their own inputs with the
            # real `AIOperationId`/`AIGenerationStatus`/`AIValidationResult`
            # closed enums (14 PKG-19 PUBLIC_INTERFACES: "unversioned
            # consequential dict payloads are forbidden where they erase
            # semantics"). Same one-directional pattern as
            # `boundaries -> evidence` (PKG-17): `ai_contracts`'s own
            # allowed set (14 section 3.1: "semantic_types, evidence read
            # contracts") does not include `boundaries`, so no cycle is
            # created.
            "ai_contracts",
            # PKG-09: `persistence` added so BND-002/003/004 evaluators
            # can read live `WorkspaceRecord`/`MembershipRecord`/
            # `RoleAssignmentRecord` state through the PKG-01/02
            # read-only Protocol repositories (06 §8/§9/§10's own
            # EVIDENCE REQUIREMENT: "SYSTEM_PROOF of object-to-Workspace
            # resolution" / "of active membership" / "of active
            # role/context" -- a caller-claimed value is explicitly not
            # sufficient, 06 §8: "Claimed Workspace IDs are not
            # authoritative by themselves"). Read-only use, same
            # disclosed-extension pattern as `application persistence`
            # (PKG-01), `persistence governance` (PKG-02),
            # `authority persistence` (PKG-03), `persistence domain`
            # (PKG-06). BND-005 does not need this extension itself: it
            # receives an already-constructed `authority.resolver.
            # AuthorityResolver` via constructor injection rather than
            # holding repositories directly.
            "persistence",
        }
    ),
    "evidence": frozenset({"domain", "semantic_types"}),
    "ai_contracts": frozenset({"semantic_types", "evidence"}),
    "ai_gateway": frozenset({"ai_contracts", "security", "persistence", "semantic_types"}),
    "command": frozenset({"domain", "semantic_types"}),
    "commit": frozenset(
        {
            "command",
            "boundaries",
            "persistence",
            "audit",
            "events",
            "semantic_types",
            # PKG-13: `authority` added so `coordinator.py` can construct
            # a real `authority.actor.ActorIdentity` for
            # `boundaries.types.BoundaryContext.actor` when invoking
            # BND-014 (14 §3.1's own row for `boundaries` already
            # requires the identical import for the same reason).
            # Type-only use: `commit` never constructs an
            # `AuthorityResolver` itself, it only carries the identity
            # value through to the boundary evaluator it holds.
            "authority",
            # PKG-13: `governance` added so `coordinator.py`'s own
            # `commit()` method can type its `required_authority_class`
            # parameter as the real `governance.authority_binding.
            # AuthorityClass` closed enum instead of an untyped string
            # (14 PKG-13 PUBLIC_INTERFACES: "unversioned consequential
            # dict payloads are forbidden where they erase semantics") --
            # the identical reason `boundaries/bnd_005_human_authority.py`
            # already imports it.
            "governance",
            # PKG-17: `evidence` added so `coordinator.py` can resolve
            # `evidence.freshness.EvidenceSetFreshnessResult` immediately
            # before invoking BND-014 (09 section 114: "BND-014 compares
            # member versions/current states") -- 14 PKG-17's own
            # OBJECTIVE is literally "BND-013 and commit freshness
            # linkage". Read-only use: `commit` calls
            # `evidence.freshness.resolve_evidence_set_freshness` (which
            # itself performs no I/O) via a caller-supplied
            # `EvidenceFreshnessPort`, and never imports
            # `persistence.evidence_repository` directly.
            "evidence",
        }
    ),
    "audit": frozenset({"semantic_types"}),
    "events": frozenset({"semantic_types"}),
    "projection": frozenset({"events", "persistence", "semantic_types"}),
    "recovery": frozenset({"command", "boundaries", "commit", "semantic_types"}),
    "security": frozenset({"semantic_types"}),
    "observability": frozenset({"semantic_types"}),
    "application": frozenset(
        {
            "command",
            "boundaries",
            "authority",
            "governance",
            "evidence",
            "ai_contracts",
            "ai_gateway",
            "recovery",
            "domain",
            "audit",
            "events",
            "projection",
            "security",
            "observability",
            "semantic_types",
            # PKG-01: `persistence` added for read-only `CanonicalReadPort`
            # use (14 §11: "Commit evaluation... use canonical reads";
            # `WorkspaceRepository.get` never returns an authority
            # conclusion, 14 §10). Writes remain forbidden at this layer —
            # `persistence`'s repositories exposed to `application` must
            # stay read-only; the one write path is through `commit`
            # (see below).
            "persistence",
            # PKG-14: `commit` added so `application.question_selection_handler`
            # can construct and invoke a real `commit.coordinator.CommitCoordinator`
            # -- 14 §3.1's own "May depend on" column for `application` reads
            # "public ports above" (`commit` appears above `application` in
            # that same table), and 14 §14's own COMMAND PROCESSOR pipeline
            # places "RUN PRECOMMIT BOUNDARIES" and "ENTER COMMIT COORDINATOR"
            # as adjacent steps of the same orchestration -- `application`'s
            # own directory-ownership row ("use-case orchestration and
            # Query/Command dispatch") is exactly this orchestrating layer.
            # No earlier package needed this edge: PKG-07's own
            # `burst_operations.py` predates both `boundaries`/`commit`
            # existing at all, and every package since (PKG-08 through
            # PKG-13) built only the generic engine, never a caller. This is
            # the first application-layer module to invoke a governed write
            # for real; `application` still never imports `persistence` for
            # anything but reads (see comment above).
            "commit",
        }
    ),
    "persistence": frozenset(
        {
            "semantic_types",
            # PKG-02: `governance` added so persistence's Record dataclasses
            # can be typed with governance's closed vocabularies
            # (`WorkspaceRole`, `MembershipStatus`, `AuthorityClass`,
            # `AuthorityBindingState`) instead of falling back to raw
            # strings. Type-only use: persistence still implements the
            # storage adapter, governance still owns "governance state"
            # (14 §3.1) — no mutation authority flows the other way,
            # since governance's own allowed set (above) does not include
            # `persistence`.
            "governance",
            # PKG-05: `domain` added so `challenge_session_mapping` can
            # map an already-fetched row into the frozen `Challenge`/
            # `Session` canonical types instead of handing callers raw
            # dicts and a text `state` column (14 §3.1: `persistence`
            # may depend on "semantic contracts" — `domain` owns
            # "Things, Relations, state specs, invariants"). Read-only,
            # one-directional use: `domain` itself may depend on
            # `semantic_types` only, so it cannot reach back into
            # persistence, and this module performs no write.
            "domain",
            # PKG-10: `command` added so `command_repository.py` can
            # store/reconstruct real `CommandEnvelope`/`CommandOutcome`
            # instances (14 §10: "CommandRepository: immutable Command
            # plus attempt records") instead of duplicating those types
            # as untyped rows. Same one-directional pattern as
            # `persistence domain`/`persistence governance`: `command`'s
            # own allowed set (14 §3.1: "domain contracts, semantic_types")
            # does not include `persistence`, so no cycle is created,
            # and this module performs the one write `command` itself is
            # forbidden from performing ("no direct write").
            "command",
            # PKG-12: `audit` added so `audit_repository.py` can
            # store/reconstruct real `AuditEvent` instances (14 §10:
            # "AuditRepository: append only") instead of duplicating
            # that type as an untyped row. Same one-directional
            # pattern: `audit`'s own allowed set (14 §3.1: "semantic_types")
            # does not include `persistence`, so no cycle is created.
            "audit",
            # PKG-12: `events` added so `outbox_repository.py` can
            # store/reconstruct real `OutboxRecord`/`DeliveryStatus`
            # instances (14 §10: "OutboxRepository: append in CommitUnit,
            # delivery-state update by worker"). Same one-directional
            # pattern: `events`'s own allowed set (14 §3.1: "semantic_types")
            # does not include `persistence`, so no cycle is created.
            "events",
            # PKG-13: `commit` added so `commit_repository.py` can
            # store/reconstruct real `CommitUnit`/`CommitOutcome`
            # instances (14 §10: "CommitRepository: CommitUnit proof
            # records"). Unlike every extension above, `commit`'s own
            # allowed set (14 §3.1) *does* already include `persistence`
            # (needed by `commit/idempotency.py`, PKG-11) -- this is
            # therefore not a one-directional pattern the way the others
            # are. It is still safe: `commit/idempotency.py` (the only
            # `commit` submodule that imports `persistence`) and
            # `commit/coordinator.py` (the only one `persistence.
            # commit_repository` imports from) are disjoint submodules,
            # so no actual Python import cycle exists at module-load
            # time -- only a package-level "ceiling" permission exists in
            # both directions, exactly as 14 PKG-13's own
            # FILES_ALLOWED_TO_CREATE explicitly separates "packages/commit
            # coordinator" from "persistence commit repository" as two
            # distinct targets, unlike PKG-11's single-file idempotency
            # design.
            "commit",
            # PKG-16: `evidence` added so `evidence_repository.py` can
            # store/reconstruct real `Evidence`/`SourceReference`/
            # `ClaimAnchor`/`EvidenceRelation`/`EvidenceSetReference`
            # instances (14 §10: "EvidenceRepository: authoritative
            # versioned Evidence and relation reads, governed writes").
            # Same one-directional pattern as `persistence -> audit`/
            # `persistence -> events`: `evidence`'s own allowed set
            # (14 §3.1: "domain, semantic_types") does not include
            # `persistence`, so no cycle is created.
            "evidence",
            # PKG-18: `ai_contracts` added so `ai_record_repository.py`
            # can store/reconstruct real `AIGeneration`/`AIDerivedArtifact`
            # instances (14 section 10: "AIRecordRepository: AIGeneration,
            # manifest and derived artifact operational writes only").
            # Same one-directional pattern as `persistence -> audit`/
            # `persistence -> events`/`persistence -> evidence`:
            # `ai_contracts`'s own allowed set (14 section 3.1: "semantic_types,
            # evidence read contracts") does not include `persistence`,
            # so no cycle is created.
            "ai_contracts",
            # PKG-19: `ai_gateway` added so `ai_record_repository.py`
            # can store/reconstruct real `ai_gateway.context.
            # AIContextManifest` instances (14 section 10's own
            # `AIRecordRepository` port covers "AIGeneration, manifest
            # and derived artifact operational writes"). Unlike every
            # extension above, `ai_gateway`'s own allowed set (14
            # section 3.1) *does* already include `persistence`
            # (`ai_gateway/gateway.py` needs it) -- this is therefore
            # not a one-directional pattern the way the others are. It
            # is still safe: `ai_gateway/gateway.py` (the only
            # `ai_gateway` submodule that imports `persistence`) and
            # `persistence/ai_record_repository.py` (the only
            # `persistence` submodule that imports `ai_gateway`, and
            # only its `context` submodule specifically) are disjoint
            # submodules, so no actual Python import cycle exists at
            # module-load time -- the identical bidirectional-edge
            # justification `commit <-> persistence` already
            # established (PKG-11/13).
            "ai_gateway",
        }
    ),
    "test_support": frozenset(KNOWN_INTERNAL_PACKAGES - {"test_support"}),
    "nquiry_api": frozenset({"application", "semantic_types"}),
    "nquiry_worker": frozenset(
        {"events", "projection", "recovery", "command", "commit", "semantic_types"}
    ),
}

_WEB_FRAMEWORK = frozenset({"fastapi", "starlette", "uvicorn"})
_DB_DRIVER = frozenset({"sqlalchemy", "psycopg", "psycopg2", "asyncpg"})
_OTEL_VENDOR = frozenset({"opentelemetry"})

# "Must not depend on" (14 §3.1) plus the forbidden-dependency matrix
# (§4), restricted to concrete external module names. Provider SDK
# checking here is deliberately redundant with
# `check_provider_sdk_imports.py` (defense in depth, single rule
# stated twice is not a forbidden shortcut).
EXTERNAL_FORBIDDEN: dict[str, frozenset[str]] = {
    "domain": _WEB_FRAMEWORK | _DB_DRIVER | _OTEL_VENDOR | PROVIDER_SDK_MODULES,
    "authority": PROVIDER_SDK_MODULES,
    "boundaries": _WEB_FRAMEWORK | PROVIDER_SDK_MODULES,
    "evidence": PROVIDER_SDK_MODULES,
    "ai_contracts": PROVIDER_SDK_MODULES,
    "ai_gateway": PROVIDER_SDK_MODULES,  # exempted for adapters/providers/, see below
    "command": _WEB_FRAMEWORK | PROVIDER_SDK_MODULES,
    "commit": PROVIDER_SDK_MODULES,
    # PKG-12: explicit DB-driver hardening, matching `application`'s own
    # entry below -- `audit`/`events` allowed-imports (14 §3.1:
    # "semantic_types") already implies no ORM code belongs here; this
    # makes that implication independently checkable rather than
    # relying only on the INTERNAL_ALLOWED table ever staying correct.
    "audit": _DB_DRIVER | PROVIDER_SDK_MODULES,
    "events": _DB_DRIVER | PROVIDER_SDK_MODULES,
    "application": _DB_DRIVER | PROVIDER_SDK_MODULES,
    "nquiry_api": _DB_DRIVER | PROVIDER_SDK_MODULES,
}

_PROVIDER_ADAPTER_PATH_MARKER = Path("ai_gateway") / "adapters" / "providers"


@dataclass(frozen=True, slots=True)
class Violation:
    file: Path
    owner_package: str
    imported: str
    lineno: int
    rule: str

    def __str__(self) -> str:
        try:
            rel = self.file.relative_to(Path(__file__).resolve().parent.parent)
        except ValueError:
            rel = self.file
        return (
            f"{rel}:{self.lineno}: package '{self.owner_package}' "
            f"imports '{self.imported}' — {self.rule}"
        )


def _is_approved_provider_adapter_file(file: Path) -> bool:
    return str(_PROVIDER_ADAPTER_PATH_MARKER) in str(file)


def check(roots: tuple[Path, ...] | None = None) -> list[Violation]:
    """Run the check. `roots` defaults to this repository's real source
    roots; tests pass a fabricated fixture tree instead so a controlled
    violation can be proven without touching real production code.
    """
    scan_roots = roots if roots is not None else (PACKAGES_ROOT, API_SRC_ROOT, WORKER_SRC_ROOT)
    violations: list[Violation] = []
    for imp in scan_owned_packages(*scan_roots):
        if imp.module == imp.owner_package:
            continue  # self-import (re-export, package __init__), never a cross-package concern

        if imp.module in KNOWN_INTERNAL_PACKAGES:
            allowed = INTERNAL_ALLOWED.get(imp.owner_package, frozenset())
            if imp.module not in allowed:
                violations.append(
                    Violation(
                        imp.file,
                        imp.owner_package,
                        imp.module,
                        imp.lineno,
                        f"'{imp.module}' is not on the 14 §3.1 'May depend on' "
                        f"list for '{imp.owner_package}'",
                    )
                )
            continue

        forbidden = EXTERNAL_FORBIDDEN.get(imp.owner_package, frozenset())
        if imp.module in forbidden:
            if (
                imp.owner_package == "ai_gateway"
                and imp.module in PROVIDER_SDK_MODULES
                and _is_approved_provider_adapter_file(imp.file)
            ):
                continue  # the one approved provider SDK import boundary
            violations.append(
                Violation(
                    imp.file,
                    imp.owner_package,
                    imp.module,
                    imp.lineno,
                    f"'{imp.module}' is forbidden for '{imp.owner_package}' by 14 §3.1/§4",
                )
            )
    return violations


def main() -> int:
    violations = check()
    if violations:
        print("ARCHITECTURE_DEPENDENCY_CHECK::FAIL")
        for v in violations:
            print(f"  {v}")
        print(f"{len(violations)} violation(s) found.")
        return 1
    print("ARCHITECTURE_DEPENDENCY_CHECK::PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
