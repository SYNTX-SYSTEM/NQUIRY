"""Workspace HTTP surface (F01 WU-01.8): `POST /workspaces`,
`GET /workspaces`, `GET /workspaces/{workspaceId}`,
`POST /workspaces/{workspaceId}/members`,
`POST /workspaces/{workspaceId}/authority-bindings/{bindingId}/revoke`.

Same thin-adapter discipline as `queries.py`/`commands.py`/`auth.py`'s
own header docstrings -- all real work happens in the five
`application.http_dispatch.dispatch_*` functions this file calls; this
module extracts plain strings from the request and serializes plain
dicts, nothing else. Identity comes from the real, `HttpOnly`
`nquiry_session` cookie (`application.http_dispatch.SESSION_COOKIE_NAME`),
same as every other authenticated route in this codebase since the
local-login field -- never a request header.

Path naming deliberately does NOT use `14_IMPLEMENTATION_SEQUENCE.md`
section 36's own literal `/v1/workspaces/...` prefix -- Architecture 17
already established the un-prefixed convention this whole HTTP surface
uses (`/workspaces/...`, `/decisions/...`, `/auth/...`); this Work Unit
stays consistent with the CODE's own established convention rather
than an older architecture document's literal text.

`NoValidSessionError` is caught before `ValueError` in every handler
below despite being a subclass of it (`application.http_dispatch`'s
own definition) -- same auth-before-input-validation precedence
`queries.py`/`commands.py` already established; catching `ValueError`
first would silently swallow session failures as generic 400s instead
of the correct 401.
"""

from __future__ import annotations

from application.http_dispatch import (
    SESSION_COOKIE_NAME,
    NoValidSessionError,
    dispatch_add_member,
    dispatch_create_workspace,
    dispatch_list_accessible_workspaces,
    dispatch_revoke_authority_binding,
    dispatch_workspace_orientation,
)
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()


class CreateWorkspaceBody(BaseModel):
    name: str


class AddMemberBody(BaseModel):
    userId: str  # noqa: N815 -- wire contract is camelCase
    role: str


def _no_session_response(exc: NoValidSessionError) -> JSONResponse:
    return JSONResponse(
        status_code=401, content={"kind": "denied", "result": "DENY", "reasonCode": str(exc)}
    )


def _malformed_input_response(exc: ValueError) -> JSONResponse:
    return JSONResponse(
        status_code=400, content={"kind": "denied", "result": "DENY", "reasonCode": str(exc)}
    )


@router.post("/workspaces")
def create_workspace(body: CreateWorkspaceBody, request: Request) -> JSONResponse:
    try:
        result = dispatch_create_workspace(
            session_token=request.cookies.get(SESSION_COOKIE_NAME), workspace_name=body.name
        )
    except NoValidSessionError as exc:
        return _no_session_response(exc)
    return JSONResponse(content=result)


@router.get("/workspaces")
def list_workspaces(request: Request) -> JSONResponse:
    try:
        result = dispatch_list_accessible_workspaces(
            session_token=request.cookies.get(SESSION_COOKIE_NAME)
        )
    except NoValidSessionError as exc:
        return _no_session_response(exc)
    return JSONResponse(content=result)


@router.get("/workspaces/{workspace_id}")
def get_workspace_orientation(workspace_id: str, request: Request) -> JSONResponse:
    try:
        result = dispatch_workspace_orientation(
            session_token=request.cookies.get(SESSION_COOKIE_NAME), workspace_id_str=workspace_id
        )
    except NoValidSessionError as exc:
        return _no_session_response(exc)
    except ValueError as exc:
        return _malformed_input_response(exc)
    return JSONResponse(content=result)


@router.post("/workspaces/{workspace_id}/members")
def add_workspace_member(workspace_id: str, body: AddMemberBody, request: Request) -> JSONResponse:
    try:
        result = dispatch_add_member(
            session_token=request.cookies.get(SESSION_COOKIE_NAME),
            workspace_id_str=workspace_id,
            new_member_user_id_str=body.userId,
            role_str=body.role,
        )
    except NoValidSessionError as exc:
        return _no_session_response(exc)
    except ValueError as exc:
        return _malformed_input_response(exc)
    return JSONResponse(content=result)


@router.post("/workspaces/{workspace_id}/authority-bindings/{binding_id}/revoke")
def revoke_authority_binding(workspace_id: str, binding_id: str, request: Request) -> JSONResponse:
    try:
        result = dispatch_revoke_authority_binding(
            session_token=request.cookies.get(SESSION_COOKIE_NAME),
            workspace_id_str=workspace_id,
            binding_id_str=binding_id,
        )
    except NoValidSessionError as exc:
        return _no_session_response(exc)
    except ValueError as exc:
        return _malformed_input_response(exc)
    return JSONResponse(content=result)


__all__ = ["router"]
