"""T11 MUTATION TESTING ENGINE: the generic runner PKG-31's own
"mutation runner" (14 §46 PUBLIC_INTERFACES) is built on.

TEST ONLY. Never imported by production code. Not itself collected by
pytest (this file has no `test_` prefix), but reachable in two ways:
`tests/mutation/mutation_cases.py` imports it directly (same directory
-- pytest's own rootless import inserts `tests/mutation/` onto
`sys.path` the moment any sibling `test_*.py` file in this directory
is collected, so a plain `from harness import ...` resolves); and
`scripts/run_mutation_harness.py` loads it by absolute file path via
`importlib.util.spec_from_file_location`, since `tests/` is not a
configured import root outside pytest (`pyproject.toml` `pythonpath`
lists `packages`/`apps/api/src`/`apps/worker/src`/`scripts`, not
`tests` -- confirmed by grep before writing this file).

WHY THIS RUNS THE PRE-EXISTING TEST SUITE, NOT NEW TESTS
--------------------------------------------------------------------
14 PKG-31's own OBJECTIVE: "Baseline PASS, mutation must make relevant
tests FAIL, restore, baseline PASS." This is empirical mutation
testing of the ALREADY-BUILT test suite's own detection power -- the
question is whether PKG-00 through PKG-30's own tests would notice if
a named invariant were removed, not whether new tests can be written
that would notice (that would prove nothing about the tests that
already exist). Each `MutationCase` therefore never adds a new
assertion of its own; it monkeypatches one real production attribute
in-process and re-invokes a real, pre-existing pytest node id.

WHY IN-PROCESS `pytest.main()`, NOT A SUBPROCESS PER PHASE
--------------------------------------------------------------------
A monkeypatch (`setattr` on a real class/module attribute) only
affects the CURRENT Python process's already-imported objects. A
subprocess-per-phase design would spawn a fresh interpreter for the
"mutated" phase that re-imports the target module from disk, seeing
the ORIGINAL, unpatched code -- the mutation would silently never take
effect and every case would report a false `SURVIVED`. Calling
`pytest.main()` three times (baseline/mutated/restored) from this same
process, targeting only the small node-id list each case names (never
the whole suite), is the standard technique real mutation-testing
tools use for exactly this reason, and keeps each phase to a handful
of already-cached-import test files rather than requiring a full
process boot per phase.
"""

from __future__ import annotations

import importlib
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

import pytest

MUTATION_IDS = tuple(f"MUT-PKG31-{n:02d}" for n in range(1, 11))
"""14's own OBJECTIVE names exactly ten mandatory mutations for this
critical package ("The listed ten mutations are mandatory... At least
10 total novel/adapted attacks are required"). Closed -- a case whose
`mutation_id` is not one of these ten fails closed at construction,
the same discipline `test_support.proof_bundle.E2E_PROOF_PATHS`
already established for PKG-30's own six named paths.
"""


class MutationInterpretation(Enum):
    """14 §27's own required vocabulary: "record invariant removed or
    weakened, expected red test, actual result, and interpretation."
    `SURVIVED` is the `TEST_DESIGN_DEFECT` case 14 §27 names explicitly
    ("If a prohibited mutation survives, classify TEST_DESIGN_DEFECT;
    do not report PASS."). `BASELINE_FAILED`/`RESTORE_FAILED` are
    HARNESS-integrity failures (a typo'd node id, a flaky fixture) --
    distinct from a genuine mutation-detection question, and reported
    separately rather than folded into `SURVIVED` so a reader is never
    misled into thinking the PRODUCTION invariant is unguarded when the
    real problem is this harness's own node-id list.
    """

    KILLED = "KILLED"
    SURVIVED = "SURVIVED"
    BASELINE_FAILED = "BASELINE_FAILED"
    RESTORE_FAILED = "RESTORE_FAILED"


@dataclass(frozen=True, slots=True)
class MutationPatch:
    """One `setattr` seam: `target_module.target_qualname` is resolved
    via `importlib`, its current value captured, replaced by
    `replacement_factory(original_value)` for the mutated phase, then
    restored verbatim. `replacement_factory` receives the real original
    (not just a placeholder) so a mutation that needs to WRAP behavior
    (MUT-PKG31-02's authority cache; MUT-PKG31-09's admin fallback) can
    still call through to genuine production logic for the cases it
    does not itself want to corrupt, while a mutation that unconditionally
    replaces behavior (e.g. MUT-PKG31-01's forced ALLOW) simply ignores
    the argument.
    """

    target_module: str
    target_qualname: str
    replacement_factory: Callable[[object], object]

    def __post_init__(self) -> None:
        if not self.target_module:
            raise ValueError("MutationPatch.target_module must be non-empty")
        if not self.target_qualname:
            raise ValueError("MutationPatch.target_qualname must be non-empty")


@dataclass(frozen=True, slots=True)
class MutationCase:
    mutation_id: str
    invariant: str
    """The architectural invariant this mutation removes or weakens,
    transcribed from 14's own OBJECTIVE line for this mutation."""
    expected_boundary: str
    """The BoundaryId (or 'N/A' where the invariant is not itself a
    BND-* evaluator, e.g. MUT-PKG31-06/10) this mutation targets."""
    patch: MutationPatch
    target_test_nodeids: tuple[str, ...]
    """Real, pre-existing pytest node ids (`path::test_name`) this
    mutation is expected to turn from PASS to FAIL. Never a new test
    written for this package -- see module docstring."""

    def __post_init__(self) -> None:
        if self.mutation_id not in MUTATION_IDS:
            raise ValueError(f"mutation_id must be one of {MUTATION_IDS}, got {self.mutation_id!r}")
        if not self.invariant:
            raise ValueError(f"{self.mutation_id}: invariant must be non-empty")
        if not self.expected_boundary:
            raise ValueError(f"{self.mutation_id}: expected_boundary must be non-empty")
        if not self.target_test_nodeids:
            raise ValueError(f"{self.mutation_id}: target_test_nodeids must be non-empty")


@dataclass(frozen=True, slots=True)
class MutationRunResult:
    mutation_id: str
    baseline_exit_code: int
    mutated_exit_code: int
    restored_exit_code: int
    interpretation: MutationInterpretation


def _resolve_owner_and_attr(module_path: str, qualname: str) -> tuple[object, str]:
    module = importlib.import_module(module_path)
    owner: object = module
    *path, attr = qualname.split(".")
    for part in path:
        owner = getattr(owner, part)
    return owner, attr


def _run_nodeids(nodeids: tuple[str, ...]) -> int:
    exit_code = pytest.main(["-q", *nodeids])
    return int(exit_code)


def run_mutation_case(case: MutationCase) -> MutationRunResult:
    """Baseline -> apply patch -> mutated -> restore patch -> restored.
    14 §46 OBJECTIVE's own exact four-phase sequence, in that order,
    unconditionally (the patch is always restored via `finally`, even
    if the mutated-phase run itself raises).
    """
    baseline = _run_nodeids(case.target_test_nodeids)

    owner, attr = _resolve_owner_and_attr(case.patch.target_module, case.patch.target_qualname)
    original = getattr(owner, attr)
    mutant = case.patch.replacement_factory(original)
    setattr(owner, attr, mutant)
    try:
        mutated = _run_nodeids(case.target_test_nodeids)
    finally:
        setattr(owner, attr, original)

    restored = _run_nodeids(case.target_test_nodeids)

    if baseline != int(pytest.ExitCode.OK):
        interpretation = MutationInterpretation.BASELINE_FAILED
    elif restored != int(pytest.ExitCode.OK):
        interpretation = MutationInterpretation.RESTORE_FAILED
    elif mutated == int(pytest.ExitCode.OK):
        interpretation = MutationInterpretation.SURVIVED
    else:
        interpretation = MutationInterpretation.KILLED

    return MutationRunResult(
        mutation_id=case.mutation_id,
        baseline_exit_code=baseline,
        mutated_exit_code=mutated,
        restored_exit_code=restored,
        interpretation=interpretation,
    )


__all__ = [
    "MUTATION_IDS",
    "MutationInterpretation",
    "MutationPatch",
    "MutationCase",
    "MutationRunResult",
    "run_mutation_case",
]
