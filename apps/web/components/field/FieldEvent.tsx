"use client";
/**
 * SF-05 (doc 26 §27) — the transient field event: a small resonance bloom at the bottom centre after a CONFIRMED
 * effect (committed + canonical re-read done). Luminous nucleus → soft aura → human-readable effect → a few
 * particles → brief hold → collapse. `role="status"` announces it once; it never blocks interaction
 * (`pointer-events: none`), never persists (its life is one CSS animation — bloom · hold · collapse — and it is
 * dismissed when that animation ends; under reduced motion the stylesheet substitutes a motionless step animation
 * of the same length, so the event still leaves), never replaces the persistent proof in the chamber, and is never a
 * source of truth. No timer: time passing changes nothing canonical (HD-11). Not confetti, not a toast stack, not
 * "Success".
 */
import { useState } from "react";
import type { EffectField } from "../../lib/field/effectLifecycle";
import { deriveFieldEvent, type FieldEvent as FieldEventModel, type FieldEventDescription } from "../../lib/field/fieldEvent";


const PARTICLES = [12, 58, 104, 151, 203, 249, 297, 341];

export function FieldEvent({ field, describe }: { readonly field: EffectField; readonly describe: (relation: string) => FieldEventDescription | null }) {
  const derived = deriveFieldEvent(field, describe);
  const [shown, setShown] = useState<FieldEventModel | null>(null);
  const [seen, setSeen] = useState<string | null>(null);
  // a new confirmed effect enters; the same confirmed effect never re-enters (its id is remembered)
  if (derived && derived.id !== seen) {
    setSeen(derived.id);
    setShown(derived);
  }
  if (!shown) return null;
  return (
    <div className="field-event" role="status" aria-live="polite" data-testid="field-event" data-relation={shown.relation} onAnimationEnd={(e) => (e.animationName === "event-life" || e.animationName === "event-hold") && setShown(null)}>
      <div className="event-aura" aria-hidden="true" />
      <div className="event-particles" aria-hidden="true">
        {PARTICLES.map((deg) => (
          <span key={deg} className="event-particle" style={{ ["--a" as string]: `${deg}deg` }} />
        ))}
      </div>
      <div className="event-nucleus" aria-hidden="true" />
      <p className="event-title">{shown.title}</p>
      <p className="event-text">{shown.text}</p>
    </div>
  );
}
