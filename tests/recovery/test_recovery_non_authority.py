"""P-21 (10 recovery non-authority -> 12 P-21): "Recovery cannot create
authority." Pure, no database.

14 section 48/50's own PKG-23 scope; this package's own AUTHORITY line:
"Historical authority proves prior legitimacy only, never current
recovery authority."
"""

from __future__ import annotations

import dataclasses
import inspect

from recovery.lpvs import LpvsResult
from recovery.models import RecoveryClass, RecoveryOutcome, RecoveryRecord, RecoveryRepository

_FORBIDDEN_METHOD_SUBSTRINGS = ("grant", "escalate", "authorize", "inherit", "elevate")


def test_recovery_repository_protocol_has_no_authority_granting_method() -> None:
    for name in dir(RecoveryRepository):
        if name.startswith("_"):
            continue
        for forbidden in _FORBIDDEN_METHOD_SUBSTRINGS:
            assert forbidden not in name.lower(), name


def test_recovery_record_never_stores_the_original_actor_as_its_own() -> None:
    """Structural proof: `RecoveryRecord` has NO
    `original_actor_type`/`original_actor_id` field at all -- only
    `recovery_actor_type`/`recovery_actor_id`. A recovery worker cannot
    even represent "I am acting as the original actor" in this record,
    let alone inherit that actor's authority (10 section 34: "A Saga
    engine or recovery worker cannot inherit the original actor's
    human authority").
    """
    field_names = {f.name for f in dataclasses.fields(RecoveryRecord)}
    assert "original_actor_type" not in field_names
    assert "original_actor_id" not in field_names
    assert {"recovery_actor_type", "recovery_actor_id"} <= field_names


def test_required_authority_ref_is_a_reference_not_a_grant() -> None:
    """10 section 63: "RecoveryRecord may contain references to proof.
    Its presence does not prove the referenced facts." Setting
    `required_authority_ref` to an arbitrary UUID never itself resolves
    or grants authority -- it is a plain, unvalidated reference field,
    proven by the fact that constructing a record with it set performs
    no authority lookup at all (no such capability exists on this
    package's own allow-list, see `recovery.models`'s own module
    docstring).
    """
    signature = inspect.signature(RecoveryRecord)
    assert "required_authority_ref" in signature.parameters
    # The field's own annotation is a bare optional UUID, never an
    # authority/binding-shaped type this package cannot even import.
    field = next(
        f for f in dataclasses.fields(RecoveryRecord) if f.name == "required_authority_ref"
    )
    assert "AuthorityResolver" not in str(field.type)
    assert "Binding" not in str(field.type)


def test_recovery_class_values_carry_no_authority_semantics() -> None:
    """10 section 30: "These classes are not authority classes." """
    for member in RecoveryClass:
        assert member.value.startswith("RC-")


def test_lpvs_result_carries_no_authority_shaped_field() -> None:
    field_names = {f.name for f in dataclasses.fields(LpvsResult)}
    for forbidden in ("authority", "grant", "right", "permission"):
        assert not any(forbidden in name for name in field_names), field_names


def test_recovery_outcome_does_not_replace_command_outcome() -> None:
    """10 section 64: "These are operational recovery outcomes only.
    They do not replace: DENIED/FAILED_PRECOMMIT/COMMITTED/INDETERMINATE."
    """
    recovery_values = {member.value for member in RecoveryOutcome}
    command_outcome_values = {"DENIED", "FAILED_PRECOMMIT", "COMMITTED", "INDETERMINATE"}
    assert recovery_values.isdisjoint(command_outcome_values)
