"use client";
/**
 * AUTH/CYAN-IDENTITY-01: React binding of `identityProjectionFrom`. The page already holds the `/auth/me` verdict
 * (the only source of identity truth); once it is `ok` the three reads run in parallel through the typed client and
 * every throw becomes a null read (fail closed). React state only; no persistence, no retry timer.
 */
import { useEffect, useState } from "react";
import { listMethods, listProviders, listSessions, type MethodListResult, type ProviderListResult, type SessionListResult } from "../api/authClient";
import { identityProjectionFrom, type IdentityProjection } from "./identityProjection";

type Reads = { readonly sessions: SessionListResult | null; readonly methods: MethodListResult | null; readonly providers: ProviderListResult | null };
const PENDING: Reads = { sessions: null, methods: null, providers: null };
const quiet = <T,>(read: Promise<T>): Promise<T | null> => read.catch(() => null);

export function useIdentityProjection(userId: string | null): IdentityProjection {
  const [reads, setReads] = useState<Reads>(PENDING);
  useEffect(() => {
    if (userId === null) return;
    let cancelled = false;
    Promise.all([quiet(listSessions()), quiet(listMethods()), quiet(listProviders())]).then(([sessions, methods, providers]) => {
      if (!cancelled) setReads({ sessions, methods, providers });
    });
    return () => {
      cancelled = true;
    };
  }, [userId]);
  return identityProjectionFrom({ me: userId === null ? null : { kind: "ok", userId }, ...reads });
}
