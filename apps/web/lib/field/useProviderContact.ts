"use client";
/**
 * AUTH/CYAN-02: React binding of `discoverProviderContact`. One discovery per mount, React state only (no
 * persistence, no retry timer); until the parsed answer arrives the contact is `none`, so the Access Field never
 * shows a provider it has not been told about.
 */
import { useEffect, useState } from "react";
import { discoverProviderContact, NO_PROVIDER_CONTACT, type ProviderContact } from "./providerContact";

export function useProviderContact(next: string): ProviderContact {
  const [contact, setContact] = useState<ProviderContact>(NO_PROVIDER_CONTACT);
  useEffect(() => {
    let cancelled = false;
    discoverProviderContact(next).then((discovered) => {
      if (!cancelled) setContact(discovered);
    });
    return () => {
      cancelled = true;
    };
  }, [next]);
  return contact;
}
