"""T4 BOUNDARY TEST: BND-018 Recovery / Rollback Boundary.

Pure-Python (no `RecoveryRepository`/database dependency -- unlike
BND-017, this evaluator takes every fact as an already-resolved
`Bnd018Input` field, per this module's own docstring).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from authority.actor import ActorClass, ActorIdentity
from boundaries.bnd_018_recovery_rollback import Bnd018Input, Bnd018RecoveryRollbackEvaluator
from boundaries.registry import BoundaryRegistry, evaluate_chain
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from recovery.models import RecoveryClass
from semantic_types.ids import CorrelationId, WorkspaceId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_EVALUATOR = Bnd018RecoveryRollbackEvaluator()


def _context(*, actor: ActorIdentity) -> BoundaryContext:
    return BoundaryContext(
        workspace_id=WorkspaceId(uuid.uuid4()),
        operation="CMD_RECOVERY_RESOLVE",
        actor=actor,
        correlation_id=CorrelationId(uuid.uuid4()),
        evaluated_at=_NOW,
    )


def _input(
    *,
    recovery_class: RecoveryClass = RecoveryClass.RC_02_RECONCILIATION,
    lpvs_resolved: bool = True,
    restores_already_legitimized_state: bool = True,
    current_human_authority_confirmed: bool = True,
    workspace_scope_preserved: bool = True,
    question_immutability_preserved: bool = True,
    raw_burst_integrity_preserved: bool = True,
    human_ai_distinction_preserved: bool = True,
    authority_history_preserved: bool = True,
    audit_reconstruction_preserved: bool = True,
    no_duplicate_consequence: bool = True,
) -> Bnd018Input:
    return Bnd018Input(
        boundary_id=BoundaryId.BND_018,
        context=_context(actor=ActorIdentity(ActorClass.SYSTEM_SERVICE, "recovery-worker-1")),
        recovery_class=recovery_class,
        lpvs_resolved=lpvs_resolved,
        restores_already_legitimized_state=restores_already_legitimized_state,
        current_human_authority_confirmed=current_human_authority_confirmed,
        workspace_scope_preserved=workspace_scope_preserved,
        question_immutability_preserved=question_immutability_preserved,
        raw_burst_integrity_preserved=raw_burst_integrity_preserved,
        human_ai_distinction_preserved=human_ai_distinction_preserved,
        authority_history_preserved=authority_history_preserved,
        audit_reconstruction_preserved=audit_reconstruction_preserved,
        no_duplicate_consequence=no_duplicate_consequence,
    )


def test_allows_a_fully_proven_deterministic_recovery() -> None:
    """Positive control: SYSTEM_SERVICE, LPVS resolved, restores an
    already-legitimized state, every invariant holds."""
    boundary_input = _input()

    proof = _EVALUATOR.evaluate(boundary_input, boundary_input.context)

    assert proof.result is BoundaryResult.ALLOW
    assert proof.reason_code == "RECOVERY_PERMITTED"


def test_denies_when_lpvs_is_not_resolved() -> None:
    """TESTABLE INVARIANT / mandatory adversarial attack: recover to a
    never-legitimate state. Checked first -- nothing else matters if
    there is no proven legitimate state to recover to at all."""
    boundary_input = _input(
        lpvs_resolved=False,
        restores_already_legitimized_state=False,
        current_human_authority_confirmed=False,
        workspace_scope_preserved=False,
    )

    proof = _EVALUATOR.evaluate(boundary_input, boundary_input.context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "NO_PROVEN_LEGITIMATE_STATE_TO_RECOVER_TO"


def test_denies_ai_processor_unconditionally() -> None:
    """Mandatory adversarial attack (06 section 25 PROHIBITED PATH):
    "AI chooses recovery outcome" -- denied even with every other
    fact proven true."""
    context = _context(actor=ActorIdentity(ActorClass.AI_PROCESSOR, "ai-gateway-1"))
    boundary_input = Bnd018Input(
        boundary_id=BoundaryId.BND_018,
        context=context,
        recovery_class=RecoveryClass.RC_02_RECONCILIATION,
        lpvs_resolved=True,
        restores_already_legitimized_state=True,
        current_human_authority_confirmed=True,
        workspace_scope_preserved=True,
        question_immutability_preserved=True,
        raw_burst_integrity_preserved=True,
        human_ai_distinction_preserved=True,
        authority_history_preserved=True,
        audit_reconstruction_preserved=True,
        no_duplicate_consequence=True,
    )

    proof = _EVALUATOR.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "AI_CANNOT_CHOOSE_RECOVERY_OUTCOME"


def test_human_user_without_current_authority_is_denied() -> None:
    """Mandatory adversarial attack: admin recovery / revoked current
    authority -- a HUMAN_USER discretionary recovery is denied unless
    `current_human_authority_confirmed` is true right now."""
    context = _context(actor=ActorIdentity(ActorClass.HUMAN_USER, "admin-user-1"))
    boundary_input = Bnd018Input(
        boundary_id=BoundaryId.BND_018,
        context=context,
        recovery_class=RecoveryClass.RC_07_MANUAL_DISCRETIONARY_RECOVERY,
        lpvs_resolved=True,
        restores_already_legitimized_state=False,
        current_human_authority_confirmed=False,
        workspace_scope_preserved=True,
        question_immutability_preserved=True,
        raw_burst_integrity_preserved=True,
        human_ai_distinction_preserved=True,
        authority_history_preserved=True,
        audit_reconstruction_preserved=True,
        no_duplicate_consequence=True,
    )

    proof = _EVALUATOR.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "DISCRETIONARY_RECOVERY_REQUIRES_CURRENT_HUMAN_AUTHORITY"


def test_human_user_with_current_authority_and_invariants_is_allowed() -> None:
    context = _context(actor=ActorIdentity(ActorClass.HUMAN_USER, "admin-user-1"))
    boundary_input = Bnd018Input(
        boundary_id=BoundaryId.BND_018,
        context=context,
        recovery_class=RecoveryClass.RC_07_MANUAL_DISCRETIONARY_RECOVERY,
        lpvs_resolved=True,
        restores_already_legitimized_state=False,
        current_human_authority_confirmed=True,
        workspace_scope_preserved=True,
        question_immutability_preserved=True,
        raw_burst_integrity_preserved=True,
        human_ai_distinction_preserved=True,
        authority_history_preserved=True,
        audit_reconstruction_preserved=True,
        no_duplicate_consequence=True,
    )

    proof = _EVALUATOR.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW
    assert proof.reason_code == "RECOVERY_PERMITTED"


def test_deterministic_actor_must_restore_an_already_legitimized_state() -> None:
    """Mandatory adversarial attack: service uses old/invented
    authority to recover to a state that was never legitimate --
    SYSTEM_SERVICE without `restores_already_legitimized_state` is
    denied even though LPVS itself resolved."""
    boundary_input = _input(restores_already_legitimized_state=False)

    proof = _EVALUATOR.evaluate(boundary_input, boundary_input.context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "DETERMINISTIC_RECOVERY_MUST_RESTORE_ALREADY_LEGITIMIZED_STATE"


def test_external_system_actor_follows_the_deterministic_branch() -> None:
    """Novel/adapted attack: EXTERNAL_SYSTEM is not HUMAN_USER and not
    AI_PROCESSOR -- it must fall into the SAME deterministic branch as
    SYSTEM_SERVICE, not silently bypass the legitimized-state check."""
    context = _context(actor=ActorIdentity(ActorClass.EXTERNAL_SYSTEM, "external-webhook-1"))
    boundary_input = Bnd018Input(
        boundary_id=BoundaryId.BND_018,
        context=context,
        recovery_class=RecoveryClass.RC_01_DETERMINISTIC_TECHNICAL_RECOVERY,
        lpvs_resolved=True,
        restores_already_legitimized_state=False,
        current_human_authority_confirmed=True,
        workspace_scope_preserved=True,
        question_immutability_preserved=True,
        raw_burst_integrity_preserved=True,
        human_ai_distinction_preserved=True,
        authority_history_preserved=True,
        audit_reconstruction_preserved=True,
        no_duplicate_consequence=True,
    )

    proof = _EVALUATOR.evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "DETERMINISTIC_RECOVERY_MUST_RESTORE_ALREADY_LEGITIMIZED_STATE"


def test_each_validation_invariant_individually_denies_when_violated() -> None:
    """Mandatory adversarial attacks: erase audit/history, break
    Workspace scope, break Human/AI distinction, duplicate consequence
    via recovery, etc. -- each of the 7 invariants is checked and
    named individually in the DENY reason code."""
    invariant_fields = (
        "workspace_scope_preserved",
        "question_immutability_preserved",
        "raw_burst_integrity_preserved",
        "human_ai_distinction_preserved",
        "authority_history_preserved",
        "audit_reconstruction_preserved",
        "no_duplicate_consequence",
    )
    for field in invariant_fields:
        kwargs = {name: True for name in invariant_fields}
        kwargs[field] = False
        boundary_input = _input(**kwargs)

        proof = _EVALUATOR.evaluate(boundary_input, boundary_input.context)

        assert proof.result is BoundaryResult.DENY, field
        assert proof.reason_code == f"RECOVERY_VALIDATION_INVARIANT_VIOLATED:{field}", field


def test_reports_all_violated_invariants_together() -> None:
    """Novel/adapted attack: multiple invariants broken at once must
    all be named, not just the first -- a partial report would hide
    the full blast radius from audit."""
    boundary_input = _input(
        workspace_scope_preserved=False,
        no_duplicate_consequence=False,
    )

    proof = _EVALUATOR.evaluate(boundary_input, boundary_input.context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == (
        "RECOVERY_VALIDATION_INVARIANT_VIOLATED:workspace_scope_preserved,no_duplicate_consequence"
    )


def test_denies_construction_with_the_wrong_boundary_id() -> None:
    context = _context(actor=ActorIdentity(ActorClass.SYSTEM_SERVICE, "recovery-worker-1"))

    try:
        Bnd018Input(
            boundary_id=BoundaryId.BND_017,  # wrong boundary
            context=context,
            recovery_class=RecoveryClass.RC_02_RECONCILIATION,
            lpvs_resolved=True,
            restores_already_legitimized_state=True,
            current_human_authority_confirmed=True,
            workspace_scope_preserved=True,
            question_immutability_preserved=True,
            raw_burst_integrity_preserved=True,
            human_ai_distinction_preserved=True,
            authority_history_preserved=True,
            audit_reconstruction_preserved=True,
            no_duplicate_consequence=True,
        )
    except ValueError as exc:
        assert "BND_018" in str(exc)
    else:
        raise AssertionError("expected ValueError for a mismatched boundary_id")


def test_denies_construction_with_a_non_recovery_class() -> None:
    context = _context(actor=ActorIdentity(ActorClass.SYSTEM_SERVICE, "recovery-worker-1"))

    try:
        Bnd018Input(
            boundary_id=BoundaryId.BND_018,
            context=context,
            recovery_class="RC-02",  # type: ignore[arg-type]
            lpvs_resolved=True,
            restores_already_legitimized_state=True,
            current_human_authority_confirmed=True,
            workspace_scope_preserved=True,
            question_immutability_preserved=True,
            raw_burst_integrity_preserved=True,
            human_ai_distinction_preserved=True,
            authority_history_preserved=True,
            audit_reconstruction_preserved=True,
            no_duplicate_consequence=True,
        )
    except TypeError as exc:
        assert "recovery_class" in str(exc)
    else:
        raise AssertionError("expected TypeError for a non-RecoveryClass recovery_class")


def test_registers_cleanly_in_the_boundary_registry() -> None:
    """Novel/adapted attack: prove BND-018 composes with the generic
    chain evaluator exactly like every other boundary -- no special-
    casing required."""
    boundary_input = _input()
    registry = BoundaryRegistry()
    registry.register(_EVALUATOR)

    chain_result = evaluate_chain(
        registry, [BoundaryId.BND_018], {BoundaryId.BND_018: boundary_input}, boundary_input.context
    )

    assert chain_result.is_allowed
    assert chain_result.proofs[0].reason_code == "RECOVERY_PERMITTED"


# ---------------------------------------------------------------------------
# MUT-PKG24-02: mutation proof for the AI-actor check (test-only mutant --
# never edits the shipped `boundaries.bnd_018_recovery_rollback` module;
# same "duplicate-and-mutate" discipline as MUT-PKG24-01 above, adapted as a
# full dispatch clone since BND-018 has no repository dependency to neuter
# -- every fact it reasons about is an intrinsic `Bnd018Input` field).
# ---------------------------------------------------------------------------

_MUT_VALIDATION_INVARIANTS = (
    "workspace_scope_preserved",
    "question_immutability_preserved",
    "raw_burst_integrity_preserved",
    "human_ai_distinction_preserved",
    "authority_history_preserved",
    "audit_reconstruction_preserved",
    "no_duplicate_consequence",
)


class _Bnd018WithoutAiCheck:
    """MUTANT (test-only): the same dispatch as
    `Bnd018RecoveryRollbackEvaluator.evaluate` with the "AI cannot
    choose recovery outcome" check removed. If
    `test_denies_ai_processor_unconditionally` were vacuous, this
    mutant would still DENY an AI_PROCESSOR actor. It does not."""

    boundary_id = BoundaryId.BND_018

    def evaluate(self, boundary_input: Bnd018Input, context: BoundaryContext) -> object:
        if not boundary_input.lpvs_resolved:
            return "DENY:NO_PROVEN_LEGITIMATE_STATE_TO_RECOVER_TO"

        # MUTATION: the real evaluator denies ActorClass.AI_PROCESSOR
        # here, unconditionally, before anything else. This mutant
        # skips straight to the HUMAN_USER/deterministic branch.
        if context.actor.actor_class is ActorClass.HUMAN_USER:
            if not boundary_input.current_human_authority_confirmed:
                return "DENY:DISCRETIONARY_RECOVERY_REQUIRES_CURRENT_HUMAN_AUTHORITY"
        else:
            if not boundary_input.restores_already_legitimized_state:
                return "DENY:DETERMINISTIC_RECOVERY_MUST_RESTORE_ALREADY_LEGITIMIZED_STATE"

        violated = tuple(
            name for name in _MUT_VALIDATION_INVARIANTS if not getattr(boundary_input, name)
        )
        if violated:
            return f"DENY:RECOVERY_VALIDATION_INVARIANT_VIOLATED:{','.join(violated)}"
        return "ALLOW:RECOVERY_PERMITTED"


def test_mut_pkg24_02_removing_the_ai_check_would_wrongly_allow_ai_to_recover() -> None:
    """MUT-PKG24-02: with the AI-actor check removed (mutant dispatch),
    the SAME scenario `test_denies_ai_processor_unconditionally` proves
    DENY for now wrongly ALLOWS -- an AI_PROCESSOR actor falls into the
    deterministic (non-HUMAN_USER) branch and, with every other fact
    proven true, is wrongly granted `RECOVERY_PERMITTED`."""
    context = _context(actor=ActorIdentity(ActorClass.AI_PROCESSOR, "ai-gateway-1"))
    boundary_input = Bnd018Input(
        boundary_id=BoundaryId.BND_018,
        context=context,
        recovery_class=RecoveryClass.RC_02_RECONCILIATION,
        lpvs_resolved=True,
        restores_already_legitimized_state=True,
        current_human_authority_confirmed=True,
        workspace_scope_preserved=True,
        question_immutability_preserved=True,
        raw_burst_integrity_preserved=True,
        human_ai_distinction_preserved=True,
        authority_history_preserved=True,
        audit_reconstruction_preserved=True,
        no_duplicate_consequence=True,
    )
    mutant = _Bnd018WithoutAiCheck()

    verdict = mutant.evaluate(boundary_input, context)

    assert verdict == "ALLOW:RECOVERY_PERMITTED"
