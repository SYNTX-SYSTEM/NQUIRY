/**
 * F03 presentation helpers for the protected Burst. Pure, no authority.
 *
 * TIMER (HD-11 / NQ-DEC-039): the timer is PRESENTATION only. This module
 * exposes elapsed time since the server-recorded start and a guidance constant.
 * It has no countdown, no deadline and no callback: nothing is scheduled and
 * nothing happens when the guidance is exceeded. Completion is a manual,
 * authorized Command (`completeBurst`).
 */

/** "Approximately four minutes" (LEVEL 1, 12 §5): non-authoritative guidance. */
export const BURST_GUIDANCE_SECONDS = 240;

/**
 * Elapsed seconds since the Burst started, measured against the SERVER clock so
 * a skewed browser clock cannot misreport it: `serverNow` and the client time
 * at which it was received are captured together.
 */
export function elapsedSeconds(startedAt: string, serverNow: string, clientMsAtLoad: number, clientMsNow: number): number {
  const startedMs = Date.parse(startedAt);
  const serverMs = Date.parse(serverNow);
  if (Number.isNaN(startedMs) || Number.isNaN(serverMs)) return 0;
  const sinceLoadMs = Math.max(0, clientMsNow - clientMsAtLoad);
  return Math.max(0, Math.floor((serverMs - startedMs + sinceLoadMs) / 1000));
}

export function formatElapsed(totalSeconds: number): string {
  const s = Math.max(0, Math.floor(totalSeconds));
  const mm = String(Math.floor(s / 60)).padStart(2, "0");
  const ss = String(s % 60).padStart(2, "0");
  return `${mm}:${ss}`;
}

const REJECTIONS: Readonly<Record<string, string>> = {
  INPUT_NOT_A_QUESTION:
    "Only questions are accepted during the Burst: end your text with a question mark. Nothing was stored.",
  INPUT_EMPTY: "There is no question to submit. Nothing was stored.",
  INPUT_TOO_LONG: "This text is too long for one question. Nothing was stored.",
  INPUT_NOT_STORABLE: "This text contains characters that cannot be stored exactly as typed. Nothing was stored.",
};

/** Plain-words explanation of an input rejection. Never presented as an authority decision. */
export function explainCaptureRejection(reasonCode: string): string {
  return REJECTIONS[reasonCode] ?? `The input was rejected (${reasonCode}). Nothing was stored.`;
}

export type Intent = { readonly key: string; readonly text: string };

/**
 * ONE Idempotency-Key per logical capture. The same key is kept while the text
 * is unchanged (a retry after no response is the same Command on the server);
 * changed text is a NEW intent, because the server treats a changed payload
 * under a reused key as a different Command and rejects it.
 */
export function intentKeyFor(previous: Intent | null, text: string, makeKey: () => string): Intent {
  if (previous !== null && previous.text === text) return previous;
  return { key: makeKey(), text };
}
