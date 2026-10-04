#!/usr/bin/env bash
# Server-wide preservation snapshot (read-only). Usage: snapshot.sh <outdir> <label>
set -u
OUT="$1"; L="$2"; mkdir -p "$OUT"
{
echo "== $(date -u +%Y-%m-%dT%H:%M:%SZ) $L =="
echo "## docker ps"; docker ps -a --no-trunc --format '{{.ID}} {{.Names}} {{.Image}} {{.Status}} {{.Ports}}' | sort -k2
echo "## docker images (nquiry + digests of running)"; docker ps -q | xargs -r docker inspect --format '{{.Name}} image={{.Image}} started={{.State.StartedAt}} restarts={{.RestartCount}} health={{if .State.Health}}{{.State.Health.Status}}{{end}}' | sort
echo "## compose ls"; docker compose ls -a --format table 2>/dev/null
echo "## volumes"; docker volume ls --format '{{.Name}} {{.Driver}}' | sort
echo "## networks"; docker network ls --format '{{.ID}} {{.Name}} {{.Driver}}' | sort -k2
echo "## listening sockets"; ss -lntupH | awk '{print $1, $5, $7}' | sort
echo "## systemd failed"; systemctl --failed --no-legend --plain
echo "## systemd running services"; systemctl list-units --type=service --state=running --no-legend --plain | awk '{print $1}' | sort
echo "## timers"; systemctl list-timers --all --no-legend --plain | awk '{print $NF, $(NF-1)}' | sort | head -60
echo "## pm2"; (export PATH="$PATH:/root/.nvm/versions/node/$(ls /root/.nvm/versions/node 2>/dev/null | tail -1)/bin"; pm2 jlist 2>/dev/null | python3 -c 'import json,sys
try:
  for p in json.load(sys.stdin): print(p["name"], p["pm2_env"]["status"], p["pm2_env"].get("pm_uptime"), p.get("pid"))
except Exception as e: print("pm2: n/a", e)')
echo "## nginx"; nginx -t 2>&1 | tail -1; echo "nginx -T sha256: $(nginx -T 2>/dev/null | sha256sum | cut -c1-64)"; for f in /etc/nginx/sites-enabled/*; do echo "$(sha256sum "$(readlink -f "$f")" | cut -c1-64) $f -> $(readlink -f "$f")"; done; echo "server_names:"; nginx -T 2>/dev/null | grep -E '^\s*server_name' | sed 's/;//' | awk '{$1="";print}' | tr ' ' '\n' | grep -v '^$' | sort -u | tr '\n' ' '; echo
echo "## certs"; for d in /etc/letsencrypt/live/*/; do echo "$(basename $d) $(openssl x509 -in $d/cert.pem -noout -enddate 2>/dev/null)"; done
echo "## cron"; crontab -l 2>/dev/null | grep -v '^#' | sed 's/^/root: /'; ls /etc/cron.d 2>/dev/null | tr '\n' ' '; echo; grep -rl -i nquiry /etc/cron* /etc/systemd/system 2>/dev/null
echo "## resources"; uptime; free -m | head -2; df -h / /var/lib/docker 2>/dev/null | tail -2; docker system df 2>/dev/null | head -5
echo "## vhost HEAD baseline (low impact)"; for n in $(nginx -T 2>/dev/null | grep -E '^\s*server_name' | sed 's/;//' | awk '{$1="";print}' | tr ' ' '\n' | grep -v '^$\|^_$\|^\*' | sort -u); do printf "%s %s\n" "$n" "$(curl -s -m 10 -o /dev/null -w '%{http_code}' -I "https://$n/" 2>/dev/null || echo err)"; done
echo "## file ownership of app roots (top level only)"; stat -c '%U:%G %a %n' /opt/* /var/www/* 2>/dev/null | sort
} > "$OUT/preservation-$L.txt" 2>&1
echo "wrote $OUT/preservation-$L.txt ($(wc -l < "$OUT/preservation-$L.txt") lines)"
