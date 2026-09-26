"""WU-PFC-A1 mutation proof: every repaired relation line is guarded by a falsifier.

Each mutation re-breaks one link of HTTP input -> application command -> domain
-> persistence -> GET projection (or the Case-2 rule) and must make
`tests/e2e/test_pfc_a1_challenge_frame.py` fail. The source file is restored
after every mutation. Exits 0 only if every mutation is KILLED.

Usage: `python scripts/pfc_a1_mutation_proof.py` with `DATABASE_URL` pointed at
the isolated A1 test database and the `.venv` active.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_API = "apps/api/src/nquiry_api/http/inquiry.py"
_DISPATCH = "packages/application/http_f02.py"
_QUERY = "packages/application/inquiry_queries.py"
_TEST = "tests/e2e/test_pfc_a1_challenge_frame.py"

MUTATIONS: list[tuple[str, str, str, str]] = [
    ("M01 body->command drops context", _API, "context=body.context,", "context=None,"),
    (
        "M02 body->command drops desiredOutcome",
        _API,
        "desired_outcome=body.desiredOutcome,",
        "desired_outcome=None,",
    ),
    (
        "M03 body->command drops constraints",
        _API,
        "constraints=body.constraints,",
        "constraints=None,",
    ),
    (
        "M04 body->command drops stakeholders",
        _API,
        "stakeholders=body.stakeholders,",
        "stakeholders=None,",
    ),
    (
        "M05 body accepts non-text context",
        _API,
        "    context: str | None = None",
        "    context: object = None",
    ),
    ("M06 command drops context", _DISPATCH, "context=_frame_text(context),", "context=None,"),
    (
        "M07 command drops desired_outcome",
        _DISPATCH,
        "desired_outcome=_frame_text(desired_outcome),",
        "desired_outcome=None,",
    ),
    (
        "M08 command drops constraints",
        _DISPATCH,
        "constraints=_frame_text(constraints),",
        "constraints=None,",
    ),
    (
        "M09 command drops stakeholders",
        _DISPATCH,
        "stakeholders=_frame_text(stakeholders),",
        "stakeholders=None,",
    ),
    (
        "M10 command silently cross-maps constraints<-stakeholders",
        _DISPATCH,
        "constraints=_frame_text(constraints),",
        "constraints=_frame_text(stakeholders),",
    ),
    (
        "M11 Case-2 rule trims stored text",
        _DISPATCH,
        "return value if value is not None and value.strip() else None",
        "return value.strip() if value is not None and value.strip() else None",
    ),
    (
        "M12 Case-2 rule stores blank text",
        _DISPATCH,
        "return value if value is not None and value.strip() else None",
        "return value",
    ),
    ("M13 projection drops context", _QUERY, '"context": challenge.context,', '"context": None,'),
    (
        "M14 projection drops desiredOutcome",
        _QUERY,
        '"desiredOutcome": challenge.desired_outcome,',
        '"desiredOutcome": None,',
    ),
    (
        "M15 projection drops constraints",
        _QUERY,
        '"constraints": challenge.constraints,',
        '"constraints": None,',
    ),
    (
        "M16 projection drops stakeholders",
        _QUERY,
        '"stakeholders": challenge.stakeholders,',
        '"stakeholders": None,',
    ),
    (
        "M17 projection cross-maps constraints<-stakeholders",
        _QUERY,
        '"constraints": challenge.constraints,',
        '"constraints": challenge.stakeholders,',
    ),
    (
        "M18 projection invents a status",
        _QUERY,
        '"stakeholders": challenge.stakeholders,',
        '"stakeholders": challenge.stakeholders, "status": "ACTIVE",',
    ),
]


def _run_tests() -> int:
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider", _TEST],
        cwd=_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode


def main() -> int:
    survived: list[str] = []
    for name, rel, old, new in MUTATIONS:
        path = _ROOT / rel
        original = path.read_text()
        if original.count(old) != 1:
            print(f"{name}: MUTATION_SITE_NOT_UNIQUE")
            survived.append(name)
            continue
        try:
            path.write_text(original.replace(old, new))
            code = _run_tests()
        finally:
            path.write_text(original)
        verdict = "KILLED" if code != 0 else "SURVIVED"
        print(f"{name}: {verdict}", flush=True)
        if code == 0:
            survived.append(name)
    print(f"{len(MUTATIONS) - len(survived)}/{len(MUTATIONS)} killed")
    return 1 if survived else 0


if __name__ == "__main__":
    raise SystemExit(main())
