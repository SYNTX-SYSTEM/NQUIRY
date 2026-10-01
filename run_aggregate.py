"""Aggregate one governed parallel proof run (evidence-only) and prove the global post-state.
Usage: python run_aggregate.py <run dir>   (reference = $ORANGE_REFERENCE_DIR, default evidence/final_closure/serial_ref = same-environment serial reference)"""

from __future__ import annotations

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from aggregate import CLAIM, aggregate, load_reference, read_junit  # noqa: E402

P = pathlib.Path(__file__).resolve().parent
R = pathlib.Path(sys.argv[1]).resolve()
REF = pathlib.Path(__import__("os").environ.get("ORANGE_REFERENCE_DIR") or P / "evidence" / "final_closure" / "serial_ref")


def lines(p: pathlib.Path) -> list[str]:
    return [l for l in p.read_text().splitlines() if l]


def num(name: str) -> float:
    return float((R / name).read_text().strip())


full = lines(R / "partition/full_nodeids.txt")
serial_part = lines(R / "partition/serial_nodeids.txt")
xdist_part = lines(R / "partition/xdist_nodeids.txt")
declared = set(lines(R / "declared_skips.txt"))
reference = load_reference(REF / "canonical_outcomes.tsv")
xdist_exit = int((R / "xdist_exit_code.txt").read_text())
serial_exit = int((R / "serial_exit_code.txt").read_text())
bad, rows = aggregate(full=full, serial_part=serial_part, xdist_part=xdist_part,
                      xdist_cases=read_junit(R / "xdist_junit.xml"), xdist_exit=xdist_exit,
                      serial_cases=read_junit(R / "serial_junit.xml"), serial_exit=serial_exit,
                      declared_skips=declared, reference=reference)
with (R / "aggregated_outcomes.tsv").open("w") as fh:
    fh.write("canonical_id\tpartition\traw_collected_id\traw_executed_junit\toutcome\tserial_reference\n")
    for r in rows:
        fh.write(f"{r['canonical']}\t{r['partition']}\t{r['raw_collected']}\t{'|'.join(r['raw_executed'])}"
                 f"\t{r['outcome']}\t{r['reference']}\n")
counts: dict[str, dict[str, int]] = {}
for r in rows:
    counts.setdefault(r["partition"], {}).setdefault(r["outcome"], 0)
    counts[r["partition"]][r["outcome"]] += 1
print(f"aggregated nodes={len(rows)} per partition={counts} xdist_exit={xdist_exit} serial_exit={serial_exit}")
print("AGGREGATION_AND_EQUIVALENCE::" + ("PASS" if not bad else f"FAIL {bad}"))

checks: dict[str, bool] = {"AGGREGATION_AND_EQUIVALENCE": not bad}
pre_tree = dict(l.split("=", 1) for l in lines(R / "pre_tree.txt"))
post_tree = dict(l.split("=", 1) for l in lines(R / "post_tree.txt"))
pre_db, post_db = (json.loads((R / f"{k}_proof_dbs.json").read_text()) for k in ("pre", "post"))
checks["TREE_UNCHANGED"] = pre_tree == post_tree and post_tree["status_entries_incl_ignored"] == "0" \
    and post_tree["diff_vs_tag"] == "none"
checks["ENV_MANIFEST_UNCHANGED"] = (R / "pre_env_manifest.json").read_text() == (R / "post_env_manifest.json").read_text()
checks["IMPORT_ORIGIN_GUARD_VALID"] = all("PASS" in (R / f"{k}_guard.txt").read_text() for k in ("pre", "post"))
checks["MIGRATION_HEADS_AND_FINGERPRINT_UNCHANGED"] = [(r["db"], r["head"], r["fingerprint"]) for r in pre_db] == \
    [(r["db"], r["head"], r["fingerprint"]) for r in post_db]
checks["PROOF_DBS_CLEAN_AND_UNCONNECTED_AFTER"] = all(r["clean"] and r["no_foreign_connections"] for r in post_db)
checks["NO_RESIDUAL_RACE_DB"] = (R / "pre_race_dbs.txt").read_text() == (R / "post_race_dbs.txt").read_text() == ""
checks["NO_RESIDUAL_ZZ_PKG25_ROLE"] = (R / "pre_zz_roles.txt").read_text() == (R / "post_zz_roles.txt").read_text() == ""
observed = (R / "observed_cluster_objects.log").read_text()
created = sorted(set(re.findall(r"db:race_[0-9a-f]+|role:zz_pkg25_[a-z0-9_]+", observed)))
checks["OBSERVED_OBJECTS_ATTRIBUTABLE"] = all(o.startswith(("db:race_", "role:zz_pkg25_mut01_no_grants_role")) for o in created)
for name, ok in checks.items():
    print(f"{name}::{'PASS' if ok else 'FAIL'}")
print(f"observed proof-created objects: {len(created)} "
      f"(race dbs {sum(o.startswith('db:') for o in created)}, roles {sum(o.startswith('role:') for o in created)})")

x = num("xdist_t1") - num("xdist_t0")
s = num("serial_t1") - num("serial_t0")
base_log = (REF / "run.log").read_text()
m = re.search(r"in ([0-9.]+)s \(", base_log)
baseline = float(m.group(1)) if m else float("nan")
print(f"DURATION xdist_partition={x:.1f}s serial_partition={s:.1f}s governed_total={x + s:.1f}s "
      f"accepted_serial_baseline={baseline:.1f}s speedup={baseline / (x + s):.2f}x")
ok = all(checks.values())
print(("RESULT: " + CLAIM) if ok else "RESULT: NOT PROVEN")
print("PARALLEL_PROOF::" + ("PASS" if ok else "FAIL"))
(R / "result.json").write_text(json.dumps({"checks": checks, "violations": bad, "counts": counts,
    "durations_s": {"xdist": x, "serial": s, "total": x + s, "serial_baseline": baseline},
    "observed_created": created, "claim": CLAIM if ok else None}, indent=1))
sys.exit(0 if ok else 1)
