"use client";
/**
 * AUTH/CYAN-IDENTITY-01: React binding of `identityProjectionFrom`. The page already holds the `/auth/me` verdict
 * (the authentication verdict); once it is `ok` the four reads (identity presentation, sessions, methods, providers)
 * run in parallel through the typed client and
 * every throw becomes a null read (fail closed). React state only; no persistence, no retry timer.
 */
import { useEffect, useState } from "react";
import { fetchIdentityPresentation, listMethods, listProviders, listSessions, type IdentityPresentationResult, type MethodListResult, type ProviderListResult, type SessionListResult } from "../api/authClient";
import { identityProjectionFrom, type IdentityProjection } from "./identityProjection";

type Reads = { readonly identity: IdentityPresentationResult | null; readonly sessions: SessionListResult | null; readonly methods: MethodListResult | null; readonly providers: ProviderListResult | null };
const PENDING: Reads = { identity: null, sessions: null, methods: null, providers: null };
const quiet = <T,>(read: Promise<T>): Promise<T | null> => read.catch(() => null);

export function useIdentityProjection(userId: string | null): IdentityProjection {
  const [reads, setReads] = useState<Reads>(PENDING);
  useEffect(() => {
    if (userId === null) return;
    let cancelled = false;
    Promise.all([quiet(fetchIdentityPresentation()), quiet(listSessions()), quiet(listMethods()), quiet(listProviders())]).then(([identity, sessions, methods, providers]) => {
      if (!cancelled) setReads({ identity, sessions, methods, providers });
    });
    return () => {
      cancelled = true;
    };
  }, [userId]);
  return identityProjectionFrom({ me: userId === null ? null : { kind: "ok", userId }, ...reads });
}
