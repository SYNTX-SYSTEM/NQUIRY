# WU-CY-01 isolated real-stack runner: the PINNED RED producer's API + this tree's Next.js + Chromium in one private
# network namespace (see infra/cy01/compose.yaml). Backend layers come from the `producer` build context (a
# `git archive` of checkpoint-PFC-B5, never this tree); web and infra come from this tree.
FROM python:3.13-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    NEXT_TELEMETRY_DISABLED=1

COPY --from=node:22-bookworm-slim /usr/local/bin/node /usr/local/bin/node
COPY --from=node:22-bookworm-slim /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
 && ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx \
 && apt-get update \
 && apt-get install -y --no-install-recommends postgresql-client curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /repo

# ---- the producer (RED, pinned) ----
COPY --from=producer pyproject.toml README.md ./
COPY --from=producer packages ./packages
COPY --from=producer apps/api ./apps/api
COPY --from=producer apps/worker ./apps/worker
RUN pip install .
COPY --from=producer migrations ./migrations
COPY --from=producer scripts ./scripts
COPY --from=producer infra/local/db_roles.sql ./infra/local/db_roles.sql
COPY --from=producer PRODUCER_IDENTITY.json ./PRODUCER_IDENTITY.json

# ---- the consumer (CYAN, this tree) ----
COPY package.json package-lock.json ./
COPY apps/web/package.json ./apps/web/package.json
RUN npm ci --no-audit --no-fund && npx playwright install --with-deps chromium
COPY infra/sf01/run-in-namespace.sh ./infra/sf01/run-in-namespace.sh
COPY apps/web ./apps/web

CMD ["bash", "infra/sf01/run-in-namespace.sh"]
