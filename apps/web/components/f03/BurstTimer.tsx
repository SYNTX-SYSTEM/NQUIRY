"use client";
/**
 * Elapsed-time PRESENTATION (HD-11): time since the server-recorded start, with
 * "about four minutes" as non-authoritative guidance. No countdown, no deadline,
 * no effect: nothing closes the Burst when the guidance is passed. Not a live
 * region (a ticking clock must not be announced every second).
 */
import { useEffect, useState } from "react";
import { BURST_GUIDANCE_SECONDS, elapsedSeconds, formatElapsed } from "../../lib/burst";

export function BurstTimer({
  startedAt,
  serverNow,
  guidanceSeconds = BURST_GUIDANCE_SECONDS,
}: {
  readonly startedAt: string;
  readonly serverNow: string;
  readonly guidanceSeconds?: number;
}) {
  const [loadedAt] = useState(() => Date.now());
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, []);
  const elapsed = elapsedSeconds(startedAt, serverNow, loadedAt, now);
  return (
    <p data-testid="burst-timer">
      Elapsed <span className="mono" data-testid="burst-elapsed">{formatElapsed(elapsed)}</span>{" "}
      <span className="muted">
        Guidance: about {Math.round(guidanceSeconds / 60)} minutes. The controller closes the Burst; nothing closes it
        automatically.
      </span>
    </p>
  );
}
