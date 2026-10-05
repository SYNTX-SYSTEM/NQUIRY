# CYAN-INTEGRATION-01 evidence (local review runtime `nquiry-cy01-inspect`, 127.0.0.1:13500, integrated tree `7f42d8e`) — 2026-10-05

Facilitator review identity (RED local login; the proxy's AUTH reads are FIXTURE_NON_PROOF; `/auth/identity` is not served, so the identity words are the fail-closed ones).

| Device | Workspaces | Session |
|---|---|---|
| desktop 1280 | rail identity panel ("Authenticated · id…", "Signed in with Local password", Log out); chambers "Found a Workspace", "Identity and access", "Access security" | governance panel present, 5 stations, current station 459–562 left of the mark |
| Pixel 7 | same chambers stacked | governance panel present, 5 stations, `scrollX` 0 after a sideways scroll attempt |

Rail measurements (same runtime): 1024 current 331–434 (103 px), 1280 459–562 (103 px), 1440 521–642 (121 px); fits left of the mark, no overlap — RAIL-01 holds on the integrated stylesheet.

Screenshots (untracked by convention): `screenshots/workspaces-{desktop-1280,pixel-7}.png`, `session-{desktop-1280,pixel-7}.png`.

## Staged mount `https://nquiry.condyn.eu/cy-review/` (assembly `cyreview-7f42d8e-20261005T104910Z`, 2026-10-05T11:29Z)
Headless, no login, desktop 1280 + Pixel 7: `/cy-review/workspaces` → `/cy-review/login`; provider contact
`https://nquiry.condyn.eu/api/auth/oidc/google/start?next=%2Fcy-review%2F`; brand asset `/cy-review/brand/nquiry-logo.png`;
requests only `GET /api/auth/me` and `GET /api/auth/providers`; zero `/cy-review/api/`, zero off-mount, zero cookies.
Served stylesheet carries the RAIL-01, governance-panel, boundary-card and account-security rules. Live `/` and `/login`
hashes unchanged before/after. Screenshots (untracked): `screenshots/origin-cy-review-login-{desktop-1280,pixel-7}.png`.
