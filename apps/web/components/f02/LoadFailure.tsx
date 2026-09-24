import type { Failure } from "../../lib/api/inquiryClient";
import { Outcome } from "./Outcome";

/** Truthful page-level failure: denied / not found / network / protocol. */
export function LoadFailure({ failure }: { readonly failure: Failure }) {
  return (
    <section aria-labelledby="load-failure-title" className="panel" data-testid="load-failure">
      <h1 id="load-failure-title">Unable to show this page</h1>
      <Outcome outcome={failure} />
    </section>
  );
}
