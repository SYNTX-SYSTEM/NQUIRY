"""ORANGE aggregation + per-node serial-vs-parallel equivalence (B4 / B5). Evidence-only.

Combines the XDIST partition (2235) and the SERIAL partition (4) into one frozen-field result and
compares it, node by node on the canonical identity, with the serial reference baseline.

Aggregation law (fail-closed):
- each partition's exit code must be 0. Exit 5 (NO_TESTS_COLLECTED) is a FAILURE, never "nothing to
  do"; every other non-zero code is a failure.
- each partition executes exactly its declared canonical set (xdist 2235, serial 4), no duplicates
  inside a partition, no node in both partitions, union == the 2239 canonical collection;
- skip set == the declared 2 nodes; zero failed / error;
- every canonical node's aggregated outcome == its outcome in the serial reference.
Raw ids are kept per node (collected raw, executed raw, partition).

Claim ceiling (Human Authority): see CLAIM (2235 parallel + 4 serial = 2239 coverage). Never
"all 2239 executed in parallel".
"""

from __future__ import annotations

import pathlib
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from canonical_ids import canonical_junit, canonical_map, canonical_nodeid  # noqa: E402

CLAIM = ("2235 nodes executed under governed 4-worker parallelism + 4 nodes executed under governed "
         "serial execution (3 volatile-identity nodes + 1 fixed-time-window node, SF-PX-03) = complete "
         "2239-node frozen-field coverage")
RANK = {"error": 3, "failed": 2, "skipped": 1, "passed": 0}


def junit_id(nodeid: str) -> tuple[str, str]:
    base, bracket, params = nodeid.partition("[")
    parts = base.split("::")
    return ".".join([parts[0][:-3].replace("/", "."), *parts[1:-1]]), parts[-1] + bracket + params


@dataclass(frozen=True)
class Case:
    classname: str
    name: str
    state: str


def read_junit(path: pathlib.Path) -> list[Case]:
    cases = []
    for c in ET.parse(path).getroot().iter("testcase"):
        state = "passed"
        for tag, label in (("skipped", "skipped"), ("failure", "failed"), ("error", "error")):
            if c.find(tag) is not None:
                state = label
        cases.append(Case(c.get("classname", ""), c.get("name", ""), state))
    return cases


def aggregate(*, full: list[str], serial_part: list[str], xdist_part: list[str],
              xdist_cases: list[Case], xdist_exit: int, serial_cases: list[Case], serial_exit: int,
              declared_skips: set[str], reference: dict[str, str]) -> tuple[list[str], list[dict]]:
    """Returns (violations, rows). `reference`: canonical id -> serial-baseline outcome."""
    bad: list[str] = []
    for name, code in (("xdist", xdist_exit), ("serial", serial_exit)):
        if code == 5:
            bad.append(f"{name.upper()}_EXIT_5_NO_TESTS_COLLECTED_IS_FAILURE")
        elif code != 0:
            bad.append(f"{name.upper()}_EXIT_{code}")
    cfull = canonical_map(full)
    by_junit = {canonical_junit(*junit_id(n)): n for n in full}
    # partitions may come from other processes: compare on canonical identity
    expected = {"xdist": {canonical_nodeid(n) for n in xdist_part},
                "serial": {canonical_nodeid(n) for n in serial_part}}
    if expected["xdist"] & expected["serial"]:
        bad.append("DECLARED_PARTITIONS_OVERLAP")
    if expected["xdist"] | expected["serial"] != set(cfull.values()):
        bad.append("DECLARED_PARTITIONS_NOT_FULL_COVERAGE")
    executed: dict[str, dict] = {}
    for part, cases in (("xdist", xdist_cases), ("serial", serial_cases)):
        seen: dict[str, list[str]] = {}
        for c in cases:
            node = by_junit.get(canonical_junit(c.classname, c.name))
            if node is None:
                bad.append(f"{part.upper()}_UNKNOWN_NODE:{c.classname}::{c.name}"[:160])
                continue
            seen.setdefault(cfull[node], []).append(c.state)
            row = executed.setdefault(cfull[node], {"canonical": cfull[node], "raw_collected": node,
                                                     "partition": part, "raw_executed": set(), "states": []})
            if row["partition"] != part:
                bad.append(f"NODE_EXECUTED_IN_BOTH_PARTITIONS:{cfull[node]}"[:160])
            row["raw_executed"].add(f"{c.classname}::{c.name}")
            row["states"].append(c.state)
        repeated = sorted(cid for cid, states in seen.items() if len(states) > 1)
        if repeated:
            # a node may appear once per partition; two junit entries mean it executed twice
            # (e.g. a re-run after a worker crash) or failed in teardown -- never silently merged.
            bad.append(f"{part.upper()}_NODE_EXECUTED_MORE_THAN_ONCE:{len(repeated)}")
        got = set(seen)
        if got != expected[part]:
            miss, extra = expected[part] - got, got - expected[part]
            bad.append(f"{part.upper()}_EXECUTED_SET_MISMATCH missing={len(miss)} extra={len(extra)}")
    if set(executed) != set(cfull.values()):
        bad.append(f"UNION_NOT_2239 ({len(executed)})")
    rows = []
    for cid, row in executed.items():
        outcome = max(row["states"], key=RANK.__getitem__)
        rows.append({**row, "raw_executed": sorted(row["raw_executed"]), "outcome": outcome,
                     "reference": reference.get(cid)})
    skipped = {r["canonical"] for r in rows if r["outcome"] == "skipped"}
    if skipped != {canonical_nodeid(s) for s in declared_skips}:
        bad.append(f"SKIP_SET_MISMATCH ({len(skipped)})")
    failing = [r["canonical"] for r in rows if r["outcome"] in ("failed", "error")]
    if failing:
        bad.append(f"FAILURES:{len(failing)}")
    diverging = [r["canonical"] for r in rows if r["outcome"] != r["reference"]]
    if diverging:
        bad.append(f"OUTCOME_DIVERGES_FROM_SERIAL_REFERENCE:{len(diverging)}")
    if len(reference) != 2239:
        bad.append("REFERENCE_NOT_2239")
    return bad, sorted(rows, key=lambda r: r["canonical"])


def load_reference(tsv: pathlib.Path) -> dict[str, str]:
    lines = tsv.read_text().splitlines()[1:]
    return {l.split("\t")[0]: l.split("\t")[3] for l in lines if l}


__all__ = ["CLAIM", "Case", "aggregate", "load_reference", "read_junit"]
