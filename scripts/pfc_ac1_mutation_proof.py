"""WU-PFC-AC1 mutation proof: production account creation under HD-28 is guarded.

Each mutation re-breaks one relation of HD-28: the dev-only path refusing a
production environment, the declared (never guessed or normalized)
environment, duplicate refusal and email normalization, the credential hash,
the password never appearing in any output or record, the operator and TB-17
attribution, the password rules, the required operator, and the refusal of a
password on the command line. Each must make the AC1 falsifiers (or the dev
provisioning suite) fail. Sources are restored byte-for-byte after every
mutation (sha256 verified).

Usage: `python scripts/pfc_ac1_mutation_proof.py` with `DATABASE_URL` pointed
at an isolated *_test database migrated to head, and the `.venv` active.
"""

# ruff: noqa: E501 -- mutation sites are exact source fragments and cannot be wrapped

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_DEV = "packages/test_support/dev_identity.py"
_APP = "packages/application/identity_provisioning.py"
_CLI = "apps/api/src/nquiry_api/operator/create_identity.py"
_TESTS = (
    "tests/e2e/test_pfc_ac1_production_account_creation.py",
    "tests/security/test_dev_identity_provisioning.py",
)

Edit = tuple[str, str, str]
MUTATIONS: list[tuple[str, list[Edit]]] = [
    (
        "M01 dev provisioning allowed on PRODUCTION",
        [(_DEV, "    if environment not in DEV_ENVIRONMENTS:", "    if False:")],
    ),
    (
        "M02 environment normalized (spoofable)",
        [(_APP, "        return Environment(raw)", "        return Environment(raw.upper())")],
    ),
    (
        "M03 undeclared environment defaults to PRODUCTION",
        [
            (
                _APP,
                '        raise IdentityCreationRefused("ENVIRONMENT_NOT_DECLARED")',
                "        return Environment.PRODUCTION",
            )
        ],
    ),
    (
        "M04 duplicate identity not refused",
        [(_APP, "    if identities.email_exists(normalized):", "    if False:")],
    ),
    (
        "M05 email not normalized",
        [(_APP, "    normalized = email.strip().lower()", "    normalized = email.strip()")],
    ),
    (
        "M06 plaintext credential persisted",
        [
            (
                _APP,
                "        user_id=user_id, password_hash=hash_password(password), now=now",
                "        user_id=user_id, password_hash=password, now=now",
            )
        ],
    ),
    (
        "M07 password leaks into the security record",
        [
            (
                _APP,
                '                    "workspaceAuthority": "NONE",',
                '                    "workspaceAuthority": "NONE",\n                    "p": password,',
            )
        ],
    ),
    (
        "M08 operator not attributed",
        [
            (
                _APP,
                "            actor_id=operator.operator_id.strip(),",
                '            actor_id="host",',
            )
        ],
    ),
    (
        "M09 wrong trust boundary",
        [
            (
                _APP,
                "            trust_boundary=TrustBoundary.TB_17_ADMINISTRATIVE_TOOLING,",
                "            trust_boundary=TrustBoundary.TB_04_APPLICATION_SERVICE,",
            )
        ],
    ),
    (
        "M10 surrounding whitespace accepted",
        [(_APP, "    if password != password.strip():", "    if False:")],
    ),
    (
        "M11 minimum length not enforced",
        [(_APP, "    if len(password) < PASSWORD_MIN_CHARS:", "    if False:")],
    ),
    (
        "M12 operator not required",
        [(_APP, "    if not operator.operator_id.strip():", "    if False:")],
    ),
    (
        "M13 password accepted on the command line",
        [
            (
                _CLI,
                '    parser.add_argument("--name", required=True)',
                '    parser.add_argument("--name", required=True)\n    parser.add_argument("--password", default="")',
            )
        ],
    ),
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run_tests() -> int:
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider", *_TESTS],
        cwd=_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode


def main() -> int:
    files = {rel for _, edits in MUTATIONS for rel, _, _ in edits}
    before = {rel: _sha(_ROOT / rel) for rel in files}
    failures: list[str] = []
    for name, edits in MUTATIONS:
        originals = {rel: (_ROOT / rel).read_text() for rel, _, _ in edits}
        texts = dict(originals)
        unique = True
        for rel, old, new in edits:
            if texts[rel].count(old) != 1:
                unique = False
                break
            texts[rel] = texts[rel].replace(old, new)
        if not unique:
            print(f"{name}: MUTATION_SITE_NOT_UNIQUE", flush=True)
            failures.append(name)
            continue
        try:
            for rel, text in texts.items():
                (_ROOT / rel).write_text(text)
            code = _run_tests()
        finally:
            for rel, text in originals.items():
                (_ROOT / rel).write_text(text)
        killed = code != 0
        print(f"{name}: {'KILLED' if killed else 'SURVIVED'}", flush=True)
        if not killed:
            failures.append(name)
    restored = all(_sha(_ROOT / rel) == digest for rel, digest in before.items())
    print(f"{len(MUTATIONS) - len(failures)}/{len(MUTATIONS)} killed; sources restored: {restored}")
    return 0 if not failures and restored else 1


if __name__ == "__main__":
    raise SystemExit(main())
