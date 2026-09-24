/**
 * SF-01 Position Trace (21 §12, §36, CF-01): the human's relational position as
 * an ordered description, not a breadcrumb.
 *
 * - established parents: closed, and linkable (moving between accessible
 *   contexts is lawful, 21 §29);
 * - current coordinate: dominant, `aria-current="location"`, never a link;
 * - possible / unavailable future relation: named with its status in words,
 *   never a destination (falsifier 32).
 *
 * The status word stays OUTSIDE the link, so a link's accessible name is exactly
 * its context name.
 */
import Link from "next/link";
import type { TraceSegment, TraceStatus } from "../../lib/field/position";

const STATUS_WORDS: Readonly<Record<TraceStatus, string>> = {
  established: "established context",
  current: "current position",
  possible: "possible next relation",
  unavailable: "not available now",
};

export function RelationTrace({ segments }: { readonly segments: readonly TraceSegment[] }) {
  return (
    <nav aria-label="Inquiry position" className="trace" data-testid="relation-trace">
      <ol>
        {segments.map((segment) => {
          const future = segment.status === "possible" || segment.status === "unavailable";
          return (
            <li
              key={`${segment.coordinate}-${segment.status}`}
              data-coordinate={segment.coordinate}
              data-status={segment.status}
              aria-current={segment.status === "current" ? "location" : undefined}
            >
              {segment.href && segment.status === "established" ? (
                <Link href={segment.href}>{segment.label}</Link>
              ) : (
                <span className="trace-label">{segment.label}</span>
              )}{" "}
              <span className={future ? "trace-status" : "visually-hidden"}>({STATUS_WORDS[segment.status]})</span>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
