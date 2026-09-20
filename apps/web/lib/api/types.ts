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

/** Everything this package's own Session-view UI needs, together --
 * the positive (`ok`) case of `SessionReadResult` below. */
export interface SessionView {
  readonly workspaceId: WorkspaceId;
  readonly challenge: ChallengeView;
  readonly session: SessionSummary;
  readonly burst: BurstView | null;
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
  | { readonly kind: "denied"; readonly result: "DENY" | "REQUIRE" | "ESCALATE"; readonly reasonCode: string }
  | { readonly kind: "indeterminate"; readonly blockedTargetRef: string };
