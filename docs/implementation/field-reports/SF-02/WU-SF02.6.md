# WORK UNIT REPORT
FIELD: SF-02 — NQIRY SYMBIOTIC INTERACTION FIELD (materialization of doc 22)
WORK_UNIT: WU-SF02.6 — Access Field (login, 22 §12.1)

## Mission
Rewrite `app/login/page.tsx` as the Access Field: a dark Field whose single Core is the identity entrance,
bound to `POST /auth/login` (local credential adapter, doc 18) and `GET /auth/me`. SF-01 browser review D-3
("/login has no layout") is closed by this Work Unit.

## MUST BECOME TRUE
- `FieldBackground regime="access"`, `main.access-field`, one `section.access-core[data-testid="access-core"]`
  with `data-core-state` (current / loading / boundary), `h1` "Log in to nquiry".
- Test ids kept: `login-form`, `login-email`, `login-password`, `login-submit`, `login-error`
  (`role="alert"`, `read-boundary` class, `data-outcome`), `login-pending` status while the request is held.
- A denied login is a boundary: announced, the form retained, no success motion, submit still reachable.
- Network loss on login reads as a read boundary ("The canonical system could not be reached. No access
  relation was established."), never as success or as "try again" advice.

## MUST REMAIN IMPOSSIBLE
- External identity providers (22 §45.1): not established in this tree → not shown (Case 1, the architecture's
  own rule "must not display … unless established").
- A workspace topology, a trace beyond the access context, or any relation before the identity read.
- Credentials kept anywhere on the client after submission.

## Proof
Mocked `auth.spec.ts` (6, unchanged): login success/denied/network, logout, redirect. Real stack: every spec logs
in through this surface (five identities in the F03 spec). Browser evidence states 1–6 (desktop, Pixel 7,
reduced motion; login and denied): axe serious/critical 0, overflow 0, keyboard reachable — WU-SF02.8.

## Result
PASS.
