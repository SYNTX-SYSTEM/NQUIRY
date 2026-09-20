/**
 * 12 §24 items 6/8/9: "verbatim human Question list", "origin marker
 * HUMAN or AI", "AI analysis shown explicitly as DERIVED / PROPOSAL".
 *
 * WHY `origin === "AI"` GETS A SECOND, EXPLICIT "DERIVED / PROPOSAL"
 * LABEL, NOT JUST THE ORIGIN MARKER ITSELF
 * --------------------------------------------------------------------
 * Item 8 (origin marker) and item 9 (AI analysis DERIVED/PROPOSAL
 * label) are two DISTINCT list entries in 12 §24 -- the origin marker
 * alone would tell a viewer WHO produced the text, but 09's own AI
 * path discipline additionally requires that AI-produced content never
 * be presented with the same evidentiary weight as human-authored
 * content (it is a DERIVED PROPOSAL, not a fact). Rendering both
 * separately (never collapsing them into one badge) keeps that
 * distinction visible even if a future package changes how origin
 * markers are styled.
 *
 * `originalText` is rendered EXACTLY as received (no trim/normalize/
 * truncate) -- 12 §24 item 6 names "verbatim" specifically.
 */
import type { QuestionView } from "../lib/api/types";

export function QuestionList({ questions }: { readonly questions: readonly QuestionView[] }) {
  return (
    <ul data-testid="question-list">
      {questions.map((question) => (
        <li key={question.questionId} data-testid="question-item">
          <span data-testid="question-origin">{question.origin}</span>
          {question.origin === "AI" ? <span data-testid="question-ai-derived-label">DERIVED / PROPOSAL</span> : null}
          <span data-testid="question-text">{question.originalText}</span>
        </li>
      ))}
    </ul>
  );
}
