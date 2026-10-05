"use client";
/**
 * AUTH/CYAN-ACCOUNT-01: React binding of `linkBoundaryFrom` over the browser's own location search (the projection
 * arrives in the URL from the API's link-callback redirect to the page-owned return target). Same discipline as
 * `useAuthBoundary`: an external store, empty on the server, re-read on history navigation; no state, no rewriting.
 */
import { useSyncExternalStore } from "react";
import { linkBoundaryFrom, type LinkBoundary } from "./linkBoundary";

function subscribe(onChange: () => void): () => void {
  window.addEventListener("popstate", onChange);
  return () => window.removeEventListener("popstate", onChange);
}
const clientSearch = () => window.location.search;
const serverSearch = () => "";

export function useLinkBoundary(): LinkBoundary {
  return linkBoundaryFrom(useSyncExternalStore(subscribe, clientSearch, serverSearch));
}
