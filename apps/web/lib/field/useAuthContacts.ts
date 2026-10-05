"use client";
/**
 * AUTH/CYAN-RECOVERY-01: React binding of `fetchAuthContacts`. One discovery per mount; until the parsed answer
 * arrives, and whenever the read fails, every optional contact is "none" — a frontend never offers a path it has
 * not been told leads somewhere (24 §24.2). No persistence, no retry timer.
 */
import { useEffect, useState } from "react";
import { type AuthContacts, fetchAuthContacts } from "../api/authClient";

export type ContactsReading = { readonly kind: "none" } | { readonly kind: "contacts"; readonly contacts: AuthContacts };
export const NO_CONTACTS: ContactsReading = { kind: "none" };

export function useAuthContacts(): ContactsReading {
  const [reading, setReading] = useState<ContactsReading>(NO_CONTACTS);
  useEffect(() => {
    let cancelled = false;
    fetchAuthContacts()
      .then((contacts) => {
        if (!cancelled) setReading({ kind: "contacts", contacts });
      })
      .catch(() => {
        if (!cancelled) setReading(NO_CONTACTS);
      });
    return () => {
      cancelled = true;
    };
  }, []);
  return reading;
}

export const recoveryOffered = (r: ContactsReading): boolean => r.kind === "contacts" && r.contacts.recovery === "AVAILABLE";
export const verificationOffered = (r: ContactsReading): boolean => r.kind === "contacts" && r.contacts.emailVerification === "AVAILABLE";
