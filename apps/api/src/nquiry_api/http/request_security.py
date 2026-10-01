"""Anti-CSRF middleware (WU-AUTH-14; 24 §21.6–21.9). Pure ASGI: for every
unsafe request it asks `application.request_security.guard_request` with the
raw header values and the request's own origin, and answers the boundary
failure itself — before routing, body parsing or any application code.

Registered inside the CORS layer, so a preflight (`OPTIONS`) is answered by
CORS and never reaches this boundary, and the boundary's own 403 still
carries the CORS headers the browser needs to show it to the page.
"""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable, MutableMapping
from typing import Any

from application.request_security import guard_request

Scope = MutableMapping[str, Any]
Receive = Callable[[], Awaitable[MutableMapping[str, Any]]]
Send = Callable[[MutableMapping[str, Any]], Awaitable[None]]
ASGIApp = Callable[[Scope, Receive, Send], Awaitable[None]]


def _header(scope: Scope, name: bytes) -> str | None:
    for key, value in scope.get("headers", ()):
        if key == name:
            return value.decode("latin-1")
    return None


def _own_origin(scope: Scope) -> str:
    """The origin the request was addressed to: the `Host` the browser used,
    with the scheme the server saw (a reverse proxy's `X-Forwarded-Proto`
    when present, as the deployment terminates TLS in front)."""
    scheme = _header(scope, b"x-forwarded-proto") or scope.get("scheme", "http")
    host = _header(scope, b"x-forwarded-host") or _header(scope, b"host") or ""
    return f"{scheme.split(',')[0].strip()}://{host.split(',')[0].strip()}"


class RequestSecurityMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return
        failure = guard_request(
            method=scope["method"],
            path=scope["path"],
            origin=_header(scope, b"origin"),
            sec_fetch_site=_header(scope, b"sec-fetch-site"),
            content_type=_header(scope, b"content-type"),
            own_origin=_own_origin(scope),
        )
        if failure is None:
            await self._app(scope, receive, send)
            return
        status, body = failure
        payload = json.dumps(body).encode("utf-8")
        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(payload)).encode("ascii")),
                ],
            }
        )
        await send({"type": "http.response.body", "body": payload})


__all__ = ["RequestSecurityMiddleware"]
