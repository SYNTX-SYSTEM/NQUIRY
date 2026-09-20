"""PACKAGE_PREDECESSORS / PACKAGE_TEST_PATHS: the real PKG-00..PKG-32
dependency graph (14 section 47's own Coding Package DAG, transcribed
verbatim) and the real test files each package actually introduced
(extracted from this repository's own git history -- `git show
--name-status --diff-filter=A <commit> -- 'tests/*' 'apps/*/tests/*'`
per package commit -- not guessed, not copied from 14 section 50's own
aspirational "Primary test file" column, which several packages
already disclosed departing from during real implementation).

TEST ONLY. Never imported by production code -- same import-graph
guard as every other module under `tests/`.

WHY GIT HISTORY, NOT 14 SECTION 50's OWN TABLE
--------------------------------------------------------------------
14 section 50 ("TEST IMPLEMENTATION MAP FOR P-01 THROUGH P-25") names
files like `tests/authority/test_ai_non_authority.py` and
`tests/proof/test_reconstruct_consequence.py` that were never actually
created -- the real, accepted implementation consolidated that
coverage into files 14 did not originally name (e.g. P-07 is really
proven by `tests/e2e/test_human_decision.py` and
`tests/e2e/test_proof_bundle_paths.py`, per PKG-30's own
`packages/test_support/proof_claim_matrix.py`). A dependency graph
built from 14's own aspirational table would therefore compute
`affected_test_paths()` results that name files that do not exist.
Every path below is drawn from a real `git show` of the actual
`PACKAGE_PASS` commit for that package, and is proven to exist on disk
by `test_regression_package_graph.py`'s own falsifiability tests.
"""

from __future__ import annotations

PACKAGE_IDS = tuple(f"PKG-{n:02d}" for n in range(33))
"""PKG-00 through PKG-32, this repository's own complete, closed
package set (14 section 46's Coding Package Manifest)."""

PACKAGE_PREDECESSORS: dict[str, tuple[str, ...]] = {
    "PKG-00": (),
    "PKG-01": ("PKG-00",),
    "PKG-02": ("PKG-01",),
    "PKG-03": ("PKG-02",),
    "PKG-04": ("PKG-02",),
    "PKG-05": ("PKG-01",),
    "PKG-06": ("PKG-05",),
    "PKG-07": ("PKG-06",),
    "PKG-08": ("PKG-07",),
    "PKG-09": ("PKG-08",),
    "PKG-10": ("PKG-09",),
    "PKG-11": ("PKG-10",),
    "PKG-12": ("PKG-10",),
    "PKG-13": ("PKG-12",),
    "PKG-14": ("PKG-13",),
    "PKG-15": ("PKG-13",),
    "PKG-16": ("PKG-13",),
    "PKG-17": ("PKG-16",),
    "PKG-18": ("PKG-17",),
    "PKG-19": ("PKG-18",),
    "PKG-20": ("PKG-13",),
    "PKG-21": ("PKG-20",),
    "PKG-22": ("PKG-13",),
    "PKG-23": ("PKG-22",),
    "PKG-24": ("PKG-23",),
    "PKG-25": ("PKG-13",),
    "PKG-26": ("PKG-25",),
    "PKG-27": ("PKG-13",),
    "PKG-28": ("PKG-21", "PKG-26"),
    "PKG-29": ("PKG-15", "PKG-19", "PKG-28"),
    "PKG-30": ("PKG-24", "PKG-26", "PKG-29"),
    "PKG-31": ("PKG-30",),
    "PKG-32": ("PKG-31",),
}
"""14 section 47's Coding Package DAG, transcribed edge-for-edge (each
value is that package's own direct predecessor set, matching every
package's own manifest `REQUIRED PREDECESSORS` field)."""


# Real test files each package's own PACKAGE_PASS commit added, per
# `git show --name-status --diff-filter=A <hash> -- 'tests/*'
# 'apps/*/tests/*'`. `.gitkeep` placeholders are excluded (they name a
# reserved directory, not an exercisable test). Frontend paths
# (`apps/web/tests/...`) are real but require the Node/Vitest/
# Playwright runner, not `pytest.main()` -- see this module's own
# `PYTHON_TEST_PATHS`/`FRONTEND_TEST_PATHS` split below and
# `test_regression_package_graph.py`'s own disclosure of this limit.
PACKAGE_TEST_PATHS: dict[str, tuple[str, ...]] = {
    "PKG-00": (
        "apps/api/tests/test_health.py",
        "apps/web/tests/smoke.test.ts",
        "tests/regression/test_architecture_dependency_checks.py",
        "tests/regression/test_provider_sdk_import_checker.py",
        "tests/regression/test_test_only_import_checker.py",
        "tests/security/test_admin_non_authority.py",
        "tests/security/test_ai_gateway.py",
        "tests/security/test_direct_write.py",
        "tests/semantic/test_clock.py",
        "tests/semantic/test_id_generator.py",
        "tests/semantic/test_ids.py",
        "tests/semantic/test_migrations_skeleton.py",
        "tests/semantic/test_versions.py",
    ),
    "PKG-01": (
        "tests/domain/test_workspace_context.py",
        "tests/domain/test_workspace_repository.py",
        "tests/security/test_identity.py",
    ),
    "PKG-02": (
        "tests/authority/test_authority_binding_repository.py",
        "tests/authority/test_membership_repository.py",
        "tests/security/test_habb_grant_constraints.py",
    ),
    "PKG-03": ("tests/authority/test_resolver.py",),
    "PKG-04": ("tests/regression/test_nonproof_bootstrap.py",),
    "PKG-05": (
        "tests/domain/test_challenge.py",
        "tests/domain/test_session.py",
        "tests/transitions/test_session_transition_constraints.py",
        "tests/transitions/test_session_transition_registry.py",
    ),
    "PKG-06": (
        "tests/domain/question/test_question.py",
        "tests/domain/question/test_question_lineage.py",
        "tests/domain/question/test_question_repository.py",
    ),
    "PKG-07": (
        "tests/ai/test_burst_ai_block.py",
        "tests/boundaries/test_burst_contamination_guard.py",
        "tests/transitions/test_burst_operations_readiness.py",
        "tests/transitions/test_burst_transition_constraints.py",
        "tests/transitions/test_burst_transition_registry.py",
    ),
    "PKG-08": (
        "tests/boundaries/test_registry.py",
        "tests/boundaries/test_types.py",
    ),
    "PKG-09": (
        "tests/boundaries/test_bnd_001_identity.py",
        "tests/boundaries/test_bnd_002_workspace.py",
        "tests/boundaries/test_bnd_003_membership.py",
        "tests/boundaries/test_bnd_004_role_context.py",
        "tests/boundaries/test_bnd_005_human_authority.py",
        "tests/boundaries/test_bnd_006_human_decision.py",
        "tests/boundaries/test_bnd_007_state_transition.py",
        "tests/boundaries/test_bnd_008_agrees_with_application_guard.py",
        "tests/boundaries/test_bnd_008_question_burst.py",
        "tests/security/test_bnd_cross_layer_isolation.py",
    ),
    "PKG-10": (
        "tests/command_commit_event/test_command_event_split.py",
        "tests/command_commit_event/test_command_registry.py",
        "tests/command_commit_event/test_command_repository.py",
        "tests/command_commit_event/test_envelope.py",
    ),
    "PKG-11": (
        "tests/command_commit_event/test_idempotency.py",
        "tests/recovery/test_idempotency_indeterminate_blocks_retry.py",
    ),
    "PKG-12": (
        "tests/command_commit_event/test_audit.py",
        "tests/command_commit_event/test_outbox.py",
    ),
    "PKG-13": (
        "tests/boundaries/test_bnd_014_commit.py",
        "tests/command_commit_event/test_commit.py",
    ),
    "PKG-14": (
        "tests/authority/test_question_selection_authority.py",
        "tests/command_commit_event/test_question_selection.py",
    ),
    "PKG-15": (
        "tests/authority/test_decision_authority.py",
        "tests/e2e/test_human_decision.py",
        "tests/transitions/test_decision_transition_constraints.py",
    ),
    "PKG-16": (
        "tests/evidence/test_claim_anchor.py",
        "tests/evidence/test_evidence_set.py",
        "tests/evidence/test_models.py",
        "tests/evidence/test_provenance.py",
        "tests/evidence/test_relation.py",
    ),
    "PKG-17": (
        "tests/boundaries/test_bnd_013_evidence.py",
        "tests/evidence/test_freshness.py",
    ),
    "PKG-18": (
        "tests/ai/test_aiop.py",
        "tests/ai/test_derived_artifact.py",
        "tests/ai/test_generation.py",
    ),
    "PKG-19": (
        "tests/ai/test_context.py",
        "tests/ai/test_gateway.py",
        "tests/ai/test_mock_provider.py",
        "tests/ai/test_prompt.py",
        "tests/ai/test_validator.py",
        "tests/boundaries/test_bnd_009_ai_invocation.py",
        "tests/boundaries/test_bnd_010_ai_output.py",
    ),
    "PKG-20": (
        "tests/command_commit_event/test_event.py",
        "tests/command_commit_event/test_outbox_worker.py",
        "tests/security/test_outbox_worker_exclusivity.py",
    ),
    "PKG-21": (
        "tests/command_commit_event/mutation/test_projection_mutations.py",
        "tests/command_commit_event/test_projection.py",
        "tests/command_commit_event/test_projection_worker.py",
        "tests/security/test_projection_worker_exclusivity.py",
    ),
    "PKG-22": (
        "tests/recovery/test_consequence_certainty.py",
        "tests/recovery/test_failure_classifier.py",
    ),
    "PKG-23": (
        "tests/recovery/test_lpvs.py",
        "tests/recovery/test_recovery_non_authority.py",
        "tests/recovery/test_recovery_record.py",
    ),
    "PKG-24": (
        "tests/boundaries/test_bnd_017_failure_indeterminate.py",
        "tests/boundaries/test_bnd_018_recovery_rollback.py",
        "tests/recovery/boundaries/test_recovery_service.py",
    ),
    "PKG-25": (
        "tests/security/test_db_principals.py",
        "tests/security/test_service_identity.py",
    ),
    "PKG-26": (
        "tests/security/test_events.py",
        "tests/security/test_workspace.py",
    ),
    "PKG-27": ("tests/security/test_observability.py",),
    "PKG-28": (
        "apps/web/tests/components/display.test.tsx",
        "apps/web/tests/e2e/session-view.spec.ts",
        "apps/web/tests/lib/client.test.ts",
    ),
    "PKG-29": (
        "apps/web/tests/components/decision-display.test.tsx",
        "apps/web/tests/e2e/decision.spec.ts",
        "apps/web/tests/lib/decisionClient.test.ts",
    ),
    "PKG-30": ("tests/e2e/test_proof_bundle_paths.py",),
    "PKG-31": (
        "tests/mutation/harness.py",
        "tests/mutation/mutation_cases.py",
        "tests/mutation/test_pkg31_mutation_registry.py",
    ),
    "PKG-32": (
        "tests/regression/package_dependency_graph.py",
        "tests/regression/test_regression_package_graph.py",
    ),
}


def _is_frontend_path(path: str) -> bool:
    return path.startswith("apps/web/tests/")


PYTHON_TEST_PATHS: dict[str, tuple[str, ...]] = {
    pkg: tuple(p for p in paths if not _is_frontend_path(p))
    for pkg, paths in PACKAGE_TEST_PATHS.items()
}
FRONTEND_TEST_PATHS: dict[str, tuple[str, ...]] = {
    pkg: tuple(p for p in paths if _is_frontend_path(p))
    for pkg, paths in PACKAGE_TEST_PATHS.items()
    if any(_is_frontend_path(p) for p in paths)
}


def downstream_of(package: str) -> frozenset[str]:
    """Every package that (transitively) depends on `package`, per
    `PACKAGE_PREDECESSORS` -- i.e. every package a change to `package`
    could affect. Does not include `package` itself."""
    if package not in PACKAGE_PREDECESSORS:
        raise ValueError(f"unknown package: {package!r}")
    affected: set[str] = set()
    changed = True
    while changed:
        changed = False
        for candidate, predecessors in PACKAGE_PREDECESSORS.items():
            if candidate in affected or candidate == package:
                continue
            if set(predecessors) & (affected | {package}):
                affected.add(candidate)
                changed = True
    return frozenset(affected)


def affected_python_test_paths(changed_packages: tuple[str, ...]) -> frozenset[str]:
    """Union of `PYTHON_TEST_PATHS` for every changed package plus
    every package downstream of it (14 Phase 14: "Run dependency-based
    affected suite"). Never the full suite by default -- a caller that
    wants the full suite asks for it explicitly, this function always
    computes the minimal dependency-justified set."""
    packages: set[str] = set()
    for pkg in changed_packages:
        packages.add(pkg)
        packages |= downstream_of(pkg)
    result: set[str] = set()
    for pkg in packages:
        result |= set(PYTHON_TEST_PATHS.get(pkg, ()))
    return frozenset(result)


__all__ = [
    "PACKAGE_IDS",
    "PACKAGE_PREDECESSORS",
    "PACKAGE_TEST_PATHS",
    "PYTHON_TEST_PATHS",
    "FRONTEND_TEST_PATHS",
    "downstream_of",
    "affected_python_test_paths",
]
