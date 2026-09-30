"""PRE_CALL_PROMPT_GOVERNANCE (PCPG) — FBR-PCPG-2 (first increment): the
Session-scoped operation index (`application.pcpg_operation_index`).

MUST BECOME TRUE: for every operation `application.inquiry_queries.
session_position` already projects readiness for, the index has exactly one
entry, with a non-empty, citation-shaped `architecture_ref`, a real
`readiness_producer` reference, and an `execution_class` consistent with this
Field's own effect-based rule (04_OBSERVATION_RESULT.md §4) and the
architecture's own AI-prohibition facts.

MUST REMAIN IMPOSSIBLE (falsifiers, each a test below):
- the index missing an operation `session_position` actually projects, or
  claiming one it does not (completeness is exact, not a subset either way);
- two entries sharing an `operation_id` (I-20: no duplicate authority
  vocabulary for the same operation);
- an entry with no citation, or a citation that doesn't reference a real
  architecture-shaped identifier (TRN-/AUTH-DEP-/AIOP-/HD-/NQ-DEC-/section);
- a decision-class or state-transition operation classified
  PROVIDER_COMPUTATION (I-08: selection, phase-advance and capture effects
  are never a provider computation);
- an AIOP-request operation classified anything other than
  PROVIDER_COMPUTATION;
- any entry classified EXTERNAL_EFFECT or DISCLOSURE (00_FIELD.md §3: no
  external dependency exists in NQUIRY today);
- the module performing any DB read or write, or importing `ai_gateway` /
  a provider adapter (this is a pure, static catalog, not a producer of its
  own).
"""

from __future__ import annotations

import ast
import importlib
import pathlib

import f03_support as f03
import pytest
import sqlalchemy as sa
import test_pfc_f09_2_isolation_sweep as isolation_sweep
from application import inquiry_queries as queries
from application.pcpg_operation_index import (
    READINESS_PRODUCER,
    ROOT_OPERATIONS,
    SESSION_SCOPED_OPERATIONS,
    ExecutionClass,
    OperationIndexEntry,
    operation_index,
    resolve_operation,
)

_ARCHITECTURE_TOKEN = (
    "TRN-",
    "AUTH-DEP-",
    "AIOP-",
    "HD-",
    "NQ-DEC-",
    "section",
    "BND-",
    "GAP-",
    "WORKSPACE_GOVERNANCE_RIGHT",
    "governance",
    "HARD-DEP-",
    "REC-",
    "WU-0",
    "R-07",
)

# 04 AUTH-DEP-SEL-001/002, HD-25, HD-26, HD-11, 06 BND-008: these effects are
# decision-class, phase-advancing or human-only-by-architecture -- never a
# provider computation, whatever text a future prompt might request.
_MUST_BE_HUMAN_COMMAND = frozenset(
    {
        "BEGIN_SETUP",
        "BEGIN_CHALLENGE_CAPTURE",
        "PREPARE_BURST",
        "ADMIT_PARTICIPANT",
        "OPEN_QUESTION_GENERATION",
        "GRANT_SESSION_CONTROL",
        "CAPTURE_QUESTION",
        "COMPLETE_BURST",
        "BEGIN_ANALYSIS",
        "BEGIN_REFLECTION",
        "BEGIN_QUESTION_SELECTION",
        "SELECT_COMPELLING_QUESTION",
        "SELECT_PRIMARY_QUESTION",
        "CREATE_IMPACT_CHAIN",
        "APPEND_IMPACT_CHAIN_NODE",
        "BEGIN_INVESTIGATION",
    }
)
_MUST_BE_PROVIDER_COMPUTATION = frozenset(
    {"REQUEST_QUESTION_ANALYSIS", "REQUEST_QUESTION_CLUSTERING"}
)


def _real_session_position_action_keys(db: sa.Connection) -> set[str]:
    """The exhaustive, real key set — read from a live call, never assumed."""
    ctx = f03.generating_context(db, participants=1)
    pos = queries.session_position(
        f03.f02.ports(db), f03.principal(ctx["fac"]), ctx["ws"], ctx["session"]
    )
    actions = pos["actions"]
    assert isinstance(actions, dict)
    return set(actions.keys())


def test_covers_every_session_position_action(db_connection: sa.Connection) -> None:
    """Scoped to `SESSION_SCOPED_OPERATIONS` specifically -- `operation_index()`
    now also carries the 8 `ROOT_OPERATIONS` entries (FBR-PCPG-2's completed
    root/Decision slice), which `session_position` never claims to project."""
    real_keys = _real_session_position_action_keys(db_connection)
    assert {e.operation_id for e in SESSION_SCOPED_OPERATIONS} == real_keys


def test_no_duplicate_operation_ids() -> None:
    ids = [e.operation_id for e in SESSION_SCOPED_OPERATIONS]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("entry", SESSION_SCOPED_OPERATIONS, ids=lambda e: e.operation_id)
def test_every_entry_has_a_real_citation_shape(entry: OperationIndexEntry) -> None:
    assert entry.architecture_ref
    for ref in entry.architecture_ref:
        assert any(token in ref for token in _ARCHITECTURE_TOKEN), (entry.operation_id, ref)


@pytest.mark.parametrize("entry", SESSION_SCOPED_OPERATIONS, ids=lambda e: e.operation_id)
def test_every_entry_names_the_real_readiness_producer(entry: OperationIndexEntry) -> None:
    assert entry.readiness_producer == READINESS_PRODUCER
    module_name, func_name = entry.readiness_producer.rsplit(".", 1)
    module = importlib.import_module(module_name)
    assert hasattr(module, func_name), entry.readiness_producer


def test_decision_and_transition_operations_are_never_provider_computation() -> None:
    for operation_id in _MUST_BE_HUMAN_COMMAND:
        entry = resolve_operation(operation_id)
        assert entry is not None, operation_id
        assert entry.execution_class is ExecutionClass.HUMAN_COMMAND, operation_id


def test_aiop_request_operations_are_exactly_provider_computation() -> None:
    for operation_id in _MUST_BE_PROVIDER_COMPUTATION:
        entry = resolve_operation(operation_id)
        assert entry is not None, operation_id
        assert entry.execution_class is ExecutionClass.PROVIDER_COMPUTATION, operation_id


def test_no_entry_is_external_effect_or_disclosure() -> None:
    for entry in SESSION_SCOPED_OPERATIONS:
        assert entry.execution_class not in (
            ExecutionClass.EXTERNAL_EFFECT,
            ExecutionClass.DISCLOSURE,
        ), entry.operation_id


def test_execution_class_partition_is_exhaustive_and_matches_the_catalog_size() -> None:
    human = [
        e for e in SESSION_SCOPED_OPERATIONS if e.execution_class is ExecutionClass.HUMAN_COMMAND
    ]
    provider = [
        e
        for e in SESSION_SCOPED_OPERATIONS
        if e.execution_class is ExecutionClass.PROVIDER_COMPUTATION
    ]
    assert len(human) == 16
    assert len(provider) == 2
    assert len(human) + len(provider) == len(SESSION_SCOPED_OPERATIONS)


def test_unknown_operation_id_resolves_to_none_never_a_guess() -> None:
    assert resolve_operation("DELETE_WORKSPACE") is None
    assert resolve_operation("") is None
    assert resolve_operation("begin_setup") is None  # case-sensitive: no fuzzy match


def test_operation_index_itself_raises_on_a_duplicate_id() -> None:
    """Direct exercise of `operation_index()`'s own defensive raise -- not
    merely the static-list check above, which cannot tell whether the
    function's guard is live or dead code."""
    import application.pcpg_operation_index as module

    duplicated = (
        *SESSION_SCOPED_OPERATIONS,
        OperationIndexEntry(
            SESSION_SCOPED_OPERATIONS[0].operation_id,
            ("TRN-TEST-DUP",),
            ExecutionClass.HUMAN_COMMAND,
        ),
    )
    original = module.SESSION_SCOPED_OPERATIONS
    module.SESSION_SCOPED_OPERATIONS = duplicated
    try:
        with pytest.raises(ValueError, match="duplicate operation_id"):
            module.operation_index()
    finally:
        module.SESSION_SCOPED_OPERATIONS = original


def test_index_is_a_pure_function_no_hidden_state() -> None:
    a = operation_index()
    b = operation_index()
    assert a == b
    assert a is not b  # a fresh dict each call: no shared mutable cache


def test_the_module_touches_no_database_and_no_provider() -> None:
    """P-01/I-16, static: this catalog is pure data. It takes no `ports`,
    `connection` or DB argument anywhere, and imports nothing from
    `ai_gateway`/`ai_contracts`'s provider adapters or any provider SDK."""
    root = pathlib.Path(__file__).resolve().parents[2] / "packages" / "application"
    source = (root / "pcpg_operation_index.py").read_text()
    tree = ast.parse(source)
    forbidden = ("ai_gateway", "anthropic", "openai", "google", "provider", "psycopg", "sqlalchemy")
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            mods = [node.module or ""]
        else:
            continue
        for mod in mods:
            assert not any(mod.split(".")[0].startswith(f) for f in forbidden), mod
    for fn in tree.body:
        if isinstance(fn, ast.FunctionDef):
            arg_names = {a.arg for a in fn.args.args}
            assert not ({"ports", "connection", "db"} & arg_names), fn.name


def test_data_inputs_are_disjoint_from_the_universal_fields() -> None:
    """`expectedVersion` (and identity/scope, proven by the ingress) are
    universal -- an entry's own `data_inputs` never repeats them, or the
    index would misstate what is operation-specific."""
    for entry in SESSION_SCOPED_OPERATIONS:
        assert "expectedVersion" not in entry.data_inputs, entry.operation_id


# ---------------------------------------------------------------------------
# FBR-PCPG-2, remaining slice: Workspace/Challenge-root and Decision
# operations (`ROOT_OPERATIONS`). These have NO single shared capability
# surface the way the 18 Session-scoped operations share `session_position`
# -- three real, differently-named producers (`workspace_overview`,
# `challenge_detail`, the workspace-creation eligibility checker) plus two
# operations (OPEN_DECISION_CONSIDERATION, RECORD_HUMAN_DECISION) that have
# NO pre-exposed producer at all (02_RELATIONS.md R-07's own vocabulary:
# "a delta with no authoritative producer ... gives INDETERMINATE with
# reason NO_AUTHORITATIVE_PRODUCER" -- `readiness_producer=None` is this
# index's honest encoding of that same fact, not a gap left unrepresented).
# ---------------------------------------------------------------------------

_ROOT_OPERATION_ROUTES: dict[str, tuple[str, str]] = {
    "CREATE_WORKSPACE": ("POST", "/workspaces"),
    "ADD_MEMBER": ("POST", "/workspaces/{ws}/members"),
    "REVOKE_AUTHORITY_BINDING": ("POST", "/workspaces/{ws}/authority-bindings/{binding}/revoke"),
    "CREATE_CHALLENGE": ("POST", "/workspaces/{ws}/challenges"),
    "CREATE_SESSION": ("POST", "/workspaces/{ws}/challenges/{challenge}/sessions"),
    "GRANT_AUTHORITY_BINDING": ("POST", "/workspaces/{ws}/authority-bindings"),
    "RECORD_HUMAN_DECISION": ("POST", "/decisions/{decision}/decide"),
}
"""Every ROOT_OPERATIONS entry that IS reachable via a real HTTP route today,
mapped verbatim from `test_pfc_f09_2_isolation_sweep.ROUTES` (itself proven
exhaustive against `app.routes` by that file's own
`test_the_sweep_covers_every_route`). OPEN_DECISION_CONSIDERATION is
deliberately absent: a real Command with a real AUTH-DEP, callable only from
inside this codebase today (`test_human_decision.py`, `test_proof_bundle_
paths.py`) -- SUCCESSOR_NOT_BUILT for HTTP wiring, disclosed below, not
silently omitted from the catalog."""

_ROOT_DEDICATED_ROUTE_PATHS = frozenset(v[1] for v in _ROOT_OPERATION_ROUTES.values())


def test_root_operations_route_map_is_exhaustive_against_the_proven_sweep() -> None:
    """Every POST Command route in the proven-exhaustive ROUTES table is
    either one of the 18 Session-scoped routes or a ROOT_OPERATIONS route --
    never neither, never double-claimed. Reuses WU-1's own already-exhaustive
    table as the completeness oracle instead of re-deriving from `app.routes`
    a second time."""
    all_post_minus_ingress = {
        (m, p)
        for m, p, _ in isolation_sweep.ROUTES
        if m == "POST" and p != "/workspaces/{ws}/prompt-observations"
    }
    session_dedicated = {
        (m, p)
        for m, p, _ in isolation_sweep.ROUTES
        if m == "POST"
        and p not in _ROOT_DEDICATED_ROUTE_PATHS
        and p != "/workspaces/{ws}/prompt-observations"
    }
    root_routes = set(_ROOT_OPERATION_ROUTES.values())
    assert all_post_minus_ingress == session_dedicated | root_routes


@pytest.mark.parametrize(
    "operation_id,route",
    _ROOT_OPERATION_ROUTES.items(),
    ids=lambda x: x if isinstance(x, str) else "",
)
def test_every_routed_root_entry_names_its_real_http_route(
    operation_id: str, route: tuple[str, str]
) -> None:
    entry = resolve_operation(operation_id)
    assert entry is not None, operation_id
    assert entry.http_route == route, operation_id
    assert route in {(m, p) for m, p, _ in isolation_sweep.ROUTES}, operation_id


def test_open_decision_consideration_has_no_http_route_by_disclosed_design() -> None:
    entry = resolve_operation("OPEN_DECISION_CONSIDERATION")
    assert entry is not None
    assert entry.http_route is None
    module = importlib.import_module("application.human_decision_handler")
    assert hasattr(module, "open_decision_consideration")  # real, just unwired


@pytest.mark.parametrize("entry", ROOT_OPERATIONS, ids=lambda e: e.operation_id)
def test_every_root_entry_has_a_real_citation_shape(entry: OperationIndexEntry) -> None:
    assert entry.architecture_ref
    for ref in entry.architecture_ref:
        assert any(token in ref for token in _ARCHITECTURE_TOKEN), (entry.operation_id, ref)


_ROOT_ENTRIES_WITH_NO_PRODUCER = frozenset({"OPEN_DECISION_CONSIDERATION", "RECORD_HUMAN_DECISION"})


@pytest.mark.parametrize("entry", ROOT_OPERATIONS, ids=lambda e: e.operation_id)
def test_every_root_entry_producer_is_real_or_honestly_absent(entry: OperationIndexEntry) -> None:
    if entry.operation_id in _ROOT_ENTRIES_WITH_NO_PRODUCER:
        assert entry.readiness_producer is None, entry.operation_id
        assert any("R-07" in ref for ref in entry.architecture_ref), entry.operation_id
        return
    assert entry.readiness_producer is not None, entry.operation_id
    module_name, func_name = entry.readiness_producer.rsplit(".", 1)
    module = importlib.import_module(module_name)
    assert hasattr(module, func_name), entry.readiness_producer


def test_all_root_entries_are_human_command() -> None:
    """Founding, membership, governance-binding, Challenge/Session creation
    and Decision effects are never a provider computation (04 AUTH-DEP-SEL-*,
    HD-25/26; 00_FIELD.md §3: no AI path exists for any of these)."""
    for entry in ROOT_OPERATIONS:
        assert entry.execution_class is ExecutionClass.HUMAN_COMMAND, entry.operation_id


def test_no_duplicate_operation_ids_across_the_full_catalog() -> None:
    ids = [e.operation_id for e in (*SESSION_SCOPED_OPERATIONS, *ROOT_OPERATIONS)]
    assert len(ids) == len(set(ids))


def test_operation_index_now_covers_the_full_catalog_size() -> None:
    assert len(SESSION_SCOPED_OPERATIONS) == 18
    assert len(ROOT_OPERATIONS) == 8
    assert len(operation_index()) == 26


def test_root_entries_have_no_expected_version_in_data_inputs() -> None:
    for entry in ROOT_OPERATIONS:
        assert "expectedVersion" not in entry.data_inputs, entry.operation_id


def test_governance_root_fact_never_diverges_across_three_projections(
    db_connection: sa.Connection,
) -> None:
    """`workspace_overview.viewer.isGovernanceRoot`,
    `workspace_overview.capabilities.addMember.available`,
    `challenge_detail.capabilities.grantSessionControl.available` and
    `session_position.actions.GRANT_SESSION_CONTROL.available` all derive
    from the identical `_holds(..., WORKSPACE_GOVERNANCE_RIGHT, "WORKSPACE",
    ws)` call in `inquiry_queries.py` -- one authority fact, four read
    surfaces. This is why GRANT_AUTHORITY_BINDING and REVOKE_AUTHORITY_
    BINDING may both cite `workspace_overview` as their readiness producer:
    proven here to never disagree with the other two surfaces, for a real
    governance-root actor AND a real non-root actor in the same Workspace."""
    ctx = f03.generating_context(db_connection, participants=1)
    ports = f03.f02.ports(db_connection)
    for actor_id, expected in ((ctx["owner"], True), (ctx["fac"], False)):
        principal = f03.principal(actor_id)
        overview = queries.workspace_overview(ports, principal, ctx["ws"])
        detail = queries.challenge_detail(
            ports, principal, ctx["ws"], ctx["challenge"].challenge_id
        )
        position = queries.session_position(ports, principal, ctx["ws"], ctx["session"])
        assert overview["viewer"]["isGovernanceRoot"] is expected, actor_id
        assert overview["capabilities"]["addMember"]["available"] is expected, actor_id
        assert detail["capabilities"]["grantSessionControl"]["available"] is expected, actor_id
        assert position["actions"]["GRANT_SESSION_CONTROL"]["available"] is expected, actor_id


def test_root_operation_index_itself_raises_on_a_cross_group_duplicate() -> None:
    """Direct exercise of `operation_index()`'s own guard when the collision
    spans the two groups (session vs. root), not only within one group --
    the WU-2 test above only ever injected a same-group duplicate."""
    import application.pcpg_operation_index as module

    duplicated_root = (
        *ROOT_OPERATIONS,
        OperationIndexEntry(
            SESSION_SCOPED_OPERATIONS[0].operation_id,
            ("TRN-TEST-DUP",),
            ExecutionClass.HUMAN_COMMAND,
        ),
    )
    original = module.ROOT_OPERATIONS
    module.ROOT_OPERATIONS = duplicated_root
    try:
        with pytest.raises(ValueError, match="duplicate operation_id"):
            module.operation_index()
    finally:
        module.ROOT_OPERATIONS = original
