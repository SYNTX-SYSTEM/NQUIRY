"use client";
/**
 * The protected Burst working surface (F03), re-homed on the SF-02 effect
 * lifecycle (22 §25, §26, §30).
 *
 * PROJECTION AND CONTROL SURFACE, NEVER AUTHORITY (20 §13):
 * - the capture form exists only when the SERVER offers `CAPTURE_QUESTION`; an
 *   unavailable capture shows the server's own reason and no control;
 * - the completion control exists only when the server offers `COMPLETE_BURST`;
 * - what is listed comes from the server's visibility filter (HD-13): the
 *   viewer's own questions while the Burst is ACTIVE, a count for the
 *   controller, the full frozen set afterwards;
 * - origin and author are never sent; the text is sent byte-exact.
 *
 * Effect law: every submission runs through the page's ONE effect lifecycle
 * (request → server verdict → canonical re-read → reconstruction). The capture
 * relation is keyed by the exact text (`session:capture:<hash>`), so a retry
 * after an UNKNOWN outcome (network loss or server INDETERMINATE) reuses the
 * same Idempotency-Key while changed text is a new intent; the server rejects a
 * reused key with a different payload. AI is absent from this surface. Time
 * passing changes nothing here (HD-11).
 */
import { useState } from "react";
import { captureBurstQuestion, completeBurst, type SessionPosition } from "../../lib/api/inquiryClient";
import { explainCaptureRejection, textFingerprint } from "../../lib/burst";
import { settleCommand, type useEffectField } from "../../lib/field/useEffectField";
import { Unavailable } from "../f02/Unavailable";
import { BoundaryMark, ChamberHead } from "../field/chambers";
import { BurstTimer } from "./BurstTimer";
import { FrozenQuestionSet } from "./FrozenQuestionSet";
import { OwnQuestions } from "./OwnQuestions";

export const CAPTURE_RELATION_PREFIX = "session:capture:";
export const COMPLETE_RELATION = "session:complete-burst";

type Props = {
  readonly workspaceId: string;
  readonly sessionId: string;
  readonly position: SessionPosition;
  readonly effect: ReturnType<typeof useEffectField>;
  readonly reload: () => Promise<boolean>;
};

export function BurstCapturePanel({ workspaceId, sessionId, position, effect, reload }: Props) {
  const [text, setText] = useState("");
  const [confirming, setConfirming] = useState(false);

  const burst = position.burst;
  if (burst === null) return null;
  const set = position.questionSet;
  const capture = position.actions.CAPTURE_QUESTION;
  const complete = position.actions.COMPLETE_BURST;
  const busy = effect.blocked;

  function submit() {
    if (busy || burst === null || text.length === 0) return;
    const submitted = text;
    void effect.run({
      relation: `${CAPTURE_RELATION_PREFIX}${textFingerprint(submitted)}`,
      keyed: true,
      send: async (intentKey) => {
        const result = await captureBurstQuestion(workspaceId, sessionId, submitted, burst.version, intentKey);
        const settled = settleCommand(result);
        if (settled.kind === "committed") return { ...settled, detail: "Your question was captured exactly as you typed it." };
        if (settled.kind === "rejected") return { ...settled, detail: explainCaptureRejection(settled.reasonCode) };
        if (settled.kind === "blocked") return { ...settled, detail: "The Burst no longer accepts questions. Your text was not stored." };
        if (settled.kind === "network_failure" || settled.kind === "indeterminate") {
          return { ...settled, detail: "Submitting the same text again retries the same submission; it cannot create a duplicate." };
        }
        return settled;
      },
      reconstruct: reload,
      onCommitted: () => {
        setText("");
        return false;
      },
    });
  }

  function confirmComplete() {
    if (busy || burst === null) return;
    void effect.run({
      relation: COMPLETE_RELATION,
      keyed: true,
      send: async (intentKey) => {
        const settled = settleCommand(await completeBurst(workspaceId, sessionId, position.session.version, burst.version, intentKey));
        return settled.kind === "committed" ? { ...settled, detail: "The Burst is completed and the human question set is frozen." } : settled;
      },
      reconstruct: reload,
      onCommitted: () => {
        setConfirming(false);
        return false;
      },
    });
  }

  return (
    <div className="stack" data-testid="burst-capture-panel" data-burst-state={burst.state}>
      {burst.state === "ACTIVE" && burst.startedAt ? (
        <BurstTimer startedAt={burst.startedAt} serverNow={position.serverNow} guidanceSeconds={burst.guidanceSeconds} />
      ) : null}

      {burst.state === "ACTIVE" ? (
        <>
          {capture.available ? (
            <form
              className="stack question-surface"
              data-human-only={burst.mode === "HUMAN_ONLY" ? "true" : undefined}
              data-testid="capture-form"
              onSubmit={(event) => {
                event.preventDefault();
                submit();
              }}
            >
              <p className="question-seal" aria-hidden="true">
                <span className="tag human">human</span> <span>{burst.mode}</span> <span>· AI absent while the Burst is open</span>
              </p>
              <div className="field">
                <label htmlFor="capture-text">Your question</label>
                <textarea
                  id="capture-text"
                  name="capture-text"
                  rows={3}
                  value={text}
                  aria-describedby="capture-hint"
                  onChange={(event) => setText(event.target.value)}
                  onKeyDown={(event) => {
                    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
                      event.preventDefault();
                      submit();
                    }
                  }}
                />
                <p id="capture-hint" className="muted">
                  Questions only, ending with a question mark. It is stored exactly as you type it. Press Ctrl+Enter to
                  submit; Enter adds a new line.
                </p>
              </div>
              <div className="actions-row">
                <button className="button" type="submit" disabled={busy || text.length === 0} data-testid="capture-submit">
                  Submit question
                </button>
              </div>
            </form>
          ) : capture.relevant ? (
            <Unavailable capability={capture} testId="action-reason-CAPTURE_QUESTION" />
          ) : null}

          {set.visibility === "OWN_ONLY_WHILE_ACTIVE" && capture.available ? (
            <section aria-labelledby="own-questions-title">
              <h3 id="own-questions-title">Your questions</h3>
              <p className="muted">
                Only you can see these while the Burst is open. Everyone sees the full set after it is completed.
              </p>
              <OwnQuestions questions={set.mine} />
            </section>
          ) : null}

          {set.capturedCount !== null ? (
            <p data-testid="captured-count">
              Questions submitted so far: <strong>{set.capturedCount}</strong>{" "}
              <span className="muted">The texts stay hidden until the Burst is completed.</span>
            </p>
          ) : null}

          {complete.relevant ? (
            complete.available ? (
              confirming ? (
                <div role="group" aria-labelledby="confirm-title" className="confirmation-chamber" data-boundary="IRREVERSIBLE_CONFIRMATION" data-testid="complete-confirm">
                  <ChamberHead id="confirm-title" level={3} semantic="confirmation" title="Close the Burst?" marker="irreversible" />
                  <BoundaryMark boundary="IRREVERSIBLE_CONFIRMATION">
                    This freezes {set.capturedCount ?? "the"} submitted question(s) as the human question set. No question can be added
                    afterwards. This cannot be undone.
                  </BoundaryMark>
                  <ul className="confirmation-facts">
                    <li>
                      <span className="fact-label">becomes immutable</span> the human question set ({set.capturedCount ?? "all submitted"} question(s))
                    </li>
                    <li>
                      <span className="fact-label">cannot happen afterwards</span> adding, removing or rewriting a question
                    </li>
                    <li>
                      <span className="fact-label">stays possible</span> keeping the Burst open (cancel below)
                    </li>
                  </ul>
                  <div className="actions-row">
                    <button className="button" type="button" disabled={busy} onClick={confirmComplete} data-testid="complete-confirm-button">
                      Freeze the set and complete the Burst
                    </button>
                    <button className="button secondary" type="button" disabled={busy} onClick={() => setConfirming(false)}>
                      Keep the Burst open
                    </button>
                  </div>
                </div>
              ) : (
                <div className="actions-row">
                  <button className="button secondary" type="button" disabled={busy} onClick={() => setConfirming(true)} data-testid="complete-button">
                    Complete Burst…
                  </button>
                </div>
              )
            ) : (
              <Unavailable capability={complete} testId="action-reason-COMPLETE_BURST" />
            )
          ) : null}
        </>
      ) : null}

      {burst.state === "COMPLETED" && set.frozen !== null ? (
        <section aria-labelledby="frozen-title" className="frozen-artifact" data-immutable="true">
          <ChamberHead id="frozen-title" level={3} semantic="frozen" title="Frozen human question set" marker="immutable" />
          <FrozenQuestionSet frozen={set.frozen} />
        </section>
      ) : null}
    </div>
  );
}
