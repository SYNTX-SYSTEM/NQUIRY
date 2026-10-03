# AUTH/CYAN-03 browser evidence (review runtime `nquiry-cy01-inspect`, 127.0.0.1:13500) — 2026-10-03

Runtime: pinned RED producer `checkpoint-PFC-PCPG-18` + this unit's CYAN tree (files copied into the runner,
`next build` re-run). The review proxy still serves the labelled FIXTURE_NON_PROOF providers body (AUTH/CYAN-02). The
`?auth=` word is supplied by opening the URL directly: no callback produces it in this runtime.

| Device | URL | Boundary | Core state | Inside core | scrollX after sideways scroll | Google contact / local login |
|---|---|---|---|---|---|---|
| desktop 1280×860 | `/login?auth=cancelled` | "The provider login was cancelled. No access relation was established." | boundary | yes | 0 | visible / visible |
| desktop | `/login?auth=unavailable` | "Signing in with this provider is not available for this account. No access relation was established." | boundary | yes | 0 | visible / visible |
| desktop | `/login?auth=success` (unknown) | none | current | — | 0 | visible / visible |
| desktop | `/login?auth=failed&auth=cancelled` (conflicting) | none | current | — | 0 | visible / visible |
| Pixel 7 | same four | same | same | yes / — | 0 | visible / visible |

Screenshots (untracked by convention): `screenshots/login-cancelled-{desktop-1280,pixel-7}.png`,
`login-unknown-{desktop-1280,pixel-7}.png`.
