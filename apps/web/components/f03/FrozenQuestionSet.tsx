/**
 * The frozen human question set (F03): a RECORD, not a form. After the Burst is
 * completed every Session member sees the same set (HD-13): each question
 * exactly as typed, marked HUMAN, with its author and capture order, plus the
 * frozen marker and the verification state of its fingerprint. The fingerprint
 * is recomputed on the server from canonical persistence; `verified: false` is
 * shown, never hidden.
 */
import type { FrozenSet } from "../../lib/api/inquiryClient";

export function FrozenQuestionSet({ frozen }: { readonly frozen: FrozenSet }) {
  return (
    <div data-testid="frozen-set" data-verified={String(frozen.verified)}>
      <p>
        <span className="tag authority" data-testid="frozen-marker">
          FROZEN
        </span>{" "}
        <strong>
          {frozen.memberCount} {frozen.memberCount === 1 ? "question" : "questions"}
        </strong>{" "}
        <span className="muted">
          The raw human set is fixed. Nothing can be added, removed or rewritten.
        </span>
      </p>
      <dl className="provenance">
        <dt>Integrity</dt>
        <dd data-testid="frozen-verified">
          {frozen.verified ? "Verified: the fingerprint matches the stored set." : "The stored fingerprint does not match the set."}
        </dd>
        <dt>Fingerprint</dt>
        <dd className="mono" data-testid="frozen-fingerprint">
          {frozen.fingerprint ?? "—"}
        </dd>
      </dl>
      <ol className="question-list" aria-label="Frozen human questions">
        {frozen.questions.map((question) => (
          <li key={question.questionId} data-testid="frozen-question" data-origin={question.origin}>
            <span className="tag human">human</span>{" "}
            <span className="muted">
              #{question.capturedOrder + 1} · {question.authorName ?? "unknown author"}
            </span>
            <pre className="verbatim" data-testid="frozen-question-text">{question.originalText}</pre>
          </li>
        ))}
      </ol>
    </div>
  );
}
