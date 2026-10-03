"use client";
/**
 * AUTH/CYAN-03: React binding of `authBoundaryFrom` over the browser's own location search (the projection arrives
 * in the URL from the API's callback redirect). The search is read as an external store: nothing on the server
 * (empty search → none), the live value on the client, re-read on history navigation. No state of its own, no
 * persistence, no URL rewriting.
 */
import { useSyncExternalStore } from "react";
import { authBoundaryFrom, type AuthBoundary } from "./authBoundary";

function subscribe(onChange: () => void): () => void {
  window.addEventListener("popstate", onChange);
  return () => window.removeEventListener("popstate", onChange);
}
const clientSearch = () => window.location.search;
const serverSearch = () => "";

export function useAuthBoundary(): AuthBoundary {
  return authBoundaryFrom(useSyncExternalStore(subscribe, clientSearch, serverSearch));
}
