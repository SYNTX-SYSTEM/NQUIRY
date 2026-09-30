"""WU-AUTH-04 mutation proof: authenticated session evolution.

Each mutation re-breaks one relation of 24 WU-AUTH-04: a revoked, expired or
method-revoked session not resolving; the session's attribution to its
method; rotation revoking the old token and never extending or re-dating the
session; the own-session scope of revoke and list; conditional, reasoned
revocation; the cookie being cleared after all-session logout; and the
database rules (revoked terminal, immutable identity, no extension, method or
proof required, closed reasons, reason with revocation, same-user method) and
the migration's backfill.

Usage: `python scripts/auth_wu04_mutation_proof.py` with `DATABASE_URL`
pointed at an isolated *_test database migrated to head.
"""

# ruff: noqa: E501 -- mutation sites are exact source fragments and cannot be wrapped

from __future__ import annotations

from _auth_mutation import Mutation, run_mutations

_MIG = "migrations/versions/b3d5f7a9c2e6_auth_session_evolution.py"
_H = "packages/application/auth_handler.py"
_REPO = "packages/persistence/local_auth_repository.py"
_DISPATCH = "packages/application/http_dispatch.py"
_TESTS = (
    "tests/e2e/test_auth_wu04_session_evolution.py",
    "tests/security/test_auth_migrations.py",
)

MUTATIONS: list[Mutation] = [
    (
        "M01 a revoked session resolves",
        [
            (
                _H,
                "    if record.revoked_at is not None:\n        return None",
                "    if False:\n        return None",
            )
        ],
    ),
    (
        "M02 an expired session resolves",
        [
            (
                _H,
                "    if record.expires_at <= now:\n        return None",
                "    if False:\n        return None",
            )
        ],
    ),
    (
        "M03 a session survives the revocation of its method",
        [
            (
                _H,
                "        and record.method_status is not AuthenticationMethodStatus.ACTIVE\n",
                "        and False\n",
            )
        ],
    ),
    (
        "M04 login does not attribute the session to its method",
        [(_H, "        method_id=record.method_id,\n", "        method_id=None,\n")],
    ),
    (
        "M05 rotation leaves the old token valid",
        [
            (
                _H,
                "    if not session_repository.revoke(\n        current.session_token_hash, revoked_at=now, reason=SessionRevocationReason.ROTATED\n    ):",
                "    if False:",
            )
        ],
    ),
    (
        "M06 rotation extends the session",
        [
            (
                _H,
                "        expires_at=current.expires_at,\n        method_id=current.method_id,",
                "        expires_at=now + SESSION_LIFETIME,\n        method_id=current.method_id,",
            )
        ],
    ),
    (
        "M07 rotation re-dates the authentication",
        [(_H, "        issued_at=current.issued_at,", "        issued_at=now,")],
    ),
    (
        "M08 rotation drops the method attribution",
        [
            (
                _H,
                "        method_id=current.method_id,\n        proof_provenance=current.proof_provenance,",
                "        method_id=None,\n        proof_provenance='rotated',",
            )
        ],
    ),
    (
        "M09 logout records the wrong reason",
        [
            (
                _H,
                "hash_session_token(raw_token), revoked_at=now, reason=SessionRevocationReason.LOGOUT",
                "hash_session_token(raw_token), revoked_at=now, reason=SessionRevocationReason.ROTATED",
            )
        ],
    ),
    (
        "M10 a user can revoke another user's session by id",
        [
            (
                _REPO,
                "                local_auth_sessions_table.c.id == session_id,\n                local_auth_sessions_table.c.user_id == user_id.value,\n",
                "                local_auth_sessions_table.c.id == session_id,\n",
            )
        ],
    ),
    (
        "M11 the session list crosses users",
        [
            (
                _REPO,
                "                    local_auth_sessions_table.c.user_id == user_id.value,\n                    local_auth_sessions_table.c.revoked_at.is_(None),\n",
                "                    local_auth_sessions_table.c.revoked_at.is_(None),\n",
            )
        ],
    ),
    (
        "M12 the session list shows revoked sessions",
        [
            (
                _REPO,
                "                    local_auth_sessions_table.c.revoked_at.is_(None),\n                    local_auth_sessions_table.c.expires_at > now,\n",
                "                    local_auth_sessions_table.c.expires_at > now,\n",
            )
        ],
    ),
    (
        "M13 the session list shows expired sessions",
        [(_REPO, "                    local_auth_sessions_table.c.expires_at > now,\n", "")],
    ),
    (
        "M14 revocation is not conditional on the session being unrevoked",
        [
            (
                _REPO,
                "            .where(local_auth_sessions_table.c.revoked_at.is_(None), *conditions)",
                "            .where(*conditions)",
            )
        ],
    ),
    (
        "M15 all-session logout revokes every user's sessions",
        [
            (
                _REPO,
                "        return self._revoke_where(\n            local_auth_sessions_table.c.user_id == user_id.value,\n",
                "        return self._revoke_where(\n",
            )
        ],
    ),
    (
        "M16 method-scope revocation is not scoped to the method",
        [
            (
                _REPO,
                "            local_auth_sessions_table.c.authentication_method_id == method_id.value,\n            revoked_at=revoked_at,",
                "            revoked_at=revoked_at,",
            )
        ],
    ),
    (
        "M17 all-session logout leaves the cookie in the browser",
        [
            (
                _DISPATCH,
                '{"kind": "ok", "revokedSessions": revoked}, clear_cookie=True)',
                '{"kind": "ok", "revokedSessions": revoked}, clear_cookie=False)',
            )
        ],
    ),
    (
        "M18 revoking the current session leaves the cookie in the browser",
        [
            (
                _DISPATCH,
                '    return SessionDispatchResult(200, {"kind": "ok"}, clear_cookie=own)',
                '    return SessionDispatchResult(200, {"kind": "ok"}, clear_cookie=False)',
            )
        ],
    ),
    (
        "M19 database lets a revoked session change",
        [(_MIG, "            IF OLD.revoked_at IS NOT NULL THEN", "            IF FALSE THEN")],
    ),
    (
        "M20 database lets a session move to another user",
        [(_MIG, "               OR NEW.user_id IS DISTINCT FROM OLD.user_id\n", "")],
    ),
    (
        "M21 database lets the token hash be rewritten",
        [
            (
                _MIG,
                "               OR NEW.session_token_hash IS DISTINCT FROM OLD.session_token_hash\n",
                "",
            )
        ],
    ),
    (
        "M22 database lets the attribution be rewritten",
        [
            (
                _MIG,
                "               OR NEW.authentication_method_id IS DISTINCT FROM OLD.authentication_method_id\n               OR NEW.proof_provenance IS DISTINCT FROM OLD.proof_provenance THEN",
                "               THEN",
            )
        ],
    ),
    (
        "M23 database lets a session be extended",
        [
            (
                _MIG,
                "            IF NEW.expires_at > OLD.expires_at THEN",
                "            IF FALSE THEN",
            )
        ],
    ),
    (
        "M24 database accepts a session with neither method nor proof",
        [
            (
                _MIG,
                '        "authentication_method_id IS NOT NULL "\n        "OR (proof_provenance IS NOT NULL AND proof_provenance <> \'\')",',
                '        "TRUE",',
            )
        ],
    ),
    (
        "M25 database accepts an unknown revocation reason",
        [
            (
                _MIG,
                '        f"revoked_reason IS NULL OR revoked_reason IN ({_REASONS})",',
                '        "TRUE",',
            )
        ],
    ),
    (
        "M26 database accepts a revocation without a reason",
        [(_MIG, '        "(revoked_at IS NULL) = (revoked_reason IS NULL)",', '        "TRUE",')],
    ),
    (
        "M27 database accepts another user's method on a session",
        [
            (
                _MIG,
                '        "fk_local_auth_sessions_method_same_user",\n        "local_auth_sessions",\n        "authentication_methods",\n        ["authentication_method_id", "user_id"],\n        ["id", "user_id"],',
                '        "fk_local_auth_sessions_method_same_user",\n        "local_auth_sessions",\n        "authentication_methods",\n        ["authentication_method_id"],\n        ["id"],',
            )
        ],
    ),
    (
        "M28 existing sessions are not attributed by the migration",
        [
            (
                _MIG,
                "        WHERE c.user_id = s.user_id\n",
                "        WHERE c.user_id = s.user_id AND FALSE\n",
            )
        ],
    ),
    (
        "M29 the migration revokes existing sessions",
        [
            (
                _MIG,
                "\"UPDATE local_auth_sessions SET revoked_reason = 'LOGOUT' WHERE revoked_at IS NOT NULL\"",
                "\"UPDATE local_auth_sessions SET revoked_reason = 'LOGOUT', revoked_at = coalesce(revoked_at, now())\"",
            )
        ],
    ),
]


if __name__ == "__main__":
    raise SystemExit(run_mutations(MUTATIONS, _TESTS))
