#!/usr/bin/env bash
# Candidate isolation for the CY-01/B5 pair: project nquiry-cy01-candidate, loopback-only ports, own volume restored
# from the pre-CY01 backup, migrations applied on the copy first. Never touches project nquiry or any other app.
set -euo pipefail
ID=cy01-b5-20260928T031904Z
A=/opt/nquiry/assembly/$ID
B=$(cat /opt/nquiry/_baseline-pre-CY01-CURRENT)
C=/opt/nquiry/candidate
mkdir -p $C; chmod 700 $C
cp /opt/nquiry/.env $C/.env; chmod 600 $C/.env
cat > $C/compose.yaml <<YAML
name: nquiry-cy01-candidate
services:
  postgres:
    image: postgres:17
    environment:
      POSTGRES_USER: \${POSTGRES_USER}
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD}
      POSTGRES_DB: \${POSTGRES_DB}
    volumes:
      - candidate_pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U \${POSTGRES_USER}"]
      interval: 5s
      timeout: 3s
      retries: 20
    mem_limit: 1g
  api:
    build:
      context: $A
      dockerfile: infra/local/api.Dockerfile
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATABASE_URL: \${DATABASE_URL}
      NQUIRY_COOKIE_SECURE: "0"
    ports:
      - "127.0.0.1:8401:8000"
    mem_limit: 1g
  web:
    build:
      context: $A
      dockerfile: infra/local/web.Dockerfile
      args:
        NEXT_PUBLIC_API_BASE_URL: \${NEXT_PUBLIC_API_BASE_URL}
    depends_on:
      - api
    environment:
      NEXT_PUBLIC_API_BASE_URL: \${NEXT_PUBLIC_API_BASE_URL}
    ports:
      - "127.0.0.1:3401:3000"
    mem_limit: 1g
volumes:
  candidate_pgdata:
YAML
CO="docker compose -p nquiry-cy01-candidate --env-file $C/.env -f $C/compose.yaml"
$CO config --format json | python3 -c 'import json,sys; c=json.load(sys.stdin); assert c["name"]=="nquiry-cy01-candidate"; ports=[p for s in c["services"].values() for p in s.get("ports",[]) if p.get("host_ip")!="127.0.0.1"]; assert not ports, ports; print("CANDIDATE_GUARD: project nquiry-cy01-candidate, loopback-only ports")'
$CO down -v --remove-orphans >/dev/null 2>&1 || true
echo "== build images (api, web) =="; $CO build api web 2>&1 | grep -E "^#[0-9]+ (DONE|ERROR)|error|Error|naming to" | tail -8
echo "== candidate postgres + restore of the pre-CY01 dump =="; $CO up -d postgres
U=$(grep ^POSTGRES_USER= $C/.env | cut -d= -f2); D=$(grep ^POSTGRES_DB= $C/.env | cut -d= -f2)
for i in $(seq 1 30); do docker exec nquiry-cy01-candidate-postgres-1 pg_isready -U $U >/dev/null 2>&1 && break; sleep 2; done
docker exec -i nquiry-cy01-candidate-postgres-1 psql -U $U -d $D -q -v ON_ERROR_STOP=1 -f /dev/stdin < $A/infra/local/db_roles.sql 2>&1 | grep -v "already exists" | head -3 || true
DUMP=$(ls $B/nquiry-db-pre-CY01-*.dump | head -1)
docker exec -i nquiry-cy01-candidate-postgres-1 pg_restore -U $U -d $D --no-owner --no-privileges < $DUMP 2>&1 | tail -3 || true
echo "candidate head before: $(docker exec nquiry-cy01-candidate-postgres-1 psql -U $U -d $D -tAc 'select version_num from alembic_version') counts: $(docker exec nquiry-cy01-candidate-postgres-1 psql -U $U -d $D -tAc "select (select count(*) from users)||' users '||(select count(*) from workspaces)||' workspaces'")"
echo "== migrations on the candidate copy (alembic upgrade head via scripts/verify_migrations.py) =="
$CO run --rm --no-deps -e DATABASE_URL="$(grep ^DATABASE_URL= $C/.env | cut -d= -f2-)" api python scripts/verify_migrations.py 2>&1 | tail -3
echo "candidate head after: $(docker exec nquiry-cy01-candidate-postgres-1 psql -U $U -d $D -tAc 'select version_num from alembic_version') tables: $(docker exec nquiry-cy01-candidate-postgres-1 psql -U $U -d $D -tAc "select count(*) from information_schema.tables where table_schema='public'")"
echo "== candidate api + web up =="; $CO up -d api web
for i in $(seq 1 60); do a=$(curl -s -m 3 -o /dev/null -w '%{http_code}' http://127.0.0.1:8401/healthz); w=$(curl -s -m 3 -o /dev/null -w '%{http_code}' http://127.0.0.1:3401/login); [ "$a$w" = 200200 ] && break; sleep 3; done
echo "candidate health api=$a web=$w after $((i*3))s"
echo "begin-analysis route (expect 401, not 404): $(curl -s -m 5 -o /dev/null -w '%{http_code}' -X POST -H 'content-type: application/json' -d '{"expectedVersion":1}' http://127.0.0.1:8401/workspaces/00000000-0000-4000-8000-000000000000/sessions/00000000-0000-4000-8000-000000000000/transitions/begin-analysis)"
echo "bundle CY-01 markers: $(docker exec nquiry-cy01-candidate-web-1 sh -c 'grep -rl analysis-chamber .next/ 2>/dev/null | wc -l') chunk(s); 'Begin analysis': $(docker exec nquiry-cy01-candidate-web-1 sh -c 'grep -rl \"Begin analysis\" .next/ 2>/dev/null | wc -l')"
echo "api log tail:"; docker logs --tail 3 nquiry-cy01-candidate-api-1 2>&1 | cut -c1-160
echo "== CANDIDATE STAGE DONE =="
