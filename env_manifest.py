"""Deterministic environment manifest (no timestamps): distributions + RECORD hashes,
interpreter identity, the .pth binding, and a content hash of every file in site-packages
(excluding __pycache__). Usage: python env_manifest.py OUT.json"""

from __future__ import annotations

import hashlib
import importlib.metadata as m
import json
import pathlib
import sys
import sysconfig

purelib = pathlib.Path(sysconfig.get_paths()["purelib"])
files = sorted(
    p for p in purelib.rglob("*") if p.is_file() and "__pycache__" not in p.parts
)
tree = hashlib.sha256()
for p in files:
    tree.update(str(p.relative_to(purelib)).encode() + b"\0" + hashlib.sha256(p.read_bytes()).digest())
doc = {
    "python": sys.version,
    "executable": sys.executable,
    "prefix": sys.prefix,
    "base_prefix": sys.base_prefix,
    "site_packages_files": len(files),
    "site_packages_content_sha256": tree.hexdigest(),
    "pth_binding": (purelib / "nquiry_orange_tree.pth").read_text().split(),
    "distributions": sorted(
        (
            {
                "name": d.metadata["Name"],
                "version": d.version,
                "record_sha256": hashlib.sha256((d.read_text("RECORD") or "").encode()).hexdigest(),
            }
            for d in m.distributions()
        ),
        key=lambda r: r["name"].lower(),
    ),
}
out = pathlib.Path(sys.argv[1])
out.write_text(json.dumps(doc, indent=1, sort_keys=True))
print(f"ENV_MANIFEST {out.name}: {len(doc['distributions'])} dists, "
      f"{doc['site_packages_files']} files, content {doc['site_packages_content_sha256'][:16]}, "
      f"manifest sha256 {hashlib.sha256(out.read_bytes()).hexdigest()[:16]}")
