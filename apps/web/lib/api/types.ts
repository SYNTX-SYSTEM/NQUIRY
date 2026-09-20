/**
 * Typed domain shapes for the "typed API client" (14 §46 PKG-28
 * PUBLIC_INTERFACES: "typed API client").
 *
 * Source: 12_MINIMUM_PROTOTYPE_ARCHITECTURE.md §23 ("MINIMUM API
 * SURFACE" -- "The exact HTTP paths are prototype interface choices.
 * The semantic Commands are authoritative"; `GET /sessions/{s}` is a
 * QUERY, "read scope only"), §24 ("MINIMUM UI" -- items 1-8, 13-14 are
 * this package's own scope: authenticated Workspace context, Challenge
 * frame, current Session state, Burst state, HUMAN_ONLY mode
 * indicator, verbatim human Question list, frozen raw-set indicator,
 * origin marker HUMAN or AI, AI analysis shown explicitly as DERIVED /
 * PROPOSAL, blocked/denied result surface, INDETERMINATE surface that
 * disables blind retry -- items 10-12/15 (Question selection control,
 * Decision boundary, human Decision action, provenance/audit view) are
 * PKG-29's own scope, "Human Decision UI").
 *
 * Every closed-vocabulary value below is transcribed VERBATIM from the
 * real Python domain types this package's own real backend already
 * defines (`packages/domain/session.py`, `packages/domain/burst.py`,
 * `packages/domain/question.py`) -- none is invented here. This
 * package builds NO backend HTTP route (`apps/api` still has only
 * `/healthz`, unchanged since PKG-00/27) -- these types are the
 * DISCLOSED PROTOTYPE INTERFACE CHOICE 12 §23 itself explicitly
 * permits ("prototype interface choices"), proven end to end against
 * a real browser via Playwright network-level route interception
 * (`tests/e2e/session-view.spec.ts`), the standard, industry-normal
 * way to test a typed frontend contract against a backend that has
 * not shipped the corresponding route yet -- see this package's own
 * completion report for the full disclosure.
 *
 * WHY IDs ARE BRANDED STRINGS, NOT A RUNTIME CLASS HIERARCHY
 * --------------------------------------------------------------------
 * `semantic_types.ids._StrongId` (the Python backend's own "strong,
 * non-semantic identity" base) has no direct, idiomatic TypeScript
 * equivalent without a heavyweight runtime wrapper class this
 * prototype's own frontend does not otherwise need. TypeScript's
 * zero-runtime-cost "branded type" pattern (`string & { readonly
 * __brand: ... }`) gives the identical COMPILE-TIME guarantee (a
 * `WorkspaceId` and a `SessionId` remain distinct, mutually
 * non-assignable types) without inventing a parallel class hierarchy
 * -- the idiomatic frontend materialization of the same discipline,
 * not a weaker substitute for it.
 */

export type WorkspaceId = string & { readonly __brand: "WorkspaceId" };
export type ChallengeId = string & { readonly __brand: "ChallengeId" };
export type SessionId = string & { readonly __brand: "SessionId" };
export type BurstId = string & { readonly __brand: "BurstId" };
export type QuestionId = string & { readonly __brand: "QuestionId" };
export type DecisionId = string & { readonly __brand: "DecisionId" };

/**
 * `packages/domain/session.py`'s own `SessionState` -- 03 §13.1's
 * exact 13-value closed vocabulary, `[SPECIFIED]` by LEVEL 1.
 *
 * RETROFIT: defined as a `const` array first, with the type DERIVED
 * from it (`(typeof SESSION_STATES)[number]`), rather than the reverse.
 * An external review of this package's own initial cut found that
 * `lib/api/client.ts` cast nested `state`/`mode`/`origin` fields with
 * `requireString(...) as X` -- a compile-time-only assertion, not a
 * runtime check -- so a server response carrying e.g. `state:
 * "FOOBAR"` passed through uncaught, contradicting this package's own
 * claimed "fails closed on any unrecognized response shape"
 * (NON_COLLAPSE_RULES: "Unknown consequential semantic input fails
 * closed"). Deriving the type from a real runtime-checkable array (used
 * by `requireEnum` in `client.ts`) makes the type and its runtime
 * membership check impossible to drift apart -- a change to one
 * literal here changes both.
 */
export const SESSION_STATES = [
  "DRAFT",
  "SETUP",
  "CHALLENGE_CAPTURE",
  "QUESTION_GENERATION",
  "QUESTION_CAPTURE",
  "ANALYSIS",
  "REFLECTION",
  "QUESTION_SELECTION",
  "INVESTIGATION",
  "EXPERIMENT",
  "ACTION",
  "REVIEW",
  "CLOSED",
] as const;
export type SessionState = (typeof SESSION_STATES)[number];

/**
 * `packages/domain/burst.py`'s own `BurstState` -- 03 §19.1's exact
 * 4-value closed vocabulary, `[ARCHITECTURAL CLOSURE]`. "No CANCELLED
 * or RECOVERING domain state is introduced." See `SESSION_STATES`
 * above for why this is an array-then-derived-type, not a bare union.
 */
export const BURST_STATES = ["PREPARED", "ACTIVE", "PAUSED", "COMPLETED"] as const;
export type BurstState = (typeof BURST_STATES)[number];

/**
 * `packages/domain/burst.py`'s own `BurstMode` -- 09 §29.1's exact
 * 3-value closed vocabulary. This package's own OBJECTIVE names only
 * `HUMAN_ONLY` Bursts (the only mode the real backend's own `domain`
 * package can construct, PKG-07) -- the other two values are still
 * represented here (closed-vocabulary fidelity, not narrowed to a
 * smaller type this package would then have to widen again for
 * PKG-29+), but this package's own UI renders the HUMAN_ONLY indicator
 * specifically for the `HUMAN_ONLY` value only.
 */
export const BURST_MODES = ["HUMAN_ONLY", "HUMAN_PLUS_AI", "AI_CHALLENGE_AFTER_HUMANS"] as const;
export type BurstMode = (typeof BURST_MODES)[number];

/**
 * `packages/domain/question.py`'s own `QuestionOrigin` -- 02 §15.2's
 * exact 4-value closed vocabulary (AC-02-002's ORIGIN axis).
 */
export const QUESTION_ORIGINS = ["HUMAN", "AI", "IMPORTED", "INFERRED"] as const;
export type QuestionOrigin = (typeof QUESTION_ORIGINS)[number];

/**
 * `packages/domain/decision.py`'s own `DecisionState` -- 03 §35.2's
 * exact 2-value closed vocabulary, `[ARCHITECTURAL CLOSURE]`. Built as
 * a `const` array with the type derived from it from day one (per the
 * PKG-28 external-review retrofit lesson), never as a bare union a
 * caller could bypass with a compile-time-only cast.
 */
export const DECISION_STATES = ["UNDER_CONSIDERATION", "DECIDED"] as const;
export type DecisionState = (typeof DECISION_STATES)[number];

/**
 * `boundaries.types.BoundaryResult`'s own DENY/REQUIRE/ESCALATE
 * outcomes (06 §2), reused verbatim for `DecisionActionResult` below --
 * the identical vocabulary `SessionReadResult`'s own `denied` case
 * already uses (PKG-28). Kept as its own named array (not re-exported
 * from `SessionReadResult`) because it is the second, independent site
 * this package needs runtime membership-checked, not because the
 * vocabulary itself differs.
 */
export const BOUNDARY_DENIAL_RESULTS = ["DENY", "REQUIRE", "ESCALATE"] as const;
export type BoundaryDenialResult = (typeof BOUNDARY_DENIAL_RESULTS)[number];

/** `packages/domain/challenge.py`'s own `Challenge` -- 12 §24 item 2
 * ("Challenge frame"). Only the fields this package's own UI displays
 * are included; `context`/`desired_outcome`/`constraints`/
 * `stakeholders` remain server-side detail this package does not
 * render (12 §24 names no requirement to show them, and Evidence's own
 * "Display only where mapped" line applies equally to unmapped
 * Challenge detail).
 */
export interface ChallengeView {
  readonly challengeId: ChallengeId;
  readonly workspaceId: WorkspaceId;
  readonly title: string;
  readonly description: string | null;
}

/** `packages/domain/session.py`'s own `Session` -- 12 §24 item 3
 * ("current Session state"). */
export interface SessionSummary {
  readonly sessionId: SessionId;
  readonly challengeId: ChallengeId;
  readonly workspaceId: WorkspaceId;
  readonly state: SessionState;
}

/** `packages/domain/question.py`'s own `Question` -- 12 §24 items 6/8
 * ("verbatim human Question list", "origin marker HUMAN or AI").
 * `originalText` only -- never `normalized_text` (12 §24 item 6 names
 * VERBATIM capture specifically; a normalized/derived rendering is out
 * of this package's own scope, and Evidence's own "Display only where
 * mapped" applies).
 */
export interface QuestionView {
  readonly questionId: QuestionId;
  readonly originalText: string;
  readonly origin: QuestionOrigin;
}

/** `packages/domain/burst.py`'s own `QuestionBurst` -- 12 §24 items
 * 4/5/7 ("Burst state", "HUMAN_ONLY mode indicator", "frozen raw-set
 * indicator after completion").
 *
 * WHY THERE IS NO SEPARATE `isFrozen` FIELD
 * --------------------------------------------------------------------
 * 03's own topology makes `COMPLETED` Bursts immutable (no further
 * BURST-scoped mutation legitimately occurs afterward) -- "frozen" is
 * therefore a DERIVED fact of `state`, not a second, independently
 * settable flag a server or a compromised client could set
 * inconsistently with `state` itself. `isBurstFrozen()` below computes
 * it from `state` alone, the same "derived predicate, not a
 * separately-settable fact" discipline `recovery.models.recovery_target_ref`'s
 * own sibling `is_target_blocked` already established server-side
 * (PKG-24).
 */
export interface BurstView {
  readonly burstId: BurstId;
  readonly sessionId: SessionId;
  readonly state: BurstState;
  readonly mode: BurstMode;
  readonly questions: readonly QuestionView[];
}

export function isBurstFrozen(burst: BurstView): boolean {
  return burst.state === "COMPLETED";
}

/**
 * `packages/ai_contracts/generation.py`'s own `AIGeneration` (PKG-19)
 * -- the minimal display shape 12 §24 item 11 ("Decision boundary
 * showing that AI recommendation is not a Decision") and this
 * package's own AI line ("Recommendation displayed separately")
 * require: enough to render an AI recommendation visibly and label it
 * as such, nothing more.
 *
 * WHY `summary` IS THE ONLY CONTENT FIELD, AND WHY IT IS DISCLOSED AS
 * OPAQUE
 * --------------------------------------------------------------------
 * `AIGeneration.output_artifact_ref` (09 §55) is itself an opaque
 * forward reference to a not-yet-built artifact store -- this package
 * does not resolve it into structured content any more than
 * `domain.decision.Decision.provenance_ref` does. `summary` stands in
 * for whatever server-side resolution a real backend route would
 * perform; this package never computes, truncates, or "cleans up" it
 * -- it only displays exactly the string the (disclosed,
 * not-yet-built) backend would already have resolved.
 */
export interface AiRecommendationView {
  readonly generationId: string;
  readonly summary: string;
}

/**
 * `packages/domain/decision.py`'s own `Decision` (PKG-15) -- 07 §54.8's
 * own "Provenance Minimums by Artifact Class: Decision" list (human
 * authoritative origin for DECIDED state; DecisionAuthority holder; AI
 * recommendations consumed where applicable; Evidence set consumed
 * where applicable; selected option; rationale; decision time) is what
 * this interface's own fields materialize -- 12 §24 item 15's own
 * "minimal provenance/audit reconstruction view" for the Decision
 * artifact class specifically, not the deeper Command/CommitUnit/
 * AuditEvent/Outbox reconstruction chain `GET /commands/{c}/reconstruction`
 * would expose (that query is not assigned to this package by 14 at
 * all; see this package's own completion report KNOWN_LIMITATIONS).
 *
 * `decidedByUserId`/`decisionAuthorityBindingId` are opaque display
 * refs (never decoded into a resolved identity/governance object here)
 * -- their mere PRESENCE once `state === "DECIDED"` is itself the
 * "human authoritative origin"/"DecisionAuthority holder" proof 07
 * §54.8 names; `Decision.__post_init__`'s own backend invariant
 * already guarantees a DECIDED row can never lack either one.
 *
 * `aiRecommendationConsumedRef` mirrors `Decision.provenance_ref`
 * (`uuid.UUID | None`) exactly, including its own honestly-disclosed
 * limitation: `application.human_decision_handler.open_decision_consideration`
 * hardcodes `provenance_ref=None` on every real Decision it creates --
 * no code path in this codebase populates it yet. This field will
 * therefore always render `null` in practice today; kept in the type
 * (not omitted) because 07 §54.8 names the minimum regardless of
 * whether any current caller populates it, the same "field mapped even
 * though the real value is always absent right now" treatment
 * `ChallengeView.description` already established (PKG-28).
 */
export interface DecisionView {
  readonly decisionId: DecisionId;
  readonly challengeId: ChallengeId;
  readonly decisionQuestionRef: QuestionId | null;
  readonly decisionQuestionText: string | null;
  readonly options: readonly string[];
  readonly criteria: readonly string[];
  readonly selectedOption: string | null;
  readonly rationale: string | null;
  readonly confidence: string | null;
  readonly state: DecisionState;
  readonly decidedByUserId: string | null;
  readonly decisionAuthorityBindingId: string | null;
  readonly aiRecommendationConsumedRef: string | null;
  readonly decidedAt: string | null;
}

/** Everything this package's own Session-view UI needs, together --
 * the positive (`ok`) case of `SessionReadResult` below.
 *
 * `decision`/`aiRecommendation` are PKG-29's own additions to the SAME
 * single `GET /workspaces/{w}/sessions/{s}` query PKG-28 already
 * established, not a second parallel query -- 12 §23 itself names no
 * dedicated Decision-read route, and richer-payload-on-the-same-query
 * is the identical "exact HTTP paths are prototype interface choices"
 * disclosure PKG-28 already relied on, extended rather than repeated
 * with a new invented endpoint.
 */
export interface SessionView {
  readonly workspaceId: WorkspaceId;
  readonly challenge: ChallengeView;
  readonly session: SessionSummary;
  readonly burst: BurstView | null;
  readonly decision: DecisionView | null;
  readonly aiRecommendation: AiRecommendationView | null;
}

/**
 * The discriminated union `GET /sessions/{s}` (12 §23's own QUERY row,
 * "read scope only") resolves to. Mirrors real, already-closed backend
 * vocabularies, never invents a new one:
 *
 * - `ok`: the query was allowed and resolved (this package's own
 *   BOUNDARIES line: "Server responses only, no client authority
 *   calculation" -- this UNION ITSELF is the server's own resolved
 *   verdict, never recomputed client-side).
 * - `denied`: `boundaries.types.BoundaryResult`'s own DENY/REQUIRE/
 *   ESCALATE outcomes (06 §2's exact 4-value vocabulary, minus ALLOW,
 *   which is the `ok` case) -- `reasonCode` mirrors
 *   `BoundaryProof.reason_code: str`'s own plain-string shape (06's
 *   own reason codes are not a single closed list; PKG-17 through
 *   PKG-26 each disclosed this same "plain string, not over-typed"
 *   treatment for reason codes).
 * - `indeterminate`: 06 §24/BND-017's own "dependency blocking
 *   metadata" concept (14 §29, PKG-24) -- the target is blocked by an
 *   unresolved, INDETERMINATE-shaped prior operation; 12 §24 item 14's
 *   own "INDETERMINATE surface that disables blind retry" is this
 *   case's own UI contract: `canRetry` is always `false` here,
 *   structurally (see `IndeterminateBanner`).
 */
export type SessionReadResult =
  | { readonly kind: "ok"; readonly data: SessionView }
  | { readonly kind: "denied"; readonly result: BoundaryDenialResult; readonly reasonCode: string }
  | { readonly kind: "indeterminate"; readonly blockedTargetRef: string };

/**
 * `POST /decisions/{d}/decide` (12 §23's own COMMAND row,
 * `CMD_RECORD_HUMAN_DECISION`) resolves to this. Mirrors
 * `SessionReadResult`'s own shape deliberately (same `denied`/
 * `indeterminate` vocabulary, same discriminated-union discipline) but
 * is NOT the same type -- a Command result and a Query result are
 * different things (NON_COLLAPSE_RULES: "Do not turn ... Event into
 * Command"; the same discipline extends to not collapsing a Command's
 * own result shape into a Query's).
 *
 * - `committed`: `application.human_decision_handler.record_human_decision`
 *   reached a real `CommitCoordinator.commit` (06's own BND-001..007
 *   chain ALLOWed, BND-014 ALLOWed) -- `decision` is the fresh,
 *   server-returned post-commit `DecisionView`, NEVER a client-guessed
 *   projection of what the UI expected to happen (see
 *   `RecordDecisionForm`'s own docstring: no optimistic rendering
 *   exists anywhere in this package).
 * - `denied`: the PRECOMMIT boundary chain (BND-001..007) did not
 *   reach ALLOW -- `application.human_decision_handler.HumanDecisionDenied`'s
 *   own real shape, mirrored here as the same DENY/REQUIRE/ESCALATE
 *   vocabulary `SessionReadResult` already uses.
 * - `indeterminate`: mirrors `SessionReadResult`'s own case (BND-017's
 *   dependency-blocking concept, PKG-24) -- a prior operation this
 *   Decision depends on is unresolved.
 * - `rejected`: a POST-boundary, application-level rejection distinct
 *   from a boundary DENY -- mirrors
 *   `application.human_decision_handler.SelectedOptionNotCandidate`
 *   (a submitted `selectedOption` not among the Decision's own real
 *   `options`) and `commit.coordinator.StaleVersionConflict` (a
 *   concurrent modification raced this submission). Kept as its own
 *   case rather than folded into `denied` because the real backend
 *   raises these as genuinely different exception types, for
 *   genuinely different reasons, AFTER the boundary chain already
 *   ALLOWed -- collapsing them into "DENY" would misrepresent which
 *   layer actually refused the request.
 */
export type DecisionActionResult =
  | { readonly kind: "committed"; readonly decision: DecisionView }
  | { readonly kind: "denied"; readonly result: BoundaryDenialResult; readonly reasonCode: string }
  | { readonly kind: "indeterminate"; readonly blockedTargetRef: string }
  | { readonly kind: "rejected"; readonly reasonCode: string };
