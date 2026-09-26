"""WU-PFC-F08-1 mutation proof: every link of the durable Event basis is guarded.

Each mutation re-breaks one relation of CommitUnit -> committed Event ->
EventEnvelope (or a contract rule) and must make
`tests/e2e/test_pfc_f08_1_event_basis.py` fail. Sources are restored
byte-for-byte after every mutation (sha256 verified). Exits 0 only if every
mutation is KILLED and every file is restored.

Usage: `python scripts/pfc_f08_1_mutation_proof.py` with `DATABASE_URL` pointed
at an isolated *_test database migrated to head, and the `.venv` active.
"""

# ruff: noqa: E501 -- mutation sites are exact source fragments and cannot be wrapped

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_COORD = "packages/commit/coordinator.py"
_CONTRACTS = "packages/events/contracts.py"
_REPO = "packages/persistence/committed_event_repository.py"
_SESSION = "packages/application/session_control_handler.py"
_CAPTURE = "packages/application/burst_capture_handler.py"
_TEST = "tests/e2e/test_pfc_f08_1_event_basis.py"

Edit = tuple[str, str, str]
MUTATIONS: list[tuple[str, list[Edit]]] = [
    (
        "M01 commit writes no Event basis",
        [
            (
                _COORD,
                "            self._append_committed_event(\n",
                "            (lambda *a, **k: None)(\n",
            )
        ],
    ),
    (
        "M02 missing Event facts accepted",
        [
            (
                _CONTRACTS,
                '    if facts is None:\n        raise EventContractViolation(f"EVENT_BASIS_MISSING: {event_type}")\n',
                "    if facts is None:\n        return next(iter(registry.values()))\n",
            )
        ],
    ),
    (
        "M03 payload keys not checked",
        [(_CONTRACTS, "    if keys != contract.payload_keys:\n", "    if False:\n")],
    ),
    (
        "M04 aggregate kind not checked",
        [(_CONTRACTS, "    if kind != contract.aggregate_kind:\n", "    if False:\n")],
    ),
    (
        "M05 unregistered event type accepted",
        [
            (
                _CONTRACTS,
                "    contract = registry.get(event_type)\n",
                "    contract = registry.get(event_type) or next(iter(registry.values()))\n",
            )
        ],
    ),
    (
        "M06 non-scalar payload value accepted",
        [
            (
                _CONTRACTS,
                "        if value is not None and not isinstance(value, str | int | bool):\n",
                "        if False:\n",
            )
        ],
    ),
    (
        "M07 version asserted instead of read from the committed row",
        [(_REPO, "    return RecordVersion(int(row.v))\n", "    return RecordVersion(1)\n")],
    ),
    (
        "M08 aggregate of another Workspace accepted",
        [(_REPO, "    if row is None or row.ws != workspace_id.value:\n", "    if row is None:\n")],
    ),
    (
        "M09 missing basis reconstructed instead of refused",
        [
            (
                _REPO,
                "        if envelope is None:\n            raise EventBasisMissing",
                "        if False:\n            raise EventBasisMissing",
            )
        ],
    ),
    (
        "M10 outbox/Event disagreement not detected",
        [
            (
                _REPO,
                "            or envelope.event_type != record.event_type\n        ):",
                "            and envelope.event_type != record.event_type\n        ):",
            )
        ],
    ),
    (
        "M11 actor reference not the committed actor",
        [
            (
                _COORD,
                'actor_ref=f"{envelope.requesting_actor_type}:{envelope.requesting_actor_id}",',
                'actor_ref=f"{envelope.requesting_actor_id}",',
            )
        ],
    ),
    (
        "M12 authority source not the commit-time source",
        [
            (
                _COORD,
                "                authority_source_ref=authority_source_ref,\n                payload=",
                "                authority_source_ref=envelope.command_id.value,\n                payload=",
            )
        ],
    ),
    (
        "M13 session transition records the previous state as the new one",
        [
            (
                _SESSION,
                '                    "previous_state": session.state.value,\n                    "state": to_state.value,',
                '                    "previous_state": session.state.value,\n                    "state": session.state.value,',
            )
        ],
    ),
    (
        "M14 user-authored Question text copied into the Event",
        [
            (
                _CONTRACTS,
                '            "captured_order",\n            "origin",\n        ),',
                '            "captured_order",\n            "origin",\n            "text",\n        ),',
            ),
            (
                _CAPTURE,
                '                    "origin": QuestionOrigin.HUMAN.value,\n',
                '                    "origin": QuestionOrigin.HUMAN.value,\n                    "text": original_text,\n',
            ),
        ],
    ),
    (
        "M15 envelope time not the commit time",
        [
            (
                _COORD,
                "                occurred_at=outbox_record.created_at,\n",
                "                occurred_at=outbox_record.created_at.replace(microsecond=1),\n",
            )
        ],
    ),
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run_tests() -> int:
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider", _TEST],
        cwd=_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode


def main() -> int:
    files = {rel for _, edits in MUTATIONS for rel, _, _ in edits}
    before = {rel: _sha(_ROOT / rel) for rel in files}
    failures: list[str] = []
    for name, edits in MUTATIONS:
        originals = {rel: (_ROOT / rel).read_text() for rel, _, _ in edits}
        texts = dict(originals)
        unique = True
        for rel, old, new in edits:
            if texts[rel].count(old) != 1:
                unique = False
                break
            texts[rel] = texts[rel].replace(old, new)
        if not unique:
            print(f"{name}: MUTATION_SITE_NOT_UNIQUE", flush=True)
            failures.append(name)
            continue
        try:
            for rel, text in texts.items():
                (_ROOT / rel).write_text(text)
            code = _run_tests()
        finally:
            for rel, text in originals.items():
                (_ROOT / rel).write_text(text)
        killed = code != 0
        print(f"{name}: {'KILLED' if killed else 'SURVIVED'}", flush=True)
        if not killed:
            failures.append(name)
    restored = all(_sha(_ROOT / rel) == digest for rel, digest in before.items())
    print(f"{len(MUTATIONS) - len(failures)}/{len(MUTATIONS)} killed; sources restored: {restored}")
    return 0 if not failures and restored else 1


if __name__ == "__main__":
    raise SystemExit(main())
