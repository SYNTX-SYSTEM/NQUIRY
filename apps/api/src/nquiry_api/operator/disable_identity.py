"""Host-operator command: disable one NQUIRY identity (WU-AUTH-13; 24 §18.2).

    python -m nquiry_api.operator.disable_identity \
        --email <email> --operator otti@condyn.eu --reason "<why>"

Effect (one transaction): the identity is marked disabled (one-way), every
session of it is revoked (ACCOUNT_DISABLED), every open recovery challenge is
revoked, and one SecurityEvent ACCOUNT_DISABLED is recorded. Authentication
methods are blocked by the identity's state, not rewritten; nothing is deleted.

The command requires `NQUIRY_ENVIRONMENT` to be declared and records it.
Authority: the host operator (HD-AUTH-05, resolving HA-AUTH-04; HD-28's
operator authority extended to identity disable). Nothing else may disable:
no HTTP route, no self-disable, no role / membership / email / session
derived authority. Re-enable is not granted (24 §36 #13, separate boundary).

Prints one JSON line on success. Exit codes: 0 disabled; 3 refused (reason
code on stderr); 2 usage error. No HTTP route performs this.
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

from application.account_disable import AccountDisableRefused, run_host_operator_disable
from application.identity_provisioning import ConnectionFactory, HostOperator


def _os_user() -> str:
    try:
        return getpass.getuser()
    except Exception:  # noqa: BLE001 -- containers may have no passwd entry
        return f"uid:{os.getuid()}"


def main(
    argv: list[str] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    connect: ConnectionFactory | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    stdout = stdout if stdout is not None else sys.stdout
    stderr = stderr if stderr is not None else sys.stderr
    environ = environ if environ is not None else os.environ
    parser = argparse.ArgumentParser(
        prog="python -m nquiry_api.operator.disable_identity",
        description="Host-operator account disable (WU-AUTH-13; HD-AUTH-05).",
    )
    parser.add_argument("--email", required=True)
    parser.add_argument("--operator", default="", help="the host operator, e.g. otti@condyn.eu")
    parser.add_argument("--reason", default="", help="why the identity is disabled (recorded)")
    args = parser.parse_args(argv)
    try:
        disabled = run_host_operator_disable(
            email=args.email,
            reason=args.reason,
            operator=HostOperator(
                operator_id=args.operator, os_user=_os_user(), host=socket.gethostname()
            ),
            environment_raw=environ.get("NQUIRY_ENVIRONMENT"),
            now=datetime.now(timezone.utc),
            connect=connect,
        )
    except AccountDisableRefused as exc:
        print(f"REFUSED: {exc.reason_code}", file=stderr)
        return 3
    print(
        json.dumps(
            {
                "userId": str(disabled.user_id.value),
                "email": disabled.email,
                "sessionsRevoked": disabled.sessions_revoked,
                "recoveryChallengesRevoked": disabled.recovery_challenges_revoked,
                "disabledBy": disabled.disabled_by,
                "environment": disabled.environment.value,
                "securityEventId": str(disabled.security_event_id.value),
            }
        ),
        file=stdout,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
