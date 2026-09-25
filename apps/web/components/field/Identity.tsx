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
      <svg className="identity-mark" viewBox="0 0 26 26" aria-hidden="true" focusable="false">
        <circle cx="13" cy="13" r="10.5" fill="none" stroke="rgba(134,171,255,0.55)" strokeWidth="1" />
        <ellipse cx="13" cy="13" rx="10.5" ry="4.2" fill="none" stroke="rgba(88,220,255,0.7)" strokeWidth="1" transform="rotate(-28 13 13)" />
        <circle cx="13" cy="13" r="3.1" fill="#58dcff" />
        <circle cx="22.2" cy="8.4" r="1.4" fill="#86abff" />
      </svg>
      <span className="identity-word" aria-hidden="true">
        n<em>q</em>uiry
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
