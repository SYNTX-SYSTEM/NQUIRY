#!/usr/bin/env bash
# Falsifiers for the canonical repairs of TF-PX-04 and TF-PX-05 (ORANGE-TF-PX-04-05). Narrow radius:
# no product test is executed, nothing is written into a product tree, no proof database is written.
#
# T04a  the chain's OWN serial pre invocation (lines taken verbatim from final_closure.sh) runs the REAL
#       serial_baseline.sh pre (read-only catalog, guard, DB-free collect-only of the frozen tree) and is
#       not refused by it.
# T04b  a legitimately refused pre phase STOPS the chain (nothing after it runs).
# T05a  the governed subshell built exactly as parallel_proof.sh builds it (H serialized via declare -f into
#       bash -c) sees PYC, and PYTHONPYCACHEPREFIX / sys.pycache_prefix resolve to the authorized prefix.
# T05b  real xdist workers started through that construction (on a synthetic tree: no product code) write
#       no .pyc into the tree, but into the prefix.
#
# usage: tooling_falsifiers_tf_px_04_05.sh <new out dir> [<tooling dir under test>]
#        (the second argument is a mutant copy; default = this lineage)
set -u
OUT=${1:?usage: $0 <new out dir> [tooling dir]}
T=$(cd "${2:-$(dirname "${BASH_SOURCE[0]}")}" && pwd)
[ -e "$OUT" ] && { echo "REFUSED: $OUT exists (evidence is never overwritten)"; exit 2; }
mkdir -p "$OUT"
XPY=/home/codi/Entwicklung/nquiry/.venv-swu-px-03/bin/python  # pytest + xdist, no ORANGE guard, no path binding
fails=0
check() {  # $1 name, $2 0|1
  if [ "$2" = 0 ]; then echo "$1::PASS"; else echo "$1::FAIL ${3:-}"; fails=$((fails + 1)); fi
}
unset ORANGE_BYTECODE_ENV ORANGE_SERIAL_DIR ORANGE_PARALLEL_DIR

# ---- T04a: the chain's own serial pre invocation is not refused
F=$OUT/t04a; S=$F/serial_ref; mkdir -p "$S"
PRE_LINES=$(grep -E '^bash "\$P/serial_baseline\.sh" pre |CHAIN STOPPED: serial pre' "$T/final_closure.sh")
echo "$PRE_LINES" > "$OUT/t04_extracted_lines.txt"
( P=$T; export ORANGE_SERIAL_DIR=$S ORANGE_CATALOG_DB=nquiry_proof_gw0_test
  eval "$PRE_LINES"; echo "CHAIN_CONTINUED" ) > "$OUT/t04a.log" 2>&1
rc=$?
grep -q "CHAIN_CONTINUED" "$OUT/t04a.log"; check T04a_CHAIN_CONTINUES_AFTER_OWN_PRE $? "(rc=$rc)"
grep -q "REFUSED" "$S/pre.log" 2>/dev/null; [ $? -ne 0 ] && [ -s "$S/pre.log" ]; check T04a_PRE_NOT_REFUSED $?
[ -s "$S/collected_nodeids.txt" ]; check T04a_PRE_COMPLETED_COLLECTION $? "($(grep -c '' "$S/collected_nodeids.txt" 2>/dev/null) ids)"
[ ! -e "$F/serial_ref.pre.log" ]; check T04a_NO_STRAY_LOG_OUTSIDE_EVIDENCE_DIR $?

# ---- T04b: a refused pre phase stops the chain
F=$OUT/t04b; S=$F/serial_ref; mkdir -p "$S"; echo "pre-existing evidence" > "$S/foreign.txt"
( P=$T; export ORANGE_SERIAL_DIR=$S ORANGE_CATALOG_DB=nquiry_proof_gw0_test
  eval "$PRE_LINES"; echo "CHAIN_CONTINUED" ) > "$OUT/t04b.log" 2>&1
grep -q "REFUSED" "$OUT/t04b.log"; check T04b_PRE_REFUSES_NON_EMPTY_DIR $?
! grep -q "CHAIN_CONTINUED" "$OUT/t04b.log"; check T04b_CHAIN_STOPS_ON_REFUSAL $?
[ "$(cat "$S/foreign.txt")" = "pre-existing evidence" ]; check T04b_EXISTING_EVIDENCE_UNTOUCHED $?

# ---- T05: the governed subshell, built exactly as parallel_proof.sh builds it
DEFS=$(sed -n '/^N=/,/^OUT=/p' "$T/parallel_proof.sh" | grep -v '^OUT=')
HDEF=$(sed -n '/^H() {/,/"\$@"; }$/p' "$T/parallel_proof.sh")
printf '%s\n%s\n' "$DEFS" "$HDEF" > "$OUT/t05_extracted_definitions.txt"
AUTH=$( eval "$DEFS"; echo "$PYC" )
( eval "$DEFS"; eval "$HDEF"
  bash -c "$(declare -f H); H printenv PYTHONPYCACHEPREFIX" > "$OUT/t05a_env.txt"
  bash -c "$(declare -f H); H env PYTHONDONTWRITEBYTECODE=1 '$XPY' -c 'import sys; print(sys.pycache_prefix)'" > "$OUT/t05a_python.txt" )
[ -n "$AUTH" ] && [ "$(cat "$OUT/t05a_env.txt")" = "$AUTH" ]; check T05a_PYC_REACHES_GOVERNED_SUBSHELL $? "(got '$(cat "$OUT/t05a_env.txt")', want '$AUTH')"
[ "$(cat "$OUT/t05a_python.txt")" = "$AUTH" ]; check T05a_PYCACHE_PREFIX_IS_AUTHORIZED $? "(got '$(cat "$OUT/t05a_python.txt")')"

TREE=$OUT/t05b/tree; PREFIX=$OUT/t05b/pyc; mkdir -p "$TREE/pkg" "$TREE/tests" "$PREFIX"
printf '' > "$TREE/pkg/__init__.py"
printf 'def double(x: int) -> int:\n    return 2 * x\n' > "$TREE/pkg/mod.py"
printf '[pytest]\npythonpath = .\n' > "$TREE/pytest.ini"
printf 'import pytest\nfrom pkg.mod import double\n\n\n@pytest.mark.parametrize("x", range(8))\ndef test_double(x: int) -> None:\n    assert double(x) == x + x\n' > "$TREE/tests/test_double.py"
before=$(cd "$TREE" && find . | sort | sha256sum)
( eval "$DEFS"; eval "$HDEF"; PYC=$PREFIX  # same export attribute as the script's own PYC
  bash -c "cd '$TREE' && $(declare -f H); H '$XPY' -m pytest -p no:cacheprovider -n 2 -q" ) > "$OUT/t05b.log" 2>&1
rc=$?
after=$(cd "$TREE" && find . | sort | sha256sum)
[ $rc -eq 0 ] && grep -q "8 passed" "$OUT/t05b.log"; check T05b_XDIST_WORKERS_RAN $? "(rc=$rc)"
[ "$before" = "$after" ] && [ -z "$(find "$TREE" -name '*.pyc' -o -name __pycache__)" ]; check T05b_NO_BYTECODE_IN_TREE $? "($(find "$TREE" -name '*.pyc' | wc -l) pyc in tree)"
[ -n "$(find "$PREFIX" -path '*pkg*' -name 'mod*.pyc')" ]; check T05b_BYTECODE_IN_AUTHORIZED_PREFIX $?

echo "TF_PX_04_05_FALSIFIERS::$([ $fails -eq 0 ] && echo PASS || echo "FAIL ($fails)")"
exit $((fails > 0))
