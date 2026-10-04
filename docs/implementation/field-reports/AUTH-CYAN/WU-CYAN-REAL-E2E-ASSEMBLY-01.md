# WORK UNIT REPORT
FIELD: STAGED_SAME_ORIGIN_E2E_ASSEMBLY
WORK_UNIT: CYAN_REAL_E2E_ASSEMBLY_01 — REVIEW_FRONTEND_MOUNT → CANDIDATE_CYAN materialized on the production origin
DATE: 2026-10-03 · PRODUCT BASE: `checkpoint-CYAN-MOUNT-01` → `09f5f0e8eb3c99bf01b147ae0befdd90feee04b2` (tree `82ad5edd…`); docs HEAD `27f344c`
AUTHORITY: `HA-AUTH-CYAN.md` → HA-CYAN-REAL-E2E-ASSEMBLY-01 (2026-10-03).

## Server reconstruction before the delta (records: `browser-evidence/e2e-assembly-01/server-records/STATE_BEFORE.txt`)
| Relation | Observed |
|---|---|
| vhost `/etc/nginx/sites-enabled/nquiry.condyn.eu` (symlink → `sites-available`) | sha256 `2317708ca475fc6f7e6ead3843d553d8b70562ffdf70eefd844714e532ba1cf2`; `/api/` → 127.0.0.1:8400 (rewrite, `proxy_cookie_path /auth /api/auth`); `/` → 127.0.0.1:3400 |
| live web | `nquiry-web-1` 127.0.0.1:3400, image `a27642a3…`, env `NEXT_PUBLIC_API_BASE_URL=https://nquiry.condyn.eu/api` (CY-01 web) |
| PURPLE API | `nquiry-api-1` 127.0.0.1:8400, image `84023ccd…`; `/api/auth/providers` 200 live body; `/api/auth/methods` 401 |
| older cutover candidate (pre-existing, not part of this Field) | `nquiry-cy01-candidate-{web 3401, api 8401, postgres}` up since 2026-09-28 → **3401 not free** → derived loopback port **3402** (free) |
| live `/` and `/login` body hashes | `e4a9860c…`, `d5e9aa20…` |
| `/cy-review/login` | 404 (no producer) |
| health | `nginx -t` ok; `/api/` answers; disk 41 % |

## Delta (deployment field only; the product checkpoint is unchanged)
| Effect | Detail |
|---|---|
| Backup | `/opt/nquiry/_baseline-pre-CYREVIEW-20261003T213429Z/`: `nquiry.condyn.eu.vhost` (byte-exact pre-change file, sha `2317708c…` — a first `cp -a` had copied the symlink and was replaced), `STATE_BEFORE.txt`, `vhost.candidate`, `apply.sh`, `nginx-t.log`, `vhost.diff` (22 added, 0 removed), `STATE_AFTER.txt`, `web.review.Dockerfile.diff`, `ROLLBACK.sh`, `SHA256SUMS.txt` |
| Assembly | `/opt/nquiry/assembly/cyreview-09f5f0e-20261003T213502Z/`: `git archive` of `apps/web` at `09f5f0e`, `SHA256SUMS` (169 files), `DEPLOYMENT_MANIFEST.json`, `web.review.Dockerfile` = live assembly `cy01-b5-20260928T031904Z/infra/local/web.Dockerfile` + `ARG NEXT_PUBLIC_FRONTEND_MOUNT=` / `ENV NEXT_PUBLIC_FRONTEND_MOUNT=$NEXT_PUBLIC_FRONTEND_MOUNT` (3 lines; diff recorded) |
| Candidate runtime | compose project `nquiry-cy-review` (`/opt/nquiry/review/compose.yaml`): ONE service `web`, build args and env `NEXT_PUBLIC_API_BASE_URL=https://nquiry.condyn.eu/api`, `NEXT_PUBLIC_FRONTEND_MOUNT=/cy-review`, `NEXT_TELEMETRY_DISABLED=1`; ports `127.0.0.1:3402:3000`; no env_file, no secrets, no mounts, no api, no postgres, no worker |
| nginx relation | two locations in the TLS server: `location = /cy-review` and `location ^~ /cy-review/` → `http://127.0.0.1:3402` (same proxy headers as `/`; no rewrite, no cookie path rewrite); `/` and `/api/` blocks byte-equal to before; `nginx -t` ok; `systemctl reload nginx`; vhost sha after `14053fb31c5dbc4e3103e1473fe3c148fa8bed6d71110c856516c405a6eb353f` |

## Proof
| Falsifier | Result |
|---|---|
| F01/F12 live `/` and `/login` before and after | 200 / 200; body hashes identical (`e4a9860c…`, `d5e9aa20…`); browser: live `/login` has the login form and no provider contact (CY-01 web) |
| F02 `GET /cy-review/login` | 200; current candidate: login form, brand `src="/cy-review/brand/nquiry-logo.png"`, 24 `/cy-review/_next/static` refs, 0 root `/_next` refs |
| F03 `/cy-review/workspaces` without session | SSR 200; browser: redirected by the candidate to `/cy-review/login` (existing auth boundary) |
| F04/F05 provider discovery and auth contact | browser requests: `GET https://nquiry.condyn.eu/api/auth/me`, `GET https://nquiry.condyn.eu/api/auth/providers` (real production PURPLE body); zero requests to `/cy-review/api/`; start href `https://nquiry.condyn.eu/api/auth/oidc/google/start?next=%2Fcy-review%2F` |
| F06 callback path | `/api/auth/oidc/google/callback` untouched (no vhost or PURPLE change; relations proof) |
| F07/F08 no candidate API / DB | the review project runs exactly one container (web); no new listener besides 3402; the older `nquiry-cy01-candidate` api/postgres pre-exist and are not this candidate's (disclosed) |
| F09/F10 Google and cookies | `.env` sha unchanged (`415a0207…`), PURPLE untouched; the review locations carry no `proxy_cookie_path`; the candidate sets no cookie (`Set-Cookie` count 0 on `/cy-review/login`; browser visit stores no cookie) |
| F11 `/api/` health | `/api/auth/providers` 200 with the live body before and after; `/api/auth/methods` 401; `/api/auth/oidc/google/start` 303 (not followed) |
| F13 assets within the mount | brand asset 200 at `/cy-review/brand/…`; all `_next` refs under `/cy-review/`; `/cy-review/_next/static/x` 404 from the candidate |
| F14 `/cy-review/` does not shadow `/api/` | `/cy-review/api/auth/providers` → 404 from the candidate (never the API); `/api/` block untouched; relations proof "no location nests /api beneath /cy-review" |
| F15 no unnecessary secrets | candidate env = `NEXT_PUBLIC_FRONTEND_MOUNT`, `NEXT_TELEMETRY_DISABLED`, `NEXT_PUBLIC_API_BASE_URL`, `PATH`, `NODE_VERSION`, `YARN_VERSION`; zero mounts |
| F16 removable | `ROLLBACK.sh`: restore the baseline vhost (hash `2317708c…`), `nginx -t`, reload, `compose down` the review project; `/` and `/api/` untouched (relations proof M10/M11) |
| `/cy-review` vs `/cy-review/` | 200 / 308 → `/cy-review` (Next trailing-slash normalization, inside the mount); `/cy-reviewx` 404 from the candidate |
| Relations + mutation proof over the applied vhost and compose text (`server-records/relations-proof.mjs`, output recorded) | **14 / 14 relations hold; 12 / 12 mutations killed** (M1 review → live web · M2 `/api` through the candidate · M3 API base `/cy-review/api` · M4 own API · M5 own DB · M6 live root → candidate · M7 callback beneath `/cy-review` · M8 separate cookie scope · M9 provider secret in the candidate · M10 rollback alters `/` · M11 rollback alters `/api` · M12 candidate on another host/port) |
| Browser proof (headless Chromium from the author's machine against the real origin, no login) | desktop + Pixel 7: boundary redirect, start href, asset path, request targets, no cookie, live root unchanged — `browser-evidence/e2e-assembly-01/` (screenshots untracked) |
| Not performed, by authority | real local login, real Google login, Human Frontend Acceptance |

## Rollback (mechanical)
```bash
bash /opt/nquiry/_baseline-pre-CYREVIEW-20261003T213429Z/ROLLBACK.sh
# = cp baseline vhost → sites-enabled (through the symlink) · nginx -t · systemctl reload nginx · docker compose -p nquiry-cy-review down
# leaves / (3400), /api/ (8400), the database, PURPLE and Google configuration untouched; /cy-review/login returns 404 again
```

## Field reconstruction after the delta
```text
PRODUCTION_ORIGIN https://nquiry.condyn.eu
├─ /            → 127.0.0.1:3400  live CYAN (CY-01 web)        unchanged (hashes equal)
├─ /cy-review/  → 127.0.0.1:3402  current candidate CYAN (09f5f0e, mount /cy-review)   NEW — the previously absent relation
├─ /api/        → 127.0.0.1:8400  production PURPLE            unchanged (block byte-equal)
│   └─ OIDC callback /api/auth/oidc/google/callback           unchanged
└─ HOST SESSION FIELD nquiry_session (host-scoped)             unchanged; consumable by both mounts
```
Only REVIEW_FRONTEND_MOUNT → CANDIDATE_CYAN was materialized.

## Status
CYAN_REAL_E2E_ASSEMBLY_01: CLOSED GREEN (staged). Claim ceiling: CURRENT CYAN CANDIDATE = STAGED ON SAME PRODUCTION
ORIGIN · LIVE CYAN = PRESERVED · PURPLE = PRESERVED · DATABASE = PRESERVED · GOOGLE CONFIGURATION = PRESERVED · REAL
PURPLE E2E = READY BUT NOT YET HUMAN-PROVEN · REAL GOOGLE E2E WITH CURRENT CYAN = READY BUT NOT YET HUMAN-PROVEN ·
AUTH/CYAN-IDENTITY-01 = HUMAN ACCEPTANCE STILL PENDING.

Disclosed: under the review mount a provider-login NON-success returns to PURPLE's root-bound `/login?auth=<word>`
(the live CY-01 login, which ignores it); a success returns to `/cy-review/` (the candidate). The older
`nquiry-cy01-candidate` stack (3401/8401/postgres) pre-exists and awaits a lifecycle decision.

Next Field boundary (not entered): REAL_SAME_ORIGIN_AUTH_E2E.
