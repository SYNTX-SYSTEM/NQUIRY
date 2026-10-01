/**
 * PCPG-R12/1 typed client + fail-closed parser (CYAN-PCPG-01; Architecture 27 v4 §13, commit b0a5101).
 *
 * The canonical RED → CYAN contract of PRE_CALL_PROMPT_GOVERNANCE is `governanceObservation` inside the response of
 * `POST /workspaces/{workspaceId}/prompt-observations` — the actor-safe R-12 projection serialized at B-10
 * (`application.http_pcpg._governance_observation_wire`, anchor `checkpoint-PFC-PCPG-18` = `41b4324`). The query is
 * side-effect-free (Architecture 26 I-18): no Idempotency-Key, nothing persisted.
 *
 * Laws of this module (v4 §00, §13.3, §13.7, §21):
 * - the types mirror the serializer field for field; nothing is added by expectation;
 * - the parser fails closed: an unknown contract identity, an unknown observation kind, an unknown closed value, a
 *   malformed or mistyped required field, an unexpected key inside the observation, or any B-10-forbidden key is a
 *   `MALFORMED_PROJECTION`, never a partial result and never an allow;
 * - `null` ≠ `false`, absent ≠ `false`, unknown ≠ denied: `null` is preserved where the contract allows it, and a
 *   missing required field is a parse failure, not a default;
 * - `canSend` is the R-10 capability projection, not a SEND gate; this module derives no label, no SEND state, no
 *   presentation and no governance fact, and sends no capability, observation or basis to the server.
 */
import { apiBaseUrl, isRecord } from "./client";
import type { Failure } from "./inquiryClient";

export const PCPG_CONTRACT = "PCPG-R12/1" as const;
export type PcpgContract = typeof PCPG_CONTRACT;

export const UNAVAILABLE_REASONS = [
  "SEMANTIC_OBSERVATION_UNAVAILABLE", // R-05 failure
  "FIELD_RECONSTRUCTION_UNAVAILABLE", // R-03 structural failure
  "PROJECTION_INCOMPLETE", // any other failure R-04 onward
] as const;
export type UnavailableReason = (typeof UNAVAILABLE_REASONS)[number];

export const EXECUTION_CLASSES = ["PROVIDER_COMPUTATION", "HUMAN_COMMAND", "EXTERNAL_EFFECT", "DISCLOSURE", "UNKNOWN"] as const;
export type ExecutionClass = (typeof EXECUTION_CLASSES)[number];

export const DELTA_RESULTS = [
  "ALLOWED",
  "HUMAN_ACTION_AVAILABLE",
  "STATE_BOUNDARY",
  "AUTHORITY_BOUNDARY",
  "DATA_BOUNDARY",
  "GOVERNANCE_BOUNDARY",
  "DENIED",
  "INDETERMINATE",
] as const;
export type DeltaResult = (typeof DELTA_RESULTS)[number];

export const MODALITIES = ["ASSERTED", "REQUESTED", "CONDITIONAL", "PROHIBITED", "HYPOTHETICAL"] as const;
export type Modality = (typeof MODALITIES)[number];

export const REQUESTED_EXECUTORS = ["HUMAN", "AI", "NONE"] as const;
export type RequestedExecutor = (typeof REQUESTED_EXECUTORS)[number];

export const PURPOSE_ALIGNMENTS = ["ALIGNED", "DRIFTED"] as const;
export type PurposeAlignment = (typeof PURPOSE_ALIGNMENTS)[number];

/** Session-level proof ceiling (partial I-12). `null` = unknown (no Session scope, or nothing retained); never GOVERNED. */
export const SESSION_PROOF_CEILINGS = ["GOVERNED", "FIXTURE_NON_PROOF"] as const;
export type SessionProofCeiling = (typeof SESSION_PROOF_CEILINGS)[number];

/** RED R-07 `DeltaRecord`, field for field (v4 §08.1). */
export interface DeltaWire {
  readonly deltaId: string;
  readonly operation: string | null; // operation-index id; null = UNKNOWN
  readonly executionClass: ExecutionClass;
  readonly target: string | null; // canonical ref | "OUT_OF_SCOPE" | null (unresolved)
  readonly sourceClause: string; // the actor's own clause text
  readonly span: readonly [number, number]; // offsets into rawIntent
  readonly currentState: string | null; // null = not applicable / unresolved
  readonly result: DeltaResult;
  readonly reasonCode: string | null;
  readonly flags: readonly string[]; // sorted closed codes
  readonly sessionProofCeiling: SessionProofCeiling | null; // Session-level proof ceiling (partial I-12)
}

/** RED R-09 chain results (v4 §09.1). */
export interface ChainWire {
  readonly firstBrokenRelation: {
    readonly predecessor: DeltaWire | null;
    readonly broken: DeltaWire;
  } | null; // null = no broken delta
  readonly maximumLegitimateTransition: readonly DeltaWire[]; // in order; currently always empty
  readonly nextValidTransition: DeltaWire | null;
  readonly humanAuthorityRequired: readonly {
    readonly deltaId: string;
    readonly result: string;
    readonly reasonCode: string | null;
  }[];
  readonly partial: boolean;
}

/** RED R-10 capability (v4 §06.2). Three independent booleans with reasons; `canSend` is a projection, never a gate. */
export interface Capability {
  readonly governanceAdmissible: boolean;
  readonly governanceAdmissibleReasons: readonly string[]; // sorted closed codes, e.g. MLT_EMPTY
  readonly providerExecutable: boolean;
  readonly providerExecutableReasons: readonly string[]; // e.g. NO_ELIGIBLE_PROVIDER_ROUTE, NO_ENVIRONMENT_DECLARED
  readonly canSend: boolean; // projection only; never a gate, never a token
}

export interface SemanticAction {
  readonly clauseIndex: number;
  readonly span: readonly [number, number];
  readonly clauseText: string;
  readonly modality: Modality;
  readonly negated: boolean;
  readonly requestedExecutor: RequestedExecutor;
  readonly candidateOperation: string | null;
  readonly target: string | null;
  readonly possibleExternalEffect: boolean;
  readonly possibleSecretContent: boolean;
  readonly decisionSubstitutionRequested: boolean;
}

export interface SemanticObservation {
  readonly ruleSetVersion: string;
  readonly clauses: readonly string[];
  readonly actions: readonly SemanticAction[];
  readonly unknownRelations: readonly string[];
  readonly relationsTouched: readonly string[];
  readonly declaredPurpose: string | null;
  readonly semanticPurpose: string | null; // null = not determinable
  readonly purposeAlignment: PurposeAlignment | null;
  readonly semanticDrift: boolean;
}

export interface GovernanceObservationCurrent {
  readonly kind: "current";
  readonly contract: PcpgContract;
  readonly basis: {
    readonly rawIntentDigestSha256: string;
    readonly derivationTime: string; // ISO-8601
  };
  readonly semanticObservation: SemanticObservation;
  readonly deltas: readonly DeltaWire[];
  readonly chain: ChainWire;
  readonly capability: Capability;
  readonly composedProofCeiling: SessionProofCeiling | null; // Session-level proof ceiling (partial I-12)
}

export type GovernanceObservation = { readonly kind: "unavailable"; readonly reasonCode: UnavailableReason } | GovernanceObservationCurrent;

/** The outer `kind: "ok"` envelope of the prompt-observation query (v4 §01, §13.2): siblings of the observation. */
export interface PromptObservation {
  readonly field: "PRE_CALL_PROMPT_GOVERNANCE";
  readonly workspace: { readonly workspaceId: string; readonly name: string };
  readonly session: { readonly sessionId: string } | null;
  readonly rawIntent: string;
  readonly rawIntentLength: number;
  readonly rawIntentDigestSha256: string;
  readonly declaredPurpose: string | null;
  readonly observedAt: string;
  readonly governanceObservation: GovernanceObservation;
}

/**
 * The typed return path for later presentation work. `malformed` is the fail-closed outcome of this parser (unknown
 * contract, kind, closed value, key or type): it is not `unavailable` (a RED kind) and never an allow.
 */
export type PromptObservationResult =
  | { readonly kind: "ok"; readonly data: PromptObservation }
  | { readonly kind: "malformed"; readonly reasonCode: "MALFORMED_PROJECTION"; readonly detail: string }
  | Failure;

export class MalformedProjection extends TypeError {
  constructor(detail: string) {
    super(`MALFORMED_PROJECTION: ${detail}`);
    this.name = "MalformedProjection";
  }
}

/**
 * B-10 / v4 §00 negative set: keys that never cross RED → CYAN. Their presence anywhere inside `governanceObservation`
 * is a contract violation and fails closed (they are not stripped and not ignored).
 */
export const B10_FORBIDDEN_KEYS = [
  "eligibleContent",
  "eligibleContentSet",
  "providerEligibility",
  "sendGate",
  "send",
  "sendRelation",
  "evidence",
  "evidenceRefs",
  "provenance",
  "provenanceRefs",
  "freshness",
  "actorProjection",
  "pulse",
  "pulseId",
  "reconstructionId",
  "snapshotId",
  "projectionId",
  "bindingId",
  "bindingVersion",
  "authorityBindingId",
  "decisionAuthorityBindingId",
  "authorityRef",
  "holderClass",
  "harHolderClass",
  "affectedSemanticLoci",
  "displaySummary",
  "nervePoints",
  "statusVector",
  "r13",
  "readinessProducer",
  "httpRoute",
  "architectureRef",
] as const;
const FORBIDDEN = new Set<string>(B10_FORBIDDEN_KEYS);

function fail(path: string, detail: string): never {
  throw new MalformedProjection(`${path}: ${detail}`);
}

function record(value: unknown, path: string): Record<string, unknown> {
  if (!isRecord(value) || Array.isArray(value)) fail(path, "expected an object");
  return value;
}

/** Exact key set: every expected key present, no key beyond them, no B-10-forbidden key anywhere. */
function exactKeys(rec: Record<string, unknown>, path: string, expected: readonly string[]): void {
  for (const key of Object.keys(rec)) {
    if (FORBIDDEN.has(key)) fail(`${path}.${key}`, "B-10-forbidden key present");
    if (!expected.includes(key)) fail(`${path}.${key}`, "unexpected key (contract PCPG-R12/1 is exact; unknown fields never become governance truth)");
  }
  for (const key of expected) {
    if (!(key in rec)) fail(`${path}.${key}`, "required key absent (absent is not false)");
  }
}

function str(rec: Record<string, unknown>, key: string, path: string): string {
  const v = rec[key];
  if (typeof v !== "string") fail(`${path}.${key}`, `expected string, got ${JSON.stringify(v)}`);
  return v;
}
function strOrNull(rec: Record<string, unknown>, key: string, path: string): string | null {
  const v = rec[key];
  if (v === null) return null;
  if (typeof v !== "string") fail(`${path}.${key}`, `expected string or null, got ${JSON.stringify(v)}`);
  return v;
}
function bool(rec: Record<string, unknown>, key: string, path: string): boolean {
  const v = rec[key];
  if (typeof v !== "boolean") fail(`${path}.${key}`, `expected boolean, got ${JSON.stringify(v)} (null and absent are not false)`);
  return v;
}
function int(rec: Record<string, unknown>, key: string, path: string): number {
  const v = rec[key];
  if (typeof v !== "number" || !Number.isInteger(v)) fail(`${path}.${key}`, `expected integer, got ${JSON.stringify(v)}`);
  return v;
}
function closed<T extends string>(rec: Record<string, unknown>, key: string, path: string, allowed: readonly T[]): T {
  const v = rec[key];
  if (typeof v !== "string" || !(allowed as readonly string[]).includes(v)) {
    fail(`${path}.${key}`, `expected one of ${JSON.stringify(allowed)}, got ${JSON.stringify(v)}`);
  }
  return v as T;
}
function closedOrNull<T extends string>(rec: Record<string, unknown>, key: string, path: string, allowed: readonly T[]): T | null {
  if (rec[key] === null) return null;
  return closed(rec, key, path, allowed);
}
function strings(rec: Record<string, unknown>, key: string, path: string): readonly string[] {
  const v = rec[key];
  if (!Array.isArray(v) || !v.every((x) => typeof x === "string")) fail(`${path}.${key}`, "expected an array of strings");
  return v as string[];
}
function span(rec: Record<string, unknown>, key: string, path: string): readonly [number, number] {
  const v = rec[key];
  if (!Array.isArray(v) || v.length !== 2 || !v.every((x) => typeof x === "number" && Number.isInteger(x))) {
    fail(`${path}.${key}`, "expected [start, end] integer span");
  }
  return [v[0] as number, v[1] as number];
}

const DELTA_KEYS = ["deltaId", "operation", "executionClass", "target", "sourceClause", "span", "currentState", "result", "reasonCode", "flags", "sessionProofCeiling"];

export function parseDeltaWire(value: unknown, path = "delta"): DeltaWire {
  const rec = record(value, path);
  exactKeys(rec, path, DELTA_KEYS);
  return {
    deltaId: str(rec, "deltaId", path),
    operation: strOrNull(rec, "operation", path),
    executionClass: closed(rec, "executionClass", path, EXECUTION_CLASSES),
    target: strOrNull(rec, "target", path),
    sourceClause: str(rec, "sourceClause", path),
    span: span(rec, "span", path),
    currentState: strOrNull(rec, "currentState", path),
    result: closed(rec, "result", path, DELTA_RESULTS),
    reasonCode: strOrNull(rec, "reasonCode", path),
    flags: strings(rec, "flags", path),
    sessionProofCeiling: closedOrNull(rec, "sessionProofCeiling", path, SESSION_PROOF_CEILINGS),
  };
}

const ACTION_KEYS = [
  "clauseIndex",
  "span",
  "clauseText",
  "modality",
  "negated",
  "requestedExecutor",
  "candidateOperation",
  "target",
  "possibleExternalEffect",
  "possibleSecretContent",
  "decisionSubstitutionRequested",
];

function parseAction(value: unknown, path: string): SemanticAction {
  const rec = record(value, path);
  exactKeys(rec, path, ACTION_KEYS);
  return {
    clauseIndex: int(rec, "clauseIndex", path),
    span: span(rec, "span", path),
    clauseText: str(rec, "clauseText", path),
    modality: closed(rec, "modality", path, MODALITIES),
    negated: bool(rec, "negated", path),
    requestedExecutor: closed(rec, "requestedExecutor", path, REQUESTED_EXECUTORS),
    candidateOperation: strOrNull(rec, "candidateOperation", path),
    target: strOrNull(rec, "target", path),
    possibleExternalEffect: bool(rec, "possibleExternalEffect", path),
    possibleSecretContent: bool(rec, "possibleSecretContent", path),
    decisionSubstitutionRequested: bool(rec, "decisionSubstitutionRequested", path),
  };
}

const SEMANTIC_KEYS = ["ruleSetVersion", "clauses", "actions", "unknownRelations", "relationsTouched", "declaredPurpose", "semanticPurpose", "purposeAlignment", "semanticDrift"];

function parseSemanticObservation(value: unknown, path: string): SemanticObservation {
  const rec = record(value, path);
  exactKeys(rec, path, SEMANTIC_KEYS);
  const actions = rec.actions;
  if (!Array.isArray(actions)) fail(`${path}.actions`, "expected an array");
  return {
    ruleSetVersion: str(rec, "ruleSetVersion", path),
    clauses: strings(rec, "clauses", path),
    actions: actions.map((a, i) => parseAction(a, `${path}.actions[${i}]`)),
    unknownRelations: strings(rec, "unknownRelations", path),
    relationsTouched: strings(rec, "relationsTouched", path),
    declaredPurpose: strOrNull(rec, "declaredPurpose", path),
    semanticPurpose: strOrNull(rec, "semanticPurpose", path),
    purposeAlignment: closedOrNull(rec, "purposeAlignment", path, PURPOSE_ALIGNMENTS),
    semanticDrift: bool(rec, "semanticDrift", path),
  };
}

const CHAIN_KEYS = ["firstBrokenRelation", "maximumLegitimateTransition", "nextValidTransition", "humanAuthorityRequired", "partial"];
const FBR_KEYS = ["predecessor", "broken"];
const HAR_KEYS = ["deltaId", "result", "reasonCode"];

export function parseChainWire(value: unknown, path = "chain"): ChainWire {
  const rec = record(value, path);
  exactKeys(rec, path, CHAIN_KEYS);
  let firstBrokenRelation: ChainWire["firstBrokenRelation"] = null;
  if (rec.firstBrokenRelation !== null) {
    const fbr = record(rec.firstBrokenRelation, `${path}.firstBrokenRelation`);
    exactKeys(fbr, `${path}.firstBrokenRelation`, FBR_KEYS);
    firstBrokenRelation = {
      predecessor: fbr.predecessor === null ? null : parseDeltaWire(fbr.predecessor, `${path}.firstBrokenRelation.predecessor`),
      broken: parseDeltaWire(fbr.broken, `${path}.firstBrokenRelation.broken`),
    };
  }
  const mlt = rec.maximumLegitimateTransition;
  if (!Array.isArray(mlt)) fail(`${path}.maximumLegitimateTransition`, "expected an array");
  const har = rec.humanAuthorityRequired;
  if (!Array.isArray(har)) fail(`${path}.humanAuthorityRequired`, "expected an array");
  return {
    firstBrokenRelation,
    maximumLegitimateTransition: mlt.map((d, i) => parseDeltaWire(d, `${path}.maximumLegitimateTransition[${i}]`)),
    nextValidTransition: rec.nextValidTransition === null ? null : parseDeltaWire(rec.nextValidTransition, `${path}.nextValidTransition`),
    humanAuthorityRequired: har.map((h, i) => {
      const p = `${path}.humanAuthorityRequired[${i}]`;
      const r = record(h, p);
      exactKeys(r, p, HAR_KEYS);
      return { deltaId: str(r, "deltaId", p), result: str(r, "result", p), reasonCode: strOrNull(r, "reasonCode", p) };
    }),
    partial: bool(rec, "partial", path),
  };
}

const CAPABILITY_KEYS = ["governanceAdmissible", "governanceAdmissibleReasons", "providerExecutable", "providerExecutableReasons", "canSend"];

export function parseCapability(value: unknown, path = "capability"): Capability {
  const rec = record(value, path);
  exactKeys(rec, path, CAPABILITY_KEYS);
  return {
    governanceAdmissible: bool(rec, "governanceAdmissible", path),
    governanceAdmissibleReasons: strings(rec, "governanceAdmissibleReasons", path),
    providerExecutable: bool(rec, "providerExecutable", path),
    providerExecutableReasons: strings(rec, "providerExecutableReasons", path),
    canSend: bool(rec, "canSend", path),
  };
}

const CURRENT_KEYS = ["kind", "contract", "basis", "semanticObservation", "deltas", "chain", "capability", "composedProofCeiling"];
const BASIS_KEYS = ["rawIntentDigestSha256", "derivationTime"];

/** Fail-closed parser of `governanceObservation`. Throws `MalformedProjection`; never returns a partial object. */
export function parseGovernanceObservation(value: unknown, path = "governanceObservation"): GovernanceObservation {
  const rec = record(value, path);
  if (rec.kind === "unavailable") {
    exactKeys(rec, path, ["kind", "reasonCode"]);
    return { kind: "unavailable", reasonCode: closed(rec, "reasonCode", path, UNAVAILABLE_REASONS) };
  }
  if (rec.kind !== "current") fail(`${path}.kind`, `unknown observation kind ${JSON.stringify(rec.kind)} (only "current" and "unavailable" exist)`);
  exactKeys(rec, path, CURRENT_KEYS);
  if (rec.contract !== PCPG_CONTRACT) fail(`${path}.contract`, `unknown contract identity ${JSON.stringify(rec.contract)}; only ${PCPG_CONTRACT} is accepted`);
  const basis = record(rec.basis, `${path}.basis`);
  exactKeys(basis, `${path}.basis`, BASIS_KEYS);
  const deltas = rec.deltas;
  if (!Array.isArray(deltas)) fail(`${path}.deltas`, "expected an array");
  return {
    kind: "current",
    contract: PCPG_CONTRACT,
    basis: { rawIntentDigestSha256: str(basis, "rawIntentDigestSha256", `${path}.basis`), derivationTime: str(basis, "derivationTime", `${path}.basis`) },
    semanticObservation: parseSemanticObservation(rec.semanticObservation, `${path}.semanticObservation`),
    deltas: deltas.map((d, i) => parseDeltaWire(d, `${path}.deltas[${i}]`)),
    chain: parseChainWire(rec.chain, `${path}.chain`),
    capability: parseCapability(rec.capability, `${path}.capability`),
    composedProofCeiling: closedOrNull(rec, "composedProofCeiling", path, SESSION_PROOF_CEILINGS),
  };
}

const FAILURE_KINDS = ["denied", "rejected", "not_found", "indeterminate", "failed_precommit", "blocked", "stale"] as const;

/** The whole response body → typed result. Never throws: every failure is a typed, closed outcome. */
export function parsePromptObservation(body: unknown): PromptObservationResult {
  if (!isRecord(body)) return { kind: "indeterminate", reasonCode: "UNRECOGNIZED_SERVER_RESPONSE" };
  if (body.kind !== "ok") {
    const kind = body.kind;
    if (typeof kind === "string" && (FAILURE_KINDS as readonly string[]).includes(kind)) {
      return { kind: kind as Failure["kind"], reasonCode: typeof body.reasonCode === "string" ? body.reasonCode : kind.toUpperCase() };
    }
    return { kind: "indeterminate", reasonCode: "UNRECOGNIZED_SERVER_RESPONSE" };
  }
  try {
    const p = "response";
    if (body.field !== "PRE_CALL_PROMPT_GOVERNANCE") fail(`${p}.field`, `expected PRE_CALL_PROMPT_GOVERNANCE, got ${JSON.stringify(body.field)}`);
    const ws = record(body.workspace, `${p}.workspace`);
    let session: PromptObservation["session"] = null;
    if (body.session !== null) {
      const s = record(body.session, `${p}.session`);
      session = { sessionId: str(s, "sessionId", `${p}.session`) };
    }
    return {
      kind: "ok",
      data: {
        field: "PRE_CALL_PROMPT_GOVERNANCE",
        workspace: { workspaceId: str(ws, "workspaceId", `${p}.workspace`), name: str(ws, "name", `${p}.workspace`) },
        session,
        rawIntent: str(body, "rawIntent", p),
        rawIntentLength: int(body, "rawIntentLength", p),
        rawIntentDigestSha256: str(body, "rawIntentDigestSha256", p),
        declaredPurpose: strOrNull(body, "declaredPurpose", p),
        observedAt: str(body, "observedAt", p),
        governanceObservation: parseGovernanceObservation(body.governanceObservation),
      },
    };
  } catch (error) {
    if (error instanceof MalformedProjection) return { kind: "malformed", reasonCode: "MALFORMED_PROJECTION", detail: error.message };
    throw error;
  }
}

export interface PromptObservationInput {
  readonly rawIntent: string;
  readonly sessionId?: string;
  readonly declaredPurpose?: string;
}

/**
 * `POST /workspaces/{workspaceId}/prompt-observations` — a query (no Idempotency-Key). The body carries exactly the
 * three contract inputs; no capability, observation or basis ever travels client → server (B-10).
 */
export async function submitPromptObservation(
  workspaceId: string,
  input: PromptObservationInput,
  fetchImpl: typeof fetch = fetch,
): Promise<PromptObservationResult> {
  const body: Record<string, string> = { rawIntent: input.rawIntent };
  if (input.sessionId !== undefined) body.sessionId = input.sessionId;
  if (input.declaredPurpose !== undefined) body.declaredPurpose = input.declaredPurpose;
  let response: Response;
  try {
    response = await fetchImpl(`${apiBaseUrl()}/workspaces/${encodeURIComponent(workspaceId)}/prompt-observations`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      credentials: "include",
      body: JSON.stringify(body),
    });
  } catch {
    return { kind: "network_failure", reasonCode: "NETWORK_FAILURE" };
  }
  let json: unknown;
  try {
    json = await response.json();
  } catch {
    return { kind: "indeterminate", reasonCode: "UNRECOGNIZED_SERVER_RESPONSE" };
  }
  return parsePromptObservation(json);
}
