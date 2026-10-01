"""Proof + falsifiers for the ORANGE execution decomposition.
Current definition (Human Authority 2026-10-01): SERIAL = serial_partition_selectors.txt =
  the 3 volatile-identity nodes (test_malformed_input_is_refused[...]) +
  the 1 fixed-time-window node (SF-PX-03, test_worker_loop_survives_a_database_outage_...)  = 4;
XDIST = the exact complement = 2235. Reads collect-only evidence only; executes no test.

Two views, both required:
 (i)  SELECTOR SEMANTICS on ONE raw collection (raw-exact), using pytest --deselect prefix semantics.
 (ii) ACTUAL separately collected partitions: raw-exact for every stable id; the volatile ids
      (different uuid per process by construction) match by canonical identity, raw preserved.
"""

from __future__ import annotations

import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from canonical_ids import canonical_map, canonical_nodeid  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
D = pathlib.Path(os.environ.get("ORANGE_PARTITION_DIR") or HERE / "evidence" / "final_closure" / "parallel" / "partition")
SELECTORS = [l for l in (D / "serial_selector.txt").read_text().splitlines() if l]
MOVED = "tests/e2e/test_pfc_f09_1_technical_failure.py::test_worker_loop_survives_a_database_outage_and_stops_gracefully"
VOLATILE_FN = "tests/security/test_dev_identity_provisioning.py::test_malformed_input_is_refused"
FULL_N, SERIAL_N, XDIST_N = 2239, 4, 2235
results: list[tuple[str, bool, str]] = []


def load(name: str) -> list[str]:
    return [l for l in (D / f"{name}_nodeids.txt").read_text().splitlines() if l]


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"{name}::{'PASS' if ok else 'FAIL'} {detail}"[:230])


def selects(nodeid: str) -> bool:  # pytest --deselect: plain prefix match on the node id
    return any(nodeid.startswith(s) for s in SELECTORS)


def verify(full: list[str], serial: list[str], xdist: list[str]) -> list[str]:
    """Returns the list of violated properties (empty = partition proven)."""
    bad = []
    if len(full) != FULL_N or len(set(full)) != FULL_N:
        bad.append(f"RAW_COLLECTION_{FULL_N}")
    if len(serial) != SERIAL_N or len(set(serial)) != SERIAL_N:
        bad.append(f"SERIAL_EXACTLY_{SERIAL_N}_NO_DUPLICATE")
    if len(xdist) != XDIST_N or len(set(xdist)) != XDIST_N:
        bad.append(f"XDIST_EXACTLY_{XDIST_N}_NO_DUPLICATE")
    try:
        cf, cs, cx = canonical_map(full), canonical_map(serial), canonical_map(xdist)
    except ValueError as exc:
        return bad + [f"CANONICAL_NOT_INJECTIVE: {exc}"]
    CF, CS, CX = set(cf.values()), set(cs.values()), set(cx.values())
    if CS & CX:
        bad.append("PARTITIONS_OVERLAP")
    if CS | CX != CF or len(CS) + len(CX) != len(CF):
        bad.append("UNION_NOT_EQUAL_FULL_OR_OMISSION")
    if {canonical_nodeid(i) for i in full if selects(i)} != CS:
        bad.append("SERIAL_NOT_EXACTLY_THE_DECLARED_SELECTION")
    if any(selects(i) for i in xdist):
        bad.append("SERIAL_NODE_IN_XDIST_PARTITION")
    if MOVED not in serial or MOVED in xdist:
        bad.append("MOVED_TIMING_NODE_NOT_ONLY_IN_SERIAL")
    stable_full = {i for i in full if canonical_nodeid(i) == i}
    stable_parts = {i for i in serial + xdist if canonical_nodeid(i) == i}
    if stable_full != stable_parts:
        bad.append("STABLE_RAW_UNION_NOT_EQUAL_FULL")
    return bad


full, serial, xdist = load("full"), load("serial"), load("xdist")
check("SELECTORS_ARE_THE_DECLARED_TWO", SELECTORS == [VOLATILE_FN, MOVED], str(SELECTORS))
for s in SELECTORS:
    check(f"SELECTOR_PREFIX_UNAMBIGUOUS[{s.rsplit('::', 1)[1][:40]}]",
          all(i == s or i.startswith(s + "[") for i in full if i.startswith(s)))

# (i) selector semantics on ONE raw collection -> raw-exact partition
sel_serial = [i for i in full if selects(i)]
sel_xdist = [i for i in full if not selects(i)]
check(f"I_SELECTOR_SERIAL_EXACTLY_{SERIAL_N}", len(sel_serial) == SERIAL_N, str(len(sel_serial)))
check(f"I_SELECTOR_COMPLEMENT_EXACTLY_{XDIST_N}", len(sel_xdist) == XDIST_N, str(len(sel_xdist)))
check("I_DISJOINT_RAW", not set(sel_serial) & set(sel_xdist))
check("I_RAW_UNION_EQUALS_FULL_NO_OMISSION", set(sel_serial) | set(sel_xdist) == set(full))
vol = [i for i in full if canonical_nodeid(i) != i]
check("I_SERIAL_CONTAINS_BOTH_VOLATILE_IDS", set(vol) <= set(sel_serial) and len(vol) == 2)
check("I_MOVED_NODE_ONLY_IN_SERIAL", MOVED in sel_serial and MOVED not in sel_xdist)

# (ii) actual separately collected partitions
violations = verify(full, serial, xdist)
check("II_ACTUAL_PARTITION_PROVEN", not violations, str(violations))
check("II_CANONICAL_INJECTIVE_PER_PARTITION_AND_UNION",
      len(set(canonical_map(serial).values())) == SERIAL_N and len(set(canonical_map(xdist).values())) == XDIST_N
      and len(set(canonical_map(serial).values()) | set(canonical_map(xdist).values())) == FULL_N)
check("II_STABLE_RAW_IDS_IDENTICAL", set(xdist) == set(sel_xdist), "xdist partition raw == selector view")

# falsifiers: each mutation of the ACTUAL partitions must be detected by verify()
no_moved = [s for s in serial if s != MOVED]
mutants = {
    "omission_of_the_moved_node": (full, no_moved, xdist),
    "omission_of_a_volatile_node": (full, [s for s in serial if s != vol_s] if (vol_s := next(
        s for s in serial if canonical_nodeid(s) != s)) else serial, xdist),
    "moved_node_back_in_xdist_(old_2236_3)": (full, no_moved, sorted(xdist + [MOVED])),
    "moved_node_in_both_partitions": (full, serial, sorted(xdist + [MOVED])),
    "volatile_node_included_in_xdist": (full, serial[1:], sorted(xdist + [serial[0]])),
    "drift_2234_5": (full, sorted(serial + [xdist[0]]), xdist[1:]),
    "xdist_node_dropped": (full, serial, xdist[1:]),
    "duplicate_in_serial": (full, serial + [serial[0]], xdist),
    "duplicate_in_xdist": (full, serial, xdist + [xdist[0]]),
    "semantically_distinct_nodes_collapse": (full, [s.replace("A-short", "A-shorter") for s in serial], xdist),
}
for name, (f, s, x) in mutants.items():
    v = verify(f, s, x)
    check(f"FALSIFIER_DETECTS[{name}]", bool(v), str(v))
a = VOLATILE_FN + "[dev-0123456789@dev.local.test-A-short]"
b = VOLATILE_FN + "[dev-0123456789@dev.local.test-A-shorter]"
check("FALSIFIER_NO_CANONICAL_COLLAPSE[distinct params]", canonical_nodeid(a) != canonical_nodeid(b))
try:
    canonical_map([a, a.replace("0123456789", "9876543210")])
    check("FALSIFIER_CANONICAL_MAP_REJECTS_MERGE", False)
except ValueError:
    check("FALSIFIER_CANONICAL_MAP_REJECTS_MERGE", True)

ok = all(r[1] for r in results)
print(f"PARTITION_PROOF::{'PASS' if ok else 'FAIL'} ({sum(r[1] for r in results)}/{len(results)})")
sys.exit(0 if ok else 1)
