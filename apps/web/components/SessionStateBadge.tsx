/** 12 §24 item 3: "current Session state" -- verbatim rendering of
 * `packages/domain/session.py`'s own `SessionState` value, never a
 * relabeled/simplified subset. */
import type { SessionState } from "../lib/api/types";

export function SessionStateBadge({ state }: { readonly state: SessionState }) {
  return <span data-testid="session-state-badge">Session state: {state}</span>;
}
