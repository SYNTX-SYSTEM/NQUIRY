# AUTH/CYAN-02 browser evidence (review runtime `nquiry-cy01-inspect`, 127.0.0.1:13500) — 2026-10-03

Runtime: pinned RED producer `checkpoint-PFC-PCPG-18` (`41b4324`) + the CYAN tree of this Work Unit (files copied into
the runner, `next build` re-run). The producer has no PURPLE AUTH routes, so the review proxy (runtime-only,
`cy01-inspect/proxy.mjs`, not in the repository) answers:
- `GET /api/auth/providers` → the exact live body of nquiry.condyn.eu (read-only probe 2026-10-03), header
  `x-nquiry-review-fixture: FIXTURE_NON_PROOF live-shape copy 2026-10-03`;
- `GET /api/auth/oidc/google/start` → a labelled review boundary page (no PURPLE API, no Google client: no login proven).

| Device | Contact | href | inside core | scrollX after sideways scroll | requests on activation |
|---|---|---|---|---|---|
| desktop 1280×860 | "Continue with Google" visible | `http://127.0.0.1:13500/api/auth/oidc/google/start?next=%2F` | yes | 0 | `GET /api/auth/providers`, then `GET …/auth/oidc/google/start?next=%2F` (one GET, no POST, no link route) |
| Pixel 7 | "Continue with Google" visible | same | yes | 0 | same |

Screenshots (untracked by convention): `screenshots/login-desktop-1280.png`, `login-pixel-7.png`,
`start-boundary-desktop-1280.png`, `start-boundary-pixel-7.png`.

Disclosed, pre-existing, not changed by this unit: on Pixel 7 the fixed ambient background (`.field-bg` nebula /
starfield) reports `scrollWidth` 465 > `clientWidth` 412 on `/login` with and without the contact (identical numbers);
the page is not sideways-scrollable (`scrollX` stays 0) and the core lies within the viewport (24–388 px).
