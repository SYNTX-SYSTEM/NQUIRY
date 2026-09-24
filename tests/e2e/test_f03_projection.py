"""F03 WU-03.8: the F03 read side (HD-13 / NQ-DEC-041) and capability
projections, against real PostgreSQL.

MUST BECOME TRUE: while the Burst is ACTIVE a participant is served ONLY their
own Questions (exactly as typed, marked HUMAN), and the controller only a
count. After completion EVERY Session member is served the same full frozen
human set with author names, capture order, human origin, the verified
fingerprint and the completion provenance. Capability projections come from the
server and share their preconditions with the Commands.

MUST REMAIN IMPOSSIBLE: another participant's Question text reaching a
participant, the controller, the Owner or an outsider during the ACTIVE Burst
(the payload is filtered on the server, not hidden by the client); a capture
affordance for a non-participant, the controller-only, the Owner, or outside
ACTIVE; a completion affordance for a non-controller; a timer field that could
be read as a deadline (HD-11).
"""

from __future__ import annotations

import json

import f02_support as f02
import f03_support as f03
import pytest
import sqlalchemy as sa
from application import inquiry_queries as queries
from application.session_control_handler import admit_participant


def _ctx_with_questions(db: sa.Connection):  # type: ignore[no-untyped-def]
    ctx = f03.generating_context(db, participants=2)
    a, b = ctx["participants"]
    f03.capture(db, ctx, a, "Alice asks why?")
    f03.capture(db, ctx, b, "Bob asks how — 如何?")
    f03.capture(db, ctx, a, "Alice asks again?")
    return ctx, a, b


def test_participant_sees_only_their_own_questions_while_active(
    db_connection: sa.Connection,
) -> None:
    ctx, a, b = _ctx_with_questions(db_connection)
    pos = f03.position(db_connection, ctx, a)
    mine = pos["questionSet"]["mine"]
    assert [q["originalText"] for q in mine] == ["Alice asks why?", "Alice asks again?"]
    assert all(q["origin"] == "HUMAN" and q["authorUserId"] == str(a.value) for q in mine)
    assert [q["capturedOrder"] for q in mine] == [0, 2]
    assert pos["questionSet"]["visibility"] == "OWN_ONLY_WHILE_ACTIVE"
    assert pos["questionSet"]["frozen"] is None
    # server-side filtering: Bob's text is nowhere in Alice's payload
    assert "Bob asks" not in json.dumps(pos, ensure_ascii=False)
    assert "如何" not in json.dumps(pos, ensure_ascii=False)


def test_the_controller_sees_only_a_count_while_active(db_connection: sa.Connection) -> None:
    ctx, a, b = _ctx_with_questions(db_connection)
    pos = f03.position(db_connection, ctx, ctx["fac"])
    assert pos["questionSet"]["capturedCount"] == 3
    assert pos["questionSet"]["mine"] == []
    payload = json.dumps(pos, ensure_ascii=False)
    for text in ("Alice asks why?", "Bob asks", "Alice asks again?"):
        assert text not in payload


def test_controller_who_participates_sees_own_questions_and_the_count(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=1, controller_participates=True)
    f03.capture(db_connection, ctx, ctx["fac"], "Controller asks?")
    f03.capture(db_connection, ctx, ctx["participants"][0], "Other asks?")
    pos = f03.position(db_connection, ctx, ctx["fac"])
    assert [q["originalText"] for q in pos["questionSet"]["mine"]] == ["Controller asks?"]
    assert pos["questionSet"]["capturedCount"] == 2
    assert "Other asks?" not in json.dumps(pos)


@pytest.mark.parametrize("who", ["owner", "outsider"])
def test_others_see_neither_questions_nor_count_while_active(
    db_connection: sa.Connection, who: str
) -> None:
    ctx, a, b = _ctx_with_questions(db_connection)
    user = ctx[who]
    pos = f03.position(db_connection, ctx, user)
    assert pos["questionSet"]["mine"] == []
    assert pos["questionSet"]["capturedCount"] is None
    payload = json.dumps(pos, ensure_ascii=False)
    assert "asks" not in payload


def test_every_member_sees_the_same_full_frozen_set_after_completion(
    db_connection: sa.Connection,
) -> None:
    ctx, a, b = _ctx_with_questions(db_connection)
    result = f03.complete(db_connection, ctx, ctx["fac"])
    views = {
        name: f03.position(db_connection, ctx, user)
        for name, user in {
            "a": a,
            "b": b,
            "controller": ctx["fac"],
            "owner": ctx["owner"],
            "outsider": ctx["outsider"],
        }.items()
    }
    reference = views["a"]["questionSet"]["frozen"]
    assert reference is not None
    assert reference["fingerprint"] == result.fingerprint and reference["verified"] is True
    assert reference["memberCount"] == 3
    assert [q["originalText"] for q in reference["questions"]] == [
        "Alice asks why?",
        "Bob asks how — 如何?",
        "Alice asks again?",
    ]
    assert [q["authorUserId"] for q in reference["questions"]] == [
        str(a.value),
        str(b.value),
        str(a.value),
    ]
    assert all(
        q["origin"] == "HUMAN" and q["captureOrigin"] == "HUMAN" for q in reference["questions"]
    )
    assert [q["capturedOrder"] for q in reference["questions"]] == [0, 1, 2]
    assert all(q["authorName"] for q in reference["questions"])
    for name, view in views.items():
        assert view["questionSet"]["frozen"] == reference, name
        assert view["questionSet"]["visibility"] == "FULL_FROZEN_SET"
        assert view["questionSet"]["mine"] == []  # nothing is served twice
    established = views["outsider"]["establishedBy"]
    assert established["commandType"] == "CMD_COMPLETE_BURST"
    assert established["authoritySourceType"] == "BINDING"
    assert established["authorityScopeRef"] == f"SESSION:{ctx['session'].value}"
    assert views["a"]["session"]["state"] == "QUESTION_CAPTURE"
    assert views["a"]["burst"]["state"] == "COMPLETED"


def test_capture_capability_for_each_viewer(db_connection: sa.Connection) -> None:
    ctx, a, b = _ctx_with_questions(db_connection)
    cap = lambda user: f03.position(db_connection, ctx, user)["actions"]["CAPTURE_QUESTION"]  # noqa: E731
    assert cap(a)["available"] is True and cap(b)["available"] is True
    for user in (ctx["outsider"], ctx["owner"], ctx["fac"]):
        c = cap(user)
        assert c["available"] is False and c["reasonCode"] == "NOT_A_PARTICIPANT"
        assert "Workspace role" in c["reason"] or "participant" in c["reason"]
    f03.complete(db_connection, ctx, ctx["fac"])
    c = cap(a)
    assert c["available"] is False and c["reasonCode"].startswith("SESSION_NOT_QUESTION_GENERATION")


def test_capture_capability_before_the_burst_is_active(db_connection: sa.Connection) -> None:
    ctx = f03.prepared_context(db_connection)
    a = f03.add_workspace_member(db_connection, ctx, "early")
    f03._step(db_connection, admit_participant, ctx, ctx["fac"], participant_user_id=a)
    c = f03.position(db_connection, ctx, a)["actions"]["CAPTURE_QUESTION"]
    assert c["available"] is False
    assert c["reasonCode"].startswith("SESSION_NOT_QUESTION_GENERATION")
    assert c["relevant"] is False


def test_complete_capability_only_for_the_controller_with_questions(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=2)
    a = ctx["participants"][0]
    complete = lambda user: f03.position(db_connection, ctx, user)["actions"]["COMPLETE_BURST"]  # noqa: E731
    empty = complete(ctx["fac"])
    assert empty["available"] is False and empty["reasonCode"] == "NO_CAPTURED_QUESTIONS"
    assert complete(a)["reasonCode"] == "NO_SESSION_CONTROL"
    assert complete(ctx["owner"])["reasonCode"] == "NO_SESSION_CONTROL"
    f03.capture(db_connection, ctx, a, "Something?")
    ready = complete(ctx["fac"])
    assert ready["available"] is True and ready["relevant"] is True
    assert complete(a)["available"] is False
    f03.complete(db_connection, ctx, ctx["fac"])
    done = complete(ctx["fac"])
    assert done["available"] is False and done["relevant"] is False


def test_a_command_agrees_with_the_projection(db_connection: sa.Connection) -> None:
    """One definition of the preconditions: what the projection says is
    unavailable, the Command refuses with the same reason code."""
    from application.session_control_handler import SessionPreconditionUnmet

    ctx = f03.generating_context(db_connection, participants=2)
    projected = f03.position(db_connection, ctx, ctx["fac"])["actions"]["COMPLETE_BURST"]
    with pytest.raises(SessionPreconditionUnmet) as exc:
        f03.complete(db_connection, ctx, ctx["fac"])
    assert exc.value.reason_code == projected["reasonCode"]


def test_timer_is_presentation_only(db_connection: sa.Connection) -> None:
    ctx, a, b = _ctx_with_questions(db_connection)
    pos = f03.position(db_connection, ctx, a)
    burst = pos["burst"]
    assert burst["startedAt"] and pos["serverNow"]
    assert burst["guidanceSeconds"] == 240 and burst["guidanceIsAuthoritative"] is False
    flat = json.dumps(pos).lower()
    for forbidden in ("deadline", "remaining", "expires", "endsat", "autocomplete", "closesat"):
        assert forbidden not in flat


def test_non_member_is_denied(db_connection: sa.Connection) -> None:
    ctx, a, b = _ctx_with_questions(db_connection)
    _, foreign = f03.new_workspace_with_member(db_connection, "nm")
    with pytest.raises(queries.QueryDenied):
        f03.position(db_connection, ctx, foreign)
    assert f02.NOW  # keep import used
