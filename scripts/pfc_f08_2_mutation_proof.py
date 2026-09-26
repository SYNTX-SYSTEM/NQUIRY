"""WU-PFC-F08-2 mutation proof: every link of delivery -> projection -> replay is guarded.

Each mutation re-breaks one relation of the running pipeline (stale-event guard,
poison fail-closed, per-event isolation, aggregate-ordered due selection,
rebuild reset, fail-closed start) and must make the F08-2 falsifiers or the
accepted PKG-21 projection tests fail. Sources are restored byte-for-byte after
every mutation (sha256 verified). Exits 0 only if every mutation is KILLED and
every file is restored.

Usage: `python scripts/pfc_f08_2_mutation_proof.py` with `DATABASE_URL` pointed
at an isolated *_test database migrated to head, and the `.venv` active.
"""

# ruff: noqa: E501 -- mutation sites are exact source fragments and cannot be wrapped

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_CONSUMER = "packages/projection/consumer.py"
_DELIVERY = "apps/worker/src/nquiry_worker/delivery.py"
_ORDERED = "packages/persistence/committed_event_repository.py"
_MAIN = "apps/worker/src/nquiry_worker/__main__.py"
_TESTS = (
    "tests/e2e/test_pfc_f08_2_delivery.py",
    "tests/command_commit_event/test_projection.py",
    "tests/command_commit_event/test_projection_worker.py",
)

Edit = tuple[str, str, str]
MUTATIONS: list[tuple[str, list[Edit]]] = [
    (
        "M01 session read model applies a stale (older) event",
        [
            (
                _CONSUMER,
                "        if _is_stale(envelope, current.last_aggregate_version if current else None):\n            return  # WU-PFC-F08-2: a late (retried) older event never regresses the row\n        payload_state",
                "        payload_state",
            )
        ],
    ),
    (
        "M02 inquiry read model applies a stale (older) event",
        [
            (
                _CONSUMER,
                "        if _is_stale(envelope, current.last_aggregate_version if current else None):\n            return  # WU-PFC-F08-2: a late (retried) older event never regresses the row\n        model = InquiryReadModel(",
                "        model = InquiryReadModel(",
            )
        ],
    ),
    (
        "M03 equal-version events treated as stale",
        [
            (
                _CONSUMER,
                "        and envelope.aggregate_version_after_commit.value < projected_version",
                "        and envelope.aggregate_version_after_commit.value <= projected_version",
            )
        ],
    ),
    (
        "M04 poison record crashes the pass instead of failing closed",
        [
            (
                _DELIVERY,
                "        except EventBasisMissing as exc:",
                "        except LookupError as exc:  # noqa\n            raise\n        except KeyError as exc:",
            )
        ],
    ),
    (
        "M05 projection write not isolated per event",
        [
            (
                _DELIVERY,
                "            with self._ports.isolated():",
                "            with __import__('contextlib').nullcontext():",
            )
        ],
    ),
    (
        "M06 projection failure swallowed and marked delivered",
        [
            (
                _DELIVERY,
                '            raise EventDeliveryFailure(f"PROJECTION_STORE_FAILURE: {exc}") from exc',
                "            return",
            )
        ],
    ),
    (
        "M07 due selection ignores per-aggregate order",
        [
            (
                _ORDERED,
                "                e.c.aggregate_ref.nulls_last(),\n                e.c.aggregate_version_after_commit.nulls_last(),\n",
                "",
            )
        ],
    ),
    (
        "M08 rebuild keeps the (possibly corrupted) projection",
        [
            (
                _DELIVERY,
                "        ports.projection.reset_projection(name, workspace_id)",
                "        pass",
            )
        ],
    ),
    (
        "M09 worker starts without a database",
        [(_MAIN, "        return 2\n", "        pass\n")],
    ),
    (
        "M10 consumer records no aggregate version",
        [
            (
                _CONSUMER,
                "            last_aggregate_version=envelope.aggregate_version_after_commit.value,\n        )\n        self._repository.upsert_session_read_model(model)",
                "        )\n        self._repository.upsert_session_read_model(model)",
            )
        ],
    ),
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run_tests() -> int:
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider", *_TESTS],
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
