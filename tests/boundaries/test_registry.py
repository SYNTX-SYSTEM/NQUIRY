"""T4 BOUNDARY TEST: `boundaries.registry` — registration and the
monotonic-restriction chain evaluator.

13 §6 T4 scope: "Boundary convergence and monotonic restriction ...
DENY/REQUIRE/ESCALATE/ALLOW as approved." P-13
(T13-P13-DENY-TERMINAL): "Boundary DENY prevents consequence ...
downstream override DENY ... no downstream override."

Pure-Python fixtures prove the generic engine's own contract (registry
collision, chain short-circuit, all four mandatory failure classes).
The cross-layer section at the bottom proves the same engine against
REAL predecessor logic -- PKG-03's `AuthorityResolver` and PKG-05's
`domain.session_transitions` -- via test-only `BoundaryEvaluator`
implementations that are never registered by production code (see
`packages/boundaries/__init__.py`'s docstring for why: implementing
BND-005/BND-007 for real is PKG-09's scope, not this package's).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from authority.actor import ActorClass, ActorIdentity
from authority.resolver import AuthorityRequest, AuthorityResolver, AuthorityVerdict
from boundaries.registry import (
    BoundaryRegistrationError,
    BoundaryRegistry,
    evaluate_chain,
)
from boundaries.types import BoundaryContext, BoundaryId, BoundaryProof, BoundaryResult
from domain.session import SessionState
from domain.session_transitions import resolve_session_transition_to_state
from governance.authority_binding import AuthorityBindingState, AuthorityClass
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.tables import human_authority_bindings_table
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import CorrelationId, UserId, WorkspaceId
from semantic_types.versions import ContractVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


def _actor() -> ActorIdentity:
    return ActorIdentity(ActorClass.HUMAN_USER, UserId(uuid.uuid4()))


def _context(**overrides: object) -> BoundaryContext:
    defaults: dict[str, object] = {
        "workspace_id": WorkspaceId(uuid.uuid4()),
        "operation": "TEST_OPERATION",
        "actor": _actor(),
        "correlation_id": CorrelationId(uuid.uuid4()),
        "evaluated_at": _NOW,
    }
    defaults.update(overrides)
    return BoundaryContext(**defaults)  # type: ignore[arg-type]


@dataclass(frozen=True, slots=True)
class _StubInput:
    boundary_id: BoundaryId
    context: BoundaryContext


class _FixedResultEvaluator:
    """Test-only evaluator returning a pre-programmed result, counting
    invocations so a test can prove it was (or was not) called.
    """

    def __init__(self, boundary_id: BoundaryId, result: BoundaryResult) -> None:
        self.boundary_id = boundary_id
        self.boundary_version = ContractVersion("1")
        self._result = result
        self.call_count = 0

    def evaluate(self, boundary_input: object, context: BoundaryContext) -> BoundaryProof:
        self.call_count += 1
        return BoundaryProof(
            boundary_id=self.boundary_id,
            boundary_version=self.boundary_version,
            result=self._result,
            reason_code="FIXED_RESULT",
            workspace_id=context.workspace_id,
            actor=context.actor,
            input_refs=(),
            authoritative_version_refs=(),
            authority_proof=None,
            evidence_proof_refs=(),
            evaluated_at=context.evaluated_at,
            correlation_id=context.correlation_id,
        )


class _RaisingEvaluator:
    boundary_id = BoundaryId.BND_003
    boundary_version = ContractVersion("1")

    def evaluate(self, boundary_input: object, context: BoundaryContext) -> BoundaryProof:
        raise RuntimeError("simulated evaluator crash")


class _MalformedResultEvaluator:
    """Returns a proof for the WRONG boundary_id -- one of the
    "missing/malformed result" shapes `evaluate_chain` must reject.
    """

    boundary_id = BoundaryId.BND_004
    boundary_version = ContractVersion("1")

    def evaluate(self, boundary_input: object, context: BoundaryContext) -> BoundaryProof:
        return BoundaryProof(
            boundary_id=BoundaryId.BND_005,  # wrong -- this evaluator is BND_004
            boundary_version=self.boundary_version,
            result=BoundaryResult.ALLOW,
            reason_code="WRONG_BOUNDARY",
            workspace_id=context.workspace_id,
            actor=context.actor,
            input_refs=(),
            authoritative_version_refs=(),
            authority_proof=None,
            evidence_proof_refs=(),
            evaluated_at=context.evaluated_at,
            correlation_id=context.correlation_id,
        )


class _NoneReturningEvaluator:
    boundary_id = BoundaryId.BND_006
    boundary_version = ContractVersion("1")

    def evaluate(self, boundary_input: object, context: BoundaryContext) -> BoundaryProof:
        return None  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# BoundaryRegistry
# ---------------------------------------------------------------------------


def test_register_and_get_round_trip() -> None:
    registry = BoundaryRegistry()
    evaluator = _FixedResultEvaluator(BoundaryId.BND_001, BoundaryResult.ALLOW)

    registry.register(evaluator)

    assert registry.get(BoundaryId.BND_001) is evaluator


def test_get_returns_none_for_an_unregistered_boundary() -> None:
    registry = BoundaryRegistry()

    assert registry.get(BoundaryId.BND_001) is None


def test_duplicate_registration_is_rejected() -> None:
    """No silent overwrite: exactly one evaluator per boundary."""
    registry = BoundaryRegistry()
    registry.register(_FixedResultEvaluator(BoundaryId.BND_001, BoundaryResult.ALLOW))

    with pytest.raises(BoundaryRegistrationError):
        registry.register(_FixedResultEvaluator(BoundaryId.BND_001, BoundaryResult.DENY))


# ---------------------------------------------------------------------------
# evaluate_chain: happy path and monotonic restriction
# ---------------------------------------------------------------------------


def test_all_allow_chain_reaches_the_end() -> None:
    registry = BoundaryRegistry()
    evaluators = [
        _FixedResultEvaluator(BoundaryId.BND_001, BoundaryResult.ALLOW),
        _FixedResultEvaluator(BoundaryId.BND_002, BoundaryResult.ALLOW),
        _FixedResultEvaluator(BoundaryId.BND_003, BoundaryResult.ALLOW),
    ]
    for e in evaluators:
        registry.register(e)
    context = _context()
    ordered = [BoundaryId.BND_001, BoundaryId.BND_002, BoundaryId.BND_003]
    inputs = {bid: _StubInput(bid, context) for bid in ordered}

    result = evaluate_chain(registry, ordered, inputs, context)

    assert result.result is BoundaryResult.ALLOW
    assert result.is_allowed
    assert len(result.proofs) == 3
    assert all(e.call_count == 1 for e in evaluators)
    assert result.terminal_boundary_id is BoundaryId.BND_003


def test_empty_chain_is_vacuously_allowed() -> None:
    registry = BoundaryRegistry()

    result = evaluate_chain(registry, [], {}, _context())

    assert result.result is BoundaryResult.ALLOW
    assert result.proofs == ()
    assert result.terminal_boundary_id is None


@pytest.mark.parametrize(
    "terminal_result", [BoundaryResult.DENY, BoundaryResult.REQUIRE, BoundaryResult.ESCALATE]
)
def test_deny_require_escalate_all_stop_the_chain_and_block_downstream(
    terminal_result: BoundaryResult,
) -> None:
    """Mandatory adversarial attack: DENY followed by ALLOW. Novel
    attack: REQUIRE/ESCALATE also block, not only DENY (06 section 3's
    algebra treats all three identically -- "cannot become downstream
    ALLOW").
    """
    registry = BoundaryRegistry()
    terminal_evaluator = _FixedResultEvaluator(BoundaryId.BND_001, terminal_result)
    downstream_spy = _FixedResultEvaluator(BoundaryId.BND_002, BoundaryResult.ALLOW)
    registry.register(terminal_evaluator)
    registry.register(downstream_spy)
    context = _context()
    ordered = [BoundaryId.BND_001, BoundaryId.BND_002]
    inputs = {bid: _StubInput(bid, context) for bid in ordered}

    result = evaluate_chain(registry, ordered, inputs, context)

    assert result.result is terminal_result
    assert result.result is not BoundaryResult.ALLOW
    # The strongest available proof: the downstream evaluator was never
    # even invoked, not merely "invoked but its ALLOW was ignored".
    assert downstream_spy.call_count == 0
    assert len(result.proofs) == 1
    assert result.terminal_boundary_id is BoundaryId.BND_001


def test_unknown_boundary_fails_closed() -> None:
    """Mandatory adversarial attack: unknown boundary."""
    registry = BoundaryRegistry()  # nothing registered
    context = _context()

    result = evaluate_chain(registry, [BoundaryId.BND_001], {}, context)

    assert result.result is BoundaryResult.DENY
    assert result.proofs[0].reason_code == "UNKNOWN_BOUNDARY_NOT_REGISTERED"


def test_missing_boundary_input_fails_closed() -> None:
    registry = BoundaryRegistry()
    registry.register(_FixedResultEvaluator(BoundaryId.BND_001, BoundaryResult.ALLOW))
    context = _context()

    result = evaluate_chain(registry, [BoundaryId.BND_001], {}, context)  # no input supplied

    assert result.result is BoundaryResult.DENY
    assert result.proofs[0].reason_code == "MISSING_BOUNDARY_INPUT"


def test_evaluator_exception_fails_closed() -> None:
    """Mandatory adversarial attack: evaluator exception. 14 PKG-08
    FAILURE_RECOVERY: "Unknown/exception on consequential chain cannot
    silently ALLOW."
    """
    registry = BoundaryRegistry()
    registry.register(_RaisingEvaluator())
    context = _context()
    inputs = {BoundaryId.BND_003: _StubInput(BoundaryId.BND_003, context)}

    result = evaluate_chain(registry, [BoundaryId.BND_003], inputs, context)

    assert result.result is BoundaryResult.DENY
    assert "EVALUATOR_EXCEPTION" in result.proofs[0].reason_code
    assert "RuntimeError" in result.proofs[0].reason_code


def test_evaluator_returning_a_proof_for_the_wrong_boundary_fails_closed() -> None:
    """Mandatory adversarial attack: missing/malformed result --
    variant where an evaluator answers for the wrong boundary_id.
    """
    registry = BoundaryRegistry()
    registry.register(_MalformedResultEvaluator())
    context = _context()
    inputs = {BoundaryId.BND_004: _StubInput(BoundaryId.BND_004, context)}

    result = evaluate_chain(registry, [BoundaryId.BND_004], inputs, context)

    assert result.result is BoundaryResult.DENY
    assert result.proofs[0].reason_code == "MALFORMED_EVALUATOR_RESULT"
    assert (
        result.proofs[0].boundary_id is BoundaryId.BND_004
    )  # the synthetic proof, not the bad one


def test_evaluator_returning_none_fails_closed() -> None:
    """Mandatory adversarial attack: missing result."""
    registry = BoundaryRegistry()
    registry.register(_NoneReturningEvaluator())
    context = _context()
    inputs = {BoundaryId.BND_006: _StubInput(BoundaryId.BND_006, context)}

    result = evaluate_chain(registry, [BoundaryId.BND_006], inputs, context)

    assert result.result is BoundaryResult.DENY
    assert result.proofs[0].reason_code == "MALFORMED_EVALUATOR_RESULT"


def test_no_caching_surface_exists_for_a_prior_proof() -> None:
    """Mandatory adversarial attack: cached ALLOW. Structural proof:
    neither `BoundaryRegistry` nor `evaluate_chain` exposes any
    parameter or method that accepts a previously produced
    `BoundaryProof`/`BoundaryChainResult` as input.
    """
    import inspect

    chain_params = inspect.signature(evaluate_chain).parameters
    assert not any("proof" in name.lower() or "result" in name.lower() for name in chain_params)
    registry_methods = [name for name in vars(BoundaryRegistry) if not name.startswith("_")]
    assert registry_methods == ["register", "get"]


def test_repeated_calls_re_evaluate_rather_than_reuse_a_prior_result() -> None:
    """Directly exercises the "always re-reads live" guarantee: calling
    `evaluate_chain` twice against an evaluator whose answer changes
    between calls returns the new answer, not a memoized old one.
    """
    registry = BoundaryRegistry()
    evaluator = _FixedResultEvaluator(BoundaryId.BND_001, BoundaryResult.ALLOW)
    registry.register(evaluator)
    context = _context()
    inputs = {BoundaryId.BND_001: _StubInput(BoundaryId.BND_001, context)}

    first = evaluate_chain(registry, [BoundaryId.BND_001], inputs, context)
    evaluator._result = BoundaryResult.DENY  # simulate the underlying fact changing
    second = evaluate_chain(registry, [BoundaryId.BND_001], inputs, context)

    assert first.result is BoundaryResult.ALLOW
    assert second.result is BoundaryResult.DENY
    assert evaluator.call_count == 2


# ---------------------------------------------------------------------------
# Cross-layer proof: real AuthorityResolver + real session_transitions,
# never registered by production code (see module docstring).
# ---------------------------------------------------------------------------


class _AuthorityBoundaryEvaluator:
    """Test-only evaluator wrapping the real `AuthorityResolver` --
    proves the engine's composition semantics against genuine PKG-03
    predecessor logic, not a stub.
    """

    boundary_id = BoundaryId.BND_005
    boundary_version = ContractVersion("1")

    def __init__(
        self,
        membership_repository: SqlAlchemyMembershipRepository,
        authority_binding_repository: SqlAlchemyAuthorityBindingRepository,
        required_authority_class: AuthorityClass,
        scope_type: str,
        scope_id: uuid.UUID,
    ) -> None:
        self._membership_repository = membership_repository
        self._authority_binding_repository = authority_binding_repository
        self._required_authority_class = required_authority_class
        self._scope_type = scope_type
        self._scope_id = scope_id
        self.call_count = 0

    def evaluate(self, boundary_input: object, context: BoundaryContext) -> BoundaryProof:
        self.call_count += 1
        resolver = AuthorityResolver(
            self._membership_repository, self._authority_binding_repository, FixedClock(_NOW)
        )
        resolution = resolver.resolve(
            AuthorityRequest(
                actor=context.actor,
                workspace_id=context.workspace_id,
                operation=context.operation,
                required_authority_class=self._required_authority_class,
                scope_type=self._scope_type,
                scope_id=self._scope_id,
            )
        )
        result = (
            BoundaryResult.ALLOW
            if resolution.verdict is AuthorityVerdict.GRANTED
            else BoundaryResult.DENY
        )
        return BoundaryProof(
            boundary_id=self.boundary_id,
            boundary_version=self.boundary_version,
            result=result,
            reason_code=resolution.proof.reason.value,
            workspace_id=context.workspace_id,
            actor=context.actor,
            input_refs=(),
            authoritative_version_refs=(),
            authority_proof=resolution.proof,
            evidence_proof_refs=(),
            evaluated_at=context.evaluated_at,
            correlation_id=context.correlation_id,
        )


class _StateTransitionBoundaryEvaluator:
    """Test-only evaluator wrapping real
    `domain.session_transitions.resolve_session_transition_to_state`."""

    boundary_id = BoundaryId.BND_007
    boundary_version = ContractVersion("1")

    def __init__(self, current_state: SessionState, target_state: SessionState) -> None:
        self._current_state = current_state
        self._target_state = target_state
        self.call_count = 0

    def evaluate(self, boundary_input: object, context: BoundaryContext) -> BoundaryProof:
        self.call_count += 1
        resolution = resolve_session_transition_to_state(
            current_state=self._current_state, target_state=self._target_state
        )
        result = BoundaryResult.ALLOW if resolution.is_state_eligible else BoundaryResult.DENY
        return BoundaryProof(
            boundary_id=self.boundary_id,
            boundary_version=self.boundary_version,
            result=result,
            reason_code=resolution.verdict.value,
            workspace_id=context.workspace_id,
            actor=context.actor,
            input_refs=(),
            authoritative_version_refs=(),
            authority_proof=None,
            evidence_proof_refs=(),
            evaluated_at=context.evaluated_at,
            correlation_id=context.correlation_id,
        )


def _grant_session_control_right(
    connection: sa.Connection, *, workspace_id: WorkspaceId, user_id: UserId
) -> None:
    connection.execute(
        sa.insert(human_authority_bindings_table).values(
            id=_ID_GEN.new_uuid(),
            workspace_id=workspace_id.value,
            human_user_id=user_id.value,
            authority_class=AuthorityClass.SESSION_CONTROL_RIGHT.value,
            scope_type="WORKSPACE",
            scope_id=workspace_id.value,
            authority_source="LEVEL_1_EXPLICIT",
            granted_by_user_id=user_id.value,
            granted_at=_NOW,
            state=AuthorityBindingState.ACTIVE.value,
            record_version=1,
        )
    )


def test_cross_layer_chain_allows_through_to_state_transition_when_authority_granted(
    db_connection: sa.Connection,
) -> None:
    """Real predecessor proof: a genuinely granted SESSION_CONTROL_RIGHT
    (PKG-03/04) plus a genuinely legal Session transition (PKG-05) both
    resolve ALLOW, and the chain reaches its end.
    """
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="chain-allow@nonproof.test")
    _grant_session_control_right(
        db_connection, workspace_id=result.workspace_id, user_id=result.owner_user_id
    )
    membership_repo = SqlAlchemyMembershipRepository(db_connection)
    binding_repo = SqlAlchemyAuthorityBindingRepository(db_connection)

    authority_evaluator = _AuthorityBoundaryEvaluator(
        membership_repo,
        binding_repo,
        AuthorityClass.SESSION_CONTROL_RIGHT,
        "WORKSPACE",
        result.workspace_id.value,
    )
    transition_evaluator = _StateTransitionBoundaryEvaluator(
        SessionState.DRAFT,
        SessionState.SETUP,  # a genuinely legal pair, 03 section 13.2
    )
    registry = BoundaryRegistry()
    registry.register(authority_evaluator)
    registry.register(transition_evaluator)

    context = _context(
        workspace_id=result.workspace_id,
        operation="BEGIN_SETUP",
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    ordered = [BoundaryId.BND_005, BoundaryId.BND_007]
    inputs = {bid: _StubInput(bid, context) for bid in ordered}

    chain_result = evaluate_chain(registry, ordered, inputs, context)

    assert chain_result.result is BoundaryResult.ALLOW
    assert authority_evaluator.call_count == 1
    assert transition_evaluator.call_count == 1
    assert chain_result.proofs[0].authority_proof is not None
    assert chain_result.proofs[0].authority_proof.reason.value == "GRANTED_EFFECTIVE_BINDING"


def test_cross_layer_real_authority_deny_terminates_before_state_evaluator_runs(
    db_connection: sa.Connection,
) -> None:
    """P-13's own scenario, with genuine predecessor logic: no
    SESSION_CONTROL_RIGHT binding exists, so the real `AuthorityResolver`
    genuinely denies -- and the downstream state-transition evaluator,
    even though it would have found the target state-eligible, is
    proven never to run.
    """
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="chain-deny@nonproof.test")
    # Deliberately no SESSION_CONTROL_RIGHT granted.
    membership_repo = SqlAlchemyMembershipRepository(db_connection)
    binding_repo = SqlAlchemyAuthorityBindingRepository(db_connection)

    authority_evaluator = _AuthorityBoundaryEvaluator(
        membership_repo,
        binding_repo,
        AuthorityClass.SESSION_CONTROL_RIGHT,
        "WORKSPACE",
        result.workspace_id.value,
    )
    transition_evaluator = _StateTransitionBoundaryEvaluator(
        SessionState.DRAFT,
        SessionState.SETUP,  # would be ALLOW if ever reached
    )
    registry = BoundaryRegistry()
    registry.register(authority_evaluator)
    registry.register(transition_evaluator)

    context = _context(
        workspace_id=result.workspace_id,
        operation="BEGIN_SETUP",
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    ordered = [BoundaryId.BND_005, BoundaryId.BND_007]
    inputs = {bid: _StubInput(bid, context) for bid in ordered}

    chain_result = evaluate_chain(registry, ordered, inputs, context)

    assert chain_result.result is BoundaryResult.DENY
    assert authority_evaluator.call_count == 1
    assert transition_evaluator.call_count == 0  # never invoked -- the whole point of P-13
    assert len(chain_result.proofs) == 1
    assert chain_result.proofs[0].authority_proof is not None
    assert chain_result.proofs[0].authority_proof.reason.value == "DENIED_NO_MATCHING_BINDING"


def test_cross_workspace_actor_is_denied_by_the_real_authority_evaluator(
    db_connection: sa.Connection,
) -> None:
    """Mandatory-category Workspace attack, exercised through the
    boundary engine: an actor's binding in Workspace A grants nothing
    when the chain is evaluated against Workspace B.
    """
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    workspace_a = bootstrap.seed(owner_email="cross-a@nonproof.test")
    workspace_b = bootstrap.seed(owner_email="cross-b@nonproof.test")
    _grant_session_control_right(
        db_connection, workspace_id=workspace_a.workspace_id, user_id=workspace_a.owner_user_id
    )
    membership_repo = SqlAlchemyMembershipRepository(db_connection)
    binding_repo = SqlAlchemyAuthorityBindingRepository(db_connection)

    authority_evaluator = _AuthorityBoundaryEvaluator(
        membership_repo,
        binding_repo,
        AuthorityClass.SESSION_CONTROL_RIGHT,
        "WORKSPACE",
        workspace_b.workspace_id.value,
    )
    registry = BoundaryRegistry()
    registry.register(authority_evaluator)

    context = _context(
        workspace_id=workspace_b.workspace_id,
        operation="BEGIN_SETUP",
        actor=ActorIdentity(ActorClass.HUMAN_USER, workspace_a.owner_user_id),
    )
    inputs = {BoundaryId.BND_005: _StubInput(BoundaryId.BND_005, context)}

    chain_result = evaluate_chain(registry, [BoundaryId.BND_005], inputs, context)

    assert chain_result.result is BoundaryResult.DENY
