"""B2 scheduling-order proof (evidence-only). Under --dist load each worker must execute node
indices in strictly increasing collection order, so no worker can run one of the 3 connection-
leaking `real_engine` tests before one of the 13 race tests (TEMPLATE clone needs exclusive access
to the worker DB). Usage: python order_proof.py <dir with order_gwN.txt> <xdist partition nodeids>."""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from canonical_ids import canonical_nodeid  # noqa: E402

LEAKERS = ("tests/e2e/test_pfc_f09_1_technical_failure.py::test_engine_reports_a_rejected_commit_as_proven_abort",
           "tests/e2e/test_pfc_f09_1_technical_failure.py::test_engine_reports_a_lost_commit_as_outcome_unknown",
           "tests/e2e/test_pfc_f09_1_technical_failure.py::test_engine_success_and_body_failure_keep_their_semantics")
RACE_FILES = ("tests/e2e/test_f03_concurrency.py::", "tests/e2e/test_f04_concurrency.py::")


def violations(orders: dict[str, list[str]], collection: list[str]) -> list[str]:
    index = {canonical_nodeid(n): i for i, n in enumerate(collection)}
    bad = []
    seen: set[str] = set()
    for worker, seq in sorted(orders.items()):
        pos = [index.get(canonical_nodeid(n), -1) for n in seq]
        if -1 in pos:
            bad.append(f"{worker}: node outside the partition")
        if any(b <= a for a, b in zip(pos, pos[1:])):
            bad.append(f"{worker}: not strictly increasing collection order")
        leak_at = [i for i, n in enumerate(seq) if n in LEAKERS]
        race_at = [i for i, n in enumerate(seq) if n.startswith(RACE_FILES)]
        if leak_at and race_at and min(leak_at) < max(race_at):
            bad.append(f"{worker}: a connection-leaking real_engine test precedes a race test")
        dup = seen & {canonical_nodeid(n) for n in seq}
        if dup:
            bad.append(f"{worker}: node(s) also executed on another worker")
        seen |= {canonical_nodeid(n) for n in seq}
    return bad


def main() -> int:
    d, part = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    # pytest collection order (not alphabetical): taken from the raw collect-only output
    raw = [l for l in (part.parent / (part.stem.replace("_nodeids", "_raw") + ".txt")).read_text().splitlines() if "::" in l]
    collection_order = raw
    assert len(collection_order) == len([l for l in part.read_text().splitlines() if l])
    orders = {p.stem.removeprefix("order_"): [l for l in p.read_text().splitlines() if l]
              for p in sorted(d.glob("order_gw*.txt"))}
    total = sum(len(v) for v in orders.values())
    ok_all = True
    v = violations(orders, collection_order)
    print(f"workers={sorted(orders)} nodes_started={total} per_worker={ {k: len(s) for k, s in orders.items()} }")
    for w, seq in sorted(orders.items()):
        lk = [i for i, n in enumerate(seq) if n in LEAKERS]; rc = [i for i, n in enumerate(seq) if n.startswith(RACE_FILES)]
        print(f"  {w}: race tests at {rc[:3]}{'...' if len(rc) > 3 else ''} ({len(rc)}), leakers at {lk}")
    print("ORDER_MONOTONE_AND_LEAK_AFTER_RACE::" + ("PASS" if not v else f"FAIL {v}"))
    ok_all &= not v
    # falsifiers
    w0 = next(iter(sorted(orders)))
    rev = {**orders, w0: list(reversed(orders[w0]))}
    f1 = violations(rev, collection_order)
    print("FALSIFIER_DETECTS[reversed_worker_order]::" + ("PASS" if f1 else "FAIL"))
    race = next(n for n in collection_order if n.startswith(RACE_FILES))
    leak_first = {"gwX": [LEAKERS[0], race]}
    f2 = violations(leak_first, collection_order)
    print("FALSIFIER_DETECTS[leaker_before_race]::" + ("PASS" if f2 else "FAIL") + f" {f2}")
    other = next(w for w in sorted(orders) if w != w0)
    dup = {**orders, other: orders[other] + [orders[w0][0]]}
    f3 = violations(dup, collection_order)
    print("FALSIFIER_DETECTS[node_on_two_workers]::" + ("PASS" if f3 else "FAIL"))
    ok_all &= bool(f1) and bool(f2) and bool(f3)
    print("ORDER_PROOF::" + ("PASS" if ok_all else "FAIL"))
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
