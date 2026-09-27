"""WU-PFC-B3 runtime proof driver: the QuestionSelection product path on the real
stack (not collected by pytest).

    python tests/e2e/pfc_b3_runtime_proof.py seed   # one Fixture Session at QUESTION_CAPTURE
    python tests/e2e/pfc_b3_runtime_proof.py drive <base-url>

`seed` drives the REAL F02/F03 handlers against DATABASE_URL and COMMITS one
Fixture Session with a completed Burst, plus local credentials for its
controller and the Workspace owner. `drive` then speaks ONLY HTTP to a running
`uvicorn nquiry_api.main:app` (dev runtime with the MockProvider):
BEGIN_ANALYSIS, BEGIN_REFLECTION, BEGIN_QUESTION_SELECTION (confirmed); a
selection before any QUESTION_SELECTION_RIGHT exists (denied); the owner grants
the right to the controller over HTTP; compelling, duplicate, primary and
second-primary selections; then the GET read model and the position.
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any

import httpx

STATE = Path(os.environ.get("PFC_B3_PROOF_STATE", "/tmp/pfc_b3_proof_state.json"))
PASSWORD = "pfc-b3-runtime-proof-password"


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
        ctx = f04.capture_context(db, fixture=True)
        world: dict[str, Any] = {
            "ws": str(ctx["ws"].value),
            "session": str(ctx["session"].value),
            "fac_id": str(ctx["fac"].value),
            "question_ids": [str(q.value) for q in ctx["question_ids"]],
        }
        for role in ("fac", "owner"):
            world[f"{role}_email"] = db.execute(
                sa.select(users_table.c.email).where(users_table.c.id == ctx[role].value)
            ).scalar_one()
            SqlAlchemyLocalCredentialRepository(db).create(
                user_id=UserId(ctx[role].value), password_hash=hash_password(PASSWORD), now=f02.NOW
            )
        db.commit()
    STATE.write_text(json.dumps(world, indent=2))
    print(f"SEEDED {STATE}")


def _login(base: str, email: str) -> httpx.Client:
    client = httpx.Client(base_url=base, timeout=60)
    assert (
        client.post("/auth/login", json={"email": email, "password": PASSWORD}).status_code == 200
    )
    return client


def drive(base: str) -> None:
    w: dict[str, Any] = json.loads(STATE.read_text())
    fac = _login(base, w["fac_email"])
    owner = _login(base, w["owner_email"])
    root = f"/workspaces/{w['ws']}/sessions/{w['session']}"
    q = w["question_ids"]

    def post(client: httpx.Client, path: str, **body: Any) -> dict[str, Any]:
        version = int(fac.get(f"{root}/position").json()["session"]["version"])
        r = client.post(
            path if path.startswith("/") else f"{root}/{path}",
            headers={"Idempotency-Key": str(uuid.uuid4())},
            json={"expectedVersion": version, **body},
        )
        return {"status": r.status_code, "body": r.json()}

    out: dict[str, Any] = {}
    out["begin_analysis"] = post(fac, "transitions/begin-analysis")["status"]
    out["begin_reflection"] = post(fac, "transitions/begin-reflection")["status"]
    out["begin_question_selection"] = post(
        fac, "transitions/begin-question-selection", reflectionCompletionConfirmed=True
    )["status"]
    out["select_without_right"] = post(fac, "question-selections", questionId=q[0])
    out["grant_question_selection_right"] = post(
        owner,
        f"/workspaces/{w['ws']}/authority-bindings",
        humanUserId=w["fac_id"],
        authorityClass="QUESTION_SELECTION_RIGHT",
        scopeType="SESSION",
        scopeId=w["session"],
    )
    out["capabilities_after_grant"] = {
        k: v
        for k, v in fac.get(f"{root}/position").json()["actions"].items()
        if k.startswith("SELECT_")
    }
    out["select_compelling_q0"] = post(fac, "question-selections", questionId=q[0])
    out["select_compelling_q0_again"] = post(fac, "question-selections", questionId=q[0])
    out["select_primary_q0"] = post(fac, "primary-question", questionId=q[0])
    out["select_primary_q1"] = post(fac, "primary-question", questionId=q[1])
    out["get_question_selections"] = fac.get(f"{root}/question-selections").json()
    position = fac.get(f"{root}/position").json()
    out["state_after"] = position["session"]["state"]
    out["proofMode"] = position["session"]["proofMode"]
    out["position_selection"] = position["selection"]
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    if sys.argv[1] == "seed":
        seed()
    else:
        drive(sys.argv[2])
