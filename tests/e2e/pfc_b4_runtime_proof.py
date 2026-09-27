"""WU-PFC-B4/B5 runtime proof driver: the ImpactChain product path and
TRN-SESS-009 on the real stack (not collected by pytest).

    python tests/e2e/pfc_b4_runtime_proof.py seed   # one Fixture Session at QUESTION_CAPTURE
    python tests/e2e/pfc_b4_runtime_proof.py drive <base-url> [--investigate]

`seed` drives the REAL F02/F03 handlers against DATABASE_URL and COMMITS one
Fixture Session with a completed Burst, plus local credentials for its
controller and the Workspace owner. `drive` then speaks ONLY HTTP to a running
`uvicorn nquiry_api.main:app` (dev runtime with the MockProvider):
BEGIN_ANALYSIS, BEGIN_REFLECTION, BEGIN_QUESTION_SELECTION (confirmed); a
the owner grants QUESTION_SELECTION_RIGHT to the controller; compelling and
primary selection; ImpactChain creation; a skipped level (blocked); levels 1..5;
a sixth append (rejected); the GET read model; with `--investigate`, then
BEGIN_INVESTIGATION.
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any

import httpx

STATE = Path(os.environ.get("PFC_B4_PROOF_STATE", "/tmp/pfc_b4_proof_state.json"))
PASSWORD = "pfc-b4-runtime-proof-password"


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


ANSWERS = (
    "Customers who leave early never see the value.",
    "Without the value they do not renew.",
    "Renewals fund the product.",
    "Without funding the team cannot improve onboarding.",
    "So the first month decides whether we survive.",
)


def drive(base: str, investigate: bool) -> None:
    w: dict[str, Any] = json.loads(STATE.read_text())
    fac = _login(base, w["fac_email"])
    owner = _login(base, w["owner_email"])
    root = f"/workspaces/{w['ws']}/sessions/{w['session']}"
    q = w["question_ids"]

    def version() -> int:
        return int(fac.get(f"{root}/position").json()["session"]["version"])

    def post(client: httpx.Client, path: str, **body: Any) -> dict[str, Any]:
        r = client.post(
            path if path.startswith("/") else f"{root}/{path}",
            headers={"Idempotency-Key": str(uuid.uuid4())},
            json=body,
        )
        return {"status": r.status_code, "body": r.json()}

    def node(level: int, answer: str) -> dict[str, Any]:
        chain_version = fac.get(f"{root}/impact-chain").json()["version"]
        return post(
            fac,
            "impact-chain/nodes",
            expectedChainVersion=chain_version,
            level=level,
            answer=answer,
        )

    out: dict[str, Any] = {}
    out["begin_analysis"] = post(fac, "transitions/begin-analysis", expectedVersion=version())[
        "status"
    ]
    out["begin_reflection"] = post(fac, "transitions/begin-reflection", expectedVersion=version())[
        "status"
    ]
    out["begin_question_selection"] = post(
        fac,
        "transitions/begin-question-selection",
        expectedVersion=version(),
        reflectionCompletionConfirmed=True,
    )["status"]
    out["grant_question_selection_right"] = post(
        owner,
        f"/workspaces/{w['ws']}/authority-bindings",
        humanUserId=w["fac_id"],
        authorityClass="QUESTION_SELECTION_RIGHT",
        scopeType="SESSION",
        scopeId=w["session"],
    )["status"]
    out["select_compelling"] = post(
        fac, "question-selections", questionId=q[0], expectedVersion=version()
    )["status"]
    out["select_primary"] = post(
        fac, "primary-question", questionId=q[0], expectedVersion=version()
    )["status"]
    out["begin_investigation_without_chain"] = post(
        fac, "transitions/begin-investigation", expectedVersion=version()
    )
    out["create_impact_chain"] = post(fac, "impact-chain", expectedVersion=version())
    out["append_level_2_first"] = node(2, ANSWERS[1])
    out["append_levels"] = [node(level, ANSWERS[level - 1]) for level in range(1, 6)]
    out["append_level_6"] = node(6, "Beyond five.")
    out["get_impact_chain"] = fac.get(f"{root}/impact-chain").json()
    if investigate:
        out["begin_investigation"] = post(
            fac, "transitions/begin-investigation", expectedVersion=version()
        )
    position = fac.get(f"{root}/position").json()
    out["state_after"] = position["session"]["state"]
    out["proofMode"] = position["session"]["proofMode"]
    out["investigation"] = position.get("investigation")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    if sys.argv[1] == "seed":
        seed()
    else:
        drive(sys.argv[2], "--investigate" in sys.argv)
