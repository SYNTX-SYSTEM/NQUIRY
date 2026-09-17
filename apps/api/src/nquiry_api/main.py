"""FastAPI application entrypoint.

PKG-00 SCOPE: toolchain boot proof only. This module wires the FastAPI
app instance and one liveness endpoint. It must not gain a Command or
Query route until `apps/api/src/nquiry_api/http/commands.py` and
`queries.py` exist (14 §35, §36; file map in 14 §48, Phase 4+), and
those must dispatch through `packages/application`, never mutate
persistence directly (14 §3.1 forbidden dependencies for `apps/api`
controllers: "ORM session mutation, provider SDK, direct CommitUnit
internals").
"""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(
    title="nquiry-api",
    version="0.0.0",
    description="NQUIRY architectural prototype API — Phase 0 skeleton.",
)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Liveness probe. Infrastructure-level only; not a Query (14 §13)."""
    return {"status": "ok", "phase": "0"}
