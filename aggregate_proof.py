"""Falsifiers for aggregate.py (B4 aggregation semantics incl. exit 5; B5 per-node equivalence).
Evidence-only: builds the positive control by splitting the REAL serial-run-2 junit into the declared
partitions, then mutates it. Executes no test. Exit 0 iff every check holds."""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from aggregate import CLAIM, Case, aggregate, junit_id, load_reference, read_junit  # noqa: E402
from canonical_ids import canonical_junit, canonical_nodeid  # noqa: E402

EV = pathlib.Path(__file__).resolve().parent / "evidence"
R2 = EV / "final_closure" / "serial_ref"  # the same-environment serial reference (committed)
PART = pathlib.Path(__import__("os").environ.get("ORANGE_PARTITION_DIR") or EV / "final_closure" / "parallel" / "partition")
full = [l for l in (R2 / "collected_nodeids.txt").read_text().splitlines() if l]
serial_part = [l for l in (PART / "serial_nodeids.txt").read_text().splitlines() if l]
xdist_part = [l for l in (PART / "xdist_nodeids.txt").read_text().splitlines() if l]
declared = {l for l in (R2 / "declared_skips.txt").read_text().splitlines() if l}
reference = load_reference(R2 / "canonical_outcomes.tsv")
cases = read_junit(R2 / "junit.xml")
serial_canon = {canonical_nodeid(n) for n in serial_part}


def is_serial(c: Case) -> bool:
    return canonical_nodeid(f"{c.classname.replace('.', '/')}.py::{c.name}") in serial_canon or \
        canonical_junit(c.classname, c.name) in {canonical_junit(*junit_id(n)) for n in serial_part}


x_cases = [c for c in cases if not is_serial(c)]
s_cases = [c for c in cases if is_serial(c)]
results: list[tuple[str, bool, str]] = []


def run(**over):  # type: ignore[no-untyped-def]
    args = dict(full=full, serial_part=serial_part, xdist_part=xdist_part, xdist_cases=x_cases,
                xdist_exit=0, serial_cases=s_cases, serial_exit=0, declared_skips=declared,
                reference=reference)
    args.update(over)
    return aggregate(**args)


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"{name}::{'PASS' if ok else 'FAIL'} {detail}"[:220])


check("CONTROL_SPLIT_IS_2235_4", len(x_cases) == 2235 and len(s_cases) == 4, f"{len(x_cases)}/{len(s_cases)}")
bad, rows = run()
check("POSITIVE_CONTROL_AGGREGATES_CLEAN", not bad and len(rows) == 2239, str(bad))
check("RAW_PROVENANCE_KEPT", all(r["raw_collected"] and r["raw_executed"] for r in rows))


def flip(state_from: str, state_to: str, where: list[Case]) -> list[Case]:
    out = list(where)
    i = next(i for i, c in enumerate(out) if c.state == state_from)
    out[i] = Case(out[i].classname, out[i].name, state_to)
    return out


mutants = {
    "xdist_exit_5_is_failure": dict(xdist_exit=5),
    "serial_exit_5_is_failure": dict(serial_exit=5),
    "xdist_exit_1": dict(xdist_exit=1),
    "empty_xdist_junit_with_exit_0": dict(xdist_cases=[]),
    "empty_serial_junit_with_exit_0": dict(serial_cases=[]),
    "xdist_node_missing": dict(xdist_cases=x_cases[1:]),
    "serial_node_missing": dict(serial_cases=s_cases[1:]),
    "serial_node_also_run_in_xdist": dict(xdist_cases=x_cases + [s_cases[0]]),
    "xdist_node_run_twice": dict(xdist_cases=x_cases + [x_cases[0]]),
    "drift_2234_5_declared": dict(xdist_part=xdist_part[1:], serial_part=serial_part + [xdist_part[0]]),
    "moved_node_run_in_xdist_instead": dict(
        xdist_cases=x_cases + [c for c in s_cases if c.name.startswith("test_worker_loop_survives")],
        serial_cases=[c for c in s_cases if not c.name.startswith("test_worker_loop_survives")]),
    "extra_skip": dict(xdist_cases=flip("passed", "skipped", x_cases)),
    "declared_skip_executed_instead": dict(xdist_cases=flip("skipped", "passed", x_cases)),
    "one_failure": dict(xdist_cases=flip("passed", "failed", x_cases)),
    "one_error": dict(serial_cases=flip("passed", "error", s_cases)),
    "unknown_node_in_junit": dict(xdist_cases=x_cases + [Case("tests.e2e.test_ghost", "test_ghost", "passed")]),
    "outcome_diverges_from_serial_reference": dict(
        reference={**reference, next(iter(sorted(reference))): "skipped"}),
    "reference_incomplete": dict(reference=dict(list(reference.items())[:-1])),
}
for name, over in mutants.items():
    b, _ = run(**over)
    check(f"FALSIFIER_DETECTS[{name}]", bool(b), str(b))
check("CLAIM_CEILING_TEXT", CLAIM.startswith("2235 nodes executed under governed 4-worker parallelism + 4 nodes")
      and "all 2239" not in CLAIM and "2239 parallel" not in CLAIM)
ok = all(r[1] for r in results)
print(f"AGGREGATION_PROOF::{'PASS' if ok else 'FAIL'} ({sum(r[1] for r in results)}/{len(results)})")
sys.exit(0 if ok else 1)
