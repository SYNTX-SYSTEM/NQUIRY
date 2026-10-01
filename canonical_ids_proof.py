"""Proof + falsifiers for canonical_ids (evidence-comparison-only canonicalization).
Reads only evidence files; runs no test. Exit 0 only if every check holds."""

from __future__ import annotations

import ast
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from canonical_ids import (  # noqa: E402
    SCOPE_PREFIX, TOKEN, VOLATILE, canonical_junit, canonical_map, canonical_nodeid,
)

P = pathlib.Path(__file__).resolve().parent
O = pathlib.Path("/home/codi/Entwicklung/nquiry/worktrees/orange-proof-infra")
EV = P / "evidence"
results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"{name}::{'PASS' if ok else 'FAIL'} {detail}")


def junit_id(nodeid: str) -> tuple[str, str]:
    base, bracket, params = nodeid.partition("[")
    parts = base.split("::")
    return ".".join([parts[0][:-3].replace("/", "."), *parts[1:-1]]), parts[-1] + bracket + params


# two INDEPENDENT collections (separate processes) of the final closure (committed evidence)
runs = {
    "closure_collection_A": [l for l in (EV / "final_closure/serial_ref/collected_nodeids.txt").read_text().splitlines() if l],
    "closure_collection_B": [l for l in (EV / "final_closure/parallel/partition/full_nodeids.txt").read_text().splitlines() if l],
}

# 1. evidence-only: nothing in the frozen tree or in any pytest-loaded proof code imports it
tree_refs = [str(p) for p in O.rglob("*.py") if "canonical_ids" in p.read_text(errors="ignore")]
guard_src = (P / "guard/src/nquiry_orange_guard.py").read_text()
guard_imports: set[str] = set()
for n in ast.walk(ast.parse(guard_src)):
    if isinstance(n, ast.Import):
        guard_imports |= {a.name for a in n.names}
    elif isinstance(n, ast.ImportFrom):
        guard_imports.add(n.module or "")
check("EVIDENCE_ONLY_NOT_IN_TREE", not tree_refs, f"refs={tree_refs}")
check("EVIDENCE_ONLY_NOT_IN_PYTEST_PLUGIN", "canonical_ids" not in guard_src and
      not any("canonical" in (m or "") for m in guard_imports))

# 2. the volatile component is exactly what is proven volatile, and only there
for run, ids in runs.items():
    check(f"RAW_COUNT_2239[{run}]", len(ids) == 2239 and len(set(ids)) == 2239, str(len(ids)))
    anywhere = [i for i in ids if VOLATILE.search(i)]
    check(f"VOLATILE_ONLY_IN_SCOPE[{run}]",
          len(anywhere) == 2 and all(i.startswith(SCOPE_PREFIX) for i in anywhere), str(len(anywhere)))
a, b = set(runs["closure_collection_A"]), set(runs["closure_collection_B"])
changed = sorted(a ^ b)
check("RAW_VOLATILITY_IS_EXACTLY_THE_UUID_SPAN",
      len(changed) == 4 and all(VOLATILE.search(i) and i.startswith(SCOPE_PREFIX) for i in changed),
      f"{len(changed)} raw ids differ between the two collections")
src = (O / "tests/security/test_dev_identity_provisioning.py").read_text()
check("SOURCE_OF_VOLATILITY_IS_UUID4_HEX10",
      'return f"dev-{uuid.uuid4().hex[:10]}@dev.local.test"' in src)

# 3. deterministic + injective + canonical sets equal across runs
maps = {}
for run, ids in runs.items():
    try:
        maps[run] = canonical_map(ids)
        check(f"INJECTIVE_OVER_2239[{run}]", len(set(maps[run].values())) == 2239)
    except ValueError as exc:
        check(f"INJECTIVE_OVER_2239[{run}]", False, str(exc))
check("DETERMINISTIC", all(canonical_nodeid(canonical_nodeid(i)) == canonical_nodeid(i) ==
                           canonical_nodeid(i) for i in runs["closure_collection_A"]))
check("CANONICAL_SETS_EQUAL_ACROSS_COLLECTIONS",
      set(maps["closure_collection_A"].values()) == set(maps["closure_collection_B"].values()))
check("ONLY_2_IDS_CHANGED_BY_CANONICALIZATION",
      sum(r != c for r, c in maps["closure_collection_A"].items()) == 2)
check("JUNIT_FORM_CONSISTENT", all(canonical_junit(*junit_id(i)) == junit_id(canonical_nodeid(i))
                                   for i in runs["closure_collection_A"]))

# 4. falsifiers: semantically different ids can never collapse
base = SCOPE_PREFIX + "dev-0123456789@dev.local.test-{}]"
pairs = {
    "distinct_params_same_function": (base.format("A-short"), base.format(" -dev-password-123")),
    "distinct_password_only": (base.format("A-short"), base.format("A-shorter")),
    "hex_len_11_not_volatile": (SCOPE_PREFIX + "dev-0123456789a@dev.local.test-A-short]",
                                SCOPE_PREFIX + "dev-0123456789b@dev.local.test-A-short]"),
    "uppercase_hex_not_volatile": (SCOPE_PREFIX + "dev-ABCDEF0123@dev.local.test-A-short]",
                                   SCOPE_PREFIX + "dev-ABCDEF0124@dev.local.test-A-short]"),
    "other_domain_not_volatile": (SCOPE_PREFIX + "dev-0123456789@dev.local.testx-A-short]",
                                  SCOPE_PREFIX + "dev-0123456789@dev.other.test-A-short]"),
    "out_of_scope_file": ("tests/e2e/test_x.py::test_y[dev-0123456789@dev.local.test]",
                          "tests/e2e/test_x.py::test_y[dev-9876543210@dev.local.test]"),
    "out_of_scope_function": (
        "tests/security/test_dev_identity_provisioning.py::test_other[dev-0123456789@dev.local.test]",
        "tests/security/test_dev_identity_provisioning.py::test_other[dev-9876543210@dev.local.test]"),
    "real_two_params": tuple(sorted(i for i in runs["closure_collection_A"] if VOLATILE.search(i))),
}
for name, (x, y) in pairs.items():
    check(f"NO_COLLAPSE[{name}]", x != y and canonical_nodeid(x) != canonical_nodeid(y))
same_node = (base.format("A-short"), base.format("A-short").replace("0123456789", "fedcba9876"))
check("VOLATILE_SPAN_REMOVED[same semantic node]",
      canonical_nodeid(same_node[0]) == canonical_nodeid(same_node[1]) and TOKEN in canonical_nodeid(same_node[0]))

# 5. the injectivity guard has teeth: a sloppy canonicalizer is detected on the real collection
sloppy = {}
collapsed = None
for i in runs["closure_collection_A"]:
    c = re.sub(r"\[.*\]$", "[*]", i)
    if c in sloppy:
        collapsed = (sloppy[c], i)
        break
    sloppy[c] = i
check("INJECTIVITY_GUARD_DETECTS_SLOPPY_MUTANT", collapsed is not None, f"e.g. {collapsed}")

ok = all(r[1] for r in results)
print(f"CANONICAL_IDENTITY_PROOF::{'PASS' if ok else 'FAIL'} ({sum(r[1] for r in results)}/{len(results)})")
sys.exit(0 if ok else 1)
