"""T2 TRANSITION TEST: `domain.burst_transitions` topology registry.

13 §6 T2 scope: "03 topology and transition eligibility." Pure Python:
mirrors `test_session_transition_registry.py`'s design exactly. The
live constraint proof is `test_burst_transition_constraints.py`.
"""

from __future__ import annotations

from domain.burst import BurstState
from domain.burst_transitions import (
    BURST_TRANSITION_SPECS,
    BurstOperation,
    BurstTransitionId,
    BurstTransitionVerdict,
    legal_state_pairs,
    resolve_burst_transition,
    resolve_burst_transition_by_operation_name,
    resolve_burst_transition_to_state,
)

# 03 §20's 5 transitions, transcribed independently of the registry
# under test, with TRN-BURST-005's two legal sources expanded.
_LEGAL_PAIRS = frozenset(
    {
        (None, BurstState.PREPARED),
        (BurstState.PREPARED, BurstState.ACTIVE),
        (BurstState.ACTIVE, BurstState.PAUSED),
        (BurstState.PAUSED, BurstState.ACTIVE),
        (BurstState.ACTIVE, BurstState.COMPLETED),
        (BurstState.PAUSED, BurstState.COMPLETED),
    }
)


def test_registry_contains_exactly_the_five_03_contracts() -> None:
    assert set(BURST_TRANSITION_SPECS) == set(BurstTransitionId)
    assert len(BURST_TRANSITION_SPECS) == 5


def test_registry_topology_matches_03_section_20_exactly() -> None:
    assert legal_state_pairs() == _LEGAL_PAIRS


def test_creation_transition_has_no_source_state() -> None:
    """TRN-BURST-001 CURRENT STATE: "QuestionBurst absent"."""
    creation = BURST_TRANSITION_SPECS[BurstTransitionId.TRN_BURST_001]

    assert creation.from_state is None
    assert creation.to_state is BurstState.PREPARED


def test_complete_burst_has_two_legal_sources() -> None:
    """03 TRN-BURST-005 CURRENT STATE: "ACTIVE or PAUSED"."""
    complete = BURST_TRANSITION_SPECS[BurstTransitionId.TRN_BURST_005]

    assert complete.from_state == (BurstState.ACTIVE, BurstState.PAUSED)
    assert complete.to_state is BurstState.COMPLETED


def test_completed_is_not_a_source_state_of_any_registered_transition() -> None:
    """03 §19.5: COMPLETED is terminal."""
    for spec in BURST_TRANSITION_SPECS.values():
        sources = spec.from_state
        if sources is None:
            continue
        flat = sources if isinstance(sources, tuple) else (sources,)
        assert BurstState.COMPLETED not in flat


def test_resolve_by_id_reports_state_eligible_for_every_legitimate_pair() -> None:
    for transition_id, spec in BURST_TRANSITION_SPECS.items():
        sources = spec.from_state
        flat = () if sources is None else (sources if isinstance(sources, tuple) else (sources,))
        for source in flat or (None,):
            resolution = resolve_burst_transition(current_state=source, transition_id=transition_id)
            assert resolution.verdict is BurstTransitionVerdict.STATE_ELIGIBLE
            assert resolution.spec is spec


def test_illegal_transition_is_denied() -> None:
    """Mandatory-category adversarial attack: illegal transition."""
    illegal_pairs = (
        (BurstState.PREPARED, BurstState.PAUSED),
        (BurstState.PREPARED, BurstState.COMPLETED),
        (BurstState.ACTIVE, BurstState.PREPARED),
        (BurstState.PAUSED, BurstState.PREPARED),
    )
    for source, target in illegal_pairs:
        resolution = resolve_burst_transition_to_state(current_state=source, target_state=target)
        assert resolution.verdict is BurstTransitionVerdict.DENIED_ILLEGAL_TRANSITION, (
            f"{source} -> {target} must be denied"
        )
        assert resolution.spec is None


def test_completed_never_transitions_anywhere() -> None:
    """03 §19.5: COMPLETED is terminal for the same QuestionBurst."""
    for target in BurstState:
        resolution = resolve_burst_transition_to_state(
            current_state=BurstState.COMPLETED, target_state=target
        )
        assert resolution.verdict is BurstTransitionVerdict.DENIED_TERMINAL_STATE, (
            f"COMPLETED -> {target} must be denied as terminal"
        )
        assert resolution.spec is None


def test_unknown_transition_name_is_denied() -> None:
    """Mandatory-category adversarial attack: unknown transition."""
    resolution = resolve_burst_transition_by_operation_name(
        current_state=BurstState.PREPARED, operation_name="TELEPORT_TO_ACTIVE"
    )
    assert resolution.verdict is BurstTransitionVerdict.DENIED_UNKNOWN_TRANSITION
    assert resolution.spec is None


def test_every_legitimate_operation_name_resolves_from_its_source() -> None:
    for operation in BurstOperation:
        assert any(spec.operation is operation for spec in BURST_TRANSITION_SPECS.values())


def test_controller_supplied_target_state_cannot_skip_the_chain() -> None:
    """Mandatory-category adversarial attack: controller-supplied
    target state. Exhaustive over the full 4x4 state matrix.
    """
    for source in BurstState:
        for target in BurstState:
            resolution = resolve_burst_transition_to_state(
                current_state=source, target_state=target
            )
            if (source, target) in _LEGAL_PAIRS:
                assert resolution.is_state_eligible
            else:
                assert not resolution.is_state_eligible, (
                    f"{source} -> {target} must not be eligible"
                )


def test_prepare_burst_against_an_existing_burst_is_denied() -> None:
    """TRN-BURST-001 requires CURRENT STATE "QuestionBurst absent"."""
    resolution = resolve_burst_transition(
        current_state=BurstState.PREPARED, transition_id=BurstTransitionId.TRN_BURST_001
    )
    assert resolution.verdict is BurstTransitionVerdict.DENIED_BURST_ALREADY_EXISTS


def test_state_eligible_verdict_never_appears_without_a_governing_spec() -> None:
    for source in list(BurstState) + [None]:
        for target in BurstState:
            resolution = resolve_burst_transition_to_state(
                current_state=source, target_state=target
            )
            if resolution.verdict is not BurstTransitionVerdict.STATE_ELIGIBLE:
                assert resolution.spec is None
