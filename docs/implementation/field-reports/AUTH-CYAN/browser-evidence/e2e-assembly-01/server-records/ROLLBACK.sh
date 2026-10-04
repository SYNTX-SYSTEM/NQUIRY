#!/usr/bin/env bash
# CYAN_REAL_E2E_ASSEMBLY_01 rollback: remove the /cy-review relation and the candidate web; / and /api/ untouched.
set -u
B=/opt/nquiry/_baseline-pre-CYREVIEW-20261003T213429Z
V=/etc/nginx/sites-enabled/nquiry.condyn.eu
cp "$B/nquiry.condyn.eu.vhost" "$V"
nginx -t && systemctl reload nginx
echo "vhost sha256: $(sha256sum $V | cut -d' ' -f1) (baseline 2317708ca475fc6f7e6ead3843d553d8b70562ffdf70eefd844714e532ba1cf2)"
docker compose -p nquiry-cy-review -f /opt/nquiry/review/compose.yaml down
echo "/cy-review/login: http $(curl -s -o /dev/null -w %{http_code} https://nquiry.condyn.eu/cy-review/login) (expect 404)"
echo "live /: http $(curl -s -o /dev/null -w %{http_code} https://nquiry.condyn.eu/)  /api/auth/providers: http $(curl -s -o /dev/null -w %{http_code} https://nquiry.condyn.eu/api/auth/providers)"
