"""P-18 (14 §50): "app/worker direct write -> technical reject or
illegitimate tamper detection".

NOT_APPLICABLE at PKG-00. No canonical writer, DB principal
separation, or persistence adapter exists yet (those are PKG-13/PKG-25
per 14 §46) — there is no "direct write" to attempt or reject.
Fabricating a fake writer here to produce a green test would be
exactly the "fake audit/commit" forbidden shortcut this package's
COPY-PASTE prompt (FORBIDDEN_SHORTCUTS) prohibits.

This test is intentionally skipped, not deleted, so P-18 stays visibly
tracked as BLOCKED_UPSTREAM rather than silently disappearing from the
suite (14 §46 PKG-00 manifest: "PROOF_CLAIMS: P-18,P-23,P-24" — tracked
here as introduced-but-not-yet-exercisable, per 15 §3 PROOF_CLAIMS
guidance: "Track each as introduced, exercised, potentially affected,
or regression required").
"""

import pytest


@pytest.mark.skip(
    reason=(
        "P-18 NOT_APPLICABLE at PKG-00: no canonical writer or DB principal "
        "separation exists yet (lands PKG-13/PKG-25). Exercise once "
        "packages/commit and packages/security/workspace.py exist."
    )
)
def test_direct_write_is_technically_rejected() -> None:
    raise AssertionError("unreachable: see skip reason")
