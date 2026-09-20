"""PROOF_CLAIM_MATRIX: the "P-claim matrix artifact" 14 PKG-30's own
FILES_ALLOWED_TO_CREATE line names, alongside the proof bundle and
`tests/e2e`.

TEST ONLY -- same import-graph guard as every other module in this
package (`scripts/check_test_only_imports.py`).

WHY THIS IS A REAL, TYPED, IMPORTABLE PYTHON STRUCTURE, NOT A MARKDOWN
TABLE
--------------------------------------------------------------------
A markdown table asserting "P-08 is exercised by X" is unfalsifiable
by anything except a human re-reading it. A `dict` keyed by the exact
`P-NN` string, whose values name a real, existing test file path this
package's own `test_matrix_evidence_files_exist_and_reference_p_claims`
test (in `tests/e2e/test_proof_bundle_paths.py`... see that file) can
`Path.exists()`-check and `grep`-check for the literal claim string,
turns "the matrix says X is covered" into something a test run either
confirms or falsifies on every CI run -- the same "collect existing
proof, do not merely assert it in prose" discipline 14 §39 states for
`TestProofBundle` itself, applied to this sibling artifact.

WHY EVERY STATUS BELOW IS `EXERCISED` OR `POTENTIALLY_AFFECTED`, NEVER
`INTRODUCED`
--------------------------------------------------------------------
This package's own ARCHITECTURAL_INVARIANT: "TESTPROOFBUNDLE COLLECTS
EXISTING PROOF ONLY." Every one of P-01 through P-25 was already
introduced and independently tested by an earlier package (cited in
each entry's own `evidence_files`); PKG-30 re-exercises six of them
directly through its own six named E2E paths (`tests/e2e/
test_proof_bundle_paths.py`) and leaves the rest correctly marked
`POTENTIALLY_AFFECTED` -- still real, still passing, in the full
regression run, but not re-run a second time by THIS package's own new
test file. HARD-DEP-001/HARD-DEP-002 remain BLOCKED regardless of any
claim's own status here (14's own OBJECTIVE line: "Keep hard
dependencies BLOCKED").
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

PROOF_CLAIM_IDS = tuple(f"P-{n:02d}" for n in range(1, 26))
"""P-01 through P-25, 14's own exact closed set (PROOF_CLAIMS line:
"14 assigns: P-01..P-25")."""


class ProofClaimStatus(Enum):
    """14's own COMPLETION_REPORT field name for tracking each claim:
    "Track each as introduced, exercised, potentially affected, or
    regression required." `REGRESSION_REQUIRED` is not used by any
    entry below -- this package's own RECURSIVE_REGRESSION step found
    none (see the completion report's own RECURSIVE_REGRESSION_RESULTS),
    but the vocabulary stays closed and complete rather than narrowed
    to only the values this run happened to use.
    """

    INTRODUCED = "INTRODUCED"
    EXERCISED = "EXERCISED"
    POTENTIALLY_AFFECTED = "POTENTIALLY_AFFECTED"
    REGRESSION_REQUIRED = "REGRESSION_REQUIRED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True, slots=True)
class ProofClaimEntry:
    claim_id: str
    canonical_result: str
    """12 §4's own "Canonical Result" column text, transcribed
    verbatim -- never paraphrased, so a reader can grep the source
    table and this entry side by side."""
    status: ProofClaimStatus
    evidence_files: tuple[str, ...]
    """Repo-relative paths of real, already-existing test files that
    exercise this claim. At least one entry per claim; PKG-30's own
    six directly-exercised claims additionally cite
    `tests/e2e/test_proof_bundle_paths.py`."""

    def __post_init__(self) -> None:
        if self.claim_id not in PROOF_CLAIM_IDS:
            raise ValueError(f"claim_id must be one of {PROOF_CLAIM_IDS}, got {self.claim_id!r}")
        if not self.evidence_files:
            raise ValueError(f"{self.claim_id}: evidence_files must be non-empty")


PROOF_CLAIM_MATRIX: dict[str, ProofClaimEntry] = {
    e.claim_id: e
    for e in (
        ProofClaimEntry(
            "P-01",
            "Canonical Question exists independently.",
            ProofClaimStatus.POTENTIALLY_AFFECTED,
            (
                "tests/domain/question/test_question.py",
                "tests/domain/question/test_question_repository.py",
            ),
        ),
        ProofClaimEntry(
            "P-02",
            "Write denied; reframe requires new Question lineage.",
            ProofClaimStatus.POTENTIALLY_AFFECTED,
            ("tests/domain/question/test_question.py",),
        ),
        ProofClaimEntry(
            "P-03",
            "Frozen membership remains unchanged.",
            ProofClaimStatus.POTENTIALLY_AFFECTED,
            ("tests/transitions/test_burst_transition_constraints.py",),
        ),
        ProofClaimEntry(
            "P-04",
            "BND-008/BND-009 denies before provider.",
            ProofClaimStatus.POTENTIALLY_AFFECTED,
            ("tests/ai/test_burst_ai_block.py", "tests/boundaries/test_bnd_008_question_burst.py"),
        ),
        ProofClaimEntry(
            "P-05",
            "Only approved post-freeze gateway path runs.",
            ProofClaimStatus.POTENTIALLY_AFFECTED,
            ("tests/ai/test_gateway.py",),
        ),
        ProofClaimEntry(
            "P-06",
            "Derived status retained.",
            ProofClaimStatus.POTENTIALLY_AFFECTED,
            ("tests/ai/test_validator.py", "tests/ai/test_derived_artifact.py"),
        ),
        ProofClaimEntry(
            "P-07",
            "Authority boundary denies.",
            ProofClaimStatus.EXERCISED,
            ("tests/e2e/test_human_decision.py", "tests/e2e/test_proof_bundle_paths.py"),
        ),
        ProofClaimEntry(
            "P-08",
            "Only current QUESTION_SELECTION_RIGHT holder commits.",
            ProofClaimStatus.POTENTIALLY_AFFECTED,
            (
                "tests/authority/test_question_selection_authority.py",
                "tests/command_commit_event/test_question_selection.py",
            ),
        ),
        ProofClaimEntry(
            "P-09",
            "Decision remains absent/UNDER_CONSIDERATION until human action.",
            ProofClaimStatus.EXERCISED,
            ("tests/e2e/test_human_decision.py", "tests/e2e/test_proof_bundle_paths.py"),
        ),
        ProofClaimEntry(
            "P-10",
            "No commit without current binding.",
            ProofClaimStatus.EXERCISED,
            ("tests/authority/test_decision_authority.py", "tests/e2e/test_proof_bundle_paths.py"),
        ),
        ProofClaimEntry(
            "P-11",
            "BND-014 detects revocation and denies.",
            ProofClaimStatus.EXERCISED,
            ("tests/boundaries/test_bnd_014_commit.py", "tests/e2e/test_proof_bundle_paths.py"),
        ),
        ProofClaimEntry(
            "P-12",
            "Binding state is required.",
            ProofClaimStatus.EXERCISED,
            (
                "tests/security/test_habb_grant_constraints.py",
                "tests/e2e/test_proof_bundle_paths.py",
            ),
        ),
        ProofClaimEntry(
            "P-13",
            "Canonical state unchanged.",
            ProofClaimStatus.EXERCISED,
            ("tests/command_commit_event/test_commit.py", "tests/e2e/test_proof_bundle_paths.py"),
        ),
        ProofClaimEntry(
            "P-14",
            "Commit rejected or proof incomplete.",
            ProofClaimStatus.POTENTIALLY_AFFECTED,
            ("tests/evidence/test_freshness.py", "tests/command_commit_event/test_commit.py"),
        ),
        ProofClaimEntry(
            "P-15",
            "Evidence boundary rejects substitution.",
            ProofClaimStatus.POTENTIALLY_AFFECTED,
            ("tests/evidence/test_models.py", "tests/ai/test_derived_artifact.py"),
        ),
        ProofClaimEntry(
            "P-16",
            "Event cannot authorize mutation.",
            ProofClaimStatus.POTENTIALLY_AFFECTED,
            (
                "tests/command_commit_event/test_command_event_split.py",
                "tests/command_commit_event/test_event.py",
            ),
        ),
        ProofClaimEntry(
            "P-17",
            "Projection rebuild only.",
            ProofClaimStatus.POTENTIALLY_AFFECTED,
            (
                "tests/command_commit_event/test_projection.py",
                "tests/command_commit_event/test_projection_worker.py",
            ),
        ),
        ProofClaimEntry(
            "P-18",
            "Technical privilege denies normal path; any privileged tamper remains "
            "illegitimate and detected.",
            ProofClaimStatus.POTENTIALLY_AFFECTED,
            ("tests/security/test_db_principals.py", "tests/security/test_service_identity.py"),
        ),
        ProofClaimEntry(
            "P-19",
            "Existing committed result returned.",
            ProofClaimStatus.POTENTIALLY_AFFECTED,
            ("tests/command_commit_event/test_idempotency.py", "tests/e2e/test_human_decision.py"),
        ),
        ProofClaimEntry(
            "P-20",
            "Retry denied; reconciliation required.",
            ProofClaimStatus.EXERCISED,
            (
                "tests/recovery/test_idempotency_indeterminate_blocks_retry.py",
                "tests/e2e/test_proof_bundle_paths.py",
            ),
        ),
        ProofClaimEntry(
            "P-21",
            "BND-018 denies.",
            ProofClaimStatus.EXERCISED,
            (
                "tests/boundaries/test_bnd_018_recovery_rollback.py",
                "tests/e2e/test_proof_bundle_paths.py",
            ),
        ),
        ProofClaimEntry(
            "P-22",
            "Denied before AI/context/commit.",
            ProofClaimStatus.EXERCISED,
            (
                "tests/security/test_bnd_cross_layer_isolation.py",
                "tests/e2e/test_proof_bundle_paths.py",
            ),
        ),
        ProofClaimEntry(
            "P-23",
            "Credential/network path unavailable.",
            ProofClaimStatus.EXERCISED,
            ("tests/ai/test_gateway.py", "tests/e2e/test_proof_bundle_paths.py"),
        ),
        ProofClaimEntry(
            "P-24",
            "Governed path denies; direct tamper is illegitimate and detectable.",
            ProofClaimStatus.POTENTIALLY_AFFECTED,
            ("tests/security/test_admin_non_authority.py", "tests/security/test_workspace.py"),
        ),
        ProofClaimEntry(
            "P-25",
            "Occurrence cannot be accepted as fully proven legitimate.",
            ProofClaimStatus.EXERCISED,
            (
                "tests/boundaries/test_bnd_018_recovery_rollback.py",
                "tests/evidence/test_provenance.py",
                "tests/e2e/test_proof_bundle_paths.py",
            ),
        ),
    )
}

assert set(PROOF_CLAIM_MATRIX) == set(PROOF_CLAIM_IDS), (
    "PROOF_CLAIM_MATRIX must cover exactly P-01..P-25"
)


__all__ = ["PROOF_CLAIM_IDS", "ProofClaimStatus", "ProofClaimEntry", "PROOF_CLAIM_MATRIX"]
