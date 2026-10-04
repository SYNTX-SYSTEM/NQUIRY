/**
 * CYAN-PCPG-06 · Architecture 27 v4 levels 1 and 2 — deliberate inspection of the SAME object: a native disclosure
 * ("Field / Governance") inside the intent chamber, whose body is the deep field view in the order the architecture
 * names: label · capability axes · basis · semantic observation · presentation attachments · deltas · boundary / FBR
 * (the §09.3 card) · Human Authority required · provider / send · Session-level proof ceiling · not materialized.
 * Words only: no control, no approval, no send-like element. The deep view states what is not materialized; it
 * neither hides nor fills it.
 */
import type { PanelModel } from "../../lib/field/pcpgRendering";

export function GovernancePanel({ panel }: { readonly panel: PanelModel }) {
  const hasCurrent = panel.semantic !== null;
  return (
    <details className="proof-depth governance-panel" data-testid="governance-panel" data-observation={panel.observation} data-superseded={panel.superseded ? "true" : undefined}>
      <summary>
        <span className="proof-depth-title">Field / Governance</span> <span className="governance-panel-label">{panel.label}</span>
      </summary>
      <div className="proof-depth-body governance-panel-body">
        <p className="visually-hidden" data-testid="governance-spoken">{panel.spoken.join(" ")}</p>
        {!hasCurrent ? (
          <p className="muted" data-testid="governance-panel-none">{panel.label}. No governance statement is made without a current observation.</p>
        ) : (
          <>
            <dl className="provenance governance-axes" data-testid="governance-capability">
              {panel.capability.map((c) => (
                <div key={c.axis}>
                  <dt>{c.axis}</dt>
                  <dd>{c.words}</dd>
                </div>
              ))}
            </dl>
            {panel.basis ? (
              <dl className="provenance" data-testid="governance-basis">
                <dt>Basis</dt>
                <dd>
                  <span className="mono">{panel.basis.digest.slice(0, 12)}…</span> <span className="muted">· derived at {panel.basis.derivationTime}</span>
                  {panel.superseded ? <span className="muted"> · the Session changed afterwards</span> : null}
                </dd>
              </dl>
            ) : null}
            {panel.semantic ? (
              <dl className="provenance" data-testid="governance-semantic">
                <dt>Semantic observation</dt>
                <dd>
                  rule set {panel.semantic.ruleSetVersion} · {panel.semantic.clauses.length} {panel.semantic.clauses.length === 1 ? "clause" : "clauses"} · relations touched:{" "}
                  {panel.semantic.relationsTouched.length ? panel.semantic.relationsTouched.join(", ") : "none"}
                  {panel.semantic.unknownRelations.length ? ` · unknown relations: ${panel.semantic.unknownRelations.join(", ")}` : ""}
                </dd>
                <dt>Purpose</dt>
                <dd>
                  declared: {panel.semantic.declaredPurpose ?? "none"} · observed: {panel.semantic.semanticPurpose ?? "not determinable"} · alignment: {panel.semantic.purposeAlignment}
                  {panel.semantic.semanticDrift ? " · semantic drift" : ""}
                </dd>
              </dl>
            ) : null}
            <section aria-labelledby="governance-deltas-title" data-testid="governance-deltas">
              <h4 id="governance-deltas-title" className="governance-h">Crossed steps and their placement</h4>
              {panel.deltas.length === 0 ? (
                <p className="muted">No step crossed.</p>
              ) : (
                <ol className="governance-delta-list">
                  {panel.deltas.map((d) => (
                    <li key={d.deltaId} data-delta-id={d.deltaId}>
                      <p className="governance-delta-line">{d.line}</p>
                      <p className="governance-delta-clause">
                        “{d.sourceClause}” <span className="muted">(span {d.span[0]}–{d.span[1]})</span>
                      </p>
                      <p className="muted governance-delta-meta">
                        target: {d.target}
                        {d.currentState ? ` · current state: ${d.currentState}` : ""}
                        {d.flags.length ? ` · flags: ${d.flags.join(", ")}` : ""}
                        {d.retained ? " · retained in the maximum legitimate transition" : ""}
                        {" · "}
                        {d.sessionProofCeiling.label}: {d.sessionProofCeiling.words}
                      </p>
                      <p className="governance-delta-place">
                        Shown at: {d.placedAt.length ? d.placedAt.join(", ") : "the panel only"} <span className="muted">(CYAN-local placement, {d.categories.join(", ") || "UNPLACED"})</span>
                      </p>
                    </li>
                  ))}
                </ol>
              )}
            </section>
            {panel.boundary ? (
              <section className="boundary-card" aria-labelledby="boundary-card-title" data-testid="boundary-card" data-partial={panel.boundary.partial ? "true" : undefined}>
                <h4 id="boundary-card-title" className="governance-h">Boundary reached</h4>
                <dl className="provenance">
                  <dt>What stopped?</dt>
                  <dd data-testid="boundary-what">{panel.boundary.whatStopped}</dd>
                  <dt>Requested in</dt>
                  <dd data-testid="boundary-clause">“{panel.boundary.requestedIn}”</dd>
                  <dt>Why?</dt>
                  <dd data-testid="boundary-why">{panel.boundary.why}</dd>
                  <dt>After</dt>
                  <dd data-testid="boundary-after">{panel.boundary.after}</dd>
                  <dt>Human Authority required for</dt>
                  <dd data-testid="boundary-har">
                    {panel.boundary.humanAuthorityRequired.length === 0 ? "no step" : panel.boundary.humanAuthorityRequired.map((h) => `${h.deltaId} → ${h.words}`).join("; ")}
                  </dd>
                  <dt>Current presentation (CYAN-local)</dt>
                  <dd data-testid="boundary-placed">{panel.boundary.placedAt.length ? panel.boundary.placedAt.join(" · ") : "the panel only"}</dd>
                </dl>
                {panel.boundary.partial ? <p className="muted">Chain partial.</p> : null}
              </section>
            ) : null}
            {panel.nextValidTransition ? (
              <dl className="provenance" data-testid="governance-nvt">
                <dt>Next valid transition</dt>
                <dd>{panel.nextValidTransition}</dd>
              </dl>
            ) : null}
            {panel.provider ? (
              <dl className="provenance" data-testid="governance-provider">
                <dt>Provider</dt>
                <dd>
                  {panel.provider.notExecutable ? "not executable" : "no provider step not executable"}
                  {panel.provider.reasons.length ? ` · ${panel.provider.reasons.join(", ")}` : ""}
                </dd>
                <dt>Send</dt>
                <dd data-testid="governance-send">{panel.provider.send}</dd>
              </dl>
            ) : null}
            {panel.proofCeiling ? (
              <dl className="provenance" data-testid="governance-ceiling">
                <dt>{panel.proofCeiling.label}</dt>
                <dd>{panel.proofCeiling.words}</dd>
              </dl>
            ) : null}
            <dl className="provenance" data-testid="governance-not-materialized">
              <dt>Not materialized</dt>
              <dd>{panel.notMaterialized.join(" · ")}</dd>
            </dl>
          </>
        )}
      </div>
    </details>
  );
}
