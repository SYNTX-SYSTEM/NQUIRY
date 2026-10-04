/**
 * CYAN-PCPG-06 · Architecture 27 v4 level 0.5 — the action-adjacent attachment marker. One quiet strip inside an
 * EXISTING object area saying which crossed steps of the current observation are PLACED here (CYAN-local placement),
 * each as "<operation> · <execution class> — <result · reasonCode>". It adds no control, no consequence, no new
 * surface: PRESENTATION LOCATION != GOVERNANCE TRUTH. Rendered only when the current observation placed a delta
 * in this area; nothing at all otherwise (NO OBSERVATION != CURRENT).
 */
import type { AreaRendering } from "../../lib/field/pcpgRendering";
import { PROVIDER_NOT_EXECUTABLE, SEND_NOT_MATERIALIZED } from "../../lib/field/pcpgRendering";

export function GovernanceAttachment({ rendering }: { readonly rendering: AreaRendering | undefined }) {
  if (!rendering) return null;
  const prominence = rendering.firstBrokenHere || rendering.humanAuthorityHere ? "prominent" : rendering.providerNotExecutable ? "explicit" : "quiet";
  return (
    <aside
      className="governance-attachment"
      data-governance-attachment={rendering.area}
      data-testid={`governance-attachment-${rendering.area}`}
      data-prominence={prominence}
      data-superseded={rendering.superseded ? "true" : undefined}
      aria-label={`Governance placed at ${rendering.words}: ${rendering.summary}${rendering.superseded ? "; the Session changed after this observation" : ""}`}
    >
      <p className="attachment-head">
        <span className="attachment-field" aria-hidden="true">Field</span>
        <span className="attachment-summary">{rendering.summary}</span>
        {rendering.superseded ? <span className="attachment-superseded">· observed before the Session changed</span> : null}
      </p>
      <ul className="attachment-deltas">
        {rendering.deltas.map((p) => (
          <li key={p.delta.deltaId} data-delta-id={p.delta.deltaId} data-result={p.delta.result} data-first-broken={p.isFirstBroken ? "true" : undefined} data-human-authority={p.humanAuthorityRequired ? "true" : undefined}>
            <span className="attachment-line">{p.line}</span>
            {p.isFirstBroken ? <span className="attachment-mark">first broken relation</span> : null}
            {p.humanAuthorityRequired ? <span className="attachment-mark">Human Authority required</span> : null}
            {p.retained ? <span className="attachment-mark">retained</span> : null}
          </li>
        ))}
      </ul>
      {rendering.providerNotExecutable ? (
        <p className="attachment-provider" data-testid="attachment-provider">
          <span>{PROVIDER_NOT_EXECUTABLE}</span> <span className="muted">· {SEND_NOT_MATERIALIZED}</span>
        </p>
      ) : null}
    </aside>
  );
}
