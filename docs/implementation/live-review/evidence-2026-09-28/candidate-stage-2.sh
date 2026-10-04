#!/usr/bin/env bash
# Candidate stage 2 (isolated project nquiry-cy01-candidate only): migrations on the candidate copy through a one-off
# api container with the assembly bind-mounted (the mechanism of the original deployment), then api + web on loopback.
set -uo pipefail
ID=cy01-b5-20260928T031904Z; A=/opt/nquiry/assembly/$ID; C=/opt/nquiry/candidate
CO="docker compose -p nquiry-cy01-candidate --env-file $C/.env -f $C/compose.yaml"
U=$(grep ^POSTGRES_USER= $C/.env | cut -d= -f2); D=$(grep ^POSTGRES_DB= $C/.env | cut -d= -f2)
echo "== images =="; docker images --format "{{.Repository}}:{{.Tag}} {{.CreatedAt}} {{.Size}}" | grep candidate
echo "== migrations (bind-mounted assembly, cwd /src) =="
$CO run --rm --no-deps -T -v $A:/src:ro -w /src -e PYTHONPATH=/src/packages -e DATABASE_URL="$(grep ^DATABASE_URL= $C/.env | cut -d= -f2-)" api python scripts/verify_migrations.py 2>&1 | tail -3
echo "candidate head after: $(docker exec nquiry-cy01-candidate-postgres-1 psql -U $U -d $D -tAc 'select version_num from alembic_version') tables: $(docker exec nquiry-cy01-candidate-postgres-1 psql -U $U -d $D -tAc "select count(*) from information_schema.tables where table_schema='public'") counts: $(docker exec nquiry-cy01-candidate-postgres-1 psql -U $U -d $D -tAc "select (select count(*) from users)||' users '||(select count(*) from workspaces)||' workspaces '||(select count(*) from audit_events)||' audit_events'")"
echo "== candidate api + web up =="; $CO up -d api web 2>&1 | tail -2
for i in $(seq 1 60); do a=$(curl -s -m 3 -o /dev/null -w '%{http_code}' http://127.0.0.1:8401/healthz); w=$(curl -s -m 3 -o /dev/null -w '%{http_code}' http://127.0.0.1:3401/login); [ "$a$w" = 200200 ] && break; sleep 3; done
echo "candidate health api=$a web=$w after $((i*3))s"
echo "healthz body: $(curl -s -m 3 http://127.0.0.1:8401/healthz)"
echo "begin-analysis route (expect 401, not 404): $(curl -s -m 5 -o /dev/null -w '%{http_code}' -X POST -H 'content-type: application/json' -d '{"expectedVersion":1}' http://127.0.0.1:8401/workspaces/00000000-0000-4000-8000-000000000000/sessions/00000000-0000-4000-8000-000000000000/transitions/begin-analysis)"
echo "begin-setup route (control, 401): $(curl -s -m 5 -o /dev/null -w '%{http_code}' -X POST -H 'content-type: application/json' -d '{"expectedVersion":1}' http://127.0.0.1:8401/workspaces/00000000-0000-4000-8000-000000000000/sessions/00000000-0000-4000-8000-000000000000/transitions/begin-setup)"
echo "position route (401 unauthenticated): $(curl -s -m 5 -o /dev/null -w '%{http_code}' http://127.0.0.1:8401/workspaces/00000000-0000-4000-8000-000000000000/sessions/00000000-0000-4000-8000-000000000000/position)"
echo "bundle CY-01 markers: analysis-chamber in $(docker exec nquiry-cy01-candidate-web-1 sh -c 'grep -rl analysis-chamber .next/ 2>/dev/null | wc -l') chunk(s); 'Begin analysis' in $(docker exec nquiry-cy01-candidate-web-1 sh -c 'grep -rl \"Begin analysis\" .next/ 2>/dev/null | wc -l'); 'FIXTURE_NON_PROOF' in $(docker exec nquiry-cy01-candidate-web-1 sh -c 'grep -rl FIXTURE_NON_PROOF .next/ 2>/dev/null | wc -l')"
echo "web api base inlined: $(docker exec nquiry-cy01-candidate-web-1 sh -c 'grep -rho \"https://nquiry.condyn.eu/api\" .next/static 2>/dev/null | head -1')"
echo "api log tail:"; docker logs --tail 4 nquiry-cy01-candidate-api-1 2>&1 | cut -c1-160
echo "== CANDIDATE STAGE 2 DONE =="
