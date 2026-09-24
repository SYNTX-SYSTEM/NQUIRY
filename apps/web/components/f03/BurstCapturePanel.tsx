"use client";
/**
 * The protected Burst working surface (F03).
 *
 * PROJECTION AND CONTROL SURFACE, NEVER AUTHORITY (20 §13):
 * - the capture form exists only when the SERVER offers `CAPTURE_QUESTION`; an
 *   unavailable capture shows the server's own reason and no control;
 * - the completion control exists only when the server offers `COMPLETE_BURST`;
 * - what is listed comes from the server's visibility filter (HD-13): the
 *   viewer's own questions while the Burst is ACTIVE, a count for the
 *   controller, the full frozen set afterwards;
 * - origin and author are never sent; the text is sent byte-exact;
 * - one Idempotency-Key per logical capture; UI debounce is not idempotency.
 *
 * AI is absent from this surface. Time passing changes nothing here.
 */
import { useRef, useState } from "react";
import {
  captureBurstQuestion,
  completeBurst,
  newIntentKey,
  type SessionPosition,
} from "../../lib/api/inquiryClient";
import { explainCaptureRejection, intentKeyFor, type Intent } from "../../lib/burst";
import type { ShownOutcome } from "../f02/Outcome";
import { Unavailable } from "../f02/Unavailable";
import { BurstTimer } from "./BurstTimer";
import { FrozenQuestionSet } from "./FrozenQuestionSet";
import { OwnQuestions } from "./OwnQuestions";

type Props = {
  readonly workspaceId: string;
  readonly sessionId: string;
  readonly position: SessionPosition;
  readonly onPosition: (position: SessionPosition) => void;
  readonly onOutcome: (outcome: ShownOutcome) => void;
  readonly reload: () => Promise<void>;
};

export function BurstCapturePanel({ workspaceId, sessionId, position, onPosition, onOutcome, reload }: Props) {
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const captureIntent = useRef<Intent | null>(null);
  const completeIntent = useRef<string | null>(null);

  const burst = position.burst;
  if (burst === null) return null;
  const set = position.questionSet;
  const capture = position.actions.CAPTURE_QUESTION;
  const complete = position.actions.COMPLETE_BURST;

  function submit() {
    if (busy || burst === null || text.length === 0) return;
    setBusy(true);
    captureIntent.current = intentKeyFor(captureIntent.current, text, newIntentKey);
    const intent = captureIntent.current;
    void captureBurstQuestion(workspaceId, sessionId, text, burst.version, intent.key).then((result) => {
      setBusy(false);
      if (result.kind === "committed") {
        captureIntent.current = null;
        setText("");
        onPosition(result.body.position);
        onOutcome({ kind: "committed", detail: "Your question was captured exactly as you typed it." });
        return;
      }
      if (result.kind === "network_failure") {
        // Keep the intent: submitting again retries the SAME submission.
        onOutcome({ ...result, detail: "Submitting again retries the same submission; it cannot create a duplicate." });
        return;
      }
      captureIntent.current = null;
      onOutcome(
        result.kind === "rejected"
          ? { ...result, detail: explainCaptureRejection(result.reasonCode) }
          : result.kind === "blocked"
            ? { ...result, detail: "The Burst no longer accepts questions. Your text was not stored." }
            : result,
      );
      if (result.kind !== "rejected") void reload();
    });
  }

  function confirmComplete() {
    if (busy || burst === null) return;
    setBusy(true);
    completeIntent.current = completeIntent.current ?? newIntentKey();
    void completeBurst(workspaceId, sessionId, position.session.version, burst.version, completeIntent.current).then(
      (result) => {
        setBusy(false);
        if (result.kind !== "network_failure") completeIntent.current = null;
        if (result.kind === "committed") {
          setConfirming(false);
          onPosition(result.body.position);
          onOutcome({ kind: "committed", detail: "The Burst is completed and the human question set is frozen." });
          return;
        }
        onOutcome(result);
        if (result.kind !== "network_failure") void reload();
      },
    );
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
              className="stack"
              data-testid="capture-form"
              onSubmit={(event) => {
                event.preventDefault();
                submit();
              }}
            >
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
                <div role="group" aria-labelledby="confirm-title" className="panel" data-testid="complete-confirm">
                  <h3 id="confirm-title">Close the Burst?</h3>
                  <p>
                    This freezes {set.capturedCount ?? "the"} submitted question(s) as the human question set. No
                    question can be added afterwards. This cannot be undone.
                  </p>
                  <div className="actions-row">
                    <button
                      className="button"
                      type="button"
                      disabled={busy}
                      onClick={confirmComplete}
                      data-testid="complete-confirm-button"
                    >
                      Freeze the set and complete the Burst
                    </button>
                    <button
                      className="button secondary"
                      type="button"
                      disabled={busy}
                      onClick={() => setConfirming(false)}
                    >
                      Keep the Burst open
                    </button>
                  </div>
                </div>
              ) : (
                <div className="actions-row">
                  <button
                    className="button secondary"
                    type="button"
                    disabled={busy}
                    onClick={() => setConfirming(true)}
                    data-testid="complete-button"
                  >
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
        <section aria-labelledby="frozen-title">
          <h3 id="frozen-title">Frozen human question set</h3>
          <FrozenQuestionSet frozen={set.frozen} />
        </section>
      ) : null}
    </div>
  );
}
