/**
 * SF-01 Proof Surface (21 §15 disclosure levels, §40 D2 VERIFY / D3 RECONSTRUCT,
 * CF-09): proof is deep, not permanently wide.
 *
 * Native `<details>`: closed by default, keyboard-operable with no custom focus
 * handling, so there is no trap. It opens in place, so the originating position
 * is never lost (falsifier 26). Content is in the DOM at every width, so proof
 * never disappears on narrow screens (falsifier 23).
 */
const DEPTH_WORDS = { D2: "verify", D3: "reconstruct" } as const;

export function ProofDepth({
  depth,
  title,
  testId,
  children,
}: {
  readonly depth: keyof typeof DEPTH_WORDS;
  readonly title: string;
  readonly testId?: string;
  readonly children: React.ReactNode;
}) {
  return (
    <details className="proof-depth" data-depth={depth} data-testid={testId}>
      <summary>
        <span className="proof-depth-title">{title}</span>{" "}
        <span className="visually-hidden">(proof, {DEPTH_WORDS[depth]})</span>
      </summary>
      <div className="proof-depth-body t-proof">{children}</div>
    </details>
  );
}
