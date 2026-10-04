#!/usr/bin/env bash
# AC1 production candidate: project nquiry-ac1-candidate, loopback-only api (8402), own volume restored from the pre-AC1
# dump, NQUIRY_ENVIRONMENT=PRODUCTION. Never touches project nquiry or anything else.
set -euo pipefail
ID=ac11-cy01-20260928T182206Z; A=/opt/nquiry/assembly/$ID; B=$(cat /opt/nquiry/_baseline-pre-AC1-CURRENT); C=/opt/nquiry/candidate-ac1
mkdir -p $C; chmod 700 $C; cp /opt/nquiry/.env $C/.env; chmod 600 $C/.env
cat > $C/compose.yaml <<YAML
name: nquiry-ac1-candidate
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
      NQUIRY_ENVIRONMENT: \${NQUIRY_ENVIRONMENT}
    ports:
      - "127.0.0.1:8402:8000"
    mem_limit: 1g
volumes:
  candidate_pgdata:
YAML
CO="docker compose -p nquiry-ac1-candidate --env-file $C/.env -f $C/compose.yaml"
$CO config --format json | python3 -c 'import json,sys; c=json.load(sys.stdin); assert c["name"]=="nquiry-ac1-candidate"; p=[x for s in c["services"].values() for x in s.get("ports",[]) if x.get("host_ip")!="127.0.0.1"]; assert not p, p; assert c["services"]["api"]["environment"]["NQUIRY_ENVIRONMENT"]=="PRODUCTION"; print("CANDIDATE_GUARD: nquiry-ac1-candidate, loopback-only, NQUIRY_ENVIRONMENT=PRODUCTION")'
$CO down -v --remove-orphans >/dev/null 2>&1 || true
echo "== build api =="; $CO build api 2>&1 | grep -E "naming to|ERROR|error" | tail -3
$CO up -d postgres
U=$(grep ^POSTGRES_USER= $C/.env | cut -d= -f2); D=$(grep ^POSTGRES_DB= $C/.env | cut -d= -f2); PG=nquiry-ac1-candidate-postgres-1
for i in $(seq 1 30); do docker exec $PG pg_isready -U $U >/dev/null 2>&1 && break; sleep 2; done
docker exec -i $PG psql -U $U -d $D -q -f /dev/stdin < $A/infra/local/db_roles.sql >/dev/null 2>&1 || true
docker exec -i $PG pg_restore -U $U -d $D --no-owner --no-privileges < $(ls $B/nquiry-db-pre-AC1-*.dump) 2>&1 | tail -2 || true
echo "candidate head: $(docker exec $PG psql -U $U -d $D -tAc 'select version_num from alembic_version')"
docker exec -i $PG psql -U $U -d $D -tA -F" " < $B/digest.sql > $C/digests-candidate-before.txt
echo "digests equal to live BEFORE: $(diff -q $B/digests-BEFORE.txt $C/digests-candidate-before.txt >/dev/null && echo yes || echo NO)"
$CO up -d api
for i in $(seq 1 40); do [ "$(curl -s -m 3 -o /dev/null -w '%{http_code}' http://127.0.0.1:8402/healthz)" = 200 ] && break; sleep 2; done
echo "health: $(curl -s -m 3 -o /dev/null -w '%{http_code}' http://127.0.0.1:8402/healthz)"
X="$CO exec -T api python -m nquiry_api.operator.create_identity"
PW=$C/probe.pw; umask 077; python3 -c 'import secrets;print(secrets.token_urlsafe(24))' > $PW
EMAIL=probe@ac1-candidate.nquiry.invalid
echo "== P1 create (PRODUCTION, operator) =="; $X --email $EMAIL --name "AC1 candidate probe" --operator otti@condyn.eu < $PW > $C/p1.out 2> $C/p1.err; echo "exit $? out $(cat $C/p1.out) err $(cat $C/p1.err)"
echo "== P2 duplicate (case variant) =="; set +e; $X --email PROBE@AC1-candidate.nquiry.invalid --name x --operator otti@condyn.eu < $PW; echo "exit $?"
echo "== P3 password on argv refused =="; $X --email p3@ac1-candidate.nquiry.invalid --name x --operator otti@condyn.eu --password nope < /dev/null 2>&1 | tail -1; echo "exit ${PIPESTATUS[0]}"
echo "== P4 undeclared environment =="; $CO exec -T -e NQUIRY_ENVIRONMENT= api python -m nquiry_api.operator.create_identity --email p4@ac1-candidate.nquiry.invalid --name x --operator otti@condyn.eu < $PW; echo "exit $?"
echo "== P5 missing operator =="; $X --email p5@ac1-candidate.nquiry.invalid --name x < $PW; echo "exit $?"
echo "== P6 dev provisioning refused under PRODUCTION =="; $CO exec -T api python -c 'import os
from test_support.dev_identity import DEV_IDENTITY_OPT_IN_VALUE as V, DevIdentityProvisioningRefused as R, check_dev_provisioning_allowed as c
try:
    c(opt_in_value=V, database_host="postgres", environment=os.environ.get("NQUIRY_ENVIRONMENT")); print("ALLOWED (FALSIFIER)")
except R as e: print("REFUSED:", e)'
echo "dev script present in image: $($CO exec -T api sh -c 'ls /repo/scripts 2>/dev/null | wc -l')"
set -e
echo "== P7 login / me / workspaces with the created identity =="
J=$C/cookies; rm -f $J
python3 - "$EMAIL" "$PW" <<'PY'
import json,sys,urllib.request,http.cookiejar
email=sys.argv[1]; pw=open(sys.argv[2]).read().strip()
cj=http.cookiejar.CookieJar(); op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
def call(m,p,b=None):
    r=urllib.request.Request("http://127.0.0.1:8402"+p,method=m,data=None if b is None else json.dumps(b).encode(),headers={"content-type":"application/json"})
    try:
        with op.open(r) as x: return x.status, json.loads(x.read() or b"{}")
    except urllib.error.HTTPError as e: return e.code, json.loads(e.read() or b"{}")
print("wrong password:", call("POST","/auth/login",{"email":email,"password":"wrong-password-xyz"})[0])
print("login:", call("POST","/auth/login",{"email":email,"password":pw})[0])
print("me:", call("GET","/auth/me"))
print("workspaces:", call("GET","/workspaces"))
print("logout:", call("POST","/auth/logout")[0], "me after logout:", call("GET","/auth/me")[0])
print("no registration route:", [call("POST",p,{"email":"x@y.z","password":"x"*16})[0] for p in ("/auth/register","/auth/signup","/users","/identities")])
PY
echo "== P8 records =="
docker exec $PG psql -U $U -d $D -tA -F" | " -c "select u.email, (select count(*) from local_auth_credentials c where c.user_id=u.id), (select left(password_hash,14) from local_auth_credentials c where c.user_id=u.id), (select count(*) from workspace_memberships m where m.user_id=u.id), (select count(*) from human_authority_bindings b where b.human_user_id=u.id), (select count(*) from session_participations p where p.user_id=u.id) from users u where u.email like '%ac1-candidate%'"
docker exec $PG psql -U $U -d $D -tA -F" | " -c "select event_type, actor_type, actor_id, trust_boundary, environment, target_ref, observed_facts from security_events"
docker exec -i $PG psql -U $U -d $D -tA -F" " < $B/digest.sql > $C/digests-candidate-after.txt
echo "real-data digests after (users/credentials change by the probe only):"; diff $B/digests-BEFORE.txt $C/digests-candidate-after.txt || true
echo "== P9 password never in output, logs or DB =="
P=$(cat $PW)
echo "api logs: $(docker logs nquiry-ac1-candidate-api-1 2>&1 | grep -cF -- "$P")  outputs: $(cat $C/p1.out $C/p1.err | grep -cF -- "$P")  db dump: $(docker exec $PG pg_dump -U $U -d $D | grep -cF -- "$P")"
rm -f $PW $J
echo "== CANDIDATE AC1 DONE =="
