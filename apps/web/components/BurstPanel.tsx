/**
 * 12 §24 items 4/5/7: "Burst state", "HUMAN_ONLY mode indicator",
 * "frozen raw-set indicator after completion" -- plus item 6/8/9 via
 * the nested `QuestionList`.
 *
 * WHY THERE IS NO AI-CONTROL ELEMENT HERE EVEN WHEN `state === "ACTIVE"`
 * --------------------------------------------------------------------
 * This package's own scope has ZERO interactive actions (Question
 * selection, Decision boundary, human Decision action are PKG-29's
 * own scope) -- this component renders only passive state/mode/origin
 * information regardless of `burst.state` or `burst.mode`, proven by
 * the "attempt AI control during ACTIVE Burst" E2E attack
 * (`tests/e2e/session-view.spec.ts`): no button, form, or
 * AI-start/AI-control element exists in this component's own output at
 * all, for any Burst shape.
 */
import { isBurstFrozen, type BurstView } from "../lib/api/types";
import { QuestionList } from "./QuestionList";

export function BurstPanel({ burst }: { readonly burst: BurstView }) {
  return (
    <section data-testid="burst-panel">
      <span data-testid="burst-state">Burst state: {burst.state}</span>
      {burst.mode === "HUMAN_ONLY" ? <span data-testid="burst-human-only-indicator">HUMAN_ONLY</span> : null}
      {isBurstFrozen(burst) ? <span data-testid="burst-frozen-indicator">Frozen (raw set immutable)</span> : null}
      <QuestionList questions={burst.questions} />
    </section>
  );
}
