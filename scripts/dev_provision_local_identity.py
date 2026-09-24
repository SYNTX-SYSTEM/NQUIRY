#!/usr/bin/env python3
"""DEV-ONLY: provision one local login identity (F02 HD-3, 16 §41 REC-003).

NOT A REGISTRATION FEATURE. Creates a `users` row + local credential and
nothing else: no membership, role, authority binding, Facilitator status
or Session authority. Membership and authority must then be established
through the governed product UI/API by a Workspace's governance root.

Refuses to run unless
    NQUIRY_DEV_IDENTITY_PROVISIONING=I_UNDERSTAND_THIS_IS_DEV_ONLY
is set and DATABASE_URL points at a local host.

Usage:
    NQUIRY_DEV_IDENTITY_PROVISIONING=I_UNDERSTAND_THIS_IS_DEV_ONLY \
    DATABASE_URL=postgresql+psycopg://...@localhost:15432/nquiry \
    python scripts/dev_provision_local_identity.py \
        --email b@dev.local.test --name "Bea" --password "<12+ characters>"

Prints one JSON line: {"userId": ..., "email": ..., "identityClass": "DEV_LOCAL_IDENTITY"}.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

import sqlalchemy as sa
from test_support.dev_identity import (
    DEV_IDENTITY_OPT_IN_ENV,
    DevIdentityProvisioningRefused,
    check_dev_provisioning_allowed,
    provision_dev_identity,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="DEV-ONLY local identity provisioning")
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args(argv)

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL is not set.", file=sys.stderr)
        return 2
    url = sa.engine.make_url(database_url)
    try:
        check_dev_provisioning_allowed(
            opt_in_value=os.environ.get(DEV_IDENTITY_OPT_IN_ENV), database_host=url.host
        )
        engine = sa.create_engine(url)
        with engine.begin() as connection:
            identity = provision_dev_identity(
                connection,
                email=args.email,
                name=args.name,
                password=args.password,
                now=datetime.now(timezone.utc),
            )
    except DevIdentityProvisioningRefused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 3
    print(
        json.dumps(
            {
                "userId": str(identity.user_id.value),
                "email": identity.email,
                "identityClass": identity.identity_class,
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
