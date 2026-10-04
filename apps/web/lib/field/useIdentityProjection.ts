"use client";
/**
 * AUTH/CYAN-IDENTITY-01: React binding of `identityProjectionFrom`. The page already holds the `/auth/me` verdict
 * (the authentication verdict); once it is `ok` the four reads (identity presentation, sessions, methods, providers)
 * run in parallel through the typed client and
 * every throw becomes a null read (fail closed). React state only; no persistence, no retry timer.
 *
 * AUTH/CYAN-ACCOUNT-01: the same reads are also the ONE source of the account-security relations, so the hook hands
 * them out next to the projection, together with `reload` — the canonical re-read after an account effect (unlink,
 * revoke). `reload` resolves true only when the two relation reads (sessions, methods) produced a current answer.
 */
import { useCallback, useEffect, useState } from "react";
import { fetchIdentityPresentation, listMethods, listProviders, listSessions, type IdentityPresentationResult, type MethodListResult, type ProviderListResult, type SessionListResult } from "../api/authClient";
import { identityProjectionFrom, type IdentityProjection, type IdentityReads } from "./identityProjection";

type Reads = { readonly identity: IdentityPresentationResult | null; readonly sessions: SessionListResult | null; readonly methods: MethodListResult | null; readonly providers: ProviderListResult | null };
const PENDING: Reads = { identity: null, sessions: null, methods: null, providers: null };
const quiet = <T,>(read: Promise<T>): Promise<T | null> => read.catch(() => null);

export type IdentityField = {
  readonly projection: IdentityProjection;
  readonly reads: IdentityReads;
  readonly reload: () => Promise<boolean>;
};

export function useIdentityProjection(userId: string | null): IdentityField {
  const [reads, setReads] = useState<Reads>(PENDING);
  const read = useCallback(async (): Promise<Reads> => {
    const [identity, sessions, methods, providers] = await Promise.all([quiet(fetchIdentityPresentation()), quiet(listSessions()), quiet(listMethods()), quiet(listProviders())]);
    return { identity, sessions, methods, providers };
  }, []);
  useEffect(() => {
    if (userId === null) return;
    let cancelled = false;
    read().then((next) => {
      if (!cancelled) setReads(next);
    });
    return () => {
      cancelled = true;
    };
  }, [userId, read]);
  const reload = useCallback(async (): Promise<boolean> => {
    if (userId === null) return false;
    const next = await read();
    setReads(next);
    return next.sessions !== null && next.sessions.kind === "ok" && next.methods !== null && next.methods.kind === "ok";
  }, [userId, read]);
  const all: IdentityReads = { me: userId === null ? null : { kind: "ok", userId }, ...reads };
  return { projection: identityProjectionFrom(all), reads: all, reload };
}
