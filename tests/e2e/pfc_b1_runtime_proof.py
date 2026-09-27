"""WU-PFC-B1 runtime proof driver: HD-24 on the real stack (not collected by pytest).

    python tests/e2e/pfc_b1_runtime_proof.py seed   # commits two Sessions at QUESTION_CAPTURE
    python tests/e2e/pfc_b1_runtime_proof.py drive <base-url>

`seed` drives the REAL F02/F03 handlers against DATABASE_URL and COMMITS one
Fixture Session and one real (non-Fixture) Session, each with a completed
Burst, and local credentials for their controllers. `drive` then speaks ONLY
HTTP to a running `uvicorn nquiry_api.main:app` (dev runtime with the
MockProvider): BEGIN_ANALYSIS (the API runs the mock analysis right after the
commit), then BEGIN_REFLECTION on both Sessions, printing each outcome and the
resulting positions as JSON.
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any

import httpx

STATE = Path(os.environ.get("PFC_B1_PROOF_STATE", "/tmp/pfc_b1_proof_state.json"))
PASSWORD = "pfc-b1-runtime-proof-password"


def seed() -> None:
    import f02_support as f02
    import f04_support as f04
    import sqlalchemy as sa
    from persistence.local_auth_repository import SqlAlchemyLocalCredentialRepository
    from persistence.tables import users_table
    from security.local_auth import hash_password
    from semantic_types.ids import UserId

    engine = sa.create_engine(os.environ["DATABASE_URL"])
    world: dict[str, Any] = {}
    with engine.connect() as db:
        for label, fixture in (("fixture", True), ("real", False)):
            ctx = f04.capture_context(db, fixture=fixture)
            email = db.execute(
                sa.select(users_table.c.email).where(users_table.c.id == ctx["fac"].value)
            ).scalar_one()
            SqlAlchemyLocalCredentialRepository(db).create(
                user_id=UserId(ctx["fac"].value), password_hash=hash_password(PASSWORD), now=f02.NOW
            )
            world[label] = {
                "ws": str(ctx["ws"].value),
                "session": str(ctx["session"].value),
                "email": email,
            }
        db.commit()
    STATE.write_text(json.dumps(world, indent=2))
    print(f"SEEDED {STATE}")


def _drive_one(base: str, s: dict[str, Any]) -> dict[str, Any]:
    client = httpx.Client(base_url=base, timeout=60)
    login = client.post("/auth/login", json={"email": s["email"], "password": PASSWORD})
    assert login.status_code == 200
    root = f"/workspaces/{s['ws']}/sessions/{s['session']}"

    def post(path: str) -> dict[str, Any]:
        version = int(client.get(f"{root}/position").json()["session"]["version"])
        r = client.post(
            f"{root}/{path}",
            headers={"Idempotency-Key": str(uuid.uuid4())},
            json={"expectedVersion": version},
        )
        return {"status": r.status_code, "body": r.json()}

    begin = post("transitions/begin-analysis")
    reflection = post("transitions/begin-reflection")
    position = client.get(f"{root}/position").json()
    return {
        "begin_analysis": {"status": begin["status"], "kind": begin["body"]["kind"]},
        "begin_reflection": reflection,
        "state_after": position["session"]["state"],
        "proofMode": position["session"]["proofMode"],
        "fixture": position["session"]["fixture"],
        "reflection": position["reflection"],
        "BEGIN_REFLECTION_capability": position["actions"]["BEGIN_REFLECTION"],
    }


def drive(base: str) -> None:
    world: dict[str, Any] = json.loads(STATE.read_text())
    print(json.dumps({label: _drive_one(base, s) for label, s in world.items()}, indent=2))


if __name__ == "__main__":
    if sys.argv[1] == "seed":
        seed()
    else:
        drive(sys.argv[2])
