# 17: Live Application Runtime Materialization

## DOCUMENT STATUS

MATERIALIZED, PROVEN AGAINST REAL POSTGRESQL AND A REAL RUNNING
CONTAINER, NOT PRODUCTION-APPROVED. This document describes a
real, now-implemented runtime layer (unlike 00-16, which precede
their own implementation). Classification remains
`ARCHITECTURAL PROTOTYPE` only (14 §43) — it does not claim production
readiness, regulatory compliance, or that HARD-DEP-001/HARD-DEP-002 are
resolved. Authored as an explicitly-authorized successor field to the
PKG-00 through PKG-32 sequence (`docs/implementation/proof-reports/PKG-32.md`,
whose own terminal-node verdict applies only to that closed sequence,
not to this field).

## AUTHORITY AND SCOPE

Authority hierarchy unchanged: LEVEL 1 → LEVEL 2 → 00 → … → 16 → this
document. This document does not redefine any upstream semantic; it
materializes exactly two already-authorized-but-unbuilt extension
points (`apps/api/src/nquiry_api/http/{queries,commands}.py`, reserved
since PKG-00) plus the one composition-root module 14 §3.1's own
forbidden-dependency matrix requires to exist somewhere
(`packages/application/http_dispatch.py`, `packages/persistence/engine.py`).
**BACKEND INTEGRATION CANNOT DECIDE WHAT THE PRODUCT CONTAINS** — this
document wires two already-specified capabilities (`apps/web/lib/api/
types.ts`'s own `SessionReadResult`/`DecisionActionResult` contract,
in place since PKG-28/29) to their real backend; it adds no new
product scope, and is not Architecture 17-product-scope in the sense
a separate, distinct capability-classification document would be.

## UPSTREAM AUTHORITATIVE SOURCES

- 14 §13 (QUERY REGISTRY: `GetSession`, "Workspace scoped")
- 14 §14 (COMMAND PROCESSOR, the 16-step pipeline)
- 14 §2.1 (reference stack: "pluggable OIDC adapter plus deterministic
  test adapter [IMPLEMENTATION CHOICE]")
- 14 §3.1 / `scripts/check_architecture_dependencies.py` (forbidden
  dependency matrix — `nquiry_api` may depend only on `{application,
  observability, semantic_types}`; neither `nquiry_api` nor
  `application` may import `sqlalchemy`/any DB driver)
- 16 §56 GAP-14-001 ("Concrete production identity provider selection
  is not required for architectural prototype semantics" — the
  deterministic adapter built here does not close this gap)
- `packages/security/identity.py` (PKG-01's own `AuthenticatedPrincipal`/
  `IdentityPort`/`ExternalCredential` port — reused, not reinvented)
- `packages/application/human_decision_handler.py` (PKG-15, unmodified
  — `open_decision_consideration`/`record_human_decision` reused as-is)
- `apps/web/lib/api/types.ts`, `client.ts`, `decisionClient.ts` (PKG-28/29
  — the exact, already-fixed wire contract this field implements)

## FIELD PURPOSE

Materialize the missing runtime coupling between the fully-implemented
NQUIRY semantic/application core (PKG-00–32) and its actual executable
HTTP surface: `GET /workspaces/{w}/sessions/{s}` and
`POST /decisions/{d}/decide`, the exact two endpoints
`apps/web`'s own typed client already assumed since PKG-28/29.

## FIELD BOUNDARY

IN SCOPE: the two named HTTP routes; the deterministic identity
adapter both need; the composition-root connection/repository wiring
required to call real `packages/application` handlers from a real
request. OUT OF SCOPE (unchanged): new generic CRUD, new product
capabilities, real AI provider, production auth provider, Research
Mode, export, worker continuous-loop wiring (see WORKER RUNTIME
ARCHITECTURE below — genuinely blocked, not merely deferred for
convenience).

## CURRENT MATERIALIZED STATE

`GET /workspaces/{workspaceId}/sessions/{sessionId}` and
`POST /decisions/{decisionId}/decide` are real FastAPI routes, proven
against real PostgreSQL (13 new T10 tests,
`tests/e2e/test_http_session_view.py`/`test_http_record_decision.py`)
and against the real, running `docker compose` `api` container (see
the implementation report's END TO END PROOF section for exact `curl`
transcripts, including a real Postgres-down failure and full recovery).

## CURRENT UNMATERIALIZED STATE

- No third HTTP route exists. `GetChallenge`/`GetBurst`/
  `GetQuestionSelection`/`GetEvidenceContext`/`GetAuditTrail`/
  `GetProvenance`/`GetCommandProof`/`GetRecoveryStatus` (14 §13's
  remaining Query rows) and every Command besides `RecordHumanDecision`
  remain unwired — `apps/web` never assumed a route for any of them
  (no frontend contract exists to implement against), so building one
  now would be exactly the "new generic API" this field's own boundary
  forbids.
- `apps/worker/src/nquiry_worker/__main__.py` still prints its Phase-0
  no-op message and exits `0`. See WORKER RUNTIME ARCHITECTURE.
- No real authentication provider. GAP-14-001 unchanged, open.

## CAPABILITY CLASSIFICATION

| Capability | Classification |
|---|---|
| `GET /workspaces/{w}/sessions/{s}` | IMPLEMENTATION_MATERIALIZATION_REQUIRED → now MATERIALIZED |
| `POST /decisions/{d}/decide` | IMPLEMENTATION_MATERIALIZATION_REQUIRED → now MATERIALIZED |
| Deterministic HTTP identity adapter | ALREADY_ARCHITECTURALLY_DEFINED (14 §2.1) → now MATERIALIZED |
| `application`/`nquiry_api` DB connection composition root | IMPLEMENTATION_MATERIALIZATION_REQUIRED (no prior production caller needed one) → now MATERIALIZED (`persistence/engine.py`, `application/http_dispatch.py`) |
| `OutboxWorker`/`ProjectionWorker` continuous production loop | BLOCKED_BY_UPSTREAM_GAP (see WORKER RUNTIME ARCHITECTURE) |
| Real production authentication (OIDC) | HUMAN_DECISION_REQUIRED / BLOCKED (GAP-14-001, unchanged, open) |
| Any Query/Command beyond the two named above | DEFERRED_OUTSIDE_FIELD (no frontend contract demands them yet) |

## RUNTIME TOPOLOGY

Unchanged `docker-compose.yml` topology (`postgres` always,
`api`/`worker`/`web` under `app` profile). No new service, container,
or port. `api`'s own `DATABASE_URL` (already wired since PKG-00) is
now actually read at request time by `packages/persistence/engine.py`.

## HTTP APPLICATION ADAPTER ARCHITECTURE

`apps/api/src/nquiry_api/http/{queries,commands}.py` are genuine thin
adapters: extract plain strings from the request (path params, two
headers, a Pydantic-validated JSON body), call exactly one
`application.http_dispatch.dispatch_*` function, serialize its
returned plain `dict` as the JSON response. Neither file imports
`persistence`/`authority`/`boundaries`/`security`/`sqlalchemy` —
verified by `scripts/check_architecture_dependencies.py`, which
already enforces `nquiry_api`'s `{application, observability,
semantic_types}` ceiling and caught two real violations during this
field's own construction (see the implementation report's DEFECTS
section).

## AUTHENTICATION / IDENTITY RESOLUTION CONTRACT

`packages/application/http_dispatch.py::resolve_actor` reads two
request claims (`x-nquiry-actor-user-id`, `x-nquiry-actor-class`,
optional, defaults `HUMAN_USER`) and constructs a real
`security.identity.AuthenticatedPrincipal` (14 §32's own exact shape)
plus the `authority.actor.ActorClass` BND-001 needs. This is the
deterministic adapter 14 §2.1 authorizes as an `[IMPLEMENTATION
CHOICE]` for THIS build phase — GAP-14-001 (real OIDC provider
selection) remains open and untouched. No cryptographic verification
occurs anywhere in this path; the claim is trusted at face value,
exactly as disclosed in `http_dispatch.py`'s own module docstring.
`AuthenticatedPrincipal` structurally cannot carry a role/authority
field (unchanged from PKG-01) — this adapter cannot invent one either.

## COMMAND DISPATCH CONTRACT

`POST /decisions/{d}/decide` → `application.http_dispatch.
dispatch_record_human_decision` → real `application.human_decision_handler.
record_human_decision` (PKG-15, byte-for-byte unmodified) → real
7-boundary precommit chain → real `CommitCoordinator`/BND-014 → real
`decisions` row. 14 §14's own 16-step COMMAND PROCESSOR pipeline is
followed exactly because `record_human_decision` itself already
implements it — this field adds no new step and skips none.

## QUERY / OBSERVATION CONTRACT

`GET /workspaces/{w}/sessions/{s}` → `application.http_dispatch.
dispatch_get_session_view` → the FIRST real Query handler this
repository has built, `application.session_view_query.get_session_view`
— see that module's own docstring for why it runs only BND-001/002/003
(never the write-side BND-004..007) and never resolves
`AuthorityResolver` at all (14 §13's own scope-rule column names
`GetSession` "Workspace scoped" only, never "read authorized" —
contrast `GetDecision`'s own "Workspace scoped/read authorized").

## APPLICATION HANDLER RELATION

Zero existing `packages/application` handler was modified.
`session_view_query.py` and `http_dispatch.py` are additive siblings.
`human_decision_handler.py` is called exactly as every predecessor
test already called it, with real constructed `SqlAlchemy*Repository`
instances in place of a test's own.

## AUTHORITY PRESERVATION

`AuthorityResolver` is resolved fresh, per request, inside
`record_human_decision` exactly as before — this field adds no
caching, no shortcut, no new grant path. The Query side never touches
`AuthorityResolver` (see QUERY / OBSERVATION CONTRACT above) because
14 names no authority gate for it — a real, disclosed asymmetry, not
an oversight.

## WORKSPACE ISOLATION

BND-002 (real `Bnd002WorkspaceEvaluator`, unmodified) runs on both
routes; `tests/e2e/test_http_session_view.py::
test_http_session_view_denies_actor_with_no_workspace_membership`
proves a real cross-Workspace-adjacent denial through the real HTTP
stack.

## BOUNDARY PRESERVATION

No boundary evaluator was modified. The read chain (BND-001/002/003)
and write chain (BND-001..007, inside `record_human_decision`,
unmodified) both run to real completion on every request; `evaluate_chain`'s
own stop-at-first-non-ALLOW guarantee (unchanged, PKG-08) is exercised
for real by every denial test in both new T10 files.

## BND-014 RELATION

Runs unmodified, inside `record_human_decision`'s own call into
`CommitCoordinator`, on every `POST /decisions/{d}/decide` that
reaches it. `tests/e2e/test_http_record_decision.py::
test_duplicate_decide_request_does_not_double_commit` proves a real,
fresh BND-014/BND-007 re-evaluation on a real replayed HTTP request.

## COMMIT UNIT RELATION

Unmodified `commit.coordinator.CommitCoordinator`, invoked exactly as
`record_human_decision` already invoked it for every predecessor test.
A real `CommitUnit`/`decisions` row is produced by the real HTTP happy
path (`test_http_record_decision_happy_path_commits_a_real_decision`),
verified by re-querying the row independently of the response body.

## PERSISTENCE RELATION

`packages/persistence/engine.py` is the one new persistence-owned
module: a lazy, pooled `sa.Engine` plus a `connect()` context manager
(one request-scoped transaction, commit on clean exit, rollback on
exception). No existing repository class was modified except two pure
additions: `BurstRepository.get_by_session`, `DecisionRepository.
get_latest_by_challenge` (both needed because the Session-read Query
starts from a `SessionId`/`ChallengeId`, never a `BurstId`/`DecisionId`
directly — see their own docstrings for why no ordering ambiguity
exists at this build phase).

## AUDIT RELATION

Unmodified — `record_human_decision`'s own real `AuditEvent` insertion,
inside the same CommitUnit transaction, runs exactly as before.

## TRANSACTIONAL OUTBOX RELATION

Unmodified — same real `OutboxRecord` insertion, inside the same
transaction. No route reads or waits on outbox delivery; that remains
`OutboxWorker`'s own job (unwired, see below).

## EVENT RELATION

Unchanged, `SUCCESSOR_NOT_BUILT` disclosure carried forward unmodified
from PKG-15/29/30: no `EventEnvelope` consumer is wired to
`RecordHumanDecision` anywhere in this codebase yet.

## WORKER RUNTIME ARCHITECTURE

**Genuinely BLOCKED_BY_UPSTREAM_GAP, not merely deferred.**
`apps/worker/src/nquiry_worker/outbox_worker.py::OutboxWorker.deliver_due`
requires a caller-supplied `EventEnvelopeSource` (`OutboxRecord →
EventEnvelope` resolver); `projection_worker.py::ProjectionWorker.
apply_batch` requires an already-resolved `Sequence[EventEnvelope]`.
Both modules' own pre-existing docstrings (PKG-20/21, unmodified)
already disclose: "no durable path from a bare `OutboxRecord.commit_id`
to a fully historically faithful `EventEnvelope` exists yet in this
codebase" (not all fields — `aggregate_version_after_commit`,
`causation_id`, `actor_ref`, `authority_source_ref`, full `payload` —
are jointly recoverable from any table this codebase's own commit path
writes). Wiring either worker into a real, continuously-running
production loop would therefore require either (a) inventing a
degraded/partial `EventEnvelope` reconstruction the real architecture
never authorized (exactly the "invent a mechanism" this field's own
law forbids), or (b) a genuine new architectural decision about what a
durable, fully-faithful Event-envelope store looks like — outside any
implementation package's own authority. `nquiry_worker/__main__.py`'s
own current no-op-and-exit-0 behavior is therefore left completely
unmodified: it is not broken, it is the honest, correct current state.

## OUTBOX WORKER MATERIALIZATION

Not performed this field. See WORKER RUNTIME ARCHITECTURE.

## PROJECTION WORKER MATERIALIZATION

Not performed this field. See WORKER RUNTIME ARCHITECTURE.

## PROJECTION NON-AUTHORITY

Unaffected — no route this field adds reads or writes a projection
table. `session_view_query.py`'s own module docstring explicitly
avoids implying `session_read_model`/`inquiry_read_model` are used;
`GetSession`'s "canonical option for proof" (14 §13) is what this
field actually reads (real `sessions`/`challenges`/`question_bursts`/
`questions`/`decisions` rows), never the projection tables.

## FAILURE SEMANTICS

`DENIED`/`FAILED_PRECOMMIT`/`COMMITTED`/`INDETERMINATE` all preserved,
verbatim, from `record_human_decision`'s own real exception types
(`HumanDecisionDenied`, `CommitFailedPrecommit`, `CommitIndeterminate`),
each mapped to its own distinct `DecisionActionResult` JSON shape
(`denied`/`rejected`/`committed`/`indeterminate`) — never collapsed
into a single generic HTTP error shape. **Known, disclosed gap**: an
unreachable database mid-request currently surfaces as FastAPI's own
generic 500 handler (proven empirically, see the implementation
report's ADVERSARIAL TESTS section) rather than a
`DecisionActionResult`/`SessionReadResult`-shaped body — honest
(never silently claims success) but not yet contract-shaped; flagged
as KNOWN_LIMITATIONS, not fixed in this field.

## CONSEQUENCE CERTAINTY

Unaffected — `CommitIndeterminate` (raised only from inside the
unmodified `CommitCoordinator`) is mapped to `{"kind": "indeterminate",
"blockedTargetRef": ...}`, never silently treated as failure or
success.

## IDEMPOTENCY

`record_human_decision` is called with `idempotency_key=None` on every
request (the frontend contract names no client-supplied idempotency
key) — a real, disclosed limitation: two genuinely-duplicate HTTP
POSTs are NOT deduplicated via `commit.idempotency`'s own mechanism;
they are instead correctly denied by the SECOND request's own fresh
BND-007 state-transition check finding the Decision already `DECIDED`
(proven by `test_duplicate_decide_request_does_not_double_commit`) —
a different, but still non-collapsing, defense.

## RETRY AUTHORITY

Unaffected. No route this field adds retries anything itself; a
client-side retry is just a second, independent request, handled by
the same fresh boundary re-evaluation every request already gets.

## RECOVERY RELATION

Unaffected — `RecoveryService`/BND-017/018 are not reachable from
either new route.

## OBSERVABILITY

Not extended this field (disclosed, not silently skipped): the two new
routes do not yet emit their own `ObservationContext` the way
`/healthz` does (PKG-27). A correlation-id IS constructed per request
(`application.http_dispatch`'s own `CorrelationId(uuid.uuid4())`) but
is not yet threaded through `LocalOtelObservationSink`. Flagged in
KNOWN_LIMITATIONS.

## HEALTH VS READINESS

`/healthz` remains unmodified, liveness-only — re-confirmed empirically
this field (Postgres stopped mid-session, `/healthz` still returned
200; see implementation report). No new readiness endpoint was added:
14 names no readiness-endpoint requirement anywhere, and inventing one
now would be scope this field's own boundary does not authorize. The
two new routes THEMSELVES now serve as an honest readiness signal by
construction — they fail loudly (500) when the database is
unreachable, never falsely claim success.

## STARTUP / SHUTDOWN SEMANTICS

Unchanged. `persistence.engine`'s `Engine` is created lazily on first
request (not at process startup) and reused for the process lifetime;
no new startup/shutdown hook was added to `main.py`.

## CONCURRENCY

Unaffected — no new concurrency primitive. Each request gets its own
connection from the pool; `CommitCoordinator`'s own existing
`SAVEPOINT`-based atomicity (PKG-13, unmodified) is what a concurrent
duplicate-decide race already relies on.

## SECURITY BOUNDARIES

No DB principal, RLS policy, or `SECURITY_CAPABILITY_MAP` entry was
touched. `packages/persistence/engine.py` connects using whatever
`DATABASE_URL` the `api` container already had (unchanged since
PKG-00) — this field grants no new privilege.

## AI NON-AUTHORITY

Unaffected — neither new route touches `ai_gateway`/`ai_contracts` at
all.

## HARD-DEP-001 RELATION

Unchanged, still BLOCKED. Every real HTTP test this field adds seeds
its Workspace via `NonProofWorkspaceBootstrap` (`FIXTURE_LEGITIMACY ==
"NON_PROOF_FIXTURE"`, unmodified) — proving the wiring, never claiming
the root's own legitimacy.

## HARD-DEP-002 RELATION

Unchanged, still BLOCKED and untouched — neither new route imports
`ai_gateway` at all.

## DEFERRED CAPABILITIES

Every other Query/Command in 14 §12/§13 (`GetChallenge`, `GetBurst`,
`GetQuestionSelection`, `GetEvidenceContext`, `GetAuditTrail`,
`GetProvenance`, `GetCommandProof`, `GetRecoveryStatus`,
`QuestionSelection`, `RecoverySelected`, …); real OutboxWorker/
ProjectionWorker production wiring; real authentication.

## FORBIDDEN COLLAPSES

None introduced. Explicitly re-verified (ARCHITECTURE_RECONSTRUCTION_RESULT
of the implementation report): no authentication claim became
authority; no client-supplied `actorClass` bypassed BND-001 (it is
INPUT to BND-001, evaluated for real, denied for real when wrong — not
trusted); no projection became canonical; no worker gained authority
(none was wired at all); no HTTP controller touched persistence
directly (architecture checker enforced this, caught two real
violations during construction).

## TDD OBLIGATIONS / ADVERSARIAL TEST MATRIX / RUNTIME PROOF REQUIREMENTS

See `docs/implementation/proof-reports/ARCH-17-RUNTIME-MATERIALIZATION.md`
for the full TDD sequence (RED observations, root causes, fixes),
the complete adversarial test list, and the real Docker-container
runtime proof (including the Postgres-down failure and recovery).

## TRACEABILITY TO EXISTING BND / PKG / P / TEST IDENTIFIERS

BND-001/002/003 (read chain, new); BND-001..007/014 (write chain,
reused unmodified from PKG-08/09/13/15). PKG-15 (`record_human_decision`,
reused), PKG-28/29 (`apps/web/lib/api/*`, the wire contract this field
implements), PKG-30 (`NonProofWorkspaceBootstrap` seeding pattern
reused in the new T10 tests), PKG-32 (baseline commit `0884f62`).
P-07/P-09/P-10/P-11/P-13 (all re-exercised through the new HTTP path,
not merely the pure-Python path PKG-30/31 already proved them
through).

## FIELD EXIT CONDITIONS

See implementation report FIELD EXIT VERDICT.

## HUMAN_DECISION_REQUIRED REGISTER

None encountered that blocked this field's own two named routes. One
item remains explicitly named, unchanged from every predecessor
package: **real production authentication provider selection
(GAP-14-001)** — question: "which concrete OIDC/IdP does NQUIRY's
production deployment use, and what does token→UserId mapping look
like for it?" — blocked on a product/infrastructure decision outside
any coding package's own authority, explicitly NOT decided here.
