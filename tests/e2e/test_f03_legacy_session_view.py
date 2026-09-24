"""F03 FBR-F03-8 (found by the Inverse DeepSweep): the PKG-28 GetSession read
(`application.session_view_query`, served at `GET /workspaces/{w}/sessions/{s}`
and rendered by the decision surface) returned EVERY captured Question with its
`original_text` to any Workspace member while the Burst was still ACTIVE. That
is a parallel read path around HD-13 (own-questions-only during the Burst).

MUST BECOME TRUE: while the Burst is not COMPLETED the legacy view carries no
Question of the Burst; after completion it carries the frozen set (visible to
every member, HD-13).
MUST REMAIN IMPOSSIBLE: any member reading another participant's Question text
through this route while the Burst is ACTIVE.
"""

from __future__ import annotations

import f02_support as f02
import f03_support as f03
import sqlalchemy as sa
from application.session_view_query import SessionViewData, get_session_view
from semantic_types.ids import CorrelationId


def _view(db: sa.Connection, ctx: dict, user):  # type: ignore[no-untyped-def,type-arg]
    import uuid

    p = f02.ports(db)
    return get_session_view(
        actor=f02.human(user),
        workspace_id=ctx["ws"],
        session_id=ctx["session"],
        correlation_id=CorrelationId(uuid.uuid4()),
        session_repository=p.sessions,
        challenge_repository=p.challenges,
        burst_repository=p.bursts,
        question_repository=p.questions,
        decision_repository=p.decisions,
        workspace_repository=p.workspaces,
        membership_repository=p.memberships,
    )


def test_legacy_view_does_not_leak_questions_while_the_burst_is_active(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=2)
    a, b = ctx["participants"]
    f03.capture(db_connection, ctx, a, "Alice's private question?")
    for viewer in (b, ctx["outsider"], ctx["owner"], ctx["fac"], a):
        view = _view(db_connection, ctx, viewer)
        assert isinstance(view, SessionViewData)
        assert view.burst_questions == ()


def test_legacy_view_serves_the_frozen_set_after_completion(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=2)
    a, b = ctx["participants"]
    f03.capture(db_connection, ctx, a, "Alice's question?")
    f03.capture(db_connection, ctx, b, "Bob's question?")
    f03.complete(db_connection, ctx, ctx["fac"])
    view = _view(db_connection, ctx, ctx["outsider"])
    assert isinstance(view, SessionViewData)
    assert [q.original_text for q in view.burst_questions] == [
        "Alice's question?",
        "Bob's question?",
    ]
