/**
 * The Decision-command extension of the typed API client (14 §46
 * PKG-29's own PUBLIC_INTERFACES: "Decision UI contract").
 *
 * SCOPE: ONLY `RecordHumanDecision` (TRN-DEC-002, `CMD_RECORD_HUMAN_DECISION`,
 * `POST /decisions/{d}/decide`) IS EXPOSED AS AN INTERACTIVE UI ACTION
 * --------------------------------------------------------------------
 * `application.human_decision_handler` (PKG-15) implements BOTH
 * `open_decision_consideration` (TRN-DEC-001) and `record_human_decision`
 * (TRN-DEC-002) -- both are real, already-governed backend commands.
 * This package's own 12 §24 item 12 names exactly one UI surface,
 * literally: "human Decision action for authorized holder" -- read as
 * TRN-DEC-002 specifically (the human's own act of DECIDING), not a
 * second "author a Decision's own question/options/criteria" form
 * TRN-DEC-001 would require. `[IMPLEMENTATION CHOICE]`, disclosed: a
 * Decision already `UNDER_CONSIDERATION` is treated as an existing
 * precondition of this page, the identical treatment PKG-28 already
 * gave Session/Challenge/Burst (real backend objects this UI reads,
 * never creates). 12 §24 item 10 ("Question selection control") is
 * separately out of scope -- PKG-14 (QuestionSelection) is not named
 * in this package's own REQUIRED PREDECESSORS (`PKG-15,PKG-19,PKG-28`),
 * and FILES_ALLOWED_TO_CREATE names only "Decision components/routes",
 * never Question-selection components. See this package's own
 * completion report KNOWN_LIMITATIONS for the full disclosure.
 *
 * WHY THIS FILE REUSES `client.ts`'s OWN `isRecord`/`requireString`/
 * `requireEnum` RATHER THAN A NEW SHARED "utils" FILE
 * --------------------------------------------------------------------
 * This package's own FILES_FORBIDDEN_TO_MODIFY line explicitly forbids
 * "broad generic utils/helpers/services/common dumping grounds" -- a
 * new `lib/api/parsing.ts` would be exactly that (a file whose entire
 * purpose is "shared generic helpers", named nothing more specific).
 * Exporting the three functions `client.ts` (PKG-28's own file, which
 * PKG-29 is authorized to modify as an "existing file directly
 * required by PKG-29") already defines is the smaller, more specific
 * change.
 */

import { apiBaseUrl, isRecord, parseDecisionView, requireEnum, requireString } from "./client";
import { BOUNDARY_DENIAL_RESULTS, type DecisionActionResult, type DecisionId } from "./types";

/**
 * `POST /decisions/{d}/decide` (12 §23's own COMMAND row). Mirrors
 * `fetchSessionView`'s own shape exactly: a real `fetch` against a
 * disclosed prototype interface choice (no real backend route exists
 * yet, see `client.ts`'s own header docstring), an injectable
 * `fetchImpl` for testing, and a fail-closed parse of whatever the
 * server actually returns -- never a client-computed guess about
 * whether the action succeeded.
 *
 * `decisionId` is the only identifier this function accepts; there is
 * no code path here that could compute or infer `DECISION_RIGHT`,
 * `BND-006`'s human-origin proof, or any other authority fact --
 * exactly this package's own AUTHORITY line ("UI never calculates
 * DECISION_RIGHT"). The single source of truth for whether this
 * action was allowed is the server's own response, parsed below.
 *
 * IDENTITY (local-login field): identical `credentials: "include"`
 * cookie treatment as `client.ts::fetchSessionView`'s own -- see that
 * function's own docstring for the full disclosure. No actor header is
 * sent.
 */
export async function recordHumanDecision(
  decisionId: DecisionId,
  selectedOption: string,
  rationale: string | null,
  confidence: string | null,
  fetchImpl: typeof fetch = fetch,
): Promise<DecisionActionResult> {
  const response = await fetchImpl(`${apiBaseUrl()}/decisions/${encodeURIComponent(decisionId)}/decide`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    credentials: "include",
    body: JSON.stringify({ selectedOption, rationale, confidence }),
  });
  const body: unknown = await response.json();
  return parseDecisionActionResult(body);
}

/**
 * Fails closed (this package's own NON_COLLAPSE_RULES: "Unknown
 * consequential semantic input fails closed") on any body shape that
 * does not match one of the four known cases -- never silently
 * defaults to `committed`. Exported separately, mirroring
 * `parseSessionReadResult`'s own precedent, so this fail-closed
 * behavior is directly unit-testable against constructed JSON bodies.
 */
export function parseDecisionActionResult(body: unknown): DecisionActionResult {
  if (!isRecord(body) || typeof body.kind !== "string") {
    throw new TypeError("DecisionActionResult response body is missing a recognizable 'kind'");
  }
  switch (body.kind) {
    case "committed":
      return { kind: "committed", decision: parseDecisionView(body.decision) };
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
      throw new TypeError(`unrecognized DecisionActionResult kind ${JSON.stringify(body.kind)}`);
  }
}

function requireNonEmptyString(record: Record<string, unknown>, key: string): string {
  const value = requireString(record, key);
  if (value.length === 0) {
    throw new TypeError(`expected non-empty string field '${key}'`);
  }
  return value;
}
