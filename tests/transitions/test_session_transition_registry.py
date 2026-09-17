"""T2 TRANSITION TEST: `domain.session_transitions` topology registry.

13 §6 T2 scope: "03 topology and transition eligibility." Pure Python:
no database, no Command, no boundary evaluator -- this proves the
registry data matches 03 §15/§16 and that the evaluator is
default-DENY. The live constraint proof (that PostgreSQL enforces the
identical topology independently) is
`test_session_transition_constraints.py`.
"""

from __future__ import annotations

from domain.session import TERMINAL_SESSION_STATES, SessionState
from domain.session_transitions import (
    SESSION_TRANSITION_SPECS,
    SessionOperation,
    SessionTransitionId,
    SessionTransitionVerdict,
    legal_state_pairs,
    resolve_session_transition,
    resolve_session_transition_by_operation_name,
    resolve_session_transition_to_state,
)

# 03 §13.2's chain, transcribed independently of the registry under
# test.
_SOURCE_ORDERED_STATES = (
    SessionState.DRAFT,
    SessionState.SETUP,
    SessionState.CHALLENGE_CAPTURE,
    SessionState.QUESTION_GENERATION,
    SessionState.QUESTION_CAPTURE,
    SessionState.ANALYSIS,
    SessionState.REFLECTION,
    SessionState.QUESTION_SELECTION,
    SessionState.INVESTIGATION,
    SessionState.EXPERIMENT,
    SessionState.ACTION,
    SessionState.REVIEW,
    SessionState.CLOSED,
)
_SOURCE_CHAIN_PAIRS = frozenset(
    zip(_SOURCE_ORDERED_STATES, _SOURCE_ORDERED_STATES[1:], strict=False)
)

# 03 §16's illegal set, transcribed verbatim (states as pairs; the
# general "CLOSED -> any Session state" rule is checked separately
# below over the full state space).
_ILLEGAL_PAIRS = (
    (SessionState.DRAFT, SessionState.CHALLENGE_CAPTURE),
    (SessionState.DRAFT, SessionState.QUESTION_GENERATION),
    (SessionState.SETUP, SessionState.QUESTION_GENERATION),
    (SessionState.CHALLENGE_CAPTURE, SessionState.ANALYSIS),
    (SessionState.QUESTION_GENERATION, SessionState.ANALYSIS),
    (SessionState.QUESTION_CAPTURE, SessionState.REFLECTION),
    (SessionState.ANALYSIS, SessionState.QUESTION_SELECTION),
    (SessionState.REFLECTION, SessionState.INVESTIGATION),
    (SessionState.QUESTION_SELECTION, SessionState.EXPERIMENT),
    (SessionState.INVESTIGATION, SessionState.ACTION),
    (SessionState.EXPERIMENT, SessionState.REVIEW),
    (SessionState.ACTION, SessionState.CLOSED),
    (SessionState.REVIEW, SessionState.DRAFT),
)


def test_registry_contains_exactly_the_thirteen_03_contracts() -> None:
    assert set(SESSION_TRANSITION_SPECS) == set(SessionTransitionId)
    assert len(SESSION_TRANSITION_SPECS) == 13


def test_registry_topology_matches_03_section_13_2_chain_exactly() -> None:
    """The registry's non-creation pairs must equal 03's ordered chain
    -- no more, no fewer.
    """
    non_creation_pairs = {
        (spec.from_state, spec.to_state)
        for spec in SESSION_TRANSITION_SPECS.values()
        if spec.from_state is not None
    }

    assert non_creation_pairs == _SOURCE_CHAIN_PAIRS
    assert legal_state_pairs() == _SOURCE_CHAIN_PAIRS | {(None, SessionState.DRAFT)}


def test_creation_transition_has_no_source_state() -> None:
    """TRN-SESS-001 CURRENT STATE: "Session absent" -- the only spec
    for which `from_state is None`.
    """
    creation = SESSION_TRANSITION_SPECS[SessionTransitionId.TRN_SESS_001]

    assert creation.from_state is None
    assert creation.to_state is SessionState.DRAFT
    no_source = [spec for spec in SESSION_TRANSITION_SPECS.values() if spec.from_state is None]
    assert no_source == [creation]


def test_closed_is_not_a_source_state_of_any_registered_transition() -> None:
    """03 §13.3 / AC-03-001: CLOSED is terminal. If it appeared as a
    source, the registry itself would already be wrong regardless of
    what the evaluator does with it.
    """
    sources = {spec.from_state for spec in SESSION_TRANSITION_SPECS.values()}

    assert SessionState.CLOSED not in sources


def test_resolve_by_id_reports_state_eligible_for_every_legitimate_pair() -> None:
    for transition_id, spec in SESSION_TRANSITION_SPECS.items():
        resolution = resolve_session_transition(
            current_state=spec.from_state, transition_id=transition_id
        )

        assert resolution.verdict is SessionTransitionVerdict.STATE_ELIGIBLE
        assert resolution.spec is spec


def test_illegal_transition_is_denied_for_every_03_section_16_pair() -> None:
    """Mandatory adversarial attack: illegal transition."""
    for source, target in _ILLEGAL_PAIRS:
        resolution = resolve_session_transition_to_state(current_state=source, target_state=target)

        assert resolution.verdict is SessionTransitionVerdict.DENIED_ILLEGAL_TRANSITION, (
            f"{source} -> {target} must be denied (03 section 16)"
        )
        assert resolution.spec is None


def test_closed_never_transitions_anywhere() -> None:
    """03 §16 general rule: "CLOSED -> any Session state" is illegal.
    Exhaustive over the full state space, not just the enumerated
    examples.
    """
    for target in SessionState:
        resolution = resolve_session_transition_to_state(
            current_state=SessionState.CLOSED, target_state=target
        )

        assert resolution.verdict is SessionTransitionVerdict.DENIED_TERMINAL_STATE, (
            f"CLOSED -> {target} must be denied as terminal"
        )
        assert resolution.spec is None


def test_unknown_transition_name_is_denied() -> None:
    """Mandatory adversarial attack: unknown transition."""
    resolution = resolve_session_transition_by_operation_name(
        current_state=SessionState.DRAFT, operation_name="TELEPORT_TO_CLOSED"
    )

    assert resolution.verdict is SessionTransitionVerdict.DENIED_UNKNOWN_TRANSITION
    assert resolution.spec is None


def test_unknown_transition_id_is_denied() -> None:
    """A `SessionTransitionId` cannot itself be forged (it is a closed
    enum), but an operation name outside `SessionOperation` must be
    denied the same way a forged ID would be if one existed.
    """
    for real_name in SessionOperation:
        # Sanity: every legitimate name resolves from *some* state.
        assert any(spec.operation is real_name for spec in SESSION_TRANSITION_SPECS.values())

    resolution = resolve_session_transition_by_operation_name(
        current_state=None, operation_name="CREATE_SESSION_AS_ADMIN"
    )
    assert resolution.verdict is SessionTransitionVerdict.DENIED_UNKNOWN_TRANSITION


def test_controller_supplied_target_state_cannot_skip_the_chain() -> None:
    """Mandatory adversarial attack: controller-supplied target state.

    An HTTP controller that let a caller name any target state
    (instead of an operation) must still be refused for every
    non-adjacent pair -- this is the direct test of the "generic
    setter" collapse the package invariant forbids.
    """
    for source in SessionState:
        for target in SessionState:
            resolution = resolve_session_transition_to_state(
                current_state=source, target_state=target
            )
            if (source, target) in _SOURCE_CHAIN_PAIRS:
                assert resolution.is_state_eligible
            else:
                assert not resolution.is_state_eligible, (
                    f"{source} -> {target} must not be state-eligible"
                )


def test_create_session_against_an_existing_session_is_denied() -> None:
    """TRN-SESS-001 requires CURRENT STATE "Session absent". A caller
    re-requesting creation against a Session that already has a state
    must not be treated as a no-op success or silently re-drafted.
    """
    resolution = resolve_session_transition(
        current_state=SessionState.DRAFT, transition_id=SessionTransitionId.TRN_SESS_001
    )

    assert resolution.verdict is SessionTransitionVerdict.DENIED_SESSION_ALREADY_EXISTS


def test_state_eligible_verdict_never_appears_without_a_governing_spec() -> None:
    """Structural guarantee: nothing can read transition requirements
    off a refused resolution.
    """
    for source in list(SessionState) + [None]:
        for target in SessionState:
            resolution = resolve_session_transition_to_state(
                current_state=source, target_state=target
            )
            if resolution.verdict is not SessionTransitionVerdict.STATE_ELIGIBLE:
                assert resolution.spec is None


def test_every_terminal_state_pair_is_covered_by_closed_denial() -> None:
    assert frozenset({SessionState.CLOSED}) == TERMINAL_SESSION_STATES
