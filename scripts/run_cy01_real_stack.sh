#!/usr/bin/env bash
# WU-CY-01 ISOLATED real-stack lane against the PINNED RED producer (HD-27 / HA-03 Option B), host entry point.
#
# 1. Verifies that the local tag named in PIN_TAG is the signed tag whose target is EXACTLY the pinned commit
#    (the tuple recorded in docs/implementation/field-reports/CY-01/). A different target stops the lane: a moving
#    branch never becomes an implicit producer.
# 2. Exports that commit's backend with `git archive` (no checkout, no worktree, nothing of this tree) and writes
#    PRODUCER_IDENTITY.json beside it (tag, tag object, commit, tree, migration head); the runner image copies it.
# 3. Starts ONLY compose project `nquiry-cy01` (infra/cy01/compose.yaml): own database volume, no published host
#    ports, the producer's API + this tree's web + Chromium in one private network namespace.
# Proof output: apps/web/test-results/cy01-real-stack/ (gitignored), including producer.json.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT="nquiry-cy01"
# PIN HISTORY (HD-27: a change of the pin needs a new explicit reconstruction and authorization):
#   2026-09-27 .. 2026-10-01  checkpoint-PFC-B5      7d3f74e4685b821cc948f45e413c1e0c207259d4  tag fd3d5600132e4dcb9203702d500daccf4c6d0439  tree bc77cc8bb6414e6104aabdd5bd2fb1874f63f750
#   2026-10-01 (CYAN-PCPG-05, local/test lanes only; production stays B5+AC1.1):
#                             checkpoint-PFC-PCPG-18  41b4324a75077ec33b00ed3a878db7a318fc00d8  tag 0e12895fc64299abde1eb5115303f962b1c227af  tree 0631c936f99c9356f6082f05b460815a09632c7b
PIN_TAG="checkpoint-PFC-PCPG-18"
PIN_COMMIT="41b4324a75077ec33b00ed3a878db7a318fc00d8"
PIN_TAG_OBJECT="0e12895fc64299abde1eb5115303f962b1c227af"
PIN_TREE="0631c936f99c9356f6082f05b460815a09632c7b"
PIN_MIGRATION_HEAD="e8c2a5f1b7d4"

cd "$ROOT"
tag_object="$(git rev-parse "refs/tags/$PIN_TAG")"
commit="$(git rev-parse "refs/tags/$PIN_TAG^{commit}")"
tree="$(git rev-parse "refs/tags/$PIN_TAG^{tree}")"
if [ "$tag_object" != "$PIN_TAG_OBJECT" ] || [ "$commit" != "$PIN_COMMIT" ] || [ "$tree" != "$PIN_TREE" ]; then
  echo "CY01_GUARD: $PIN_TAG resolves to tag $tag_object commit $commit tree $tree; pinned $PIN_TAG_OBJECT / $PIN_COMMIT / $PIN_TREE" >&2
  exit 3
fi
git verify-tag "$PIN_TAG" >/dev/null 2>&1 || { echo "CY01_GUARD: $PIN_TAG signature not verified" >&2; exit 3; }
if [ "$(git ls-tree --name-only "$commit" -- migrations/versions/ | grep -c "/${PIN_MIGRATION_HEAD}_")" = "0" ]; then
  echo "CY01_GUARD: migration head $PIN_MIGRATION_HEAD not in the pinned tree" >&2
  exit 3
fi

EXPORT="${CY01_EXPORT_DIR:-${TMPDIR:-/tmp}/nquiry-cy01-producer-$commit}"
rm -rf "$EXPORT"
mkdir -p "$EXPORT"
git archive --format=tar "$commit" pyproject.toml README.md packages apps/api apps/worker migrations scripts infra/local/db_roles.sql | tar -x -C "$EXPORT"
cat >"$EXPORT/PRODUCER_IDENTITY.json" <<JSON
{"line": "RED", "branch_of_origin": "pfc-integration (not consumed as a branch)", "tag": "$PIN_TAG", "tagObject": "$tag_object", "commit": "$commit", "tree": "$tree", "migrationHead": "$PIN_MIGRATION_HEAD", "status": "TECHNICALLY_CLOSED, CHECKPOINTED; not REVIEWED_FIELD, not PUBLISHED_FIELD", "aiProvider": "mock (NQUIRY_ENVIRONMENT=TEST); MOCK / NON_PROOF", "exportedAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"}
JSON
export CY01_PRODUCER_DIR="$EXPORT" CY01_PRODUCER_COMMIT="$commit"
COMPOSE=(docker compose -p "$PROJECT" -f "$ROOT/infra/cy01/compose.yaml")

"${COMPOSE[@]}" config --format json | python3 -c '
import json, sys
config = json.load(sys.stdin)
name = config.get("name")
if name != "nquiry-cy01":
    sys.exit(f"CY01_GUARD: compose project is {name!r}, expected nquiry-cy01")
published = [s for s, svc in config.get("services", {}).items() if svc.get("ports")]
if published:
    sys.exit(f"CY01_GUARD: services publish host ports: {published}")
print("CY01_GUARD: project nquiry-cy01, no host ports")
'

OUT="$ROOT/apps/web/test-results/cy01-real-stack"
mkdir -p "$OUT"
cp "$EXPORT/PRODUCER_IDENTITY.json" "$OUT/producer.json"
"${COMPOSE[@]}" down -v --remove-orphans >/dev/null 2>&1 || true
set +e
"${COMPOSE[@]}" run --build --rm runner bash infra/sf01/run-in-namespace.sh "$@"
status=$?
set -e
"${COMPOSE[@]}" down --remove-orphans >/dev/null 2>&1 || true
exit "$status"
