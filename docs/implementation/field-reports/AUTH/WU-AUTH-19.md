# WORK UNIT REPORT

FIELD: AUTH — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)
WORK_UNIT: WU-AUTH-19 — credential rotation by the authenticated identity (24 §9.2 "credential rotation", §17.1)

| Item | Value |
|---|---|
| ARCHITECTURE_SOURCE | 24 §9.2 ("If password login is an official product method, add … credential rotation …" — official since HD-AUTH-09), §17.1 (credential reset = replace after proof), §31 (audit), §21.7 (unsafe request = anti-CSRF boundary) |
| PREDECESSOR | `dea52bf` (Field closure #2) |
| AUTHORITY | the human mandate of 2026-10-05: complete the operational identity and access lifecycle including the password lifecycle |
| PROOF_RADIUS | WU-19 falsifiers (9) → route-table suites (isolation sweep, WU-16, WU-15, WU-17 db principal, WU-14 csrf): 234 passed |
| HUMAN_AUTHORITY_STATE | none crossed: rotation needs the live session AND the current password; recovery (HA-AUTH-02) untouched |

## FIRST_BROKEN_RELATION_BEFORE
LOCAL_PASSWORD was accepted as an official production method (HD-AUTH-09) but
its owner could not rotate it: the only credential replacement was the
recovery effect (production DENIED). 24 §9.2 names rotation as an obligation
of an official password method.

## DELTA
| File | Change |
|---|---|
| `packages/persistence/local_auth_repository.py` | `get_by_user_id`, `revoke_all_for_user_except(keep_session_id)` |
| `packages/application/credential_rotation.py` (new) | `rotate_password`: live session → own credential → current password verified → new password validated (recovery rules; must differ) → hash replaced → every OTHER session revoked `CREDENTIAL_RESET` → `PASSWORD_CHANGED`; a wrong current password → `PASSWORD_CHANGE_FAILED` (class only), session kept |
| `packages/application/http_credential.py`, `apps/api/src/nquiry_api/http/credential.py`, `main.py` | `POST /auth/password/change` `{currentPassword, newPassword}` → `200 {kind: ok, sessionsRevoked}` / `401 NO_SESSION` / `403 CURRENT_PASSWORD_INVALID \| NO_LOCAL_CREDENTIAL` / `400 PASSWORD_INVALID` |
| `packages/security/auth_audit.py` | vocabulary + `PASSWORD_CHANGED`, `PASSWORD_CHANGE_FAILED` |
| `tests/e2e/test_pfc_f09_2_isolation_sweep.py` | route registered (own-identity, cross-workspace exempt) |
| `tests/e2e/test_auth_wu19_credential_rotation.py` (new) | 9 falsifiers |

## FALSIFIERS
rotation replaces the hash, keeps the proving session, ends the other with `CREDENTIAL_RESET`, leaves the method row byte-equal, old password refused / new accepted, event with ids only and no secret · wrong / empty current password → 403, audited, nothing changed, session kept · invalid or unchanged new password (5 shapes) → 400 before any effect · no session → 401, no event · a provider-bootstrapped identity → `NO_LOCAL_CREDENTIAL`, session kept.

## CLAIM_CEILING
CREDENTIAL ROTATION = MATERIALIZED for the identity that holds the credential and a live session. Not in scope (disclosed): setting a FIRST local password on a provider-only identity (a method addition, 24 §9; not required by the accepted scope); recovery without the credential (HA-AUTH-02). Frontend contact: the CYAN Access security chamber (AUTH/CYAN-ACCOUNT-02, same mandate).
