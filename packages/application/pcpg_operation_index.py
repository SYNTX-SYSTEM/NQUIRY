"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — the full consumable operation index
(Architecture 26, FBR-PCPG-2, closed: both increments).

Source: `docs/architecture/26_PRE_CALL_PROMPT_GOVERNANCE_SFE/00_FIELD.md` §12:
"FBR-PCPG-2: SEMANTIC DELTA → CANONICAL OPERATION. There is no vocabulary
relation mapping an observed action onto the existing operation catalog. That
catalog is Commands (09), transitions (03), AUTH-DEPs (04) and AIOP contracts
(08). The catalog exists, spread across these homes, with per-operation
capability in `session_position.actions`. What is missing is its **consumable
index**: per operation, its execution class, authority home, readiness
producer, effect class and data inputs." `02_RELATIONS.md` R-06 AUTHORITATIVE
HOME: "the operation catalog in its existing homes ... this Field, for
execution classes."

WHAT THIS MODULE IS
--------------------
A pure, read-only, in-memory CATALOG -- not a Query, not a Command, not a
boundary evaluator. It quotes facts already stated in real production code
(the citations in each entry's `architecture_ref` are copied verbatim from the
handler docstrings named there, not re-derived), and it computes NOTHING from
a raw intent (that is R-05/SIMPLIX, a later Work Unit; HA-PCPG-2 governs it).
It is the "consumable index" R-06 will read from; R-06 itself is not
materialized here.

SCOPE: FBR-PCPG-2 IN FULL (both increments; this module now closes it)
------------------------------------------------------------------------
`SESSION_SCOPED_OPERATIONS`: the 18 operations `application.inquiry_queries.
session_position` already projects readiness for (`actions` dict keys) --
proven exhaustive against that REAL function's own output, not assumed
(`test_pcpg_operation_index.py::test_covers_every_session_position_action`).

`ROOT_OPERATIONS`: the remaining 8 real Commands -- CREATE_WORKSPACE,
CREATE_CHALLENGE, ADD_MEMBER, GRANT_AUTHORITY_BINDING,
REVOKE_AUTHORITY_BINDING, CREATE_SESSION, OPEN_DECISION_CONSIDERATION,
RECORD_HUMAN_DECISION -- none of which shares `session_position`'s single
surface. Their own completeness proof instead reuses `test_pfc_f09_2_
isolation_sweep.ROUTES` (already proven exhaustive against `app.routes` by
that file's own guard) as the oracle: every non-Session POST Command route
maps to exactly one `ROOT_OPERATIONS` entry
(`test_root_operations_route_map_is_exhaustive_against_the_proven_sweep`).

WHY READINESS_PRODUCER IS THE SAME STRING FOR EVERY SESSION-SCOPED ENTRY,
BUT THREE DIFFERENT STRINGS -- OR `None` -- ACROSS `ROOT_OPERATIONS`
------------------------------------------------------------------------
Session-scoped: there is exactly ONE existing capability-projection surface
for all 18 -- `session_position` itself (00_FIELD.md's own words:
"per-operation capability in `session_position.actions`", singular surface).

Root: there is no such single surface. `workspace_overview` projects
`capabilities.createChallenge` / `capabilities.addMember` /
`viewer.isGovernanceRoot`; `challenge_detail` projects
`capabilities.openSession` / `capabilities.grantSessionControl`; Workspace
founding has its own real, named, currently-permissive eligibility port
(`workspace_creation_handler.AllowAllWorkspaceCreationEligibilityChecker`,
HARD-DEP-001, F01 WU-01.4). `test_governance_root_fact_never_diverges_
across_three_projections` proves `workspace_overview.viewer.isGovernanceRoot`,
`workspace_overview.capabilities.addMember`, `challenge_detail.capabilities.
grantSessionControl` and `session_position.actions.GRANT_SESSION_CONTROL`
are the SAME authority fact (`inquiry_queries.py`'s own identical `_holds(...,
WORKSPACE_GOVERNANCE_RIGHT, "WORKSPACE", ws)` call), never four divergent
ones -- which is why GRANT_AUTHORITY_BINDING and REVOKE_AUTHORITY_BINDING may
both honestly cite `workspace_overview` regardless of which scope
(WORKSPACE/CHALLENGE/SESSION) the binding itself targets.

Two entries -- OPEN_DECISION_CONSIDERATION and RECORD_HUMAN_DECISION -- have
NO pre-exposed producer at all: `human_decision_handler.py`'s own docstring
confirms AUTH-DEP-DEC-001/002 are checked fresh only at Command-commit time,
never pre-projected anywhere (`http_dispatch.py` has no `canDecide`-shaped
surface; grepped, confirmed absent). `readiness_producer=None` is this
index's honest encoding of exactly the gap `02_RELATIONS.md` R-07 itself
names: "a delta with no authoritative producer for its authority gives
INDETERMINATE with reason `NO_AUTHORITATIVE_PRODUCER`" -- not a placeholder,
not a guessed nearest surface.

OPEN_DECISION_CONSIDERATION also has `http_route=None`: the function is
real (`human_decision_handler.open_decision_consideration`, a fully governed
Command) but is, today, called only from tests
(`test_human_decision.py`, `test_proof_bundle_paths.py`) -- no HTTP route
wires it. This is disclosed here as a real, catalogable operation that is
SUCCESSOR_NOT_BUILT for HTTP reachability, not silently dropped from the
index because the live API surface doesn't yet expose it (R-06's own
catalog spans "Commands (09), transitions (03), AUTH-DEPs (04) and AIOP
contracts (08)" -- a broader set than "what HTTP already wires").

EXECUTION CLASS (04_OBSERVATION_RESULT.md §4; this Field's own vocabulary,
"by the EFFECT, not the verb"): of the 18 Session-scoped operations, exactly
two -- REQUEST_QUESTION_ANALYSIS (AIOP-001) and REQUEST_QUESTION_CLUSTERING
(AIOP-002) -- are PROVIDER_COMPUTATION: a model-eligible computation whose
maximum canonical effect is derived output only (08 §39). The other 16, and
all 8 `ROOT_OPERATIONS` entries, are HUMAN_COMMAND: each is a state
transition, a relation/binding creation or a decision-class effect an AI is
explicitly prohibited from causing (04 AUTH-DEP-SEL-001/002, HD-25, HD-26).
None is EXTERNAL_EFFECT or DISCLOSURE -- matching 00_FIELD.md §3's own Pulse
note, "EXTERNAL_DEPENDENCIES: ... none exist in NQUIRY today."
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ExecutionClass(Enum):
    """04_OBSERVATION_RESULT.md §4, verbatim vocabulary. This Field's own
    classification, reused by every later relation that needs it (I-20: one
    definition, not a second divergent one)."""

    PROVIDER_COMPUTATION = "PROVIDER_COMPUTATION"
    HUMAN_COMMAND = "HUMAN_COMMAND"
    EXTERNAL_EFFECT = "EXTERNAL_EFFECT"
    DISCLOSURE = "DISCLOSURE"
    UNKNOWN = "UNKNOWN"


READINESS_PRODUCER = "application.inquiry_queries.session_position"
"""The one real, existing capability-projection function every
`SESSION_SCOPED_OPERATIONS` entry defers to -- not re-implemented, not
re-derived; the completeness falsifier re-reads its live `actions` keys."""

READINESS_PRODUCER_WORKSPACE_OVERVIEW = "application.inquiry_queries.workspace_overview"
"""Projects `capabilities.createChallenge`, `capabilities.addMember` and
`viewer.isGovernanceRoot` -- the producer for CREATE_CHALLENGE, ADD_MEMBER,
GRANT_AUTHORITY_BINDING and REVOKE_AUTHORITY_BINDING."""

READINESS_PRODUCER_CHALLENGE_DETAIL = "application.inquiry_queries.challenge_detail"
"""Projects `capabilities.openSession` -- the producer for CREATE_SESSION."""

READINESS_PRODUCER_WORKSPACE_ELIGIBILITY = (
    "application.workspace_creation_handler.AllowAllWorkspaceCreationEligibilityChecker"
)
"""The named, replaceable eligibility port CREATE_WORKSPACE defers to
(HARD-DEP-001, F01 WU-01.4) -- real and currently permissive, not "no
producer"."""


@dataclass(frozen=True, slots=True)
class OperationIndexEntry:
    operation_id: str
    """Matches the exact `session_position.actions` key for a Session-scoped
    entry (stratum 1 fact); a real Command name otherwise."""
    architecture_ref: tuple[str, ...]
    """Citations copied verbatim from the real handler's own docstring --
    never re-derived from the architecture text directly by this module."""
    execution_class: ExecutionClass
    readiness_producer: str | None = READINESS_PRODUCER
    """`None` means no pre-exposed producer exists for this operation today
    -- 02_RELATIONS.md R-07's own `NO_AUTHORITATIVE_PRODUCER` vocabulary,
    not a placeholder and never a guessed nearest surface."""
    data_inputs: tuple[str, ...] = ()
    """Field names the real HTTP Command route requires beyond the universal
    `expectedVersion` (and identity/scope, proven by the ingress). Taken
    verbatim from the real route bodies in
    `tests/e2e/test_pfc_f09_2_isolation_sweep.py`'s own `ROUTES` table."""
    http_route: tuple[str, str] | None = None
    """`(method, path)` exactly as `ROUTES` spells it, or `None` when no HTTP
    route wires this operation yet (disclosed, not silently omitted --
    OPEN_DECISION_CONSIDERATION today)."""

    def __post_init__(self) -> None:
        if not self.operation_id:
            raise ValueError("OperationIndexEntry.operation_id must be non-empty")
        if not self.architecture_ref:
            raise ValueError(
                f"OperationIndexEntry({self.operation_id!r}).architecture_ref must be non-empty"
            )
        if not isinstance(self.execution_class, ExecutionClass):
            raise TypeError(
                f"execution_class must be an ExecutionClass, got {type(self.execution_class)!r}"
            )
        if self.http_route is not None and len(self.http_route) != 2:
            raise ValueError(
                f"OperationIndexEntry({self.operation_id!r}).http_route must be a (method, path) "
                f"pair or None"
            )


SESSION_SCOPED_OPERATIONS: tuple[OperationIndexEntry, ...] = (
    OperationIndexEntry(
        "BEGIN_SETUP",
        ("03 TRN-SESS-002", "04 AUTH-DEP-SESS-002"),
        ExecutionClass.HUMAN_COMMAND,
        data_inputs=(),
    ),
    OperationIndexEntry(
        "BEGIN_CHALLENGE_CAPTURE",
        ("03 TRN-SESS-003", "04 AUTH-DEP-SESS-003"),
        ExecutionClass.HUMAN_COMMAND,
        data_inputs=(),
    ),
    OperationIndexEntry(
        "PREPARE_BURST",
        ("03 TRN-BURST-001", "04 AUTH-DEP-BURST-001"),
        ExecutionClass.HUMAN_COMMAND,
        data_inputs=(),
    ),
    OperationIndexEntry(
        "ADMIT_PARTICIPANT",
        ("09 section 28", "GAP-09-007", "F02 HD-7"),
        ExecutionClass.HUMAN_COMMAND,
        data_inputs=("participantUserId",),
    ),
    OperationIndexEntry(
        "OPEN_QUESTION_GENERATION",
        ("03 TRN-SESS-004", "03 TRN-BURST-002", "04 AUTH-DEP-SESS-004"),
        ExecutionClass.HUMAN_COMMAND,
        data_inputs=(),
    ),
    OperationIndexEntry(
        "GRANT_SESSION_CONTROL",
        ("04 WORKSPACE_GOVERNANCE_RIGHT", "05 governance"),
        ExecutionClass.HUMAN_COMMAND,
        readiness_producer=READINESS_PRODUCER,
        data_inputs=("humanUserId", "authorityClass", "scopeType", "scopeId"),
    ),
    OperationIndexEntry(
        "CAPTURE_QUESTION",
        ("03 TRN-Q-001", "04 AUTH-DEP-Q-001", "06 BND-008"),
        ExecutionClass.HUMAN_COMMAND,
        data_inputs=("originalText", "expectedBurstVersion"),
    ),
    OperationIndexEntry(
        "COMPLETE_BURST",
        ("03 TRN-SESS-005", "03 TRN-BURST-005", "F03 HD-9", "F03 HD-11"),
        ExecutionClass.HUMAN_COMMAND,
        data_inputs=("expectedBurstVersion",),
    ),
    OperationIndexEntry(
        "BEGIN_ANALYSIS",
        ("03 TRN-SESS-006", "04 AUTH-DEP-SESS-006", "HD-1", "HD-9", "HD-16"),
        ExecutionClass.HUMAN_COMMAND,
        data_inputs=(),
    ),
    OperationIndexEntry(
        "REQUEST_QUESTION_ANALYSIS",
        ("08 AIOP-001", "HD-16", "HD-23"),
        ExecutionClass.PROVIDER_COMPUTATION,
        data_inputs=("case",),
    ),
    OperationIndexEntry(
        "REQUEST_QUESTION_CLUSTERING",
        ("08 AIOP-002", "HD-16", "HD-23"),
        ExecutionClass.PROVIDER_COMPUTATION,
        data_inputs=("case",),
    ),
    OperationIndexEntry(
        "BEGIN_REFLECTION",
        ("03 TRN-SESS-007", "04 AUTH-DEP-SESS-007", "06 BND-017", "HD-20", "HD-24"),
        ExecutionClass.HUMAN_COMMAND,
        data_inputs=(),
    ),
    OperationIndexEntry(
        "BEGIN_QUESTION_SELECTION",
        ("03 TRN-SESS-008", "04 AUTH-DEP-SESS-008", "HD-25", "NQ-DEC-053"),
        ExecutionClass.HUMAN_COMMAND,
        data_inputs=("reflectionCompletionConfirmed",),
    ),
    OperationIndexEntry(
        "SELECT_COMPELLING_QUESTION",
        ("03 TRN-SEL-001", "04 AUTH-DEP-SEL-001"),
        ExecutionClass.HUMAN_COMMAND,
        data_inputs=("questionId",),
    ),
    OperationIndexEntry(
        "SELECT_PRIMARY_QUESTION",
        ("03 TRN-SEL-002", "04 AUTH-DEP-SEL-002"),
        ExecutionClass.HUMAN_COMMAND,
        data_inputs=("questionId",),
    ),
    OperationIndexEntry(
        "CREATE_IMPACT_CHAIN",
        ("02 section 28", "03 section 40", "09 section 86", "HD-26", "NQ-DEC-054"),
        ExecutionClass.HUMAN_COMMAND,
        data_inputs=(),
    ),
    OperationIndexEntry(
        "APPEND_IMPACT_CHAIN_NODE",
        ("02 section 28", "03 section 40", "09 section 86", "HD-26", "NQ-DEC-054"),
        ExecutionClass.HUMAN_COMMAND,
        data_inputs=("expectedChainVersion", "level", "answer"),
    ),
    OperationIndexEntry(
        "BEGIN_INVESTIGATION",
        ("03 TRN-SESS-009", "04 AUTH-DEP-SESS-009", "HD-26", "NQ-DEC-054"),
        ExecutionClass.HUMAN_COMMAND,
        data_inputs=(),
    ),
)


ROOT_OPERATIONS: tuple[OperationIndexEntry, ...] = (
    OperationIndexEntry(
        "CREATE_WORKSPACE",
        ("HARD-DEP-001", "F01 WU-01.4", "HD-6", "16 REC-004"),
        ExecutionClass.HUMAN_COMMAND,
        readiness_producer=READINESS_PRODUCER_WORKSPACE_ELIGIBILITY,
        data_inputs=("name",),
        http_route=("POST", "/workspaces"),
    ),
    OperationIndexEntry(
        "CREATE_CHALLENGE",
        ("04 AUTH-DEP-CH-001", "04 section 84", "03 TRN-CH-001"),
        ExecutionClass.HUMAN_COMMAND,
        readiness_producer=READINESS_PRODUCER_WORKSPACE_OVERVIEW,
        data_inputs=("title",),
        http_route=("POST", "/workspaces/{ws}/challenges"),
    ),
    OperationIndexEntry(
        "ADD_MEMBER",
        ("04 GAP-04-014", "05 governance"),
        ExecutionClass.HUMAN_COMMAND,
        readiness_producer=READINESS_PRODUCER_WORKSPACE_OVERVIEW,
        data_inputs=("userId", "role"),
        http_route=("POST", "/workspaces/{ws}/members"),
    ),
    OperationIndexEntry(
        "GRANT_AUTHORITY_BINDING",
        ("04 GAP-04-014", "04 WORKSPACE_GOVERNANCE_RIGHT", "05 governance"),
        ExecutionClass.HUMAN_COMMAND,
        readiness_producer=READINESS_PRODUCER_WORKSPACE_OVERVIEW,
        data_inputs=("humanUserId", "authorityClass", "scopeType", "scopeId"),
        http_route=("POST", "/workspaces/{ws}/authority-bindings"),
    ),
    OperationIndexEntry(
        "REVOKE_AUTHORITY_BINDING",
        ("05 section 8", "04 GAP-04-014", "F01 WU-01.6"),
        ExecutionClass.HUMAN_COMMAND,
        readiness_producer=READINESS_PRODUCER_WORKSPACE_OVERVIEW,
        data_inputs=(),
        http_route=("POST", "/workspaces/{ws}/authority-bindings/{binding}/revoke"),
    ),
    OperationIndexEntry(
        "CREATE_SESSION",
        ("04 AUTH-DEP-SESS-001", "03 TRN-SESS-001", "F02 WU-02.3"),
        ExecutionClass.HUMAN_COMMAND,
        readiness_producer=READINESS_PRODUCER_CHALLENGE_DETAIL,
        data_inputs=(),
        http_route=("POST", "/workspaces/{ws}/challenges/{challenge}/sessions"),
    ),
    OperationIndexEntry(
        "OPEN_DECISION_CONSIDERATION",
        ("04 AUTH-DEP-DEC-001", "03 TRN-DEC-001", "14 section 12", "14 section 21", "02 R-07"),
        ExecutionClass.HUMAN_COMMAND,
        readiness_producer=None,
        data_inputs=("decisionQuestionRef", "decisionQuestionText", "options", "criteria"),
        http_route=None,
    ),
    OperationIndexEntry(
        "RECORD_HUMAN_DECISION",
        ("04 AUTH-DEP-DEC-002", "03 TRN-DEC-002", "14 section 12", "02 R-07"),
        ExecutionClass.HUMAN_COMMAND,
        readiness_producer=None,
        data_inputs=("selectedOption", "rationale", "confidence"),
        http_route=("POST", "/decisions/{decision}/decide"),
    ),
)


def operation_index() -> dict[str, OperationIndexEntry]:
    """The catalog keyed by `operation_id`. Raises if any two entries share an
    id (a defect in this module, never a runtime possibility to silently
    tolerate)."""
    index: dict[str, OperationIndexEntry] = {}
    for entry in (*SESSION_SCOPED_OPERATIONS, *ROOT_OPERATIONS):
        if entry.operation_id in index:
            raise ValueError(f"duplicate operation_id in the index: {entry.operation_id!r}")
        index[entry.operation_id] = entry
    return index


def resolve_operation(operation_id: str) -> OperationIndexEntry | None:
    """`None` means UNKNOWN (I-04): this operation is not in the catalog. A
    caller must never guess a "closest match" -- an absent entry is exactly
    as informative as a present one."""
    return operation_index().get(operation_id)


__all__ = [
    "READINESS_PRODUCER",
    "READINESS_PRODUCER_CHALLENGE_DETAIL",
    "READINESS_PRODUCER_WORKSPACE_ELIGIBILITY",
    "READINESS_PRODUCER_WORKSPACE_OVERVIEW",
    "ROOT_OPERATIONS",
    "SESSION_SCOPED_OPERATIONS",
    "ExecutionClass",
    "OperationIndexEntry",
    "operation_index",
    "resolve_operation",
]
