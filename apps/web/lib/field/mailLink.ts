"use client";
/**
 * AUTH/CYAN-RECOVERY-01: the challenge that arrives in a mail link (`?recovery=&token=` or
 * `?challengeId=&token=`) is captured ONCE per page load and removed from the address bar; the page then reads it
 * as an external store (no React state is set inside an effect, no ref is read during render). Server snapshot:
 * nothing captured. The values never leave this module except into the one typed request the page sends.
 */
import { useEffect, useSyncExternalStore } from "react";

type Capture = { search: string | null; listeners: Set<() => void> };
const capture: Capture = { search: null, listeners: new Set() };

function captureOnce(): void {
  if (capture.search !== null) return;
  capture.search = window.location.search;
  if (capture.search) window.history.replaceState(null, "", window.location.pathname);
  capture.listeners.forEach((l) => l());
}
function subscribe(l: () => void): () => void {
  capture.listeners.add(l);
  return () => capture.listeners.delete(l);
}

export type MailLinkState = { readonly captured: false } | { readonly captured: true; readonly params: URLSearchParams };

/** Captures on mount; returns the captured query (once) or `captured: false` before the capture / on the server. */
export function useMailLink(): MailLinkState {
  useEffect(() => {
    captureOnce();
  }, []);
  const search = useSyncExternalStore(
    subscribe,
    () => capture.search,
    () => null,
  );
  return search === null ? { captured: false } : { captured: true, params: new URLSearchParams(search) };
}

/** Test seam: forget a capture (a new page load in a test harness). */
export function resetMailLinkCapture(): void {
  capture.search = null;
}
