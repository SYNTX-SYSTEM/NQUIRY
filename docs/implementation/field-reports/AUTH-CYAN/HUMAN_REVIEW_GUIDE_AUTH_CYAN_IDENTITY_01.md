# HUMAN FRONTEND REVIEW — AUTH/CYAN-IDENTITY-01 · the authentication relation in "Identity and access"

**Runtime:** `http://127.0.0.1:13500` (container `nquiry-cy01-inspect-runner`, loopback only). Log in with the LOCAL
review identity of this runtime (`facilitator@cy01.local.test`; the local review password of CY-01, not written here;
never a production credential). The runtime's `/auth/sessions` and `/auth/methods` are labelled FIXTURE_NON_PROOF
answers (a Google-produced current session over a linked local + Google method pair with a review-only provider
email); `/auth/me` is the runtime's real verdict.

## What you are judging
Whether the human's current authentication relation reads as part of the organism (a proof chamber, not a SaaS
profile dashboard), whether "current authentication" is understandable, whether the provider email cannot be mistaken
for the nquiry identity, and whether nothing implies authority.

## Steps
1. Log in and arrive on `/workspaces`. The Workspaces core, the orbit and "Found a Workspace" are unchanged and
   primary. The "Identity and access" chamber (right column on desktop, below on a phone) now reads, in this order:
   AUTHENTICATED IDENTITY (the id token with copy) · CURRENT AUTHENTICATION "Google" · PROVIDER ACCOUNT
   `review-fixture@cy01.local.test` with the words "an attribute of the provider method, not your nquiry identity" ·
   SESSION "current · authenticated".
2. Confirm nothing else appeared: no avatar, no name, no menu, no settings, no account-security panel, no role or
   authority word in that chamber. The rail is unchanged (trace · nquiry mark · Log out).
3. Narrow to a phone width (or Pixel 7): the chamber stacks under the organism; no sideways scrolling; lines wrap
   inside the chamber.
4. Log out and log in again: the same chamber (the runtime's fixture is static; on the live system a local login
   would read "Local password" and show no provider account — proven in the mocked lane, not visible here).
5. Optional fail-closed check: block `/api/auth/methods` in devtools and reload — "Current authentication" and
   "Provider account" disappear, the identity and the session line stay.

## Falsifiers for the eye
- The chamber reads like a profile page, settings page or account dashboard → FAIL.
- The provider email stands where the identity stands, or is not marked as a provider attribute → FAIL.
- Any wording of role, ownership, authority, permission or control inside the chamber → FAIL.
- A human name, initials or avatar → FAIL (no producer provides one).
- The organism (core, orbit, founding form) no longer primary → FAIL.

## Record your decision
Reply with `HUMAN_FRONTEND_ACCEPTANCE = ACCEPTED | REJECTED (+ what you saw)`. Acceptance moves the unit to
FIELD_GREEN_WITH_DISCLOSED_CEILINGS (WU scope); not REVIEWED_FIELD, not PUBLISHED_FIELD; no deployment authority.
