# ASP-03 — verification of the real production effect and reconstruction of the Authentication / Authorization Field (CYAN view) — 2026-10-06

HUMAN_AUTHORITY_DECISION (verbatim essentials): "ASP-03 production propagation is authorized. Execute the already prepared and
proven ASP-03 propagation. After the real production effect, verify and reconstruct the resulting Authentication and
Authorization Field under canonical SFE. Do not create, infer, expose, or modify production mail-provider credentials."

## 1. Execution — NOT repeated by this session
The decision was recorded upstream as **HD-AUTH-11** and **executed 2026-10-05T23:53Z by the PURPLE engineering session**
(`origin/auth-identity` `4ae1bc0` "closure #4 — ASP-03 live"; `evidence/asp03_production_state.txt`; host baseline
`/opt/nquiry/_baseline-pre-ASP03-20261005T235257Z`). This session found the effect already applied before acting and did not
run `deploy-asp03.sh` a second time: its guards require the predecessor compose contexts and the recorded `.env` shape, both
already replaced; a second run would have aborted at guard 0 and, had it not, would have been a double production effect.
No mail-provider credential was created, inferred, read, exposed or modified; environment variables were observed by NAME
only.

## 2. Real production effect, verified read-only (2026-10-05T23:59Z–2026-10-06T00:05Z)
| Relation | Observed |
|---|---|
| compose contexts | api `./assembly/auth-d03d5ce-20261005T235257Z` (source `accb976`, code `d03d5ce`), web `./assembly/cyanroot-7d214e6-20261005T235257Z` (AUTH/CYAN-RECOVERY-01) |
| containers | `nquiry-api-1`, `nquiry-web-1` recreated 23:53Z (images `8c0a7040…`, `81e62c7d…`), running; postgres unchanged (up 10 days); `nquiry-cy-review-web-1` untouched (12 h) |
| migration head | `e3a5c7d9f1b4` before and after (no migration) |
| `.env` | 20 non-empty lines (19 + `NQUIRY_PUBLIC_WEB_BASE_URL`); `NQUIRY_RECOVERY_POLICY=VERIFIED_EMAIL_SELF_SERVICE`; **no `NQUIRY_EMAIL_DELIVERY_MODE`, no `NQUIRY_SMTP_*` (by name)**; the api container's `NQUIRY_*` names carry no mail variable either |
| vhost | sha `14053fb3…` unchanged |
| `GET /api/auth/contacts` | `200 {kind: ok, recovery: UNAVAILABLE, emailVerification: UNAVAILABLE}` (was 404) |
| `POST /api/auth/recovery/start` (unknown address, same-origin) | `503 {kind: unavailable, reasonCode: RECOVERY_NOT_AVAILABLE}` |
| `GET /api/auth/providers` | unchanged `[google · PRODUCTION_PROVIDER]` |
| pages `/`, `/login`, `/recover`, `/recover/reset`, `/account/verify-email` | 200 each; `/cy-review/login` 200 (still `7f42d8e`) |
| headless product probe, desktop 1280 + Pixel 7, no login (`browser-evidence/asp-03/screenshots/`) | `/login`: provider contact present, **no "Forgot your password?" contact** (recovery UNAVAILABLE → not offered); `/recover`: boundary "Password recovery is not offered by this deployment. Ask the operator who created your account.", the Send control **disabled**, "Back to the login"; `/recover/reset`: "This page needs the link from the reset message"; requests only `GET /api/auth/providers` and `GET /api/auth/contacts`; zero cookies |
| preservation BEFORE/AFTER (host record) | only the two recreated containers differ |
| rollback | `_baseline-pre-ASP03-20261005T235257Z/ROLLBACK-asp03.sh` (predecessor compose + `.env`, anchor images; schema untouched) |

Observation for the Human Visual Authority (not a defect claim): while recovery is UNAVAILABLE, `/recover` keeps its
explanatory sentence ("If it is a verified address … a reset link is on its way.") above the boundary; the control is
disabled and nothing can be sent, but the page states a promise and its boundary at once. The login page is coherent (no
contact offered).

## 3. The Authentication / Authorization Field after ASP-03 (reconstructed)
| Layer | State |
|---|---|
| PURPLE | `origin/auth-identity` `4ae1bc0` — closure #4; HD-AUTH-10 (recovery = VERIFIED_EMAIL_SELF_SERVICE, part of the product), HD-AUTH-11 (ASP-03 executed). Closure regression #4 on `accb976`: 2538 / 2. Remaining: **one EXTERNAL DEPENDENCY, not a Human Authority decision** — the host MTA's SASL credential and sender identity (`NQUIRY_EMAIL_DELIVERY_MODE=smtp`, `NQUIRY_SMTP_*`, operator-created). Until they exist the deployment answers recovery = UNAVAILABLE and says so. |
| Production api | `d03d5ce` (+ docs `accb976`), head `e3a5c7d9f1b4`; routes live: identity, providers, methods, sessions, link/unlink, revoke, logout-all, password/change, lockout 429, membership revoke/role, **contacts**, recovery start/complete (503 while unavailable), e-mail verification (401 without session; unavailable) |
| Production web | CYAN `7d214e6` (ACCOUNT-01 + ACCOUNT-02 + RECOVERY-01). **Without RAIL-01 and PCPG-06** (the rail overlap remains live). Human Frontend Acceptance recorded only up to ACCOUNT-01 (HD-AUTH-09); ACCOUNT-02 and RECOVERY-01 surfaces live without one. |
| CYAN lineage | `origin/frontend-symbiotic` `9f950c4` (`checkpoint-CYAN-INTEGRATION-02b`) **contains `7d214e6`** → the production root is an ancestor of the CYAN line; no divergence. `auth-cyan-reconstruction` moved to `572e2fd` (docs only: "mocked preservation set 194 passed, cold-compile flake disclosed") — the next, trivial propagation. |
| Staged `/cy-review/` | `7f42d8e` — superseded twice over; rebuild from `9f950c4` prepared (`FIELD_RECONSTRUCTION_2026-10-06.md` §3), refused to this session, human-run |
| Local review runtime :13500 | `9f950c4` + RED `checkpoint-PFC-PCPG-18` |
| Laws observed live | UNAVAILABLE != DENIED (503 `unavailable`, not a denial); CONTACT OFFERED ONLY ON AVAILABLE (login shows none); DELIVERY != VERIFICATION; the schema and vhost untouched; no credential anywhere in records or events |

## 4. Boundary — HUMAN_AUTHORITY / EXTERNAL
1. **External dependency (operator, not this Field):** the production MTA's SASL credential and sender identity, placed in the production `.env` by the operator; then ASP-04-style api restart to activate recovery. Nothing here may be created or inferred by a session.
2. **Review-mount rebuild from `9f950c4`** (prepared, human-run) and **Human Frontend Acceptance** of ACCOUNT-02, RECOVERY-01 (its UNAVAILABLE states now; its AVAILABLE flow only after 1), RAIL-01 and the lineage on `/cy-review/`; PCPG-06 on :13500.
3. **Root cutover of the CYAN lineage** (`9f950c4`, or its successor after integrating `572e2fd`) after acceptance — publishes RAIL-01 and PCPG-06; a separate authorized Field.
4. Housekeeping: delete the erroneous tag `checkpoint-CYAN-INTEGRATION-02`; `auth-cyan-reconstruction` push/retirement; `nquiry-cy01-candidate` stack.
