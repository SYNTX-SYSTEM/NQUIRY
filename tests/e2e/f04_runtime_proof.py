"""F04 runtime proof driver (WU-04.10): the RED API as a real process.

Not collected by pytest. Usage (see docs/implementation/field-reports/F04/
evidence/RUNTIME_PROOF.md):

    python tests/e2e/f04_runtime_proof.py seed   # commit a QUESTION_CAPTURE Session
    python tests/e2e/f04_runtime_proof.py drive <base-url> <phase>

`seed` drives the REAL F02/F03 handlers against DATABASE_URL and COMMITS, and
writes the world (ids, emails) to $F04_PROOF_STATE. `drive` then talks ONLY
HTTP to a running `uvicorn nquiry_api.main:app`: login cookies, Idempotency-Key,
the real begin-analysis / request routes, and position reads by several
members. Each HTTP request runs in real database transactions (PI-2: T1 is
committed before the system run's T2a / T2b+T3).
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any

import httpx

STATE = Path(os.environ.get("F04_PROOF_STATE", "/tmp/f04_proof_state.json"))
PASSWORD = "f04-runtime-proof-password"


def seed() -> None:
    import f02_support as f02
    import f04_support as f04
    import sqlalchemy as sa
    from persistence.local_auth_repository import SqlAlchemyLocalCredentialRepository
    from persistence.tables import users_table
    from security.local_auth import hash_password
    from semantic_types.ids import UserId

    engine = sa.create_engine(os.environ["DATABASE_URL"])
    with engine.connect() as db:
        ctx = f04.capture_context(db)
        people = {
            "fac": ctx["fac"],
            "participant": ctx["participants"][0],
            "owner": ctx["owner"],
            "outsider": ctx["outsider"],
            "stranger": f02.insert_user(db, "stranger"),
        }
        emails = {}
        for name, user in people.items():
            email = db.execute(
                sa.select(users_table.c.email).where(users_table.c.id == user.value)
            ).scalar_one()
            SqlAlchemyLocalCredentialRepository(db).create(
                user_id=UserId(user.value), password_hash=hash_password(PASSWORD), now=f02.NOW
            )
            emails[name] = email
        db.commit()
    STATE.write_text(
        json.dumps(
            {
                "ws": str(ctx["ws"].value),
                "session": str(ctx["session"].value),
                "emails": emails,
                "questions": [str(q.value) for q in ctx["question_ids"]],
            },
            indent=2,
        )
    )
    print(f"SEEDED {STATE}")


def _client(base: str, email: str) -> httpx.Client:
    client = httpx.Client(base_url=base, timeout=30)
    r = client.post("/auth/login", json={"email": email, "password": PASSWORD})
    assert r.status_code == 200, r.text
    return client


def drive(base: str, phase: str) -> None:
    world: dict[str, Any] = json.loads(STATE.read_text())
    root = f"/workspaces/{world['ws']}/sessions/{world['session']}"
    c = {name: _client(base, email) for name, email in world["emails"].items()}

    def pos(name: str = "fac") -> dict[str, Any]:
        r = c[name].get(f"{root}/position")
        assert r.status_code == 200, (name, r.text)
        return r.json()

    def post(name: str, path: str, body: dict[str, Any]) -> httpx.Response:
        return c[name].post(
            f"{root}/{path}", headers={"Idempotency-Key": str(uuid.uuid4())}, json=body
        )

    out: dict[str, Any] = {"phase": phase}
    if phase == "begin-failing":
        # server started with NQUIRY_AI_MOCK_OUTCOME_AIOP_001=TIMEOUT
        version = pos()["session"]["version"]
        out["participant_begin"] = post(
            "participant", "transitions/begin-analysis", {"expectedVersion": version}
        ).json()
        r = post("fac", "transitions/begin-analysis", {"expectedVersion": version})
        body = r.json()
        out["begin_status"] = r.status_code
        out["begin_kind"] = body["kind"]
        out["begin_run"] = body["analysis"]
        p = pos("participant")
        out["state_after"] = p["session"]["state"]
        out["established_by"] = p["establishedBy"]
        out["participant_view_status"] = p["analysis"]["analysis"]["status"]
        out["clustering_status"] = p["analysis"]["clustering"]["status"]
        out["frozen_questions_still_served"] = p["questionSet"]["visibility"]
        out["fac_request_cap"] = pos("fac")["actions"]["REQUEST_QUESTION_ANALYSIS"]
        out["participant_request_cap"] = p["actions"]["REQUEST_QUESTION_ANALYSIS"]
    elif phase == "retry":
        version = pos()["session"]["version"]
        out["wrong_case"] = post(
            "fac", "analysis/request", {"expectedVersion": version, "case": "RECOVERY"}
        ).json()
        out["owner_retry"] = post(
            "owner", "analysis/request", {"expectedVersion": version, "case": "RETRY"}
        ).status_code
        r = post("fac", "analysis/request", {"expectedVersion": version, "case": "RETRY"})
        out["retry_status"] = r.status_code
        out["retry_run"] = r.json()["analysis"]
        views = {n: pos(n)["analysis"] for n in ("fac", "participant", "owner", "outsider")}
        out["audience_views_identical"] = all(v == views["fac"] for v in views.values())
        a = views["participant"]
        out["marker"] = a["marker"]
        out["analysis_status"] = a["analysis"]["status"]
        out["artifact_proof_class"] = a["analysis"]["artifact"]["proofClass"]
        out["clustering_status"] = a["clustering"]["status"]
        out["cluster_count"] = len(a["clustering"]["clusters"])
        out["generations"] = [
            (
                g["operation"],
                g["status"],
                g["provider"],
                g["authorization"]["shape"],
                g["authorization"]["requestCase"],
            )
            for g in a["generations"]
        ]
        out["stranger_position"] = c["stranger"].get(f"{root}/position").status_code
        out["human_questions_verbatim"] = [
            q["originalText"] for q in pos("participant")["questionSet"]["frozen"]["questions"]
        ]
        out["after_accept_cap"] = pos("fac")["actions"]["REQUEST_QUESTION_ANALYSIS"]
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    if sys.argv[1] == "seed":
        seed()
    else:
        drive(sys.argv[2], sys.argv[3])
