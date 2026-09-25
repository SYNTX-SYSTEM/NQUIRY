/**
 * F02 unavailable capability, projected in the SF-05 boundary grammar (doc 26 §26): the server's own reason stays
 * verbatim and is the element's text (legacy contract); the boundary CLASS is derived from the reason code and
 * written in words and structure. A boundary is not an error and not a warning.
 */
import type { Capability } from "../../lib/api/inquiryClient";
import { BoundaryMark, boundaryClassOf } from "../field/chambers";

export function Unavailable({ capability, testId }: { readonly capability: Capability; readonly testId: string }) {
  if (capability.available) {
    return null;
  }
  return (
    <BoundaryMark boundary={boundaryClassOf(capability.reasonCode)} reasonCode={capability.reasonCode} testId={testId}>
      {capability.reason}
    </BoundaryMark>
  );
}
