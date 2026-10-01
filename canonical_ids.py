"""Proof-lane canonicalization of VOLATILE node identity, for evidence comparison only.

Human Authority "TEST IDENTITY EQUIVALENCE" (2026-10-01). This module never runs inside a
pytest process and is never imported by the frozen tree: it only rewrites node-id STRINGS read
from evidence files (collect-only output, junit.xml). Test execution and test input values are
untouched; raw ids are always kept next to their canonical form.

The only proven volatile component in the frozen PCPG-5 collection is the uuid4-derived email of
tests/security/test_dev_identity_provisioning.py:
    def _email() -> str:
        return f"dev-{uuid.uuid4().hex[:10]}@dev.local.test"
used in the parametrize list of `test_malformed_input_is_refused`. Canonicalization therefore:
- applies ONLY to node ids of that exact file and function (SCOPE), and
- replaces ONLY an exact `dev-<10 lowercase hex>@dev.local.test` span (VOLATILE) with a fixed token.
Anything else (other files/functions, other hex lengths, uppercase, other domains) is unchanged.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

SCOPE_PREFIX = "tests/security/test_dev_identity_provisioning.py::test_malformed_input_is_refused["
JUNIT_SCOPE = ("tests.security.test_dev_identity_provisioning", "test_malformed_input_is_refused[")
VOLATILE = re.compile(r"(?<![0-9a-zA-Z])dev-[0-9a-f]{10}@dev\.local\.test(?![0-9a-zA-Z.])")
TOKEN = "dev-<uuid4hex10>@dev.local.test"


def canonical_nodeid(nodeid: str) -> str:
    if not nodeid.startswith(SCOPE_PREFIX):
        return nodeid
    return VOLATILE.sub(TOKEN, nodeid)


def canonical_junit(classname: str, name: str) -> tuple[str, str]:
    if classname != JUNIT_SCOPE[0] or not name.startswith(JUNIT_SCOPE[1]):
        return classname, name
    return classname, VOLATILE.sub(TOKEN, name)


def canonical_map(raw_ids: Iterable[str]) -> dict[str, str]:
    """raw -> canonical; raises if canonicalization is not injective over the given set."""
    raw = list(raw_ids)
    if len(set(raw)) != len(raw):
        raise ValueError("raw collection contains duplicate node ids")
    mapping = {r: canonical_nodeid(r) for r in raw}
    inverse: dict[str, str] = {}
    for r, c in mapping.items():
        if c in inverse:
            raise ValueError(f"NOT INJECTIVE: {inverse[c]!r} and {r!r} -> {c!r}")
        inverse[c] = r
    return mapping


__all__ = ["TOKEN", "VOLATILE", "canonical_junit", "canonical_map", "canonical_nodeid"]
