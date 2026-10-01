"use client";
/**
 * CYAN-PCPG-05: React binding of the observation state machine (`observation.ts`). React state only — no
 * persistence of any kind (I-18, HA-PCPG-3); a reload returns to "No observation". The request body is exactly what
 * `submitPromptObservation` sends (rawIntent, sessionId, declaredPurpose?): no capability, authority, result, basis,
 * provider eligibility, send gate or proof ceiling ever leaves the client.
 */
import { useCallback, useReducer } from "react";
import { submitPromptObservation, type PromptObservationResult } from "../api/pcpgClient";
import { INITIAL_OBSERVATION, observationReducer, runObservation, type ObjectVersions, type ObservationState } from "./observation";

export function useObservation(workspaceId: string, sessionId: string): {
  readonly state: ObservationState;
  readonly observe: (rawIntent: string, declaredPurpose: string | undefined, versions: ObjectVersions) => Promise<PromptObservationResult>;
} {
  const [state, dispatch] = useReducer(observationReducer, INITIAL_OBSERVATION);
  const observe = useCallback(
    (rawIntent: string, declaredPurpose: string | undefined, versions: ObjectVersions) =>
      // no persistence: React state only (I-18, HA-PCPG-3)
      runObservation(dispatch, () => submitPromptObservation(workspaceId, { rawIntent, sessionId, ...(declaredPurpose ? { declaredPurpose } : {}) }), versions),
    [workspaceId, sessionId],
  );
  return { state, observe };
}
