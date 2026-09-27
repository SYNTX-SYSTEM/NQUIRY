/**
 * F02 typed client for the governed inquiry surfaces (WU-02.10).
 *
 * Every response goes through ONE envelope parser. Each outcome kind the server
 * sends (`application.http_f02`) stays distinct here and in the UI:
 * committed / denied / rejected / stale / blocked / failed_precommit /
 * indeterminate / not_found. A rejected `fetch` (no response at all) becomes
 * `network_failure`, which is never confused with any server verdict.
 *
 * This module computes no authority. Capabilities come from the server
 * (`available` / `reasonCode` / `reason`) and are rendered as-is.
 *
 * Idempotency: every Command carries an `Idempotency-Key` created once per
 * logical intent by the caller (`newIntentKey()`), so a retry of the same
 * intent is the same Command on the server. UI DEBOUNCE ≠ IDEMPOTENCY.
 */
import { apiBaseUrl, isRecord } from "./client";

export type Capability = {
  readonly available: boolean;
  readonly reasonCode: string | null;
  readonly reason: string | null;
};

export type Member = { readonly userId: string; readonly name: string; readonly email: string; readonly role: string | null };

export type BindingProvenance = {
  readonly bindingId: string;
  readonly holderUserId: string;
  readonly holderName: string;
  readonly authorityClass: string;
  readonly scope: string;
  readonly grantedByUserId: string;
  readonly grantedByName: string;
  readonly grantedAt: string;
};

export type WorkspaceRef = { readonly workspaceId: string; readonly name: string; readonly governedFounding: boolean };

export type WorkspaceOverview = {
  readonly workspace: WorkspaceRef;
  readonly viewer: { readonly userId: string; readonly role: string | null; readonly isGovernanceRoot: boolean };
  readonly members: readonly Member[];
  readonly challenges: readonly { readonly challengeId: string; readonly title: string; readonly description: string | null; readonly createdAt: string }[];
  readonly capabilities: { readonly createChallenge: Capability; readonly addMember: Capability };
};

export type ChallengeDetail = {
  readonly workspace: WorkspaceRef;
  readonly challenge: { readonly challengeId: string; readonly title: string; readonly description: string | null; readonly createdAt: string };
  readonly sessions: readonly { readonly sessionId: string; readonly state: string; readonly version: number; readonly createdAt: string }[];
  readonly sessionControllers: readonly BindingProvenance[];
  readonly members: readonly Member[];
  readonly capabilities: { readonly openSession: Capability; readonly grantSessionControl: Capability };
};

export type SessionActionName =
  | "BEGIN_SETUP"
  | "BEGIN_CHALLENGE_CAPTURE"
  | "PREPARE_BURST"
  | "ADMIT_PARTICIPANT"
  | "OPEN_QUESTION_GENERATION"
  | "GRANT_SESSION_CONTROL";

/**
 * WU-CY-01 (HD-27): the ANALYSIS boundary as projected by the pinned RED producer `checkpoint-PFC-B5`
 * (`7d3f74e4685b821cc948f45e413c1e0c207259d4`). Its `actions` is a superset of the F03 contract; only
 * `BEGIN_ANALYSIS` (TRN-SESS-006, `transitions/begin-analysis`) is consumed here. The key is OPTIONAL in the type:
 * the published F03 producer does not send it, and its absence means "not projected" (no affordance, no reason),
 * never a default.
 */
export type AnalysisActionName = "BEGIN_ANALYSIS";

/** F03: the burst-scoped actions the server projects (capability, never authority). */
export type BurstActionName = "CAPTURE_QUESTION" | "COMPLETE_BURST";

export type CapturedQuestion = {
  readonly questionId: string;
  readonly originalText: string;
  readonly origin: string;
  readonly captureOrigin: string;
  readonly authorUserId: string | null;
  readonly authorName: string | null;
  readonly capturedOrder: number;
  readonly capturedAt: string;
};

export type FrozenSet = {
  readonly fingerprint: string | null;
  readonly verified: boolean;
  readonly memberCount: number;
  readonly completedAt: string | null;
  readonly questions: readonly CapturedQuestion[];
};

/** HD-13: what the server entitles THIS viewer to see of the Burst's questions. */
export type QuestionSet = {
  readonly visibility: "NONE" | "OWN_ONLY_WHILE_ACTIVE" | "FULL_FROZEN_SET";
  readonly mine: readonly CapturedQuestion[];
  readonly capturedCount: number | null;
  readonly frozen: FrozenSet | null;
};

/** The producer's marker on every derived item (analysis_projection.py `marker`): origin, derivation and proof in words. */
export type AnalysisMarker = {
  readonly origin: string;
  readonly derived: boolean;
  readonly kind: string;
  readonly provider: string | null;
  readonly proof: string;
  readonly isMock: boolean;
  readonly note: string;
};

/**
 * `position.analysis` (F04 HD-22 via the pinned producer): served exactly when the full frozen set is served;
 * `{visible: false}` otherwise. The artifact's `content` is typed as opaque and is never rendered (WU-CY-01 scope).
 */
export type AnalysisProjection =
  | { readonly visible: false }
  | {
      readonly visible: true;
      readonly audience: string;
      readonly marker: AnalysisMarker;
      readonly analysis: {
        readonly status: string;
        readonly reasonCode: string | null;
        readonly artifact: {
          readonly artifactId: string;
          readonly generationId: string;
          readonly proofClass: string | null;
          readonly isMockNonProof: boolean;
          readonly acceptedAt: string;
          readonly acceptedByCommandId: string | null;
          readonly marker: AnalysisMarker;
          readonly content: unknown;
        } | null;
      };
      // the producer sends more (runId, clusters, authorization, …); only these fields are consumed, the rest is tolerated
      readonly clustering?: { readonly status: string; readonly reasonCode: string | null } & Readonly<Record<string, unknown>>;
      readonly generations?: readonly ({ readonly generationId: string; readonly status: string; readonly provider: string | null } & Readonly<Record<string, unknown>>)[];
    };

export type SessionPosition = {
  readonly workspace: WorkspaceRef;
  readonly challenge: { readonly challengeId: string; readonly title: string | null; readonly description: string | null };
  readonly session: {
    readonly sessionId: string;
    readonly state: string;
    readonly version: number;
    readonly method: string;
    readonly createdAt: string;
    /** HD-24 (pinned producer): a Fixture (NON_PROOF) Session, declared at creation. Absent from the F03 producer. */
    readonly fixture?: boolean;
    /** "GOVERNED" | "FIXTURE_NON_PROOF" from the pinned producer; absent from the F03 producer. */
    readonly proofMode?: string;
  };
  readonly phases: readonly { readonly state: string; readonly status: "done" | "current" | "upcoming" }[];
  readonly serverNow: string;
  readonly burst: {
    readonly burstId: string;
    readonly state: string;
    readonly mode: string;
    readonly version: number;
    readonly startedAt: string | null;
    readonly completedAt: string | null;
    readonly guidanceSeconds: number;
    readonly guidanceIsAuthoritative: boolean;
  } | null;
  readonly questionSet: QuestionSet;
  readonly participants: readonly { readonly userId: string; readonly name: string | null; readonly joinedAt: string; readonly admittedByUserId: string }[];
  readonly sessionControllers: readonly BindingProvenance[];
  readonly establishedBy: {
    readonly commandType: string;
    readonly actorName: string | null;
    readonly occurredAt: string;
    readonly commitId: string;
    readonly authoritySourceType: string | null;
    readonly authoritySourceRef: string;
    readonly authorityScopeRef: string | null;
  } | null;
  readonly viewer: { readonly userId: string; readonly role: string | null; readonly isSessionController: boolean; readonly isGovernanceRoot: boolean };
  readonly actions: Readonly<Record<SessionActionName | BurstActionName, Capability & { readonly relevant: boolean }>> &
    Readonly<Partial<Record<AnalysisActionName, Capability & { readonly relevant: boolean }>>>;
  readonly admitCandidates: readonly { readonly userId: string; readonly name: string }[];
  readonly grantCandidates: readonly { readonly userId: string; readonly name: string }[];
  /** WU-CY-01: the derived field, as the pinned producer projects it; absent from the F03 producer. */
  readonly analysis?: AnalysisProjection;
};

export type FailureKind =
  | "denied"
  | "rejected"
  | "stale"
  | "blocked"
  | "failed_precommit"
  | "indeterminate"
  | "not_found"
  | "network_failure";

export type Failure = {
  readonly kind: FailureKind;
  readonly reasonCode: string;
  readonly currentState?: string;
  readonly currentVersion?: number;
};

export type QueryResult<T> = { readonly kind: "ok"; readonly data: T } | Failure;

export type CommandResult<T = Record<string, unknown>> = { readonly kind: "committed"; readonly body: T } | Failure;

const FAILURE_KINDS: readonly FailureKind[] = [
  "denied",
  "rejected",
  "stale",
  "blocked",
  "failed_precommit",
  "indeterminate",
  "not_found",
];

function asFailure(body: Record<string, unknown>): Failure | null {
  const kind = body.kind;
  if (typeof kind !== "string" || !(FAILURE_KINDS as readonly string[]).includes(kind)) {
    return null;
  }
  const failure: Failure = {
    kind: kind as FailureKind,
    reasonCode: typeof body.reasonCode === "string" ? body.reasonCode : kind.toUpperCase(),
    ...(typeof body.currentState === "string" ? { currentState: body.currentState } : {}),
    ...(typeof body.currentVersion === "number" ? { currentVersion: body.currentVersion } : {}),
  };
  return failure;
}

/** Fail closed: an unrecognized body is a protocol error, never a success. */
function protocolError(): Failure {
  return { kind: "indeterminate", reasonCode: "UNRECOGNIZED_SERVER_RESPONSE" };
}

export function parseQuery<T>(body: unknown): QueryResult<T> {
  if (!isRecord(body)) return protocolError();
  if (body.kind === "ok") return { kind: "ok", data: body as unknown as T };
  return asFailure(body) ?? protocolError();
}

export function parseCommand<T>(body: unknown): CommandResult<T> {
  if (!isRecord(body)) return protocolError();
  if (body.kind === "committed") return { kind: "committed", body: body as unknown as T };
  return asFailure(body) ?? protocolError();
}

export function newIntentKey(): string {
  return crypto.randomUUID();
}

async function get<T>(path: string, fetchImpl: typeof fetch): Promise<QueryResult<T>> {
  let response: Response;
  try {
    response = await fetchImpl(`${apiBaseUrl()}${path}`, {
      headers: { Accept: "application/json" },
      credentials: "include",
    });
  } catch {
    return { kind: "network_failure", reasonCode: "NETWORK_FAILURE" };
  }
  try {
    return parseQuery<T>(await response.json());
  } catch {
    return protocolError();
  }
}

async function post<T>(path: string, intentKey: string, body: unknown, fetchImpl: typeof fetch): Promise<CommandResult<T>> {
  let response: Response;
  try {
    response = await fetchImpl(`${apiBaseUrl()}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json", "Idempotency-Key": intentKey },
      credentials: "include",
      body: JSON.stringify(body ?? {}),
    });
  } catch {
    return { kind: "network_failure", reasonCode: "NETWORK_FAILURE" };
  }
  try {
    return parseCommand<T>(await response.json());
  } catch {
    return protocolError();
  }
}

const enc = encodeURIComponent;

export function fetchWorkspaceOverview(workspaceId: string, fetchImpl: typeof fetch = fetch) {
  return get<WorkspaceOverview>(`/workspaces/${enc(workspaceId)}/overview`, fetchImpl);
}

export function fetchChallengeDetail(workspaceId: string, challengeId: string, fetchImpl: typeof fetch = fetch) {
  return get<ChallengeDetail>(`/workspaces/${enc(workspaceId)}/challenges/${enc(challengeId)}`, fetchImpl);
}

export function fetchSessionPosition(workspaceId: string, sessionId: string, fetchImpl: typeof fetch = fetch) {
  return get<SessionPosition>(`/workspaces/${enc(workspaceId)}/sessions/${enc(sessionId)}/position`, fetchImpl);
}

export function createChallenge(
  workspaceId: string,
  input: { readonly title: string; readonly description: string },
  intentKey: string,
  fetchImpl: typeof fetch = fetch,
) {
  return post<{ readonly challengeId: string }>(`/workspaces/${enc(workspaceId)}/challenges`, intentKey, input, fetchImpl);
}

/**
 * CMD_CREATE_SESSION. `fixture: true` (HD-24, pinned producer) declares a Fixture (NON_PROOF) Session and is sent
 * only when the human chose it; otherwise the body stays the F03 contract `{}` (the F03 producer takes no body).
 */
export function openSession(
  workspaceId: string,
  challengeId: string,
  intentKey: string,
  options: { readonly fixture?: boolean } = {},
  fetchImpl: typeof fetch = fetch,
) {
  return post<{ readonly sessionId: string }>(
    `/workspaces/${enc(workspaceId)}/challenges/${enc(challengeId)}/sessions`,
    intentKey,
    options.fixture === true ? { fixture: true } : {},
    fetchImpl,
  );
}

export function grantSessionControl(
  workspaceId: string,
  holderUserId: string,
  scope: { readonly type: "CHALLENGE" | "SESSION"; readonly id: string },
  intentKey: string,
  fetchImpl: typeof fetch = fetch,
) {
  return post(
    `/workspaces/${enc(workspaceId)}/authority-bindings`,
    intentKey,
    { humanUserId: holderUserId, authorityClass: "SESSION_CONTROL_RIGHT", scopeType: scope.type, scopeId: scope.id },
    fetchImpl,
  );
}

const SESSION_COMMAND_PATHS: Readonly<Record<Exclude<SessionActionName, "GRANT_SESSION_CONTROL"> | AnalysisActionName, string>> = {
  BEGIN_SETUP: "transitions/begin-setup",
  BEGIN_CHALLENGE_CAPTURE: "transitions/begin-challenge-capture",
  PREPARE_BURST: "burst",
  ADMIT_PARTICIPANT: "participants",
  OPEN_QUESTION_GENERATION: "transitions/open-question-generation",
  BEGIN_ANALYSIS: "transitions/begin-analysis",
};

export function runSessionCommand(
  workspaceId: string,
  sessionId: string,
  action: Exclude<SessionActionName, "GRANT_SESSION_CONTROL"> | AnalysisActionName,
  expectedVersion: number,
  intentKey: string,
  extra: { readonly participantUserId?: string } = {},
  fetchImpl: typeof fetch = fetch,
) {
  return post<{ readonly position: SessionPosition; readonly replayed: boolean }>(
    `/workspaces/${enc(workspaceId)}/sessions/${enc(sessionId)}/${SESSION_COMMAND_PATHS[action]}`,
    intentKey,
    { expectedVersion, ...extra },
    fetchImpl,
  );
}

/**
 * CMD_CAPTURE_BURST_QUESTION. The wire contract is EXACTLY the text and the
 * Burst version the viewer saw. Origin and author are never sent: the server
 * takes them from the verified session (a client-supplied one is rejected).
 * `originalText` is sent byte-exact: no trim, no normalization.
 */
export function captureBurstQuestion(
  workspaceId: string,
  sessionId: string,
  originalText: string,
  expectedBurstVersion: number,
  intentKey: string,
  fetchImpl: typeof fetch = fetch,
) {
  return post<{ readonly position: SessionPosition; readonly replayed: boolean; readonly questionId: string }>(
    `/workspaces/${enc(workspaceId)}/sessions/${enc(sessionId)}/burst/questions`,
    intentKey,
    { originalText, expectedBurstVersion },
    fetchImpl,
  );
}

/** CMD_COMPLETE_BURST: TRN-SESS-005 + TRN-BURST-005 as one manual, authorized bundle. */
export function completeBurst(
  workspaceId: string,
  sessionId: string,
  expectedSessionVersion: number,
  expectedBurstVersion: number,
  intentKey: string,
  fetchImpl: typeof fetch = fetch,
) {
  return post<{ readonly position: SessionPosition; readonly replayed: boolean }>(
    `/workspaces/${enc(workspaceId)}/sessions/${enc(sessionId)}/transitions/complete-burst`,
    intentKey,
    { expectedVersion: expectedSessionVersion, expectedBurstVersion },
    fetchImpl,
  );
}

export function addMemberCommand(
  workspaceId: string,
  userId: string,
  role: string,
  fetchImpl: typeof fetch = fetch,
): Promise<CommandResult> {
  // F01 route (no idempotency key in F01's contract; its success body is {kind: "ok"}).
  return fetchImpl(`${apiBaseUrl()}/workspaces/${enc(workspaceId)}/members`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    credentials: "include",
    body: JSON.stringify({ userId, role }),
  })
    .then((r) => r.json())
    .then((body: unknown): CommandResult => {
      if (isRecord(body) && body.kind === "ok") return { kind: "committed", body };
      if (isRecord(body)) return asFailure(body) ?? protocolError();
      return protocolError();
    })
    .catch((): CommandResult => ({ kind: "network_failure", reasonCode: "NETWORK_FAILURE" }));
}

export const OUTCOME_TEXT: Readonly<Record<FailureKind | "committed", string>> = {
  committed: "Committed. The canonical state below was re-read from the server.",
  denied: "Denied. The current authority or boundary checks did not allow this.",
  rejected: "Rejected. The request was invalid (no authority decision was made).",
  stale: "Stale. The Session changed since you loaded it. The current state is shown now.",
  blocked: "Blocked. A required precondition is not met yet.",
  failed_precommit: "Not committed. The change was rolled back before commit.",
  indeterminate: "Outcome unknown. Do not retry blindly. Reload to see the canonical state.",
  not_found: "Not found in this Workspace.",
  network_failure: "The server could not be reached. Nothing is assumed to have changed.",
};
