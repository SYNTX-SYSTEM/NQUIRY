# CYAN_REAL_E2E_ASSEMBLY_01 evidence — 2026-10-03

`server-records/`: `STATE_BEFORE.txt`, `STATE_AFTER.txt` (same-origin HTTP proof), `vhost.diff` (22 added lines, the two
review locations), `nginx-t.log`, `web.review.Dockerfile.diff`, `ROLLBACK.sh`, `DEPLOYMENT_MANIFEST.json`,
`SHA256SUMS.txt` (server baseline directory), `vhost.candidate` (the applied vhost text; certificate paths only, no
secrets), `compose.applied.yaml` (web only, no secrets), `relations-proof.mjs` + `RELATIONS_PROOF_OUTPUT.txt`
(14/14 relations, 12/12 mutations killed).

Browser proof from the author's machine against `https://nquiry.condyn.eu`, no login, desktop and Pixel 7:
`/cy-review/workspaces` → `/cy-review/login`; start href `https://nquiry.condyn.eu/api/auth/oidc/google/start?next=%2Fcy-review%2F`;
brand `/cy-review/brand/nquiry-logo.png`; API requests only `GET /api/auth/me`, `GET /api/auth/providers`; zero
`/cy-review/api/` requests; zero off-mount page requests; no cookie stored; live `/login` still the CY-01 web (login
form, no provider contact). Screenshots (untracked): `screenshots/origin-cy-review-login-{desktop-1280,pixel-7}.png`.
