"use client";
/**
 * SF-01/SF-04 Traversal Trace (21 §12, §36, CF-01; doc 25 §11): the human's relational position as an ordered
 * description of ROUTE NODES joined by a trace, not a breadcrumb.
 *
 * - established parents: closed route nodes, linkable (moving between accessible contexts is lawful, 21 §29);
 * - current coordinate: the active membrane node, `aria-current="location"`, never a link;
 * - possible / unavailable future relation: named with its status in words, never a destination (falsifier 32).
 *
 * The status word stays OUTSIDE the link, so a link's accessible name is exactly its context name. The trace between
 * nodes is decorative (`::before`, shimmer on the stylesheet's ambient layer). On phones the trace compresses to the
 * current node as a chip; the "path" toggle expands the full route (doc 25 §11.4, §15.4). Expansion is
 * projection-local UI state: it changes nothing canonical.
 */
import Link from "next/link";
import { useId, useState } from "react";
import type { TraceSegment, TraceStatus } from "../../lib/field/position";

const STATUS_WORDS: Readonly<Record<TraceStatus, string>> = {
  established: "established context",
  current: "current position",
  possible: "possible next relation",
  unavailable: "not available now",
};

export function RelationTrace({ segments }: { readonly segments: readonly TraceSegment[] }) {
  const [expanded, setExpanded] = useState(false);
  const listId = useId();
  const others = segments.filter((s) => s.status !== "current").length;
  return (
    <nav aria-label="Inquiry position" className="trace" data-testid="relation-trace" data-expanded={expanded ? "true" : undefined}>
      {others > 0 ? (
        <button type="button" className="trace-chip-toggle" aria-expanded={expanded} aria-controls={listId} onClick={() => setExpanded((v) => !v)} data-testid="trace-toggle">
          <span className="visually-hidden">{expanded ? "Hide the route" : "Show the route"}</span>
          <span className="trace-chip-count" aria-hidden="true">{expanded ? "−" : `+${others}`}</span>
        </button>
      ) : null}
      <ol id={listId}>
        {segments.map((segment) => {
          const future = segment.status === "possible" || segment.status === "unavailable";
          return (
            <li
              key={`${segment.coordinate}-${segment.status}`}
              className="route-node"
              data-coordinate={segment.coordinate}
              data-status={segment.status}
              aria-current={segment.status === "current" ? "location" : undefined}
            >
              <span className="route-membrane" aria-hidden="true" />
              {segment.href && segment.status === "established" ? (
                <Link href={segment.href} title={segment.label}>
                  {segment.label}
                </Link>
              ) : (
                <span className="trace-label" title={segment.status === "current" ? undefined : segment.label}>
                  {segment.label}
                </span>
              )}{" "}
              <span className={future ? "trace-status" : "visually-hidden"}>({STATUS_WORDS[segment.status]})</span>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
