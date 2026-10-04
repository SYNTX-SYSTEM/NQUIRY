# Live cutover results (2026-09-28T03:43Z; server records in /opt/nquiry/_baseline-pre-CY01-20260928T031733Z/)

## Cutover (script `cutover-cy01.sh`, guards passed: compose sha 6a34bd92…, .env sha d7f20377…, assembly checksums, manifest identities, live head f6b2c4d9a318, backup present)
- `.env`: predecessor copy kept (0600, inside the baseline dir); `NQUIRY_ENVIRONMENT=PRODUCTION` appended (HD-LIVE-1); `NQUIRY_AI_PROVIDER` unset.
- `compose.yaml`: build contexts `./repo` → `./assembly/cy01-b5-20260928T031904Z`; api env passthrough `NQUIRY_ENVIRONMENT`; header naming the pair. `compose config` OK. sha256 after `3bcad9eb…`; predecessor `compose.yaml.pre` kept.
- Images built from the assembly (cache from the candidate).
- Migrations f6b2c4d9a318 → e8c2a5f1b7d4 through a one-off api container with the assembly bind-mounted read-only: `MIGRATION_STATIC_CHECK::PASS (32 revision(s), single head ['e8c2a5f1b7d4'])`, `MIGRATION_LIVE_CHECK::PASS`; 43 tables.
- `up -d --no-build api web`: both started 03:43:39Z; postgres container untouched (started 2026-09-25T23:31:15Z, same id 22530f6b…).
- The script's own `set -e` ended it at the first health poll (curl exit 56 while the api was starting); steps 5 (probes, after-record) were completed immediately afterwards by hand with the same commands. No falsifier fired; no rollback.

## Live proof (03:44Z)
| Check | Result |
|---|---|
| API health (loopback + public) | `{"status":"ok","phase":"0"}` |
| Web health | `/login` 200 (loopback + public) |
| Public login field | renders on desktop 1280, Pixel 7, reduced motion; invalid login → boundary "Incorrect email or password." on `/login`; unauthenticated direct Session URL → `/login` |
| DB connectivity + migration head | head `e8c2a5f1b7d4`, 43 tables |
| begin-analysis route | public `POST …/transitions/begin-analysis` → **401** (was 404) |
| CY-01 markers in the deployed bundle | `analysis-chamber` 3 chunks, `FIXTURE_NON_PROOF` 9, API base `https://nquiry.condyn.eu/api` inlined |
| Runtime identity | api env `NQUIRY_ENVIRONMENT=PRODUCTION`, provider unset |
| Existing real users / Workspace | 2 users, 1 Workspace, 0 Sessions, 2 audit_events — unchanged before/after |
| Deployed identities | after-record: assembly `cy01-b5-20260928T031904Z`; RED `checkpoint-PFC-B5 7d3f74e4685b821cc948f45e413c1e0c207259d4`; CYAN `field-CY-01 54f8b4f91b12f7c05c10eb98d6281bbe1ba19859` |
| Containers after | web `2d92fd34…` (image `a27642a3…`), api `0c82d012…` (image `ccb65d79…`), postgres `22530f6b…` (unchanged) |
| nginx | untouched, sha256 `7e2f7e73…` before and after |
| axe (login field) | 0 serious/critical on desktop, Pixel 7, reduced motion; reduced motion → 0 running animations |
| Observation (pre-existing, not CY-01) | Pixel 7 `/login`: 53 px horizontal overflow from the fixed background layers (`.field-bg`, `.nebula`, `.starfield`); identical on the SF-06 reference runtime :13400, the CY-01 runtime :13500 and live |

## Preservation after cutover (BEFORE 03:17:33Z vs AFTER-CUTOVER; volatile lines excluded)
NQUIRY-owned only: api/web container ids and images (recreated), docker-proxy pids for 127.0.0.1:3400/8400, the
candidate project's resources; one transient postfix `smtpd` per-connection child (master pid 2252746 unchanged).
Unrelated containers, compose project `backend`, systemd units, pm2, sockets, vhost hashes, certificates, ownership:
identical. Expected unrelated delta NONE: **met**.
