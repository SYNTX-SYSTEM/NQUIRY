"""Secret / evidence boundary gate (TF-PX-09). Provider-neutral and name-neutral.

Fails if the value of ANY variable of this process's environment occurs in a file that would be versioned
(or in any file under an explicit directory). It knows no provider and no variable name: a credential is whatever
the environment holds. Values are compared in memory only; the report names the variable and the file, never
the value. It reads no .env file and no application configuration.

usage: python evidence_secret_gate.py [DIR | --rev REV [REPO]]
  no argument    : every file git would version in this worktree (tracked + untracked, not ignored)
  DIR            : every file under DIR
  --rev REV REPO : every blob reachable from REV (the whole history that publishing REV would publish);
                   REPO defaults to this worktree
exit: 0 = no environment value found; 1 = at least one found; 2 = usage.
Not candidates (cannot be credentials, would only produce noise): values shorter than 12 characters, values that
are filesystem paths (start with "/"), and PATH / PWD / OLDPWD / HOME.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys

SKIP_NAMES = {"PATH", "PWD", "OLDPWD", "HOME"}


def candidates() -> dict[str, bytes]:
    return {k: v.encode() for k, v in os.environ.items()
            if k not in SKIP_NAMES and len(v) >= 12 and not v.startswith("/")}


def files(argv: list[str]) -> tuple[pathlib.Path, list[pathlib.Path]]:
    if len(argv) > 2:
        print(__doc__.strip().splitlines()[-6]); sys.exit(2)
    if len(argv) == 2:
        root = pathlib.Path(argv[1])
        if not root.is_dir():
            print(f"usage: not a directory: {root}"); sys.exit(2)
        return root, sorted(p for p in root.rglob("*") if p.is_file())
    root = pathlib.Path(__file__).resolve().parent
    out = subprocess.run(["git", "-C", str(root), "ls-files", "-co", "--exclude-standard", "-z"],
                         capture_output=True, check=True).stdout
    return root, [root / n.decode() for n in out.split(b"\0") if n]


def history(rev: str, repo: str) -> int:
    """Every blob reachable from REV: a value removed by a later commit is still published with the history."""
    cands = candidates()
    listing = subprocess.run(["git", "-C", repo, "rev-list", "--objects", rev], capture_output=True, check=True).stdout
    objs = [l.split(b" ", 1) for l in listing.splitlines()]
    batch = subprocess.run(["git", "-C", repo, "cat-file", "--batch"], input=b"\n".join(o[0] for o in objs) + b"\n",
                           capture_output=True, check=True).stdout
    hits: list[tuple[str, str]] = []
    pos = 0
    for o in objs:
        end = batch.index(b"\n", pos)
        _, kind, size = batch[pos:end].split()
        data = batch[end + 1:end + 1 + int(size)]
        pos = end + 2 + int(size)
        if kind == b"blob":
            label = f"{o[0].decode()[:12]} ({o[1].decode() if len(o) > 1 else '?'})"
            hits.extend((name, label) for name, value in cands.items() if value in data)
    for name, label in hits:
        print(f"  environment value of {name} found in reachable blob {label}")
    verdict = "PASS" if not hits else f"FAIL ({len(hits)})"
    print(f"EVIDENCE_SECRET_GATE[history of {rev[:12]}]::{verdict} ({len(objs)} reachable objects, "
          f"{len(cands)} candidate environment variables)")
    return 1 if hits else 0


def main(argv: list[str]) -> int:
    if len(argv) in (3, 4) and argv[1] == "--rev":
        return history(argv[2], argv[3] if len(argv) == 4 else str(pathlib.Path(__file__).resolve().parent))
    root, paths = files(argv)
    cands = candidates()
    hits: list[tuple[str, str]] = []
    for p in paths:
        try:
            data = p.read_bytes()
        except OSError:
            continue
        hits.extend((name, str(p.relative_to(root))) for name, value in cands.items() if value in data)
    for name, path in hits:
        print(f"  environment value of {name} found in {path}")
    verdict = "PASS" if not hits else f"FAIL ({len(hits)})"
    print(f"EVIDENCE_SECRET_GATE::{verdict} ({len(paths)} files, {len(cands)} candidate environment variables)")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
