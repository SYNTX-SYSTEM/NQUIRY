"use client";
/**
 * CYAN-PCPG-05: the context chamber in which the actor observes a drafted intent for this Session (Architecture 27
 * v4 §01, §04.1, §14, §22). Title "Your intent", eyebrow "observed, never sent", one control labelled "Observe".
 *
 * OBSERVE ≠ EXECUTE, OBSERVE ≠ SEND, RAW INTENT ≠ AUTHORITY. The chamber is not gated by role, viewer flags, Session
 * control, bindings or participation: observation is a read-scope operation of every authenticated Workspace member
 * who may read the Session, and the server's denial stays authoritative. The raw text is the actor's own, shown only
 * here, never logged. The chamber renders the observation's own facts (observed at, digest) and the legitimate failure
 * presentation; the governance words belong to the membrane.
 */
import { type FormEvent, useState } from "react";
import type { ObservationState } from "../../lib/field/observation";
import type { ObservationPresence } from "../../lib/field/pcpgPresentation";
import { ChamberHead } from "./chambers";
import { Plane } from "./topology/FieldStage";

export const RAW_INTENT_MAX_CHARS = 8000;
export const DECLARED_PURPOSE_MAX_CHARS = 2000;

const FAILURE_WORDS: Readonly<Record<string, string>> = {
  rejected: "Not observed. The request was invalid; nothing was read.",
  denied: "Not observed. The server denied the observation.",
  not_found: "Not observed. The Session was not found in this Workspace.",
  network_failure: "The server could not be reached. Nothing is assumed to have changed.",
  indeterminate: "Outcome unknown. Nothing is assumed; observe again if you wish.",
  malformed: "The governance projection could not be read. Governance is unavailable (fail closed).",
};

const WHEN = new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" });

export function IntentObservationChamber({
  state,
  presence,
  onObserve,
}: {
  readonly state: ObservationState;
  /** The presence the membrane consumes (with supersession), so the chamber says the same thing. */
  readonly presence: ObservationPresence;
  readonly onObserve: (rawIntent: string, declaredPurpose: string | undefined) => void;
}) {
  const [text, setText] = useState("");
  const [purpose, setPurpose] = useState("");
  const busy = state.phase === "observing";
  const superseded = presence.kind === "observation" && presence.supersededByObjectChange;
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy || text.trim().length === 0) return;
    onObserve(text, purpose.trim().length > 0 ? purpose : undefined);
  }
  return (
    <Plane kind="context" semantic="context" labelledBy="intent-title" testId="intent-chamber">
      <ChamberHead id="intent-title" semantic="context" title="Your intent" marker="observed, never sent" />
      <p className="chamber-lede">
        Draft what you intend for this Session and observe how it relates to the current Field. Observing executes nothing, sends nothing and grants
        nothing; the observation exists for this view only.
      </p>
      <form onSubmit={submit} className="stack intent-form" data-testid="intent-form" data-observation-phase={state.phase}>
        <div className="field">
          <label htmlFor="intent-text">Your intent</label>
          <textarea
            id="intent-text"
            value={text}
            maxLength={RAW_INTENT_MAX_CHARS}
            rows={3}
            disabled={busy}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(event) => {
              if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
                event.preventDefault();
                event.currentTarget.form?.requestSubmit();
              }
            }}
            data-testid="intent-text"
          />
        </div>
        <div className="field">
          <label htmlFor="intent-purpose">Declared purpose (optional)</label>
          <input id="intent-purpose" type="text" value={purpose} maxLength={DECLARED_PURPOSE_MAX_CHARS} disabled={busy} onChange={(e) => setPurpose(e.target.value)} data-testid="intent-purpose" />
        </div>
        <div className="actions-row">
          <button className="button secondary" type="submit" disabled={busy || text.trim().length === 0} data-testid="observe-button">
            Observe
          </button>
        </div>
      </form>
      {busy ? (
        <p className="effect-intent t-system" role="status" data-testid="observe-pending">
          Observing… the Field is read; nothing is executed.
        </p>
      ) : null}
      {state.failure ? (
        <p className="read-boundary" data-outcome={state.failure.kind} data-testid="observe-failure">
          <span>{FAILURE_WORDS[state.failure.kind] ?? "Not observed."}</span>{" "}
          <span className="mono" data-testid="observe-failure-code">
            {state.failure.reasonCode}
          </span>
        </p>
      ) : null}
      {state.envelope ? (
        <dl className="provenance" data-testid="observation-facts">
          <dt>Observed</dt>
          <dd>
            <span data-testid="observed-at">{WHEN.format(new Date(state.envelope.observedAt))}</span>{" "}
            <span className="muted">· for this view only; a reload returns to “No observation”.</span>
          </dd>
          <dt>Digest</dt>
          <dd className="mono" data-testid="observed-digest">
            {state.envelope.rawIntentDigestSha256.slice(0, 12)}…
          </dd>
          {superseded ? (
            <>
              <dt>Superseded</dt>
              <dd data-testid="observe-superseded">The Session changed after this observation. Observe again for the current Field.</dd>
            </>
          ) : null}
        </dl>
      ) : null}
    </Plane>
  );
}
