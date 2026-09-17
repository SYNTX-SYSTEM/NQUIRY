"""P-24 (14 §50): "admin/root decides -> no legitimate transition".

NOT_APPLICABLE at PKG-00. No AuthorityResolver, Decision, or admin
concept exists yet (lands PKG-03/PKG-15 per 14 §46). There is no
authority path to attempt to bypass.

Skipped, not deleted, so P-24 stays visibly tracked rather than
silently vanishing from the suite — see `test_direct_write.py` for the
identical rationale applied to P-18.
"""

import pytest


@pytest.mark.skip(
    reason=(
        "P-24 NOT_APPLICABLE at PKG-00: no AuthorityResolver or Decision "
        "concept exists yet (lands PKG-03/PKG-15). Exercise once "
        "packages/authority and packages/governance are implemented."
    )
)
def test_admin_cannot_create_a_legitimate_decision() -> None:
    raise AssertionError("unreachable: see skip reason")
