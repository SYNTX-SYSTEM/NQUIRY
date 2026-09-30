#!/usr/bin/env bash
# AUTH Field: the final full-repository regression of one Work Unit, with
# proof that the working tree did not change while it ran.
#
# Prints an evidence block to stdout (git status and a content hash of every
# tracked and untracked, non-ignored file before and after; the two pytest
# lanes with counts and exit codes). It writes nothing into the repository:
# the caller records the block in the Work Unit's evidence file afterwards.
#
# Env: DATABASE_URL (isolated *_test database at head), PYTHON (default python3).
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="${PYTHON:-python3}"
cd "$ROOT"

tree_hash() {
  git ls-files -co --exclude-standard -z | sort -z | xargs -0 sha256sum | sha256sum | cut -d' ' -f1
}

echo "HEAD: $(git rev-parse HEAD) ($(git branch --show-current))"
echo "PRE_RUN_GIT_STATUS:"
git status --short | sed 's/^/  /'
PRE="$(tree_hash)"
echo "PRE_RUN_TREE_HASH: $PRE"

echo "LIVE_COMMAND: DATABASE_URL=<isolated test db> $PYTHON -m pytest -q -p no:cacheprovider"
LIVE_OUT="$("$PYTHON" -m pytest -q -p no:cacheprovider 2>&1)"
LIVE_CODE=$?
echo "LIVE_RESULT: $(printf '%s\n' "$LIVE_OUT" | tail -1)"
echo "LIVE_EXIT_CODE: $LIVE_CODE"
if [ "$LIVE_CODE" -ne 0 ]; then
  printf '%s\n' "$LIVE_OUT" | grep -E "^(FAILED|ERROR)" | head -40 | sed 's/^/  /'
fi

echo "NO_DB_COMMAND: env -u DATABASE_URL $PYTHON -m pytest -q -p no:cacheprovider"
NODB_OUT="$(env -u DATABASE_URL "$PYTHON" -m pytest -q -p no:cacheprovider 2>&1)"
NODB_CODE=$?
echo "NO_DB_RESULT: $(printf '%s\n' "$NODB_OUT" | tail -1)"
echo "NO_DB_EXIT_CODE: $NODB_CODE"
if [ "$NODB_CODE" -ne 0 ]; then
  printf '%s\n' "$NODB_OUT" | grep -E "^(FAILED|ERROR)" | head -40 | sed 's/^/  /'
fi

echo "MIGRATIONS: $("$PYTHON" scripts/verify_migrations.py 2>/dev/null | tr '\n' ' ')"
echo "POST_RUN_GIT_STATUS:"
git status --short | sed 's/^/  /'
POST="$(tree_hash)"
echo "POST_RUN_TREE_HASH: $POST"
if [ "$PRE" = "$POST" ]; then echo "TREE_UNCHANGED_DURING_RUN: true"; else echo "TREE_UNCHANGED_DURING_RUN: false"; fi
[ "$LIVE_CODE" -eq 0 ] && [ "$NODB_CODE" -eq 0 ] && [ "$PRE" = "$POST" ]
