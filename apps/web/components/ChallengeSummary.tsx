/** 12 §24 item 2: "Challenge frame". Passive display only -- no edit
 * control (Challenge mutation is out of this package's own scope). */
import type { ChallengeView } from "../lib/api/types";

export function ChallengeSummary({ challenge }: { readonly challenge: ChallengeView }) {
  return (
    <section data-testid="challenge-summary">
      <h2>{challenge.title}</h2>
      {challenge.description !== null ? <p>{challenge.description}</p> : null}
    </section>
  );
}
