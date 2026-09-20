"""PKG-31 mutation runner: 14 section 46's own required PUBLIC_INTERFACE
("mutation runner") for CI pipeline step 19 ("T11 mutation").

Runs each of the ten mandatory PKG-31 mutations (`tests/mutation/
mutation_cases.py`) against the real, pre-existing test suite in three
phases -- baseline, mutated, restored -- and prints one line per
mutation plus a final summary. Exits 0 only if every mutation was
genuinely KILLED (baseline PASS, mutated FAIL, restored PASS); exits 1
otherwise, naming which mutation(s) failed and why (SURVIVED is a
`TEST_DESIGN_DEFECT`, per 14 section 27; BASELINE_FAILED/RESTORE_FAILED
are this harness's own integrity failures, reported distinctly).

Usage: `python scripts/run_mutation_harness.py` with `DATABASE_URL`
pointed at a real local PostgreSQL (same requirement every DB-backed
test in this repository already has) and the `.venv` active.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]

# `tests/` is not a configured import root outside pytest (pyproject.toml's
# `pythonpath` lists `packages`/`apps/api/src`/`apps/worker/src`/`scripts`,
# not `tests`) -- both `harness.py` and `mutation_cases.py` are loaded by
# absolute file path via `importlib`, never a plain `import`, so this
# script's own module-level static imports stay fully mypy-resolvable
# without widening MYPYPATH for a `scripts`-wide type-check run.
for _relative in ("packages", "apps/api/src", "apps/worker/src"):
    _path = str(_REPO_ROOT / _relative)
    if _path not in sys.path:
        sys.path.insert(0, _path)


def _load_by_path(module_name: str, relative_path: str) -> Any:
    spec = importlib.util.spec_from_file_location(module_name, _REPO_ROOT / relative_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {relative_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    harness = _load_by_path("pkg31_mutation_harness", "tests/mutation/harness.py")
    MutationInterpretation = harness.MutationInterpretation
    run_mutation_case = harness.run_mutation_case

    # `mutation_cases.py` does `from harness import ...` -- registering the
    # already-loaded harness module under the bare name `harness` in
    # `sys.modules` first (see `_load_by_path` above) lets that plain
    # import resolve without needing `tests/mutation` on `sys.path`.
    sys.modules["harness"] = harness
    mutation_cases = _load_by_path("pkg31_mutation_cases", "tests/mutation/mutation_cases.py")
    mutations = mutation_cases.MUTATIONS
    print(f"PKG-31 MUTATION HARNESS -- {len(mutations)} mutations registered\n")

    results = []
    for case in mutations:
        print(f"--- {case.mutation_id} ---")
        print(f"invariant: {case.invariant}")
        print(f"expected_boundary: {case.expected_boundary}")
        print(f"target_test_nodeids: {case.target_test_nodeids}")
        result = run_mutation_case(case)
        results.append(result)
        print(
            f"baseline_exit={result.baseline_exit_code} "
            f"mutated_exit={result.mutated_exit_code} "
            f"restored_exit={result.restored_exit_code} "
            f"-> {result.interpretation.value}"
        )
        print()

    killed = [r for r in results if r.interpretation is MutationInterpretation.KILLED]
    survived = [r for r in results if r.interpretation is MutationInterpretation.SURVIVED]
    harness_failures = [
        r
        for r in results
        if r.interpretation
        in (MutationInterpretation.BASELINE_FAILED, MutationInterpretation.RESTORE_FAILED)
    ]

    print("=== SUMMARY ===")
    print(f"KILLED: {len(killed)}/{len(results)}")
    if survived:
        print(f"SURVIVED (TEST_DESIGN_DEFECT): {[r.mutation_id for r in survived]}")
    if harness_failures:
        print(f"HARNESS_INTEGRITY_FAILURE: {[r.mutation_id for r in harness_failures]}")

    return 0 if not survived and not harness_failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
