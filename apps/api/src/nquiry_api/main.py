"""FastAPI application entrypoint.

ARCHITECTURE 17 UPDATE: `http/commands.py`/`http/queries.py` are now
real (`POST /decisions/{decisionId}/decide`, `GET /workspaces/{w}/
sessions/{s}`) -- see `docs/architecture/17_LIVE_APPLICATION_RUNTIME_MATERIALIZATION.md`.
Both dispatch through `packages/application.http_dispatch` only; this
module still never touches persistence/authority/boundaries directly
(14 §3.1 forbidden dependencies for `apps/api`, enforced by
`scripts/check_architecture_dependencies.py`'s own `nquiry_api` entry).

LOCAL-LOGIN FIELD UPDATE
(`docs/architecture/18_LOCAL_AUTHENTICATION_ADAPTER.md`): `http/auth.py`
adds `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`. Identity
for the two Architecture-17 routes now comes from a real, verified
`nquiry_session` cookie (`application.http_dispatch.resolve_session`),
not from a bare request header -- closes the disclosed GAP-14-001
weakness Architecture 17's own `resolve_actor` recorded ("no
cryptographic verification occurs anywhere in this path").
`CORSMiddleware` gains `allow_credentials=True` (a cross-origin cookie
is not sent by the browser at all without it) and drops the two now-
unused `x-nquiry-actor-*` headers from `allow_headers` -- neither route
reads them anymore (see `http/queries.py`'s own updated docstring for
why supplying them now has zero effect on either route).

PKG-27 ADDITION: `/healthz` emits one real `ObservationContext` through
`LocalOtelObservationSink` per request -- still the only
UNCONDITIONALLY-instrumented call site; the real routes below get their
own observability through `application.http_dispatch`'s own
correlation-id construction (see that module).

CORS (found during the full-stack local runtime acceptance field): the
real browser-facing frontend (`apps/web`, `http://localhost:3000`)
issues real cross-origin `fetch()` calls against this API
(`http://localhost:8000`) -- a different port is a different origin
under the browser's own same-origin policy. Without this, the browser
itself refuses to deliver the response, regardless of what this API
sends -- discovered only by a real browser request (curl, `requests`,
and `TestClient` do not enforce CORS at all; the existing Playwright
E2E suite mocks the network layer via `page.route()` and never issues
a real cross-origin request either). `CORSMiddleware` decides only
WHICH BROWSER ORIGIN may attempt a request -- it grants no authority of
its own (`FRONTEND != AUTHORITY`, unchanged); real session verification
and the real boundary chain still decide everything about WHO may do
WHAT once a request arrives. The allowed origin is deliberately the one
real local frontend origin this repository's own `docker-compose.yml`
publishes web on, not a wildcard -- required anyway, since
`allow_credentials=True` and a wildcard origin are mutually exclusive
under the CORS spec itself (browsers reject the combination).
"""

from __future__ import annotations

import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from observability.context import LocalOtelObservationSink, ObservationContext
from semantic_types.ids import CorrelationId

from nquiry_api.http import auth as auth_router
from nquiry_api.http import commands as commands_router
from nquiry_api.http import queries as queries_router

app = FastAPI(
    title="nquiry-api",
    version="0.0.0",
    description="NQUIRY architectural prototype API — local-login runtime materialization.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
    allow_credentials=True,
)
app.include_router(auth_router.router)
app.include_router(queries_router.router)
app.include_router(commands_router.router)

_observation_sink = LocalOtelObservationSink(tracer_name="nquiry.api")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Liveness probe. Infrastructure-level only; not a Query (14 §13)."""
    _observation_sink.emit(
        ObservationContext(
            correlation_id=CorrelationId(uuid.uuid4()),
            operation="healthz",
        )
    )
    return {"status": "ok", "phase": "0"}
