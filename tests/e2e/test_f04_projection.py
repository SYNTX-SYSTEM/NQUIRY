"""F04 WU-04.7: `position.analysis` audience and honest states (HD-22).

MUST BECOME TRUE: the derived field is served exactly when the full frozen set
is served (HD-13 audience), identically to every member; its states are honest
(NOT_BEGUN, PENDING, UNAVAILABLE, ACCEPTED; clustering NOT_RUN without an
accepted analysis).

MUST REMAIN IMPOSSIBLE: any derived field (or its absence being mistaken for a
result) while the Burst is ACTIVE; a different view per viewer.

FALSIFIERS: G1, G5 (states), plus the audience boundary during the Burst.
"""

from __future__ import annotations

import f03_support as f03
import f04_support as f04
import sqlalchemy as sa
from ai_contracts.aiop import AIOperationId
from ai_gateway.adapters.providers.mock import MockProviderOutcome
from application.analysis_runtime import UNAVAILABLE


def test_no_derived_field_while_the_burst_is_active(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    for user in (ctx["fac"], ctx["participants"][0], ctx["outsider"]):
        assert f03.position(db_connection, ctx, user)["analysis"] == {"visible": False}


def test_states_are_honest_and_identical_for_the_audience(db_connection: sa.Connection) -> None:
    ctx = f04.capture_context(db_connection)
    view = f03.position(db_connection, ctx, ctx["participants"][0])["analysis"]
    assert view["visible"] is True and view["analysis"]["status"] == "NOT_BEGUN"
    assert view["clustering"]["status"] == "NOT_BEGUN"

    result = f04.begin(db_connection, ctx)
    ctx["oa1"] = result.authorization_id
    f04.run(db_connection, ctx, ctx["oa1"], runtime=UNAVAILABLE)
    assert (
        f03.position(db_connection, ctx, ctx["fac"])["analysis"]["analysis"]["status"] == "PENDING"
    )

    f04.run(
        db_connection,
        ctx,
        ctx["oa1"],
        scripted={AIOperationId.AIOP_001: MockProviderOutcome.TIMEOUT},
    )
    views = [
        f03.position(db_connection, ctx, u)["analysis"]
        for u in (ctx["fac"], ctx["participants"][0], ctx["owner"], ctx["outsider"])
    ]
    assert all(v == views[0] for v in views)
    assert views[0]["analysis"]["status"] == "UNAVAILABLE"
    assert views[0]["analysis"]["reasonCode"] == "PROVIDER_TIMEOUT"
    assert views[0]["clustering"]["status"] == "NOT_RUN"
    assert views[0]["clustering"]["reasonCode"] == "NO_ACCEPTED_ANALYSIS"
