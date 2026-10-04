# NQUIRY_LIVE_MATERIALIZATION — Report (2026-09-28)

**Authority:** NQUIRY PRODUCTION MATERIALIZATION FIELD (human operator, 2026-09-28): the exact pair RED
`checkpoint-PFC-B5` @ `7d3f74e4685b821cc948f45e413c1e0c207259d4` + CYAN `field-CY-01` @
`54f8b4f91b12f7c05c10eb98d6281bbe1ba19859`. **Untracked; not committed.**

## 1. Final status

**READY_FOR_HUMAN_LIVE_REVIEW** (2026-09-28T19:05Z). The account-creation boundary of §14 is closed by the
PRODUCTION_ACCOUNT_CREATION Field (§23–§29): HD-28, WU-PFC-AC1 / AC1.1, deployed to live as an api-only delta; the four
review identities exist through it, the review field through the product API, and the automatic live run passed 21/21.
Not PUBLISHED_FIELD; Human Live Review is the next and separate authority.

Earlier status (kept for the record): **LIVE_MATERIALIZED_WITH_DISCLOSED_REVIEW_BOUNDARY** (2026-09-28T03:44Z). The exact pair is live on
`https://nquiry.condyn.eu`; all automatic live proof is complete; server preservation is proved (unrelated delta none);
the live review field could not be created because the pinned producer has no production-safe identity provisioning
path (§14 below) — recorded as the next First Broken Relation and Case 3 boundary, not bypassed. Not PUBLISHED_FIELD;
the RED producer's ceiling (checkpointed, not reviewed) is unchanged; DEPLOYED ≠ PUBLISHED_FIELD.

Earlier the same day: the cutover, the live identity provisioning and the record transfer had been refused by the
execution environment's permission gate; the cutover was then explicitly authorized by the human operator
(PRODUCTION MATERIALIZATION AUTHORITY) and executed as prepared. The provisioning and the transfer stayed refused/excluded.

## 2. Production Field definition (written before any write)

- **FIELD** NQUIRY_LIVE_MATERIALIZATION. **PURPOSE** materialize the pair on nquiry.condyn.eu. **SCOPE** `/opt/nquiry`,
  compose project `nquiry` (+ the NQUIRY-owned candidate project), the `nquiry` database, the NQUIRY vhost. **NOT IN
  SCOPE** every other application, container, volume, vhost, certificate, unit, user, cron, package on `mail.condyn.eu`.
- **AUTHORITATIVE CURRENT STATE** (read 03:17–03:18Z): clone `/opt/nquiry/repo` detached at `field-SF-06` with the A8
  production `web.Dockerfile` delta; containers `nquiry-postgres-1` (postgres:17), `nquiry-api-1` (127.0.0.1:8400),
  `nquiry-web-1` (127.0.0.1:3400), started 2026-09-25 23:31Z, no restarts; volume `nquiry_nquiry_pgdata`; head
  `f6b2c4d9a318`, 36 tables, 10 MB, 2 users, 1 Workspace, 0 Sessions, 2 audit events; roles ai_gateway_writer,
  api_reader, audit_reader, governed_commit_writer, migration_owner, nquiry, projection_writer, recovery_reader,
  security_event_writer, test_principal; vhost `/etc/nginx/sites-available/nquiry.condyn.eu` (sha256 `7e2f7e73…`) →
  8400 (`/api/`), 3400 (`/`); cert to 2026-12-24; compose sha256 `6a34bd92…`; `.env` sha256 `d7f20377…` (keys only:
  POSTGRES_USER/PASSWORD/DB, DATABASE_URL, NQUIRY_COOKIE_SECURE, NEXT_PUBLIC_API_BASE_URL); no worker; health api/web/public 200.
- **TARGET STATE** the pair above, assembled deterministically, migration head `e8c2a5f1b7d4`, same topology (no
  worker: at B5 no HTTP route reads the F08 projection read models; no nginx change: routes unchanged).
- **PRODUCERS** the two tag targets only (verified remotely and by signature). **CONSUMERS** api, web, DB, nginx route, browser.
- **MATERIAL RELATIONS** compose build contexts → assembly; DB → +7 additive migrations; api/web containers → recreated
  from new images; nginx/TLS/postgres container/volume/.env → untouched.
- **ALLOWED DELTA** `/opt/nquiry/compose.yaml` (contexts `./repo` → `./assembly/<id>`), the 7 migrations, the two
  images and containers. **BOUNDARIES** §4 of the field verbatim (no prune, no unrelated mutation, no firewall/SSH/cert
  change, no broad restart). **AUTHORITY** this field only; MockProvider on PRODUCTION is *not* authorized by it (HD-19/HA-20).
- **MUST BECOME TRUE** begin-analysis route answers 401 not 404; bundle carries the CY-01 projection; head `e8c2a5f1b7d4`;
  existing rows preserved; health 200; deployed identities = manifest. **MUST REMAIN TRUE** every unrelated
  application's process/service/port/volume/vhost/TLS identity; the two real accounts and the real Workspace; NQUIRY's
  nginx route; the predecessor images and clone. **MUST REMAIN IMPOSSIBLE** §4 list; a mock result shown as proof;
  FIXTURE_NON_PROOF disappearing; the client inventing authority. **FALSIFIERS** §12 of the field.
- **RECOVERABLE PREDECESSOR** established (§8 below). **PROOF CONDITIONS** §13–§17 of the field. **RECONSTRUCTION PATH** §21.

## 3. Source pair verification
`refs/tags/checkpoint-PFC-B5` = tag `fd3d5600…` → `7d3f74e4685b821cc948f45e413c1e0c207259d4`, tree
`bc77cc8bb6414e6104aabdd5bd2fb1874f63f750`, signed, good signature. `refs/tags/field-CY-01` = tag `cf9372c7…` →
`54f8b4f91b12f7c05c10eb98d6281bbe1ba19859`, tree `f980bde0b07e9d54e82fa460c1bf81ae55844b8a`, signed, good signature.
**HD-27 is persisted on RED** (`origin/pfc-integration` `6921bf5` "record Human Authority decision HD-27"): the CYAN
note calling it open is stale; nothing duplicated.

## 4. Assembly
Overlap since base `c9d86ba`: only five `docs/implementation/frontend/*.md`, byte-identical; RED changed nothing under
`apps/web`, `package*.json`, `infra/`, `pyproject`; CYAN changed nothing under `packages/`, `apps/api`, `apps/worker`,
`migrations`, `pyproject`. No semantic collision. Assembly `cy01-b5-20260928T031904Z` = `git archive` of B5
(pyproject, README, packages, apps/api, apps/worker, migrations, scripts minus mutation-proof scripts, infra/local) +
`git archive` of CY-01 (apps/web, package.json, package-lock.json) + the A8 production `infra/local/web.Dockerfile` from
the live clone (sha `4d8a8e76…`); 372 files, `SHA256SUMS` digest `73a38194…`; `DEPLOYMENT_MANIFEST.json`; on the server
`/opt/nquiry/assembly/cy01-b5-20260928T031904Z/`, every file hash verified there; copies in the baseline dir. Local
copies: `evidence-2026-09-28/DEPLOYMENT_MANIFEST.json`, `SHA256SUMS`.

## 5–8. Predecessor, baseline, backup
`/opt/nquiry/_baseline-pre-CY01-20260928T031733Z/` (0700): `preservation-before.txt` (215 lines: docker, compose,
volumes, networks, sockets, systemd, timers, pm2, nginx hashes + server_names, certs, cron, resources, vhost HEAD
baseline, ownership), `live-predecessor-record.txt` (commit, delta, head, container ids `1e263c0d…` web /
`86feb7f7…` api / `22530f6b…` postgres, image digests `aa04ea59…` web / `5867d1ca…` api / `d74eeac9…` postgres, nginx/
compose/.env hashes, DB identity `nquiry oid=16384 PostgreSQL 17.11`, size, roles, counts, volume, health),
`compose.yaml.pre`, `nginx.nquiry.condyn.eu.pre`, `web.Dockerfile.pre`, `DEPLOYMENT_MANIFEST.json`, `SHA256SUMS`,
`db-backup-record.txt`, **backup** `nquiry-db-pre-CY01-20260928T031930Z.dump` (pg_dump -Fc, 196 KB, sha256
`4ee5ea84b3531c11fc61989620f63d0c00d07ab41e134ae759734d7988bdf588`, head `f6b2c4d9a318`, 36 TOC data entries, 0600) +
`nquiry-db-roles-globals-….sql` (no passwords). The 2026-09-25 baselines are preserved. Pointer:
`/opt/nquiry/_baseline-pre-CY01-CURRENT`.

## 9. Migration gate
Verified live head `f6b2c4d9a318`, target `e8c2a5f1b7d4`; 7 revisions, all additive, all with downgrade, no data
rewrite, no unrelated object; roles granted to all exist. Full table: `evidence-2026-09-28/MIGRATION_ANALYSIS.md`.
Applied on the candidate copy only.

## 10. Candidate isolation (done)
Project `nquiry-cy01-candidate`, loopback 8401/3401, own volume restored from the backup, migrations LIVE PASS (36 → 43
tables, rows preserved), api/web healthy in 6 s, begin-analysis **401**, bundle markers present (analysis-chamber 3,
"Begin analysis" 4, FIXTURE_NON_PROOF 9), API base inlined. Still running for your inspection (ssh tunnel to
127.0.0.1:3401 / :8401). Details: `evidence-2026-09-28/CANDIDATE_AND_PRESERVATION_RESULTS.md`, scripts `candidate-stage-1.sh`, `-2.sh`.

## 11–13. Cutover — EXECUTED (2026-09-28T03:43Z, authorized)
Guards passed (compose sha, .env sha, assembly checksums, manifest identities, live head, backup present). Delta exactly:
`.env` + `NQUIRY_ENVIRONMENT=PRODUCTION` (HD-LIVE-1; predecessor copy 0600 in the baseline dir); `compose.yaml` build
contexts → `./assembly/cy01-b5-20260928T031904Z` + api env passthrough (sha after `3bcad9eb…`, `compose.yaml.pre` kept);
images from the assembly; migrations f6b2c4d9a318 → e8c2a5f1b7d4 via one-off api container with the assembly
bind-mounted read-only (STATIC PASS 32 revisions, LIVE PASS, 43 tables); `up -d --no-build api web`. nginx: **not
touched** (routes valid; hash unchanged). The script ended on its own `set -e` at the first health poll (curl 56 while
the api was starting); the probes and the after-record were completed by hand with the same commands. No falsifier
fired; no rollback. Live proof table: `evidence-2026-09-28/LIVE_CUTOVER_RESULTS.md`; server record
`live-after-record.txt`. Containers: api `0c82d0123be2880ebb5145a5b546fe81a734ef92886abfaf255d6af43c5df312`
(image `ccb65d79…`), web `2d92fd3448f08331a169951be5b1cf28077f55fdd0bd6ed27ed6383d3f7afe78` (image `a27642a3…`),
postgres unchanged. Public: healthz ok, login 200, begin-analysis **401**, bundle markers present, env PRODUCTION,
provider unset, real data unchanged (2 users, 1 Workspace, 2 audit events).

## 14–16. Live review identities and product test — BLOCKED (disclosed boundary)
Reconstruction at `checkpoint-PFC-B5`: identity routes are `/auth/login`, `/auth/logout`, `/auth/me` only; no
registration, invitation, self-service or admin provisioning route or command exists (doc 18: "No self-service
registration/password reset UI or route"; GAP-14-001 production identity provider open; doc 24 OIDC is architecture,
HA-09). The only provisioning script (`scripts/dev_provision_local_identity.py`) is gated by the dev flag you excluded;
`scripts/seed_local_demo.py` is a dev seed. **No production-safe path exists; none was bypassed.** Therefore no review
users, Workspace, Challenge or Sessions exist on live, and the authenticated live product test (§16) did not run.
Unauthenticated live proof ran (login field on desktop/Pixel 7/reduced motion, invalid-login boundary, unauthenticated
direct URL → login, axe 0, no horizontal overflow on desktop). **Next First Broken Relation:** HUMAN IDENTITY →
PRODUCTION ACCOUNT (a legitimate production account-creation relation; HA-09 / GAP-14-001 / doc 24). Case 3 for Human
Authority: how production accounts — including review accounts — may come into being.

**Production analysis semantics (HD-LIVE-1):** a real Session reaching ANALYSIS shows "authorized, not yet executed"
with the producer's reason; ACCEPTED / MOCK / NON_PROOF is impossible on live (no provider, PRODUCTION identity).

## 17. Preservation proof
Three snapshots: BEFORE (03:17:33Z), AFTER the candidate, AFTER the cutover. Diff BEFORE → AFTER-CUTOVER (volatile
lines excluded): only NQUIRY's own api/web container ids, images and docker-proxy pids on 127.0.0.1:3400/8400, the
candidate project's resources (loopback 3401/8401), and one transient postfix `smtpd` per-connection child (master
unchanged). Unrelated containers, compose project `backend`, systemd, pm2, sockets, vhost hashes, certificates,
ownership: identical. **Expected unrelated delta NONE: met.** Real accounts and Workspace preserved (counts unchanged).
Pre-existing and unchanged: `certbot.service` failed; `bot.bl1zzard.eu`, `dev.syntx-system.com` unreachable.

## 18. Test plans
A. `docs/implementation/live-review/NQUIRY_LIVE_TEST_PLAN.md` — untracked, sanitized, updated to the deployed
production semantics (HD-LIVE-1) and the open review-identity boundary; identifiers stay `<…>`.
B. **not created** (by rule: only if legitimate production review accounts exist): none do; `/tmp/nquiry-live-review/`
does not exist.

## 19. Rollback identity (not needed; recorded and executable)
Predecessor: `field-SF-06` @ `d3d9bd6…` + F03, images `aa04ea59…` (web) / `5867d1ca…` (api), head `f6b2c4d9a318`,
backup `nquiry-db-pre-CY01-20260928T031930Z.dump` (sha `4ee5ea84…`). To revert: `cp _baseline-pre-CY01-…/compose.yaml.pre
/opt/nquiry/compose.yaml && docker compose -p nquiry --env-file /opt/nquiry/.env -f /opt/nquiry/compose.yaml up -d --build api web`
(predecessor images rebuild from `/opt/nquiry/repo` at `field-SF-06`; cache present), DB either left at `e8c2a5f1b7d4`
(F03 code ignores the additive tables) or `alembic downgrade f6b2c4d9a318` through the one-off container, or restore of
the dump (`db-backup-record.txt`). nginx needs nothing.

## 20. Uncommitted / untracked files (this machine)
`docs/implementation/live-review/HUMAN_DECISIONS_LIVE.md`, `evidence-2026-09-28/LIVE_CUTOVER_RESULTS.md`, `cutover-cy01.sh.EXECUTED`, `public-proof/*.png` (added 2026-09-28T03:5xZ).
`docs/implementation/live-review/` (this report, the test plan, `evidence-2026-09-28/`: DEPLOYMENT_MANIFEST.json,
SHA256SUMS, MIGRATION_ANALYSIS.md, CANDIDATE_AND_PRESERVATION_RESULTS.md, CLEANUP_MANIFEST.md, migration-chain.txt,
candidate-stage-1.sh, candidate-stage-2.sh, snapshot-preservation.sh, BASELINE_DIR.txt). Scratch (outside the repo):
`…/scratchpad/live/assembly/cy01-b5-20260928T031904Z(.tar.gz)`. On the server: `/opt/nquiry/assembly/…`, `/opt/nquiry/candidate/`,
`/opt/nquiry/_baseline-pre-CY01-…/`, `/opt/nquiry/candidate-stage*.sh|.log`, `/opt/nquiry/snapshot-preservation.sh`. Git: clean.

## 21. Remaining Case 3 / execution boundaries
1. ~~Production cutover~~ — authorized and executed. 2. **Production account creation** (review identities): no
   legitimate path at B5; Case 3 (HA-09 / GAP-14-001 / doc 24). 3. Copying server records to this machine — refused;
   the records stay in the baseline dir on the server. 4. **HA-20 — RESOLVED** by HD-LIVE-1 (2026-09-28, `HUMAN_DECISIONS_LIVE.md`): live is PRODUCTION, MockProvider stays
   unavailable, the derived relation stays "authorized, not yet executed" with the producer's reason; a production AI
   provider is a separate Field. 5. Pre-existing `certbot.service` failed unit on the host (unrelated; observation only).

## 22. Exact next human action (superseded by §29)
Decide how production accounts for the live review may come into being (the next First Broken Relation, HA-09 /
GAP-14-001 / doc 24) — or perform the live review with the two real accounts yourself, outside my hands. Optionally
authorize the candidate teardown (`evidence-2026-09-28/CLEANUP_MANIFEST.md`). Live is materialized and stable; the
candidate stays on loopback until you say otherwise.

Next authority after successful execution: HUMAN LIVE REVIEW.


---

# PRODUCTION ACCOUNT CREATION FIELD (2026-09-28, human operator: full SFE execution authorization + HD-28)

## 23. Field and Human Authority
- **First Broken Relation** (§14): PRODUCTION AUTHORITY → legitimate account-creation relation → persisted identity →
  credential issuance → audit provenance. At B5 only `/auth/login`, `/auth/logout` and `/auth/me` existed. Doc 24's
  account creation policy is HUMAN_AUTHORITY_REQUIRED, and 04 §17 allows no implicit administrator.
- **Case 3 asked and decided: HD-28 / NQ-DEC-056 (RED ledger, commit `bb1931a`).**
  - Option A: an explicit host-operator command; the operator is recorded as `otti@condyn.eu`.
  - The credential is set only at creation; no password reset.
  - No in-app admin role, Workspace-owner creation, public or self-service registration.
  - No automatic membership, role, governance or Session authority.
- **Reconstruction also found a defect:** the dev-only provisioning guard accepted the live DB host name `postgres` and
  ignored the environment. It was repaired in AC1 (refusal for PRODUCTION / STAGING).

## 24. Work Unit and checkpoints (RED, `pfc-integration`)
- **`checkpoint-PFC-AC1`** → `1a94a586df3400fab08c444d650ab33032894339` (signed tag `d430c4ef…`). WU-PFC-AC1:
  - `application.identity_provisioning` and `persistence.identity_repository`;
  - the command `python -m nquiry_api.operator.create_identity --email --name --operator` (password from stdin only);
  - one transaction: `users` + a PBKDF2 credential + a SecurityEvent IDENTITY_CREATED (HOST_OPERATOR, TB-17, declared
    environment; 11 §47);
  - the dev guard's environment refusal.
  - Proof: falsifiers 24 (RED 23/24); mutation 13/13 killed; live 2005/2, no-DB 921.
  - The first full run found an HD-6 violation (an own savepoint in an application module). It was repaired at the root
    by using the command's single transaction; the allow-list was not widened.
- **`checkpoint-PFC-AC1.1`** → `e91961e4a66ab21d9edf45d74bb43b8fbd324737` (tree `af6da710…`, signed tag `4bbba5e1…`).
  - The production candidate proved that `nquiry_api.operator` was missing from the api image: pyproject's explicit
    package list, which a local test cannot see.
  - Added a packaging-completeness falsifier (RED: `['nquiry_api.operator']`) and the entry.
  - Live 2007/2, no-DB 923.
- **Deployed-path delta vs B5:** the three new modules, the dev guard, the dev script and `pyproject.toml`. No route, no
  migration, no web change.

## 25. Production candidate proof (server, `nquiry-ac1-candidate`, loopback 8402, PRODUCTION, restored pre-AC1 dump)
From `evidence-2026-09-28/AC1_CANDIDATE_RESULTS.log`:
- **Create:** exit 0, JSON without the password, `createdBy` otti@condyn.eu, environment PRODUCTION.
- **Refusals:**
  - a case-variant duplicate: IDENTITY_ALREADY_EXISTS;
  - `--password` on argv: rejected (exit 2);
  - an empty `NQUIRY_ENVIRONMENT`: ENVIRONMENT_NOT_DECLARED;
  - no operator: OPERATOR_REQUIRED;
  - dev provisioning under PRODUCTION: REFUSED; the dev script is not in the image.
- **Login:** a wrong password gives 401; login 200; `me` returns the new id; `/workspaces` returns `[]`; after logout
  `me` gives 401. The registration paths give 404.
- **Records:** a `pbkdf2_sha256$` credential; 0 memberships, bindings and participations; the SecurityEvent reads
  HOST_OPERATOR / TB-17 / PRODUCTION.
- **Secrets:** the password appears 0 times in the api logs, the command outputs and a full DB dump.
- **Preservation:** pre-existing identity and credential digests are equal to live.
- The candidate was torn down afterwards: it held a production data copy.

## 26. Deployment (recoverable; api only)
- **Baseline** `/opt/nquiry/_baseline-pre-AC1-20260928T181736Z` (0700):
  - `compose.yaml.pre` (sha `3bcad9eb…`) and `.env.pre`;
  - `live-predecessor-record.txt`;
  - content digests of users, credentials, workspaces, memberships, roles, bindings, challenges and audit;
  - `preservation-BEFORE.txt`;
  - the DB dump `nquiry-db-pre-AC1-20260928T181736Z.dump` (sha256 `374bc906264c42d0f709207ca0f4aba1d5890aac417524b73264cdb8caed1e81`,
    43 TABLE DATA).
- **Assembly** `ac11-cy01-20260928T182206Z`:
  - a copy of `cy01-b5-20260928T031904Z` with the RED paths from AC1.1;
  - its diff against the deployed assembly is exactly the AC1.1 delta;
  - 377 files, SHA256SUMS digest `b50b528f…`;
  - `evidence-2026-09-28/DEPLOYMENT_MANIFEST_AC1.json`.
- **Cutover** 2026-09-28T18:50Z (`evidence-2026-09-28/cutover-ac1.sh.EXECUTED`, `AC1_CUTOVER.log`):
  - The guards passed: compose and `.env` hashes, assembly checksums, manifest identities, head `e8c2a5f1b7d4`,
    api container = predecessor, backup present.
  - The rollback anchor `nquiry-api:pre-ac1` → image `ccb65d79…` was created.
  - The only compose change is the **api build context** (+ a header line; sha after `d3319a83…`).
  - `build api`, then `up -d --no-deps api`.
- **Result:**
  - api container `521dac0a4420dc8c3abe6f153f5906cb828d276bc1114d7923d006dfe2d05dfa`, image `a81b3f47…`;
  - **web** `2d92fd34…` and **postgres** `22530f6b…` unchanged;
  - `.env`, nginx (sha `7e2f7e73…`), TLS, schema and data untouched;
  - `NQUIRY_ENVIRONMENT=PRODUCTION`, `NQUIRY_AI_PROVIDER` unset.
- **Live probes:**
  - health: api 200, public 200, web 200;
  - a bad login and an unauthenticated begin-analysis both give 401. The cutover log shows 400 for these two: that was
    a quoting artefact of the script's inline JSON, re-probed correctly;
  - the registration paths give 404;
  - the operator command is present, and the refusal smoke gives OPERATOR_REQUIRED with nothing written;
  - the real-data digests are unchanged.
- **Preservation BEFORE → AFTER-CUTOVER:** only NQUIRY's api container, image and docker-proxy pid on 127.0.0.1:8400,
  plus Docker disk usage. One volatile unrelated line: the systemd-networkd DHCP socket fd number. **Unrelated delta: none.**
- **Rollback:**
  - `cp $B/compose.yaml.pre /opt/nquiry/compose.yaml && docker tag nquiry-api:pre-ac1 nquiry-api:latest && docker compose -p nquiry --env-file /opt/nquiry/.env -f /opt/nquiry/compose.yaml up -d --no-build --no-deps api`;
  - the DB needs nothing (no schema change). Identities created after the cutover would remain; they carry no authority.

## 27. Identity creation provenance and the review field
**Identities** (host-operator command over SSH; each password piped to stdin, never in argv, output or file outside `/tmp/nquiry-live-review`):

| Username | User id | SecurityEvent IDENTITY_CREATED (HOST_OPERATOR otti@condyn.eu, TB-17, PRODUCTION) |
|---|---|---|
| `owner@livereview.nquiry.condyn.eu` | `91b04e93-2e75-492f-a3e8-f3400bb0e5bf` | `42089917-e1d2-49c8-94d2-7e21e0f26622` |
| `maya@livereview.nquiry.condyn.eu` | `06b8043d-a83d-4e66-8404-aeb2b6c656fe` | `340c6949-414f-4c29-aff2-04bb8c98fc96` |
| `ravi@livereview.nquiry.condyn.eu` | `99197c0b-b2b8-4efc-87ee-b68bb779453f` | `9a2b085c-afb3-48b3-af56-139282e66601` |
| `elena@livereview.nquiry.condyn.eu` | `2162e130-b7b1-4413-b520-94afc4f586ab` | `90f3fec5-dd08-45f4-bbe8-d863ef12fc28` |

**Review field** (product API only, each step by the acting user):
- the Owner founds Workspace `8311d170-2f30-461f-9085-7a0b9e0e34ac` and adds Maya (Facilitator), Ravi and Elena (Contributors);
- Maya creates Challenge `b9bc6c4c-d419-4091-a223-7f491c6b8a48`;
- the Owner grants Maya SESSION_CONTROL_RIGHT at the CHALLENGE and at each SESSION;
- Maya opens the Sessions and runs setup → challenge capture → Burst → admits Ravi, Elena and herself → question generation;
- the participants capture their questions; Maya completes the Burst.

| Session | Id | State | Proof mode | Frozen |
|---|---|---|---|---|
| A | `95f027cb-c279-5a22-81b6-039f83a6366a` | QUESTION_CAPTURE | GOVERNED | 3 |
| B | `d1827699-2cdc-56e2-be3e-e9834d54686c` | QUESTION_CAPTURE | FIXTURE_NON_PROOF | 2 |
| C | `493dd951-b26d-5605-84d4-de72336325b1` | ANALYSIS — run NOT_EXECUTED / AI_PROVIDER_UNAVAILABLE; view PENDING / AUTHORIZATION_NOT_EXECUTED ("authorized, not yet executed") | GOVERNED | 3 |
| D (automation) | `5c257b05-1be6-5a9e-aa9e-9276395bc570` | ANALYSIS (pressed by the automatic run) | GOVERNED | 3 |

**Preservation:** pre-existing identities, credentials, Workspaces, memberships, roles, bindings and audit are
byte-identical to the pre-AC1 digests. No password appears in the api logs, a full DB dump, the journal (2 h), any
worktree or the job scratch space.

## 28. Automatic live run (`evidence-2026-09-28/live-review-auto/`, Chromium 1280/1600, Pixel 7, axe wcag2a/aa, reduced motion)
**21/21 PASS** after one corrected assertion (the first run is recorded in the results file as a FAIL; see its row).

| Result | Check | Detail |
|---|---|---|
| PASS | unauthenticated direct Session URL lands on /login |  |
| PASS | wrong password: boundary, no session, no alert storm | re-verified: exactly one application alert element, p#login-error 'Incorrect email or password.'; the second getByRole('alert') match was the Next.js route anno |
| PASS | Ravi logs in; exactly the review Workspace is listed | 1 Workspace (8311d170-2f30-461f-9085-7a0b9e0e34ac) |
| PASS | Session A as Ravi: QUESTION_CAPTURE, 3 frozen, no Begin analysis, MISSING_AUTHORITY, not begun, GOVERNED | direct URL |
| PASS | Session A as Ravi after refresh: identical | reload |
| PASS | Ravi logout and relogin: identical | relogin |
| PASS | API: Ravi's begin-analysis on A is denied, A unchanged | 403 denied DENIED_NO_MATCHING_BINDING |
| PASS | Session C as Ravi: ANALYSIS, derived field visible (frozen-set audience), authorized not yet executed, no affordance |  |
| PASS | axe Session A (QUESTION_CAPTURE) as Ravi | A/QUESTION_CAPTURE: 0 violation types, 0 serious/critical |
| PASS | desktop 1280 no horizontal scroll | scrollWidth 1280 <= 1280 |
| PASS | desktop 1600 no horizontal scroll | scrollWidth 1600 <= 1600 |
| PASS | Session A as Maya: Begin analysis available (not pressed; kept for the Human Live Review) |  |
| PASS | Session D as Maya: press Begin analysis -> committed, canonical re-read, ANALYSIS, authorized not yet executed, no proof, no mock | canonical: ANALYSIS, PENDING / AUTHORIZATION_NOT_EXECUTED, version 5 -> 6 |
| PASS | Session D reload: the same canonical state re-read |  |
| PASS | API: Maya repeating begin-analysis with the old version is stale/blocked, never a second transition | 409 stale |
| PASS | axe Session D (ANALYSIS) as Maya | D/ANALYSIS: 0 violation types, 0 serious/critical |
| PASS | Session B as Maya: FIXTURE_NON_PROOF at the core and in the proof chamber; Begin analysis available (not pressed) |  |
| PASS | Owner: Workspace listed; Session A shows no Begin analysis (no Session control) |  |
| PASS | Pixel 7: Session A readable, no horizontal scroll | scrollWidth 412 <= 412 |
| PASS | Pixel 7: login page no horizontal scroll | scrollWidth 465 <= 465 |
| PASS | reduced motion: no running animations on Session C; meaning intact | 0 finite / 0 infinite running animations |

Human visual acceptance remains separate. One CYAN observation for it: at 1280 px the centred wordmark overlaps the
breadcrumb's current-state chip (`live-review-auto/02-ravi-session-A-desktop.png`). It was not changed: CYAN is out of scope.

## 29. Plans, cleanup, remaining boundaries, next human action
- **Sanitized plan:** `docs/implementation/live-review/NQUIRY_LIVE_TEST_PLAN.md` (untracked, completed, no passwords).
- **Secret plan:** `/tmp/nquiry-live-review/NQUIRY_LIVE_TEST_PLAN_WITH_CREDENTIALS.md` (0600, in a 0700 directory,
  never committed, staged or pushed).
- **Cleanup manifest:** `evidence-2026-09-28/CLEANUP_MANIFEST.md`.
- **Rollback identity:** §26 (api delta) and §19 (pair).
- **Remaining boundaries:**
  - a production AI provider (a separate Field; HD-LIVE-1);
  - password reset, deactivation and identity cleanup (HD-28 §2);
  - HA-23 (Investigation completion);
  - HA-09 runtime DB-principal isolation;
  - CY-02 (not started);
  - the CY-01 candidate project still running on loopback (teardown not authorized);
  - the host's pre-existing failed `certbot.service` (unrelated).
- **Status:** READY_FOR_HUMAN_LIVE_REVIEW. Not PUBLISHED_FIELD.
- **Human Live Review starting URL:** https://nquiry.condyn.eu/login (first user: Ravi,
  `ravi@livereview.nquiry.condyn.eu`).
