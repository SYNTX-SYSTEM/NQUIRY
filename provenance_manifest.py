"""Dependency provenance manifest: every installed distribution classified as DECLARED
(by the frozen tree's pyproject), TRANSITIVE (required by a declared/transitive dist, markers
and extras evaluated) or PROOF_ONLY (with its reason), plus EQUIVALENCE_PINNED versions.
Usage: python provenance_manifest.py OUT.json"""

from __future__ import annotations

import hashlib
import importlib.metadata as m
import json
import pathlib
import sys
import sysconfig
import tomllib

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name as c

O = pathlib.Path("/home/codi/Entwicklung/nquiry/worktrees/orange-proof-infra")
P = pathlib.Path(__file__).resolve().parent
proj = tomllib.load((O / "pyproject.toml").open("rb"))["project"]
dev = [Requirement(r) for r in proj["optional-dependencies"]["dev"]]
roots = [(Requirement(r), "runtime") for r in proj["dependencies"]] + [(r, "dev") for r in dev]
dists = {c(d.metadata["Name"]): d for d in m.distributions()}
pins = {
    c(Requirement(l).name): l.strip()
    for l in (P / "equivalence-pins.txt").read_text().splitlines()
    if l.strip() and not l.startswith("#")
}
why: dict[str, set[str]] = {}


def walk(req: Requirement, parent: str) -> None:
    n = c(req.name)
    if n not in dists:
        return
    new = n not in why
    why.setdefault(n, set()).add(parent)
    if not new:
        return
    for s in dists[n].requires or []:
        r = Requirement(s)
        if r.marker is None or any(r.marker.evaluate({"extra": e}) for e in ["", *sorted(req.extras)]):
            walk(r, n)


for r, kind in roots:
    walk(r, f"pyproject.toml ({kind})")

PROOF_ONLY = {
    "pytest-xdist": "PX field: parallel workers; not declared by the frozen tree",
    "execnet": "required by pytest-xdist",
    "httpx": "the only HTTP-client family the frozen tree names (5 runtime-proof scripts import it); "
    "TestClient dependency; 0.28.1 = historical proven version",
    "httpcore": "required by httpx",
    "certifi": "required by httpx",
    "nquiry-orange-guard": "PX-1 proof-owned import-origin guard (pytest11 plugin)",
}
rows = []
for n, d in sorted(dists.items()):
    if n in why:
        cls = "DECLARED" if any(p.startswith("pyproject") for p in why[n]) else "TRANSITIVE"
        reason = "required by " + ", ".join(sorted(why[n]))
    else:
        cls, reason = "PROOF_ONLY", PROOF_ONLY.get(n, "UNEXPLAINED")
    if n in pins:
        reason += f" | EQUIVALENCE_PINNED {pins[n]} (historical proven state; equivalence-pins.txt)"
    rows.append({
        "name": d.metadata["Name"], "version": d.version, "class": cls, "reason": reason,
        "record_sha256": hashlib.sha256((d.read_text("RECORD") or "").encode()).hexdigest(),
    })
doc = {"python": sys.version, "prefix": sys.prefix, "purelib": sysconfig.get_paths()["purelib"],
       "frozen_target": "checkpoint-PFC-PCPG-5 e0a6b3b25d4309d16d6e3db3ee0958183a279dfd",
       "equivalence_pins": sorted(pins.values()), "distributions": rows}
out = pathlib.Path(sys.argv[1])
out.write_text(json.dumps(doc, indent=1))
counts: dict[str, int] = {}
for r in rows:
    counts[r["class"]] = counts.get(r["class"], 0) + 1
unexplained = [r["name"] for r in rows if r["reason"].startswith("UNEXPLAINED")]
bad_pins = [p for n, p in pins.items() if n not in dists or not Requirement(p).specifier.contains(dists[n].version)]
print(f"{len(rows)} dists {counts}; unexplained={unexplained}; pins={sorted(pins.values())} "
      f"pins_satisfied={not bad_pins}")
sys.exit(1 if unexplained or bad_pins else 0)
