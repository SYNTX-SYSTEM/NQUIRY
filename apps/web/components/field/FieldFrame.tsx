/**
 * SF-01 Field Frame (21 §7 PF-01, §36): the persistent frame of the Relational
 * Interaction Field. It carries position (Relation Trace) and the active
 * semantic regime; it owns no domain state machine.
 *
 * Layout law (21 §30, §34): DOM order IS the relational order, so the narrow
 * layout needs no re-ordering and hides nothing:
 *
 *   POSITION (header trace) → CENTRE (active relation) → NEAR (affordance /
 *   boundary) → OUTER (context, closed relations) → DEPTH (proof)
 *
 * On wide screens the primary column holds centre + near and the secondary
 * column holds outer + depth. Only the column count changes with width.
 *
 * Page chrome (skip link, orientation rail, centred identity, exit) stays outside <main>, as in the F02
 * AppShell, so the F02 "no action element in main" proofs keep their scope. SF-03 (doc 23 §9–§10): the rail is
 * trace · identity · exit, one grid, the identity centred on desktop; the trace is the orientation relation.
 * SF-02: the frame mounts the Background Presentation Field (22 §17) with the
 * surface class as its regime; the background carries no authoritative claim.
 * The exit control ("Log out") is an effect on the identity relation, so a
 * surface passes `exit={null}` while its authoritative read is still pending:
 * no access affordance is shown before identity is confirmed (22 §21.7,
 * §28.9). Denied / not-found boundaries keep it (the identity exists).
 */
import { LogoutButton } from "../LogoutButton";
import type { TraceSegment } from "../../lib/field/position";
import { FieldBackground, type BackgroundRegime } from "./FieldBackground";
import { Identity } from "./Identity";
import { RelationTrace } from "./RelationTrace";

export type FieldRegime = BackgroundRegime;

export function FieldFrame({
  trace,
  regime,
  exit = <LogoutButton />,
  children,
}: {
  readonly trace: readonly TraceSegment[];
  readonly regime: FieldRegime;
  readonly exit?: React.ReactNode;
  readonly children: React.ReactNode;
}) {
  return (
    <>
      <FieldBackground regime={regime} />
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <header className="shell-header field-header">
        <RelationTrace segments={trace} />
        <Identity />
        <div className="rail-exit">{exit}</div>
      </header>
      <main id="main" className="shell-main field-main" data-field-regime={regime}>
        {children}
      </main>
    </>
  );
}

export type FieldZoneName = "centre" | "near" | "outer" | "depth";

/** One spatial zone of the field (21 §30). Structure, not decoration. */
export function FieldZone({
  zone,
  labelledBy,
  label,
  children,
}: {
  readonly zone: FieldZoneName;
  readonly labelledBy?: string;
  readonly label?: string;
  readonly children: React.ReactNode;
}) {
  return (
    <section className="field-zone" data-field-zone={zone} aria-labelledby={labelledBy} aria-label={label}>
      {children}
    </section>
  );
}

/** Primary column: centre + near. Secondary column (optional): outer + depth. */
export function FieldLayout({ primary, secondary }: { readonly primary: React.ReactNode; readonly secondary?: React.ReactNode }) {
  return (
    <div className="field-layout" data-columns={secondary ? 2 : 1}>
      <div className="field-primary">{primary}</div>
      {secondary ? <div className="field-secondary">{secondary}</div> : null}
    </div>
  );
}
