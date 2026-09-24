# SF-01 isolated real-stack runner: this tree's API + Next.js + Chromium in one
# private network namespace (see infra/sf01/compose.yaml for why).
#
# Python 3.13 (pyproject `requires-python >= 3.13`) + Node 22 copied from the
# official image (no curl-to-shell installer). Dependencies are installed from
# the committed lockfile (`npm ci`) and pyproject; nothing is added.
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

COPY pyproject.toml README.md ./
COPY packages ./packages
COPY apps/api ./apps/api
COPY apps/worker ./apps/worker
RUN pip install .

COPY package.json package-lock.json ./
COPY apps/web/package.json ./apps/web/package.json
RUN npm ci --no-audit --no-fund && npx playwright install --with-deps chromium

COPY migrations ./migrations
COPY scripts ./scripts
COPY infra ./infra
COPY apps/web ./apps/web

CMD ["bash", "infra/sf01/run-in-namespace.sh"]
