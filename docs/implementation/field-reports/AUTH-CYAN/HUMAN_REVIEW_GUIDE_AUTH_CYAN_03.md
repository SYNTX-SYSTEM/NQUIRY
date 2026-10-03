# HUMAN FRONTEND REVIEW — AUTH/CYAN-03 · provider-login result boundary on the Access Field

**Runtime:** `http://127.0.0.1:13500` (container `nquiry-cy01-inspect-runner`, loopback only). No login needed; do not
enter production credentials. The `?auth=` word normally arrives from the API's callback redirect; this runtime has no
PURPLE routes, so you open the URLs directly.

## What you are judging
Whether a known provider-login non-success is presented as an honest boundary inside the existing Access Field,
visually in the core's own boundary vocabulary, without competing with the local login or the Google contact, and
whether every unknown value presents nothing.

## Steps
1. `http://127.0.0.1:13500/login?auth=cancelled` — expected: the usual core (Email, Password, **Log in**, "or",
   **Continue with Google**) and below the contact one boundary line "The provider login was cancelled. No access
   relation was established."; the core edge in its boundary state; nothing else new; no modal, no panel.
2. Repeat for `?auth=provider_unavailable`, `?auth=provider_error`, `?auth=failed`, `?auth=unavailable` — one sentence
   each (see `WU-AUTH-CYAN-03.md`), always ending "No access relation was established."
3. `?auth=success`, `?auth=ok`, `?auth=FAILED`, `?auth=`, `?auth=failed&auth=cancelled`, plain `/login` — expected:
   no boundary line at all, the core in its current (calm) state.
4. On `?auth=failed`, enter a wrong email/password and submit: the provider boundary disappears while the request is
   pending and the local verdict ("Incorrect email or password.") appears instead; never two boundaries.
5. Narrow to a phone width (or Pixel 7 emulation): the boundary stays inside the core; no sideways scrolling.

## Falsifiers for the eye
- Any wording implying success, sign-in, authority, role, denial of authority, account creation or linking → FAIL.
- A boundary shown for an unknown or malformed value → FAIL.
- The boundary above or competing with the local form / the Google contact, or outside the core → FAIL.
- A modal, panel, new route or changed URL → FAIL.

## Record your decision
Reply with `HUMAN_FRONTEND_ACCEPTANCE = ACCEPTED | REJECTED (+ what you saw)`. Acceptance moves the unit to
FIELD_GREEN_WITH_DISCLOSED_CEILINGS (WU scope); not REVIEWED_FIELD, not PUBLISHED_FIELD; no deployment authority.
