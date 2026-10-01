/**
 * CYAN-PCPG-04: the Session object membrane (Architecture 27 v4 §03 Level 0, §07.1, §07.4, §15, §17).
 *
 * MEMBRANE = presentation of already-crossed governance truth. It consumes ONLY `presentationOf(observation)`
 * (CYAN-PCPG-02): it never parses PCPG-R12/1, never re-derives governance, never reads roles, auth or backend
 * internals, and renders no control — PCPG-R12/1 has no SEND relation, so there is nothing to offer. The label and its
 * precedence are the derivation's own (§06.1); the membrane only chooses prominence (§07.4), a presentation property
 * keyed by that label, and says the capability facts in words for assistive technology (§17).
 */
import type { MembraneLabel, ObservationPresentation } from "../../lib/field/pcpgPresentation";

export type MembraneProminence = "quiet" | "visible" | "prominent" | "explicit";

/** v4 §07.4: prominence from the derived label only. Presentation, never a new governance value. */
export const PROMINENCE: Readonly<Record<MembraneLabel, MembraneProminence>> = {
  NO_OBSERVATION: "quiet",
  OBSERVED: "quiet",
  PARTIAL: "visible",
  GOVERNANCE_UNAVAILABLE: "visible",
  SUPERSEDED: "visible",
  BOUNDARY_REACHED: "prominent",
  HUMAN_AUTHORITY_REQUIRED: "prominent",
  PROVIDER_NOT_EXECUTABLE: "explicit",
};

const WHEN = new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" });

export function GovernanceMembrane({ presentation }: { readonly presentation: ObservationPresentation }) {
  const label = presentation.label;
  const words = presentation.words;
  const humanAuthority = presentation.label === "HUMAN_AUTHORITY_REQUIRED";
  const prominence = PROMINENCE[label];
  const current = presentation.aggregates.current;
  const observedAt = presentation.basis ? WHEN.format(new Date(presentation.basis.derivationTime)) : null;
  // §17: the crossed capability facts in words; a projection, never an affordance
  const detail = current
    ? [
        `Governance admissible: ${current.capability.governanceAdmissible ? "true" : "false"}${current.capability.governanceAdmissibleReasons.length > 0 ? ` (${current.capability.governanceAdmissibleReasons.join(", ")})` : ""}.`,
        `Provider executable: ${current.capability.providerExecutable ? "true" : "false"}${current.capability.providerExecutableReasons.length > 0 ? ` (${current.capability.providerExecutableReasons.join(", ")})` : ""}.`,
        current.capability.canSend === null ? "Can send: absent (observation superseded)." : `Can send: ${current.capability.canSend ? "true" : "false"} (projection only).`,
        presentation.send ? `${presentation.send.text}.` : null,
      ].filter((s): s is string => s !== null)
    : [];
  return (
    <section
      className="governance-membrane"
      role="status"
      aria-live="polite"
      data-testid="governance-membrane"
      data-membrane-label={label}
      data-prominence={prominence}
      data-observation={presentation.aggregates.observation}
      data-human-authority={humanAuthority ? "required" : undefined}
    >
      <span className="visually-hidden">Governance for this session: </span>
      <span className="membrane-field" aria-hidden="true">
        Field
      </span>
      <span className="membrane-words" data-testid="membrane-words">
        {words}
      </span>
      {observedAt ? (
        <span className="membrane-time muted" data-testid="membrane-observed-at">
          observed at {observedAt}
        </span>
      ) : null}
      {detail.length > 0 ? <span className="visually-hidden">{detail.join(" ")}</span> : null}
      {/* no control: PCPG-R12/1 has no SEND relation */}
    </section>
  );
}
