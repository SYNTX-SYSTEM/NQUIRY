"""WU-PFC-A1 (PFC-A Challenge Frame Completion): the four Challenge frame fields
survive the complete legitimate relation.

Architecture: 09 §25 (Challenge data contract: context, desired_outcome,
constraints, stakeholders), 09 §80 (Challenge API: POST / GET
/workspaces/{w}/challenges[/{c}], CMD_CREATE_CHALLENGE, Facilitator source
right), 02 §9 (Challenge). Governing Field: Architecture 25 §23.

FIRST BROKEN RELATION (before this Work Unit): HTTP input → application command.
The body model accepted only title/description (extra keys silently ignored)
and `dispatch_create_challenge` passed `None` for all four fields; the Challenge
detail projection returned only title/description. Domain, handler, payload
fingerprint, repository and table already carried the four fields.

MUST BECOME TRUE: the four fields enter through CMD_CREATE_CHALLENGE over HTTP
and return through the authoritative Challenge projection (GET detail) exactly as
stored: never replaced by None, dropped, rewritten or transformed.

MUST REMAIN TRUE: title required; Facilitator-only creation (Owner and
Contributor denied; no Owner fallback); idempotency (replay, key collision);
description behaviour; the pre-existing detail / overview / position keys and
values (CYAN compatibility); F02 / F03 behaviour.

MUST REMAIN IMPOSSIBLE: a Challenge status (NQ-GAP-018 open); any AI rewrite; a
new authority path; a denied request that stores anything.
"""

from __future__ import annotations

import uuid
from typing import Any

import f02_support as f02
import pytest
import sqlalchemy as sa
import test_http_f02 as http_f02
from governance.membership import WorkspaceRole
from persistence.tables import audit_events_table, challenges_table
from test_http_f02 import _client, _idem

db_app = http_f02.db_app  # the F02 request-connection harness (real PostgreSQL)

FRAME = {
    "context": "  Q3 churn doubled after the pricing change.\nSales says it's the onboarding.  ",
    "desired_outcome": "Understand *why* customers leave — before we change anything. 🙂",
    "constraints": "No new hires; decision by 30 Oct.\n\t- keep the free tier",
    "stakeholders": "Customers (SMB), Support, Sales, Product; Ünïcödé & <b>markup</b> stay text",
}
FIELDS = ("context", "desired_outcome", "constraints", "stakeholders")
WIRE = {
    "context": "context",
    "desired_outcome": "desiredOutcome",
    "constraints": "constraints",
    "stakeholders": "stakeholders",
}


def _setup(db: sa.Connection) -> dict[str, Any]:
    owner = f02.insert_user(db, "owner")
    fac = f02.insert_user(db, "fac")
    contributor = f02.insert_user(db, "contrib")
    ws = f02.found_workspace(db, owner=owner, name="PFC-A1").workspace_id
    f02.add_member(db, owner=owner, workspace_id=ws, member=fac)
    f02.add_member(
        db, owner=owner, workspace_id=ws, member=contributor, role=WorkspaceRole.CONTRIBUTOR
    )
    stranger = f02.insert_user(db, "stranger")
    return {
        "ws": str(ws.value),
        "owner": _client(db, owner),
        "fac": _client(db, fac),
        "contributor": _client(db, contributor),
        "stranger": _client(db, stranger),
    }


def _body(**frame: Any) -> dict[str, Any]:
    body: dict[str, Any] = {"title": "Why are customers leaving?", "description": "d"}
    body.update({WIRE[k]: v for k, v in frame.items()})
    return body


def _row(db: sa.Connection, challenge_id: str) -> Any:
    return (
        db.execute(
            sa.select(challenges_table).where(challenges_table.c.id == uuid.UUID(challenge_id))
        )
        .mappings()
        .one()
    )


def _count(db: sa.Connection) -> int:
    return db.execute(sa.select(sa.func.count()).select_from(challenges_table)).scalar_one()


# ------------------------------------------------------------ MUST BECOME TRUE


def test_frame_fields_round_trip_exactly(db_app: sa.Connection) -> None:
    w = _setup(db_app)
    r = w["fac"].post(f"/workspaces/{w['ws']}/challenges", headers=_idem(), json=_body(**FRAME))
    assert r.status_code == 200, r.text
    cid = r.json()["challengeId"]
    # persistence: byte-exact, nothing trimmed or rewritten
    row = _row(db_app, cid)
    for field in FIELDS:
        assert row[field] == FRAME[field], field
    # authoritative projection (09 §80 GET detail): exactly as stored
    detail = w["fac"].get(f"/workspaces/{w['ws']}/challenges/{cid}").json()["challenge"]
    for field in FIELDS:
        assert detail[WIRE[field]] == FRAME[field], field
    # every Workspace member who can read the Challenge reads the same frame
    for reader in ("owner", "contributor"):
        other = w[reader].get(f"/workspaces/{w['ws']}/challenges/{cid}").json()["challenge"]
        assert {WIRE[f]: other[WIRE[f]] for f in FIELDS} == {WIRE[f]: FRAME[f] for f in FIELDS}


@pytest.mark.parametrize("field", FIELDS)
def test_each_field_travels_independently(db_app: sa.Connection, field: str) -> None:
    w = _setup(db_app)
    cid = (
        w["fac"]
        .post(
            f"/workspaces/{w['ws']}/challenges",
            headers=_idem(),
            json=_body(**{field: FRAME[field]}),
        )
        .json()["challengeId"]
    )
    detail = w["fac"].get(f"/workspaces/{w['ws']}/challenges/{cid}").json()["challenge"]
    for other in FIELDS:
        assert detail[WIRE[other]] == (FRAME[field] if other == field else None)


# ------------------------------------------------------------ Case-2 choice


@pytest.mark.parametrize("value", [None, "", "   ", "\n\t "])
def test_absent_null_empty_or_blank_means_not_provided(db_app: sa.Connection, value: Any) -> None:
    w = _setup(db_app)
    cid = (
        w["fac"]
        .post(
            f"/workspaces/{w['ws']}/challenges",
            headers=_idem(),
            json=_body(**{f: value for f in FIELDS}),
        )
        .json()["challengeId"]
    )
    row = _row(db_app, cid)
    assert all(row[f] is None for f in FIELDS)
    detail = w["fac"].get(f"/workspaces/{w['ws']}/challenges/{cid}").json()["challenge"]
    assert all(detail[WIRE[f]] is None for f in FIELDS)


@pytest.mark.parametrize("bad", [42, ["a"], {"x": 1}, True])
def test_non_text_frame_value_is_rejected_and_nothing_stored(
    db_app: sa.Connection, bad: Any
) -> None:
    w = _setup(db_app)
    before = _count(db_app)
    r = w["fac"].post(f"/workspaces/{w['ws']}/challenges", headers=_idem(), json=_body(context=bad))
    assert r.status_code == 400 and r.json()["kind"] == "rejected"
    assert _count(db_app) == before


# ------------------------------------------------------------ MUST REMAIN TRUE


def test_title_remains_required(db_app: sa.Connection) -> None:
    w = _setup(db_app)
    before = _count(db_app)
    r = w["fac"].post(
        f"/workspaces/{w['ws']}/challenges",
        headers=_idem(),
        json={"title": "  ", **{WIRE[k]: v for k, v in FRAME.items()}},
    )
    assert r.status_code == 400 and r.json()["reasonCode"] == "TITLE_REQUIRED"
    assert _count(db_app) == before


@pytest.mark.parametrize("who", ["owner", "contributor", "stranger"])
def test_authority_unchanged_and_denial_stores_nothing(db_app: sa.Connection, who: str) -> None:
    w = _setup(db_app)
    before = _count(db_app)
    r = w[who].post(f"/workspaces/{w['ws']}/challenges", headers=_idem(), json=_body(**FRAME))
    assert r.status_code == 403 and r.json()["kind"] == "denied"
    assert _count(db_app) == before


def test_idempotency_covers_the_frame(db_app: sa.Connection) -> None:
    w = _setup(db_app)
    key = {"Idempotency-Key": str(uuid.uuid4())}
    first = (
        w["fac"].post(f"/workspaces/{w['ws']}/challenges", headers=key, json=_body(**FRAME)).json()
    )
    again = (
        w["fac"].post(f"/workspaces/{w['ws']}/challenges", headers=key, json=_body(**FRAME)).json()
    )
    assert first["challengeId"] == again["challengeId"]
    changed = dict(FRAME, constraints="different")
    collision = w["fac"].post(
        f"/workspaces/{w['ws']}/challenges", headers=key, json=_body(**changed)
    )
    assert collision.json()["kind"] == "rejected"
    assert _row(db_app, first["challengeId"])["constraints"] == FRAME["constraints"]


def test_cyan_shaped_request_and_pre_existing_keys_are_unchanged(db_app: sa.Connection) -> None:
    """The CYAN client sends exactly {title, description} and reads named keys."""
    w = _setup(db_app)
    cid = (
        w["fac"]
        .post(
            f"/workspaces/{w['ws']}/challenges",
            headers=_idem(),
            json={"title": "T", "description": "D"},
        )
        .json()["challengeId"]
    )
    detail = w["fac"].get(f"/workspaces/{w['ws']}/challenges/{cid}").json()
    challenge = detail["challenge"]
    assert challenge["challengeId"] == cid
    assert challenge["title"] == "T" and challenge["description"] == "D"
    assert isinstance(challenge["createdAt"], str)
    # additive only: the pre-existing keys are all still present
    assert {"challengeId", "title", "description", "createdAt"} <= set(challenge)
    assert set(detail) == {
        "kind",
        "workspace",
        "challenge",
        "sessions",
        "sessionControllers",
        "members",
        "capabilities",
    }
    # the overview list keeps its exact shape (NOT AFFECTED by this Work Unit)
    listed = w["fac"].get(f"/workspaces/{w['ws']}/overview").json()["challenges"][0]
    assert set(listed) == {"challengeId", "title", "description", "createdAt"}


def test_description_behaviour_unchanged(db_app: sa.Connection) -> None:
    w = _setup(db_app)
    cid = (
        w["fac"]
        .post(
            f"/workspaces/{w['ws']}/challenges",
            headers=_idem(),
            json={"title": "  T  ", "description": "  D  "},
        )
        .json()["challengeId"]
    )
    row = _row(db_app, cid)
    assert (row["title"], row["description"]) == ("T", "D")  # F02: stripped, as before


# ------------------------------------------------------------ MUST REMAIN IMPOSSIBLE


def test_no_status_and_no_new_fields(db_app: sa.Connection) -> None:
    w = _setup(db_app)
    cid = (
        w["fac"]
        .post(f"/workspaces/{w['ws']}/challenges", headers=_idem(), json=_body(**FRAME))
        .json()["challengeId"]
    )
    challenge = w["fac"].get(f"/workspaces/{w['ws']}/challenges/{cid}").json()["challenge"]
    assert set(challenge) == {"challengeId", "title", "description", "createdAt", *WIRE.values()}
    assert "status" not in challenge and "emotionalTemperature" not in challenge
    assert "status" not in challenges_table.c


def test_status_or_unknown_input_is_not_honoured(db_app: sa.Connection) -> None:
    """Unknown keys stay unrepresentable: they are ignored as before, never stored."""
    w = _setup(db_app)
    cid = (
        w["fac"]
        .post(
            f"/workspaces/{w['ws']}/challenges",
            headers=_idem(),
            json={**_body(**FRAME), "status": "ACTIVE", "emotionalTemperature": 7},
        )
        .json()["challengeId"]
    )
    challenge = w["fac"].get(f"/workspaces/{w['ws']}/challenges/{cid}").json()["challenge"]
    assert "status" not in challenge and "emotionalTemperature" not in challenge
    assert "status" not in _row(db_app, cid)


def test_one_governed_commit_with_facilitator_role_provenance(db_app: sa.Connection) -> None:
    w = _setup(db_app)
    cid = (
        w["fac"]
        .post(f"/workspaces/{w['ws']}/challenges", headers=_idem(), json=_body(**FRAME))
        .json()["challengeId"]
    )
    audits = list(
        db_app.execute(
            sa.select(audit_events_table).where(
                audit_events_table.c.command_type == "CMD_CREATE_CHALLENGE",
                audit_events_table.c.target_refs.any(f"challenge:{cid}"),
            )
        ).mappings()
    )
    assert len(audits) == 1
    assert audits[0]["authority_source_type"] == "ROLE"
    assert audits[0]["actor_type"] == "HUMAN_USER"
