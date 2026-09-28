"""Host-operator command: create one NQUIRY identity (WU-PFC-AC1; HD-28 / NQ-DEC-056).

    docker compose -p nquiry exec -T api \
        python -m nquiry_api.operator.create_identity \
        --email <email> --name "<display name>" --operator otti@condyn.eu \
        < password-file

The password is read from standard input (one line; without a TTY) or asked
twice without echo (with a TTY). It is never accepted as an argument (argv is
visible in process listings and shell history) and never printed. The command
requires `NQUIRY_ENVIRONMENT` to be declared (DEVELOPMENT, TEST, STAGING or
PRODUCTION) and records it.

Prints one JSON line on success: userId, email, identityClass, createdBy,
environment, securityEventId. Exit codes: 0 created; 3 refused (reason code on
stderr); 2 usage error.

It creates an identity and a credential only: no Workspace membership, role,
authority binding, governance authority or Session authority (HD-28). It does
not change existing identities and has no password reset (HD-28 §2).
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import socket
import sys
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import TextIO

from application.identity_provisioning import (
    IDENTITY_CLASS,
    ConnectionFactory,
    HostOperator,
    IdentityCreationRefused,
    run_host_operator_creation,
)


def _read_password(stdin: TextIO) -> str:
    if stdin.isatty():
        first = getpass.getpass("Password (not echoed): ")
        if getpass.getpass("Repeat password: ") != first:
            raise IdentityCreationRefused("PASSWORD_CONFIRMATION_MISMATCH")
        return first
    line = stdin.readline()
    return line[:-1] if line.endswith("\n") else line


def _os_user() -> str:
    try:
        return getpass.getuser()
    except Exception:  # noqa: BLE001 -- containers may have no passwd entry
        return f"uid:{os.getuid()}"


def main(
    argv: list[str] | None = None,
    *,
    stdin: TextIO | None = None,
    environ: Mapping[str, str] | None = None,
    connect: ConnectionFactory | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    stdin = stdin if stdin is not None else sys.stdin
    stdout = stdout if stdout is not None else sys.stdout
    stderr = stderr if stderr is not None else sys.stderr
    environ = environ if environ is not None else os.environ
    parser = argparse.ArgumentParser(
        prog="python -m nquiry_api.operator.create_identity",
        description="Host-operator account creation (HD-28). Password from stdin.",
    )
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--operator", default="", help="the host operator, e.g. otti@condyn.eu")
    args = parser.parse_args(argv)
    try:
        created = run_host_operator_creation(
            email=args.email,
            name=args.name,
            password=_read_password(stdin),
            operator=HostOperator(
                operator_id=args.operator, os_user=_os_user(), host=socket.gethostname()
            ),
            environment_raw=environ.get("NQUIRY_ENVIRONMENT"),
            now=datetime.now(timezone.utc),
            connect=connect,
        )
    except IdentityCreationRefused as exc:
        print(f"REFUSED: {exc.reason_code}", file=stderr)
        return 3
    print(
        json.dumps(
            {
                "userId": str(created.user_id.value),
                "email": created.email,
                "identityClass": IDENTITY_CLASS,
                "createdBy": created.created_by,
                "environment": created.environment.value,
                "securityEventId": str(created.security_event_id.value),
            }
        ),
        file=stdout,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
