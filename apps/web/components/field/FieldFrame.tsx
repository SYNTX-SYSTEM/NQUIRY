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
 * Page chrome (skip link, brand, exit) stays outside <main>, as in the F02
 * AppShell, so the F02 "no action element in main" proofs keep their scope.
 * The F02 AppShell itself is left untouched: the Session page (F03 contact
 * zone) still uses it until the post-F03 synchronization.
 */
import Link from "next/link";
import { LogoutButton } from "../LogoutButton";
import type { TraceSegment } from "../../lib/field/position";
import { RelationTrace } from "./RelationTrace";

export type FieldRegime = "workspace-access" | "workspace" | "challenge";

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
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <header className="shell-header field-header">
        <Link className="brand" href="/workspaces">
          nquiry
        </Link>
        <RelationTrace segments={trace} />
        {exit}
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
