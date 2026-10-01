"""Instrumentation inertness: per-node serial outcomes under guard 1.2.0 (new serial reference) vs the
accepted serial reference under guard 1.0.0 (serial_run2), on canonical identity. The only node allowed
to differ is the documented SF-PX-03 node (FIXED_TIME_WINDOW_NOT_EXECUTION_LOAD_INVARIANT); every other
difference falsifies inertness. Usage: python inertness_compare.py <new serial dir> <accepted serial dir>"""

from __future__ import annotations

import pathlib
import sys

SF_PX_03 = "tests/e2e/test_pfc_f09_1_technical_failure.py::test_worker_loop_survives_a_database_outage_and_stops_gracefully"


def outcomes(d: pathlib.Path) -> dict[str, str]:
    rows = [l.split("\t") for l in (d / "canonical_outcomes.tsv").read_text().splitlines()[1:] if l]
    return {r[0]: r[3] for r in rows}


def compare(new: dict[str, str], old: dict[str, str]) -> tuple[list[str], list[str]]:
    bad, documented = [], []
    if set(new) != set(old) or len(new) != 2239:
        bad.append(f"CANONICAL_SETS_DIFFER (new {len(new)}, accepted {len(old)})")
    for cid in sorted(set(new) & set(old)):
        if new[cid] != old[cid]:
            (documented if cid == SF_PX_03 else bad).append(f"{cid}: {old[cid]} -> {new[cid]}")
    return bad, documented


def main() -> int:
    new, old = outcomes(pathlib.Path(sys.argv[1])), outcomes(pathlib.Path(sys.argv[2]))
    bad, documented = compare(new, old)
    same = sum(new[c] == old.get(c) for c in new)
    print(f"nodes={len(new)} identical_outcomes={same} documented_SF-PX-03_differences={documented} "
          f"undocumented_differences={bad}")
    # falsifiers: an undocumented difference must be caught; the documented one must not be hidden
    probe = dict(new); k = next(c for c in sorted(probe) if c != SF_PX_03)
    probe[k] = "failed" if probe[k] != "failed" else "passed"
    f1, _ = compare(probe, old)
    probe2 = dict(new); probe2.pop(k)
    f2, _ = compare(probe2, old)
    print("FALSIFIER_DETECTS[undocumented_outcome_change]::" + ("PASS" if f1 else "FAIL"))
    print("FALSIFIER_DETECTS[missing_node]::" + ("PASS" if f2 else "FAIL"))
    print(f"SF_PX_03_NODE: accepted={old.get(SF_PX_03)} new={new.get(SF_PX_03)} (documented, never normalized)")
    ok = not bad and bool(f1) and bool(f2)
    print("INSTRUMENTATION_INERT_FOR_SERIAL_OUTCOMES::" + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
