# Candidate proof and preservation results (2026-09-28, server-side records in /opt/nquiry/_baseline-pre-CY01-20260928T031733Z/)

## Candidate isolation (compose project `nquiry-cy01-candidate`, loopback only, own volume restored from the pre-CY01 dump)
- Guard: project name `nquiry-cy01-candidate`, all published ports on 127.0.0.1 (8401 api, 3401 web).
- Images built from the assembly: `nquiry-cy01-candidate-api` (328 MB, 03:20:40Z), `nquiry-cy01-candidate-web` (1.87 GB, 03:22:54Z).
- Restore of `nquiry-db-pre-CY01-20260928T031930Z.dump` into the candidate: head `f6b2c4d9a318`, 2 users, 1 workspace.
- Migrations (one-off api container, assembly bind-mounted read-only, `scripts/verify_migrations.py`): STATIC PASS (32 revisions, head `e8c2a5f1b7d4`), LIVE PASS; 43 tables; rows preserved.
- Boot: api 200 `{"status":"ok","phase":"0"}`, web `/login` 200 after 6 s.
- Contract: `POST …/transitions/begin-analysis` → **401** (route present; live F03 answers 404); `begin-setup` 401; `position` 401 unauthenticated.
- Bundle: `analysis-chamber` in 3 chunks, "Begin analysis" in 4, `FIXTURE_NON_PROOF` in 9; API base inlined `https://nquiry.condyn.eu/api`.
- Left running for inspection (see CLEANUP_MANIFEST.md).

## Server-wide preservation (BEFORE 03:17:33Z, AFTER after the candidate; volatile load/memory lines excluded)
Delta = NQUIRY-owned candidate resources only: 3 containers (`nquiry-cy01-candidate-{postgres,api,web}-1`), 1 volume
(`nquiry-cy01-candidate_candidate_pgdata`), 1 network (`nquiry-cy01-candidate_default`), compose project row, loopback
sockets 127.0.0.1:3401 / 127.0.0.1:8401. One transient line: a postfix `smtpd` worker child on port 25 present BEFORE
and absent AFTER (per-connection child of the unchanged `master`, pid 2252746). Every unrelated container, compose
project (`backend` /var/www/bot/ProTrainer1), systemd unit, pm2 process, socket, vhost hash, certificate and file
ownership: identical. Pre-existing and unchanged: `certbot.service` failed (before and after), vhosts `bot.bl1zzard.eu`
and `dev.syntx-system.com` unreachable (before and after). Live NQUIRY containers unchanged (ids and start times of
2026-09-25). Live vhost HEAD baseline: 200 for admin.condyn.eu, admin/analyzer/entry.syntx-system.com, condyn.eu,
www.condyn.eu, nquiry.condyn.eu; 404 audit.syntx-system.com (before and after).

## Candidate re-probe under HD-LIVE-1 / HA-20 (candidate project only; live untouched — nquiry-api-1 still started 2026-09-25T23:31:27Z)
Candidate api recreated with `NQUIRY_ENVIRONMENT=PRODUCTION`, `NQUIRY_AI_PROVIDER` unset: healthz 200
`{"status":"ok","phase":"0"}`, begin-analysis route 401, no refusal in the api log. The pinned producer boots as
PRODUCTION without any AI provider; its run outcome for a committed BEGIN_ANALYSIS is NOT_EXECUTED / AI_PROVIDER_UNAVAILABLE.
