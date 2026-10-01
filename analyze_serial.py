"""Post-run analysis of the ORANGE serial baseline (read-only over evidence files).

Proves: executed node-id set == declared collection; skip set == declared 2 nodes;
zero failures / errors; the 13 concurrency tests EXECUTED (not skipped); pre/post
state equality (tree, environment, proof DBs, cluster objects, guard).
"""

from __future__ import annotations

import json
import pathlib
import sys
import xml.etree.ElementTree as ET

S = pathlib.Path(__import__("os").environ.get("ORANGE_SERIAL_DIR") or pathlib.Path(__file__).resolve().parent / "evidence" / "final_closure" / "serial_ref")


def junit_id(nodeid: str) -> tuple[str, str]:
    # split on "::" only OUTSIDE the parametrize brackets (ids may contain "::", e.g. ::jsonb)
    base, bracket, params = nodeid.partition("[")
    parts = base.split("::")
    module = parts[0][:-3].replace("/", ".") if parts[0].endswith(".py") else parts[0]
    return ".".join([module, *parts[1:-1]]), parts[-1] + bracket + params


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from canonical_ids import canonical_junit, canonical_map, canonical_nodeid  # noqa: E402
"""Human Authority "TEST IDENTITY EQUIVALENCE": comparison uses the proof-lane canonical identity
(evidence only; proven by canonical_ids_proof.py); raw ids are kept alongside."""


def main() -> int:
    ok = True
    collected = [l for l in (S / "collected_nodeids.txt").read_text().splitlines() if l]
    declared_skips = {l for l in (S / "declared_skips.txt").read_text().splitlines() if l}
    canon = canonical_map(collected)  # raises if not injective over the 2239 raw ids
    by_junit = {canonical_junit(*junit_id(n)): n for n in collected}
    assert len(by_junit) == len(collected), "ambiguous junit mapping"

    states: dict[str, list[str]] = {}
    raw_exec: dict[str, set[str]] = {}
    unknown: list[tuple[str, str]] = []
    for case in ET.parse(S / "junit.xml").getroot().iter("testcase"):
        key = (case.get("classname", ""), case.get("name", ""))
        state = "passed"
        for tag, label in (("skipped", "skipped"), ("failure", "failed"), ("error", "error")):
            if case.find(tag) is not None:
                state = label
        node = by_junit.get(canonical_junit(*key))
        if node is None:
            unknown.append(key)
            continue
        states.setdefault(node, []).append(state)
        raw_exec.setdefault(node, set()).add("::".join(key))
    rank = {"error": 3, "failed": 2, "skipped": 1, "passed": 0}
    # worst state wins (junit may emit a second entry for a teardown error)
    outcomes = {n: max(st, key=rank.__getitem__) for n, st in states.items()}
    multi = {n: st for n, st in states.items() if len(st) > 1}
    if multi:
        print("nodes with multiple junit entries:", list(multi.items())[:10])
    with (S / "canonical_outcomes.tsv").open("w") as fh:
        fh.write("canonical_id\traw_collected_id\traw_executed_junit\toutcome\n")
        for n in collected:
            fh.write(f"{canon[n]}\t{n}\t{'|'.join(sorted(raw_exec.get(n, [])))}\t{outcomes.get(n)}\n")
    volatile = [(n, sorted(raw_exec.get(n, []))) for n in collected if canon[n] != n]
    print(f"canonical identities: {len(set(canon.values()))} (volatile raw ids canonicalized: {len(volatile)})")
    for n, ex in volatile:
        print(f"    {canon[n].split('::')[-1]}  raw collected={n.split('::')[-1]}  raw executed={[e.split('::')[-1] for e in ex]}  = {outcomes.get(n)}")

    executed = set(outcomes)
    missing = sorted(set(collected) - executed)
    counts: dict[str, int] = {}
    for s in outcomes.values():
        counts[s] = counts.get(s, 0) + 1
    skipped = {n for n, s in outcomes.items() if s == "skipped"}
    bad = sorted(n for n, s in outcomes.items() if s in ("failed", "error"))
    concurrency = [n for n in collected if "test_f03_concurrency.py" in n or "test_f04_concurrency.py" in n]
    conc_states = {n: outcomes.get(n) for n in concurrency}

    print(f"collected={len(collected)} executed_in_junit={len(executed)} counts={counts}")
    checks = {
        "COLLECTED_2239": len(collected) == 2239,
        "EXECUTED_SET_EQUALS_COLLECTION": not missing and not unknown and len(executed) == len(collected),
        "SKIP_SET_EQUALS_DECLARED_2": skipped == declared_skips,
        "ZERO_FAILURES_ERRORS": not bad,
        "CONCURRENCY_13_EXECUTED": len(concurrency) == 13 and all(v == "passed" for v in conc_states.values()),
        "EXIT_CODE_0": (S / "run_exit_code.txt").read_text().strip() == "0",
    }
    if missing:
        print("missing from junit:", missing[:10])
    if unknown:
        print("junit cases not in collection:", unknown[:10])
    if bad:
        print("failed/error:", bad[:20])
    if skipped != declared_skips:
        print("skip diff: extra", sorted(skipped - declared_skips), "missing", sorted(declared_skips - skipped))
    print("concurrency states:", sorted(set(conc_states.values()), key=str))

    def read(name: str) -> str:
        return (S / name).read_text()

    pre_tree = dict(l.split("=", 1) for l in read("pre_tree.txt").splitlines())
    post_tree = dict(l.split("=", 1) for l in read("post_tree.txt").splitlines())
    pre_db = json.loads(read("pre_proof_dbs.json"))
    post_db = json.loads(read("post_proof_dbs.json"))
    checks.update(
        {
            "TREE_UNCHANGED": pre_tree == post_tree
            and post_tree["status_entries_incl_ignored"] == "0"
            and post_tree["diff_vs_tag"] == "none",
            "ENV_MANIFEST_UNCHANGED": read("pre_env_manifest.json") == read("post_env_manifest.json"),
            "GUARD_GREEN_BEFORE_AND_AFTER": "PASS" in read("pre_guard.txt") and "PASS" in read("post_guard.txt"),
            "PROOF_DBS_SAME_HEAD_FINGERPRINT": [(r["db"], r["head"], r["fingerprint"]) for r in pre_db]
            == [(r["db"], r["head"], r["fingerprint"]) for r in post_db],
            "PROOF_DBS_CLEAN_AFTER": all(r["clean"] for r in post_db),
            "PROOF_DBS_NO_CONNECTIONS_AFTER": all(r["no_foreign_connections"] for r in post_db),
            "NO_RESIDUAL_RACE_DB": read("pre_race_dbs.txt") == read("post_race_dbs.txt") == "",
            "NO_RESIDUAL_ZZ_PKG25_ROLE": read("pre_zz_roles.txt") == read("post_zz_roles.txt") == "",
        }
    )
    for name, value in checks.items():
        print(f"{name}::{'PASS' if value else 'FAIL'}")
        ok = ok and value
    (S / "analysis.json").write_text(
        json.dumps({"checks": checks, "counts": counts, "skipped": sorted(skipped),
                    "concurrency": conc_states, "failed_or_error": bad}, indent=1)
    )
    print("SERIAL_BASELINE::" + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
