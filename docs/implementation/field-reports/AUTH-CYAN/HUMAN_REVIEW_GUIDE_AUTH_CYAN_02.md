# HUMAN FRONTEND REVIEW — AUTH/CYAN-02 · provider contact on the Access Field

**Runtime:** `http://127.0.0.1:13500/login` (container `nquiry-cy01-inspect-runner`, loopback only). No login is needed
for this review; do not enter production credentials anywhere. The page is the existing CYAN Access Field with this
unit's tree. `GET /api/auth/providers` is answered by the review proxy with the exact live production body
(FIXTURE_NON_PROOF, labelled by a response header); the start route is a labelled review boundary.

## What you are judging
Whether the external-provider contact is part of the existing Access Field (visually secondary to the local login,
same core, same vocabulary) and whether its presence is honest: it is a configured contact, not a proven login.

## Steps
1. Open `/login` on desktop (≈1280 wide). Expect: the Access core with Email, Password, **Log in**; below the form an
   "or" rule and one outlined action **Continue with Google**, inside the core, full width of the core's content.
   Nothing else is new. The local form is unchanged and still first.
2. Narrow the window to a phone width (or use the Pixel 7 emulation). Expect the same order; the action stays inside
   the core; no sideways scrolling.
3. Hover **Log in**: the field gathers as before (SF-05). Hover **Continue with Google**: a quiet secondary hover
   only; the field does not gather around it (it is not the primary action).
4. Activate **Continue with Google**. Expect a plain navigation (GET) to `/api/auth/oidc/google/start?next=%2F`, which
   this runtime answers with a labelled "Review boundary" page (no PURPLE API here). Use "Back to the Access Field".
   On the live system this route would redirect to Google; that is not exercised and not claimed.
5. Enter a wrong email/password and submit. Expect the known boundary ("Incorrect email or password."), the core in its
   boundary state, and the provider contact still present and unchanged.
6. Optional fail-closed check (devtools → Network → block `/api/auth/providers`, reload): the contact disappears and
   the local login is untouched. Any malformed or denied answer behaves the same (browser lane `cy06-provider`).

## Falsifiers for the eye
- A second login surface, a panel, a dashboard, a new route, an "account", "link", "sign up" or "create" word → FAIL.
- The contact shown while the providers answer is missing, malformed or empty → FAIL.
- The contact competing with **Log in** (filled, larger, first) → FAIL (visual law: Access Field primary).
- Any success motion or wording implying the Google login works → FAIL (GOOGLE_AVAILABLE != GOOGLE_LOGIN_PROVEN).

## Record your decision
Reply with `HUMAN_FRONTEND_ACCEPTANCE = ACCEPTED | REJECTED (+ what you saw)`. Acceptance moves the unit to
FIELD_GREEN_WITH_DISCLOSED_CEILINGS (WU scope); it does not make it REVIEWED_FIELD or PUBLISHED_FIELD and authorizes
no deployment.
