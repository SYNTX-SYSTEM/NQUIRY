/**
 * The viewer's OWN captured questions during the ACTIVE Burst (HD-13). The
 * server only ever sends the viewer their own; this component renders what it
 * is given, exactly as stored. `white-space: pre-wrap` keeps every character
 * of `original_text` visible as typed.
 */
import type { CapturedQuestion } from "../../lib/api/inquiryClient";

export function OwnQuestions({ questions }: { readonly questions: readonly CapturedQuestion[] }) {
  if (questions.length === 0) {
    return (
      <p className="muted" data-testid="own-questions-empty">
        You have not submitted a question yet.
      </p>
    );
  }
  return (
    <ol className="question-list" data-testid="own-questions" aria-label="Your questions">
      {questions.map((question) => (
        <li key={question.questionId} data-testid="own-question" data-origin={question.origin}>
          <span className="tag human">human</span>{" "}
          <span className="muted">#{question.capturedOrder + 1}</span>
          <pre className="verbatim" data-testid="own-question-text">{question.originalText}</pre>
        </li>
      ))}
    </ol>
  );
}
