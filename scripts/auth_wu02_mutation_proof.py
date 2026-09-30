"""WU-AUTH-02 mutation proof: the authentication method model is guarded.

Each mutation re-breaks one relation of 24 §9.1 / §13.2: the closed method
vocabulary (a proof or protocol relation accepted as a method), the
ACTIVE/REVOKED consistency, the one-active-local-password rule, the
created-ACTIVE rule, REVOKED as terminal, the immutable method identity, the
canonical-user requirement, provenance, and the repository's by-user scoping
and single revocation. Each must make the WU-AUTH-02 falsifiers fail.

Usage: `python scripts/auth_wu02_mutation_proof.py` with `DATABASE_URL`
pointed at an isolated *_test database migrated to head.
"""

# ruff: noqa: E501 -- mutation sites are exact source fragments and cannot be wrapped

from __future__ import annotations

from _auth_mutation import Mutation, run_mutations

_MIG = "migrations/versions/f1a7c3d9b2e4_auth_authentication_methods.py"
_TYPES = "packages/security/auth_methods.py"
_REPO = "packages/persistence/authentication_method_repository.py"
_TESTS = ("tests/security/test_authentication_methods.py",)

MUTATIONS: list[Mutation] = [
    (
        "M01 database accepts a recovery challenge / OIDC transaction as a method",
        [
            (
                _MIG,
                "\"method_type IN ('LOCAL_PASSWORD', 'GOOGLE_OIDC', 'TEST_PROVIDER')\",",
                "\"method_type <> ''\",",
            )
        ],
    ),
    (
        "M02 status and revocation time may disagree",
        [
            (
                _MIG,
                "\"(status = 'ACTIVE' AND revoked_at IS NULL) \"\n            \"OR (status = 'REVOKED' AND revoked_at IS NOT NULL)\",",
                "\"status IN ('ACTIVE', 'REVOKED')\",",
            )
        ],
    ),
    (
        "M03 two active local password methods per user",
        [(_MIG, "        unique=True,\n", "        unique=False,\n")],
    ),
    (
        "M04 a method may be created already revoked",
        [(_MIG, "            IF NEW.status <> 'ACTIVE' THEN", "            IF FALSE THEN")],
    ),
    (
        "M05 a revoked method may change again",
        [(_MIG, "            IF OLD.status = 'REVOKED' THEN", "            IF FALSE THEN")],
    ),
    (
        "M06 a method may move to another user",
        [(_MIG, "               OR NEW.user_id IS DISTINCT FROM OLD.user_id\n", "")],
    ),
    (
        "M07 a method may change its type",
        [(_MIG, "               OR NEW.method_type IS DISTINCT FROM OLD.method_type\n", "")],
    ),
    (
        "M08 provenance may be rewritten",
        [
            (
                _MIG,
                "               OR NEW.provenance_ref IS DISTINCT FROM OLD.provenance_ref THEN",
                "               THEN",
            )
        ],
    ),
    (
        "M09 creation time may be rewritten",
        [(_MIG, "               OR NEW.created_at IS DISTINCT FROM OLD.created_at\n", "")],
    ),
    (
        "M10 method id may be rewritten",
        [
            (
                _MIG,
                "            IF NEW.id IS DISTINCT FROM OLD.id\n               OR NEW.user_id",
                "            IF NEW.user_id",
            )
        ],
    ),
    (
        "M11 a method without a canonical user",
        [(_MIG, 'sa.ForeignKey("users.id", ondelete="RESTRICT"), ', "")],
    ),
    (
        "M12 empty provenance accepted by the database",
        [(_MIG, "\"provenance_ref <> ''\"", '"provenance_ref IS NOT NULL"')],
    ),
    (
        "M13 RECOVERY_CHALLENGE becomes a method type",
        [
            (
                _TYPES,
                '    TEST_PROVIDER = "TEST_PROVIDER"\n',
                '    TEST_PROVIDER = "TEST_PROVIDER"\n    RECOVERY_CHALLENGE = "RECOVERY_CHALLENGE"\n',
            )
        ],
    ),
    (
        "M14 record allows REVOKED without a revocation time",
        [(_TYPES, "        if revoked != (self.revoked_at is not None):", "        if False:")],
    ),
    (
        "M15 record allows missing provenance",
        [(_TYPES, "        if not self.provenance_ref:", "        if False:")],
    ),
    (
        "M16 record allows naive timestamps",
        [
            (
                _TYPES,
                "    if value is not None and value.tzinfo is None:",
                "    if False:",
            )
        ],
    ),
    (
        "M17 record allows untyped method type",
        [
            (
                _TYPES,
                "        if not isinstance(self.method_type, AuthenticationMethodType):",
                "        if False:",
            )
        ],
    ),
    (
        "M18 methods listed across users",
        [
            (
                _REPO,
                "                .where(authentication_methods_table.c.user_id == user_id.value)\n",
                "",
            )
        ],
    ),
    (
        "M19 revoke reports success for an already revoked or unknown method",
        [(_REPO, "        return result.rowcount == 1", "        return True")],
    ),
    (
        "M20 revoke does not record the revocation",
        [
            (
                _REPO,
                "            .values(status=AuthenticationMethodStatus.REVOKED.value, revoked_at=revoked_at)",
                "            .values(last_authenticated_at=revoked_at)",
            )
        ],
    ),
]


if __name__ == "__main__":
    raise SystemExit(run_mutations(MUTATIONS, _TESTS))
