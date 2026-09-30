"""WU-AUTH-03 mutation proof: local credentials through the method model.

Each mutation re-breaks one relation of 24 WU-AUTH-03: login requiring an
ACTIVE method (the single, atomic check), the recorded authentication, the
credential's method being created with it and named in its provenance, the
method being a LOCAL_PASSWORD method of the same user, the immutable link, and
the migration's backfill and downgrade preserving existing credentials.

Usage: `python scripts/auth_wu03_mutation_proof.py` with `DATABASE_URL`
pointed at an isolated *_test database migrated to head.
"""

# ruff: noqa: E501 -- mutation sites are exact source fragments and cannot be wrapped

from __future__ import annotations

from _auth_mutation import Mutation, run_mutations

_MIG = "migrations/versions/a2c4e6f8b1d3_auth_local_credential_method.py"
_LOGIN = "packages/application/auth_handler.py"
_REPO = "packages/persistence/local_auth_repository.py"
_TESTS = (
    "tests/e2e/test_auth_wu03_local_credential_method.py",
    "tests/security/test_auth_migrations.py",
)

MUTATIONS: list[Mutation] = [
    (
        "M01 login does not require an active method",
        [
            (
                _LOGIN,
                "    if not credential_repository.mark_authenticated(record.method_id, at=now):",
                "    if False:",
            )
        ],
    ),
    (
        "M02 the method check reports success without changing an active method",
        [
            (
                _REPO,
                "            .values(last_authenticated_at=at)\n        )\n        return result.rowcount == 1",
                "            .values(last_authenticated_at=at)\n        )\n        return True",
            )
        ],
    ),
    (
        "M03 the method check ignores the method status",
        [
            (
                _REPO,
                "                authentication_methods_table.c.status == AuthenticationMethodStatus.ACTIVE.value,\n            )\n            .values(last_authenticated_at=at)",
                "            )\n            .values(last_authenticated_at=at)",
            )
        ],
    ),
    (
        "M04 the authentication is not recorded on the method",
        [
            (
                _REPO,
                "            .values(last_authenticated_at=at)",
                "            .values(status='ACTIVE')",
            )
        ],
    ),
    (
        "M05 a failed login is recorded as an authentication",
        [
            (
                _LOGIN,
                "    if not normalized_password or not verify_password(normalized_password, record.password_hash):\n        raise InvalidCredentials",
                "    if not normalized_password or not verify_password(normalized_password, record.password_hash):\n        credential_repository.mark_authenticated(record.method_id, at=now)\n        raise InvalidCredentials",
            )
        ],
    ),
    (
        "M06 the method provenance does not name the credential",
        [
            (
                _REPO,
                '            provenance_ref=f"local-credential:{credential_id}",',
                '            provenance_ref="local-credential",',
            )
        ],
    ),
    (
        "M07 a credential is created on a non-password method",
        [
            (
                _REPO,
                "            method_type=AuthenticationMethodType.LOCAL_PASSWORD,",
                "            method_type=AuthenticationMethodType.GOOGLE_OIDC,",
            )
        ],
    ),
    (
        "M08 database accepts a credential on a non-password method",
        [
            (
                _MIG,
                "            IF linked_type IS DISTINCT FROM 'LOCAL_PASSWORD' THEN",
                "            IF FALSE THEN",
            )
        ],
    ),
    (
        "M09 a credential may be moved to another method",
        [(_MIG, "            IF TG_OP = 'UPDATE' AND (", "            IF FALSE AND (")],
    ),
    (
        "M10 a credential may use another user's method",
        [
            (
                _MIG,
                '        ["authentication_method_id", "user_id"],\n        ["id", "user_id"],',
                '        ["authentication_method_id"],\n        ["id"],',
            )
        ],
    ),
    (
        "M11 backfilled methods lose the credential's creation time",
        [(_MIG, "'ACTIVE', c.created_at, NULL,", "'ACTIVE', now(), NULL,")],
    ),
    (
        "M12 backfilled methods do not name their credential",
        [
            (
                _MIG,
                "               NULL, '{_PROVENANCE_PREFIX}' || c.id::text\n        FROM local_auth_credentials c\n",
                "               NULL, '{_PROVENANCE_PREFIX}' || c.user_id::text\n        FROM local_auth_credentials c\n",
            ),
            (
                _MIG,
                "        WHERE m.provenance_ref = '{_PROVENANCE_PREFIX}' || c.id::text",
                "        WHERE m.provenance_ref = '{_PROVENANCE_PREFIX}' || c.user_id::text",
            ),
        ],
    ),
    (
        "M13 existing credentials are not backfilled",
        [
            (
                _MIG,
                '        FROM local_auth_credentials c\n        """\n    )\n    op.execute(\n        f"""\n        UPDATE',
                '        FROM local_auth_credentials c WHERE FALSE\n        """\n    )\n    op.execute(\n        f"""\n        UPDATE',
            )
        ],
    ),
    (
        "M14 downgrade leaves orphan methods behind",
        [
            (
                _MIG,
                "    op.execute(\"DELETE FROM authentication_methods WHERE method_type = 'LOCAL_PASSWORD'\")\n",
                "",
            )
        ],
    ),
]


if __name__ == "__main__":
    raise SystemExit(run_mutations(MUTATIONS, _TESTS))
