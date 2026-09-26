"""F04 RED proof by mutation (WU-04.10).

Each mutation removes or inverts ONE predicate the F04 materialization added,
runs the falsifier that guards it, and expects it to FAIL (mutation killed).
The source file is restored byte-for-byte afterwards, even on error. Run from
the repository root with DATABASE_URL set to a *_test database:

    python scripts/f04_mutation_proof.py

Exit status 0 only if every mutation is killed and every file is restored.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MUTATIONS: list[tuple[str, str, str, str, str]] = [
    # (id, file, old, new, pytest node selector)
    (
        "M01 BND-008 requester-keyed again (FBR-F04-3)",
        "packages/boundaries/bnd_008_question_burst.py",
        "        if operation in _AI_ONLY_OPERATIONS and burst_state in PROTECTED_BURST_STATES:",
        (
            "        if actor_class is ActorClass.AI_PROCESSOR"
            " and operation in _AI_ONLY_OPERATIONS and burst_state in PROTECTED_BURST_STATES:"
        ),
        "tests/boundaries/test_f04_protected_set_ai_boundary.py",
    ),
    (
        "M02 BND-009 ignores Burst state",
        "packages/boundaries/bnd_009_ai_invocation.py",
        "        if boundary_input.burst_state is not BurstState.COMPLETED:",
        "        if False:",
        "tests/boundaries/test_f04_protected_set_ai_boundary.py",
    ),
    (
        "M03 SYSTEM_OPERATION accepts any actor class",
        "packages/boundaries/system_operation.py",
        "    if actor.actor_class is not ActorClass.SYSTEM_SERVICE:",
        "    if False:",
        "tests/e2e/test_f04_system_operation_gate.py::test_c1_human_actor_is_denied",
    ),
    (
        "M04 SYSTEM_OPERATION executes a superseded OA",
        "packages/boundaries/system_operation.py",
        "    if reader.latest_sequence(session_id, oa.ai_operation_id) != oa.sequence_no:",
        "    if False:",
        "tests/e2e/test_f04_analysis_run.py::test_e11_recovery_of_an_unconsumed_oa1",
    ),
    (
        "M05 SYSTEM_OPERATION ignores consumption",
        "packages/boundaries/system_operation.py",
        '        if carrier is not None:\n            return _deny("ALREADY_CONSUMED")',
        '        if False:\n            return _deny("ALREADY_CONSUMED")',
        "tests/e2e/test_f04_analysis_run.py::test_e6_a_second_run_for_the_same_oa_is_refused",
    ),
    (
        "M06 SYSTEM_OPERATION skips the OA-3 authorizer check (K15)",
        "packages/boundaries/system_operation.py",
        "            oa.shape is AuthorizationShape.OA_3\n            and x_generation",
        "            False\n            and x_generation",
        "tests/e2e/test_f04_clustering.py::test_k15_oa3_not_authorized_by_xs_command_is_denied_at_the_gate",
    ),
    (
        "M07 SYSTEM_OPERATION ignores Session state",
        "packages/boundaries/system_operation.py",
        "    if state[1] is not SessionState.ANALYSIS:",
        "    if False:",
        "tests/e2e/test_f04_analysis_run.py::test_e12_run_while_session_not_analysis_is_blocked",
    ),
    (
        "M08 BND-014 never denies SYSTEM_OPERATION",
        "packages/boundaries/bnd_014_commit.py",
        "            if not system_operation.granted or system_operation.source is None:",
        "            if False:",
        "tests/e2e/test_f04_system_operation_gate.py::test_bnd014_denies_system_operation_for_a_human_and_allows_the_service",
    ),
    (
        "M09 BEGIN_ANALYSIS skips frozen-set verification",
        "packages/application/analysis_begin_handler.py",
        "            frozen_verified=verify_frozen_set(ports, fresh_burst).matches,",
        "            frozen_verified=True,",
        "tests/e2e/test_f04_begin_analysis.py::test_a4_unverified_frozen_set_is_blocked",
    ),
    (
        "M10 BEGIN_ANALYSIS creates no OA-1 (HD-16)",
        "packages/application/analysis_begin_handler.py",
        "        ports.ai_authorizations.create(\n            OperationAuthorization(",
        "        (lambda *_: None)(\n            OperationAuthorization(",
        "tests/e2e/test_f04_begin_analysis.py::test_a1_controller_begins_analysis",
    ),
    (
        "M11 validator allows unknown fields (HD-18)",
        "packages/ai_gateway/validator.py",
        "    if extra:\n",
        "    if False:\n",
        (
            "tests/ai/test_validator.py "
            "tests/e2e/test_f04_analysis_input.py::test_d4_d5_schema_is_closed_and_refs_are_manifest_only"
        ),
    ),
    (
        "M12 validator allows out-of-manifest refs",
        "packages/ai_gateway/validator.py",
        "    if not isinstance(value, str) or value not in allowed:",
        "    if not isinstance(value, str):",
        "tests/e2e/test_f04_analysis_input.py::test_d7_no_cross_workspace_refs",
    ),
    (
        "M13 manifest binding ignores extra inputs (D2)",
        "packages/application/analysis_input.py",
        "    if actual - expected:",
        "    if False:",
        "tests/e2e/test_f04_analysis_input.py::test_d2_extra_missing_or_foreign_question_is_refused",
    ),
    (
        "M14 acceptance creates no OA-3 (HD-23)",
        "packages/application/analysis_system.py",
        "    if op is AIOperationId.AIOP_001:\n            # HD-23 / R7",
        "    if False:\n            # HD-23 / R7",
        "tests/e2e/test_f04_analysis_run.py::test_e1_e2_original_run_is_accepted_atomically",
    ),
    (
        "M15 request accepts a mismatched case (E18)",
        "packages/application/analysis_request_handler.py",
        "        if availability.case is not case:",
        "        if False:",
        "tests/e2e/test_f04_analysis_run.py::test_e18_case_mismatch_is_rejected",
    ),
    (
        "M16 request allowed while a generation is non-terminal (E10)",
        "packages/application/analysis_request_handler.py",
        '        return RequestAvailability(None, "GENERATION_IN_PROGRESS")',
        "        pass",
        "tests/e2e/test_f04_analysis_run.py::test_e10_request_while_a_generation_is_non_terminal_is_blocked",
    ),
    (
        "M17 BND-010 ignores fields outside the contract (E14)",
        "packages/boundaries/bnd_010_ai_output.py",
        "            if outside:",
        "            if False:",
        "tests/e2e/test_f04_analysis_run.py::test_e14_output_claiming_a_decision_is_denied_by_bnd_010",
    ),
    (
        "M18 mock allowed in production (F1)",
        "packages/application/analysis_runtime.py",
        "    if environment not in _DEV_ENVIRONMENTS:",
        "    if False:",
        "tests/regression/test_f04_static_gates.py",
    ),
    (
        "M19 mock projected without its marker (HD-19)",
        "packages/application/analysis_projection.py",
        '"proof": "MOCK / NON_PROOF" if mock else "NON_PROOF",',
        '"proof": "NON_PROOF",',
        "tests/e2e/test_http_f04.py::test_h1_h2_h3_g1_g3_g4_begin_and_derived_field",
    ),
    (
        "M20 derived field served before the frozen set (HD-22)",
        "packages/application/inquiry_queries.py",
        'visible=question_set.get("visibility") == "FULL_FROZEN_SET",',
        "visible=True,",
        "tests/e2e/test_f04_projection.py",
    ),
    # ---- independent review R1 / R2 (FBR-F04-R1, FBR-F04-R2)
    (
        "M21 accepted content re-serialized again (R1)",
        "packages/application/analysis_system.py",
        "                content=response.raw_content,",
        (
            # the exact pre-repair code. (A default-separator re-serialization is an
            # EQUIVALENT mutant for the mock: its bytes are json.dumps(sort_keys=True)
            # and survive a json round-trip unchanged. The DB binding refuses any
            # divergence for every provider.)
            '                content=__import__("json").dumps(validation.payload,'
            ' sort_keys=True, separators=(",", ":"), ensure_ascii=False),'
        ),
        "tests/e2e/test_f04_accepted_output_binding.py::test_r1_every_accepted_artifact_is_the_validated_bytes",
    ),
    (
        "M22 resolver accepts a non-VALIDATED proof (R1)",
        "packages/application/analysis_provenance.py",
        '    if proof.validation_result != "VALIDATED":',
        "    if False:",
        "tests/e2e/test_f04_accepted_output_binding.py::test_r1_resolver_refuses_a_chain_without_the_validated_proof",
    ),
    (
        "M22b resolver skips the byte binding (R1)",
        "packages/application/analysis_provenance.py",
        "    if not (content_sha == artifact.content_fingerprint == proof.output_fingerprint):",
        "    if False:",
        "tests/e2e/test_f04_accepted_output_binding.py::test_r1_resolver_refuses_a_chain_without_the_validated_proof",
    ),
    (
        "M23 VALIDATED proof persisted on a denied acceptance (R2)",
        "packages/application/analysis_system.py",
        "    if proof is not None and proof.validation_result is not AIValidationResult.VALIDATED:",
        "    if proof is not None:",
        "tests/e2e/test_f04_accepted_output_binding.py::test_r2_denied_acceptance_persists_no_validated_proof",
    ),
]


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    results: list[tuple[str, str]] = []
    ok = True
    for mid, rel, old, new, selector in MUTATIONS:
        path = ROOT / rel
        original = path.read_bytes()
        before = _digest(path)
        text = original.decode("utf-8")
        if text.count(old) != 1:
            results.append((mid, f"NOT_APPLIED (anchor count {text.count(old)})"))
            ok = False
            continue
        try:
            path.write_text(text.replace(old, new, 1), encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-q",
                    "-x",
                    "-p",
                    "no:cacheprovider",
                    *selector.split(),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            # 0 = the falsifier passed (mutation survived); 5 = nothing collected
            killed = proc.returncode not in (0, 5)
            results.append((mid, "KILLED" if killed else "SURVIVED"))
            ok = ok and killed
        finally:
            path.write_bytes(original)
        if _digest(path) != before:
            results.append((mid, "RESTORE_FAILED"))
            ok = False
    for mid, verdict in results:
        print(f"{verdict:14} {mid}")
    print("F04_MUTATION_PROOF::" + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
