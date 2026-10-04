/**
 * AUTH/CYAN-ACCOUNT-01: the three account effects as keyless Settlements for `useEffectField` (the page's one effect
 * field; one effect in flight at a time, canonical re-read afterwards):
 *
 *   removeMethod(methodId)  → POST /auth/methods/{id}/unlink   committed { currentSessionEnded } · denied LAST_METHOD /
 *                                                              UNLINK_DENIED / NO_SESSION · rejected MALFORMED_METHOD_ID
 *   endSession(sessionId)   → POST /auth/sessions/{id}/revoke  committed {} · denied SESSION_NOT_FOUND / NO_SESSION
 *   signOutEverywhere()     → POST /auth/logout-all            committed { revokedSessions }
 *
 * A lost response is an UNKNOWN consequence (network_failure), an unrecognized one is indeterminate — never success,
 * never "nothing happened" (Network Failure != Proof Of No Effect). The server's reason codes pass through verbatim.
 */
import { logoutAll, revokeSession, unlinkMethod } from "../api/authClient";
import type { Settlement } from "./useEffectField";

type Outcome<T> = { readonly kind: "ok" } & T;
type Result<T> = Outcome<T> | { readonly kind: "denied" | "rejected"; readonly reasonCode: string };

/** Tells transport loss apart from an unrecognized response, as the founding effect of the Workspaces field does. */
async function settle<T extends object>(send: (fetchImpl: typeof fetch) => Promise<Result<T>>): Promise<Settlement<T>> {
  let reached = true;
  const tracked: typeof fetch = (input, init) =>
    fetch(input, init).catch((error: unknown) => {
      reached = false;
      throw error;
    });
  try {
    const result = await send(tracked);
    if (result.kind === "ok") {
      const body: Record<string, unknown> = { ...result };
      delete body.kind;
      return { kind: "committed", reasonCode: null, body: body as T };
    }
    return { kind: result.kind, reasonCode: result.reasonCode };
  } catch {
    return reached ? { kind: "indeterminate", reasonCode: "UNRECOGNIZED_SERVER_RESPONSE" } : { kind: "network_failure", reasonCode: "NETWORK_FAILURE" };
  }
}

export type RemovedMethod = { readonly methodId: string; readonly sessionsRevoked: number; readonly currentSessionEnded: boolean };
export function removeMethod(methodId: string): Promise<Settlement<RemovedMethod>> {
  return settle<RemovedMethod>((f) => unlinkMethod(methodId, f));
}

export type EndedSession = Record<never, never>;
export function endSession(sessionId: string): Promise<Settlement<EndedSession>> {
  return settle<EndedSession>((f) => revokeSession(sessionId, f));
}

export type SignedOutEverywhere = { readonly revokedSessions: number };
export function signOutEverywhere(): Promise<Settlement<SignedOutEverywhere>> {
  return settle<SignedOutEverywhere>((f) => logoutAll(f));
}

/** Relation names of the page's effect field (one prefix, so one outcome surface owns all three). */
export const ACCOUNT_RELATION_PREFIX = "account-security:";
export const removeRelation = (methodId: string) => `${ACCOUNT_RELATION_PREFIX}remove:${methodId}`;
export const endRelation = (sessionId: string) => `${ACCOUNT_RELATION_PREFIX}end:${sessionId}`;
export const SIGN_OUT_EVERYWHERE_RELATION = `${ACCOUNT_RELATION_PREFIX}sign-out-everywhere`;
