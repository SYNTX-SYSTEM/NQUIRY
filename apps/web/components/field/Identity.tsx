/**
 * SF-03 global product identity (doc 23 §10): a designed, centred NQIRY mark in the orientation rail.
 *
 * Product identity ONLY: it is not a Core, not authority, not governance, not system state and not a commit
 * indicator (doc 23 §10.2). In the rail it stays a link to the accessible Workspaces with the accessible name
 * "nquiry" the F02/F03 lanes already rely on; on the Access Field (no identity relation yet) it is a plain mark.
 * The glyph is decorative (`aria-hidden`); the wordmark carries the name.
 */
import Link from "next/link";

function Mark() {
  return (
    <>
      {/* the designed wordmark (assets/logo, transparent): decorative — the link / figure carries the name "nquiry" */}
      <span className="identity-glow" aria-hidden="true" />
      <img className="identity-logo" src="/brand/nquiry-logo.png" srcSet="/brand/nquiry-logo.png 1x, /brand/nquiry-logo@2x.png 2x" alt="" width="640" height="234" decoding="async" />
      <span className="identity-word visually-hidden" aria-hidden="true">
        nquiry
      </span>
    </>
  );
}

export function Identity({ link = true }: { readonly link?: boolean }) {
  if (!link) {
    return (
      <div className="identity" aria-label="nquiry" role="img" data-testid="identity">
        <Mark />
      </div>
    );
  }
  return (
    <Link className="identity brand" href="/workspaces" aria-label="nquiry" data-testid="identity">
      <Mark />
    </Link>
  );
}
