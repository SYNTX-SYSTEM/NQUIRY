# AUTH/CYAN-IDENTITY-01 browser evidence (review runtime `nquiry-cy01-inspect`, 127.0.0.1:13500) — 2026-10-03

Runtime: pinned RED producer `checkpoint-PFC-PCPG-18` + this unit's CYAN tree (files copied into the runner, `next
build` re-run). The producer has no PURPLE `/auth/sessions` or `/auth/methods`; the review proxy (runtime-only, not in
the repository) answers both with live-SHAPED fixtures, labelled `x-nquiry-review-fixture: FIXTURE_NON_PROOF …`: a
LOCAL_PASSWORD session (not current) and a GOOGLE_OIDC session (current) over a linked LOCAL_PASSWORD + GOOGLE_OIDC
method pair with the review-only provider email `review-fixture@cy01.local.test`. `/auth/me` is the runtime's real
verdict for the local review identity; `/auth/providers` is the AUTH/CYAN-02 fixture.

| Device | Authenticated identity | Current authentication | Provider account | Session | scrollX | Organism |
|---|---|---|---|---|---|---|
| desktop 1280×860 | `e239b0e4-026c-4f3a-a22d-b67e48ff2c62` (the review identity's real id) | Google (joined from provider truth) | `review-fixture@cy01.local.test` · "an attribute of the provider method, not your nquiry identity" | `aaaaaaaa-2222-…` current · authenticated | 0 | Workspaces core, orbit, founding form, Log out all visible |
| Pixel 7 | same | same | same | same | 0 | same |

Screenshots (untracked by convention): `screenshots/workspaces-identity-{desktop-1280,pixel-7}.png` (whole field),
`identity-chamber-{desktop-1280,pixel-7}.png` (the chamber alone).

## Second pass (Human Review delta, 2026-10-03)

Review runtime, Google fixture case, after the panel and the nested account object:

| Device | Rail panel (innerText) | Panel box | Header box | Chamber "Current authentication" | scrollX |
|---|---|---|---|---|---|
| desktop 1280×860 | SIGNED IN WITH · Google · GOOGLE ACCOUNT · review-fixture@cy01.local.test · Log out | x 754, w 420, h 73 | w 1280, h 90 | Google → GOOGLE ACCOUNT review-fixture@cy01.local.test "a provider-method attribute · not your nquiry identity" | 0 |
| Pixel 7 | same | x 130, w 270 (beside the mark, not over it; first capture before the CSS repair was x 28, w 372 and covered the mark) | w 412, h 144 | same | 0 |

Mocked lane (`:3301`, routes), local-password current session with a linked Google method: panel SIGNED IN WITH ·
Local password · Log out, no email, no "Google"; chamber Current authentication "Local password", no account object.

Screenshots (untracked by convention): `screenshots/r2-workspaces-identity-{desktop-1280,pixel-7}.png`,
`r2-identity-chamber-*.png`, `r2-identity-panel-*.png` (runtime, Google case); `r2-local-workspaces-*.png`,
`r2-local-identity-panel-*.png` (mocked lane, local case).
