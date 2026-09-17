"""Toolchain boot proof: the FastAPI app imports and answers /healthz.

This is not a T0-T12 architectural proof test (it asserts nothing
about authority, Boundary, or CommitUnit); it exists solely to prove
the Phase 0 toolchain gate ("build/lint/typecheck pass... forbidden
imports detected", 14 §44 PHASE 0).
"""

from __future__ import annotations

from fastapi.testclient import TestClient
from nquiry_api.main import app


def test_healthz_reports_ok() -> None:
    client = TestClient(app)
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "phase": "0"}
