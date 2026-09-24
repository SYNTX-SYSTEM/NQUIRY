/**
 * The typed API client (14 §46 PKG-28's own PUBLIC_INTERFACES).
 *
 * WHY THIS CALLS A REAL, CONFIGURABLE BASE URL DESPITE NO REAL BACKEND
 * ROUTE EXISTING YET
 * --------------------------------------------------------------------
 * `apps/api/src/nquiry_api/main.py` still exposes only `/healthz`
 * (unchanged since PKG-00/PKG-27) -- no `GET /sessions/{s}` route
 * exists anywhere in this codebase yet. This client is nonetheless
 * real, real production code, not a stub: it issues a genuine `fetch`
 * against `NEXT_PUBLIC_API_BASE_URL` (defaulting to
 * `docker-compose.yml`'s own `api` service port, 8000), parses a real
 * HTTP response, and narrows it into the real `SessionReadResult`
 * union `types.ts` declares. Proven end to end via Playwright's own
 * real browser + real network-layer route interception
 * (`tests/e2e/session-view.spec.ts`), not a mocked module import --
 * the identical "prove the mechanism for real, disclose the missing
 * concrete backend route as SUCCESSOR_NOT_BUILT" pattern this
 * codebase's own backend packages have used repeatedly (PKG-13/16/17/
 * 25/26/27), applied here from the frontend's own side of the same
 * gap.
 *
 * WHY THIS IS A CLIENT-SIDE FETCH, NOT A NEXT.JS SERVER COMPONENT
 * SERVER-SIDE FETCH
 * --------------------------------------------------------------------
 * A server-side `fetch` executed during Next.js SSR runs in the
 * Node.js process itself and never crosses the BROWSER's own network
 * stack -- Playwright's `page.route()` can only intercept requests the
 * browser actually issues. Making the fetch happen in the browser
 * (`"use client"` components calling this module) is what makes the
 * real E2E proof possible at all without a live backend; this is a
 * disclosed `[IMPLEMENTATION CHOICE]`, not an architectural
 * requirement either way (12 §23/24 name no rendering strategy).
 */

import {
  BOUNDARY_DENIAL_RESULTS,
  BURST_MODES,
  BURST_STATES,
  DECISION_STATES,
  QUESTION_ORIGINS,
  SESSION_STATES,
  type AiRecommendationView,
  type BurstView,
  type ChallengeView,
  type DecisionView,
  type SessionId,
  type SessionReadResult,
  type SessionSummary,
  type WorkspaceId,
} from "./types";

export const DEFAULT_API_BASE_URL = "http://localhost:8000";

export function apiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? DEFAULT_API_BASE_URL;
}

/**
 * `GET /sessions/{s}` (12 §23's own QUERY row). `workspaceId` is
 * accepted so the CALLER's own claimed scope is visible in the
 * request/response cycle for the "forged Workspace in client" attack
 * proof (`tests/e2e/session-view.spec.ts`) -- this function itself
 * never uses `workspaceId` to decide anything; it is sent to the
 * server and the server's own response (`SessionReadResult`) is the
 * only thing this function ever returns. There is no code path here
 * that could grant access a `denied`/`indeterminate` server response
 * did not already grant.
 *
 * IDENTITY (local-login field, `docs/architecture/18_LOCAL_AUTHENTICATION_ADAPTER.md`):
 * this function no longer sends any actor identity header. Identity now
 * travels as the real, `HttpOnly` `nquiry_session` cookie a real
 * `POST /auth/login` call issues (`lib/api/authClient.ts`) -- `credentials:
 * "include"` below is what makes the browser attach that cookie to this
 * real cross-origin (`localhost:3000` -> `localhost:8000`) request at
 * all. This function still computes no authority of its own and reads
 * no cookie value itself; a caller with no valid session gets the same
 * real `401`/`denied` response the server already returns for a missing
 * or invalid session -- never a client-side guess.
 */
export async function fetchSessionView(
  workspaceId: WorkspaceId,
  sessionId: SessionId,
  fetchImpl: typeof fetch = fetch,
): Promise<SessionReadResult> {
  const response = await fetchImpl(
    `${apiBaseUrl()}/workspaces/${encodeURIComponent(workspaceId)}/sessions/${encodeURIComponent(sessionId)}`,
    { headers: { Accept: "application/json" }, credentials: "include" },
  );
  const body: unknown = await response.json();
  return parseSessionReadResult(body);
}

/**
 * Narrows an arbitrary JSON body into the real `SessionReadResult`
 * union. Fails closed (this package's own NON_COLLAPSE_RULES:
 * "Unknown consequential semantic input fails closed") on any body
 * shape that does not match one of the three known cases -- never
 * silently defaults to `ok`. This now includes every NESTED
 * closed-vocabulary field (`state`, `mode`, `origin`), not only the
 * top-level `kind`/`denied.result` discriminators -- see `requireEnum`
 * below and `types.ts`'s own `SESSION_STATES`/`BURST_STATES`/
 * `BURST_MODES`/`QUESTION_ORIGINS` retrofit note for why the earlier
 * `requireString(...) as X` casts on those fields were a compile-time-
 * only assertion, not the runtime fail-closed check this docstring
 * always claimed.
 */
export function parseSessionReadResult(body: unknown): SessionReadResult {
  if (!isRecord(body) || typeof body.kind !== "string") {
    throw new TypeError("SessionReadResult response body is missing a recognizable 'kind'");
  }
  switch (body.kind) {
    case "ok":
      return { kind: "ok", data: parseSessionView(body.data) };
    case "denied":
      return {
        kind: "denied",
        result: requireEnum(body, "result", BOUNDARY_DENIAL_RESULTS),
        reasonCode: requireNonEmptyString(body, "reasonCode"),
      };
    case "indeterminate":
      return { kind: "indeterminate", blockedTargetRef: requireNonEmptyString(body, "blockedTargetRef") };
    case "rejected":
      return { kind: "rejected", reasonCode: requireNonEmptyString(body, "reasonCode") };
    default:
      throw new TypeError(`unrecognized SessionReadResult kind ${JSON.stringify(body.kind)}`);
  }
}

function parseSessionView(value: unknown): SessionView {
  if (!isRecord(value)) {
    throw new TypeError("SessionView body must be an object");
  }
  return {
    workspaceId: requireString(value, "workspaceId") as WorkspaceId,
    challenge: parseChallengeView(value.challenge),
    session: parseSessionSummary(value.session),
    burst: value.burst === null ? null : parseBurstView(value.burst),
    decision: value.decision === null ? null : parseDecisionView(value.decision),
    aiRecommendation: value.aiRecommendation === null ? null : parseAiRecommendationView(value.aiRecommendation),
  };
}

/**
 * `packages/domain/decision.py`'s own `Decision` (PKG-15), narrowed
 * from the same `GET /workspaces/{w}/sessions/{s}` response
 * `parseSessionView` already parses -- see `DecisionView`'s own
 * docstring in `types.ts` for why this lives on the SAME query rather
 * than a second invented endpoint.
 */
export function parseDecisionView(value: unknown): DecisionView {
  if (!isRecord(value)) {
    throw new TypeError("DecisionView body must be an object");
  }
  if (!Array.isArray(value.options) || !value.options.every((o) => typeof o === "string")) {
    throw new TypeError("DecisionView.options must be an array of strings");
  }
  if (!Array.isArray(value.criteria) || !value.criteria.every((c) => typeof c === "string")) {
    throw new TypeError("DecisionView.criteria must be an array of strings");
  }
  return {
    decisionId: requireString(value, "decisionId") as DecisionView["decisionId"],
    challengeId: requireString(value, "challengeId") as DecisionView["challengeId"],
    decisionQuestionRef:
      value.decisionQuestionRef === null
        ? null
        : (requireString(value, "decisionQuestionRef") as DecisionView["decisionQuestionRef"]),
    decisionQuestionText: value.decisionQuestionText === null ? null : requireString(value, "decisionQuestionText"),
    options: value.options,
    criteria: value.criteria,
    selectedOption: value.selectedOption === null ? null : requireString(value, "selectedOption"),
    rationale: value.rationale === null ? null : requireString(value, "rationale"),
    confidence: value.confidence === null ? null : requireString(value, "confidence"),
    state: requireEnum(value, "state", DECISION_STATES),
    decidedByUserId: value.decidedByUserId === null ? null : requireString(value, "decidedByUserId"),
    decisionAuthorityBindingId:
      value.decisionAuthorityBindingId === null ? null : requireString(value, "decisionAuthorityBindingId"),
    aiRecommendationConsumedRef:
      value.aiRecommendationConsumedRef === null ? null : requireString(value, "aiRecommendationConsumedRef"),
    decidedAt: value.decidedAt === null ? null : requireString(value, "decidedAt"),
  };
}

function parseAiRecommendationView(value: unknown): AiRecommendationView {
  if (!isRecord(value)) {
    throw new TypeError("AiRecommendationView body must be an object");
  }
  return {
    generationId: requireString(value, "generationId"),
    summary: requireString(value, "summary"),
  };
}

function parseChallengeView(value: unknown): ChallengeView {
  if (!isRecord(value)) {
    throw new TypeError("ChallengeView body must be an object");
  }
  return {
    challengeId: requireString(value, "challengeId") as ChallengeView["challengeId"],
    workspaceId: requireString(value, "workspaceId") as WorkspaceId,
    title: requireString(value, "title"),
    description: value.description === null ? null : requireString(value, "description"),
  };
}

function parseSessionSummary(value: unknown): SessionSummary {
  if (!isRecord(value)) {
    throw new TypeError("SessionSummary body must be an object");
  }
  return {
    sessionId: requireString(value, "sessionId") as SessionId,
    challengeId: requireString(value, "challengeId") as SessionSummary["challengeId"],
    workspaceId: requireString(value, "workspaceId") as WorkspaceId,
    state: requireEnum(value, "state", SESSION_STATES),
  };
}

function parseBurstView(value: unknown): BurstView {
  if (!isRecord(value)) {
    throw new TypeError("BurstView body must be an object");
  }
  if (!Array.isArray(value.questions)) {
    throw new TypeError("BurstView.questions must be an array");
  }
  return {
    burstId: requireString(value, "burstId") as BurstView["burstId"],
    sessionId: requireString(value, "sessionId") as SessionId,
    state: requireEnum(value, "state", BURST_STATES),
    mode: requireEnum(value, "mode", BURST_MODES),
    questions: value.questions.map((q) => {
      if (!isRecord(q)) {
        throw new TypeError("QuestionView body must be an object");
      }
      return {
        questionId: requireString(q, "questionId") as BurstView["questions"][number]["questionId"],
        originalText: requireString(q, "originalText"),
        origin: requireEnum(q, "origin", QUESTION_ORIGINS),
      };
    }),
  };
}

/**
 * Shared, exported so `decisionClient.ts` (PKG-29) reuses the exact
 * same fail-closed parsing discipline rather than re-implementing (and
 * risking re-diverging) its own copy -- a minimal, disclosed extension
 * of this existing file, not a new generic "utils" dumping ground
 * (this package's own FILES_FORBIDDEN_TO_MODIFY line).
 */
export function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

export function requireString(record: Record<string, unknown>, key: string): string {
  const value = record[key];
  if (typeof value !== "string") {
    throw new TypeError(`expected string field '${key}', got ${JSON.stringify(value)}`);
  }
  return value;
}

function requireNonEmptyString(record: Record<string, unknown>, key: string): string {
  const value = requireString(record, key);
  if (value.length === 0) {
    throw new TypeError(`expected non-empty string field '${key}'`);
  }
  return value;
}

/**
 * Runtime companion to `requireString`: also checks the value is one
 * of `allowed` (a closed-vocabulary array from `types.ts`), fails
 * closed on anything else. Retrofitted per external review -- see the
 * `parseSessionReadResult` docstring above and `types.ts`'s own
 * `SESSION_STATES` retrofit note.
 */
export function requireEnum<T extends string>(record: Record<string, unknown>, key: string, allowed: readonly T[]): T {
  const value = requireString(record, key);
  if (!(allowed as readonly string[]).includes(value)) {
    throw new TypeError(`expected one of ${JSON.stringify(allowed)} for field '${key}', got ${JSON.stringify(value)}`);
  }
  return value as T;
}

// Re-exported so callers importing only from `client.ts` still get the
// `SessionView` type this module's own parsing functions produce.
import type { SessionView } from "./types";
export type { SessionView };
