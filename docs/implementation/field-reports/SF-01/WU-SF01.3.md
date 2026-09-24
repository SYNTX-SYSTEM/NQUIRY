# WORK UNIT REPORT
FIELD: SF-01 — SYMBIOTIC FRONTEND FOUNDATION
WORK_UNIT: WU-SF01.3 — Semantic primitives

## Mission
Compile the doc-21 §36 semantic roles that SF-01 needs into primitives whose distinctions survive with
no CSS (21 §31, §35).

## Files changed (all NEW)
- `apps/web/components/field/RelationTrace.tsx`: `nav[aria-label="Inquiry position"] > ol`.
  - Current coordinate: `aria-current="location"`, never a link.
  - Established parents are links. Future relations are text with their status in words.
  - The status word sits outside the link, so a link's accessible name is exactly its context name.
- `apps/web/components/field/FieldFrame.tsx`:
  - `FieldFrame`: skip link, brand, trace and exit (slot, default Logout) outside `<main data-field-regime>`.
  - `FieldZone`: `data-field-zone` centre / near / outer / depth.
  - `FieldLayout`: DOM order = relational order = mobile order. Secondary column optional.
- `apps/web/components/field/EffectSurface.tsx`:
  - `EffectIntent`: REQUESTED, not committed, `role=status`.
  - `EffectOutcome` (Commit Marker + Boundary Surface): `data-outcome`, `data-consequence`, `data-reconstruction`, §39 title, reason code, consequence line, reconstruction line, and "Re-read current state" after a failed re-read. Legacy hooks `reasonTestId` / `committedTestId`.
  - `ReconstructionNote`: marks the view as last confirmed.
- `apps/web/components/field/ReadBoundary.tsx`: read-path boundary. No effect claim; only confirmed context is kept.
- `apps/web/components/field/ProofDepth.tsx`: native `<details>`, D2 verify / D3 reconstruct. Closed by default, no trap, opens in place.
- `apps/web/components/field/Origin.tsx`:
  - `OriginMark` covers the four origin classes, each with an accessible origin name. AI-derived throws without `lineage`.
  - `StateName` renders SYSTEM STATE.
- `apps/web/tests/field/primitives.test.tsx` (21, static markup, no CSS).
- CSS: see WU-SF01.4 (append-only).

## Test-first intent
- **TRUE:** every settled kind is distinct in text and attributes; the commit marker claims a re-read only when it is done; C3-06 wording; ReadBoundary claims no effect; proof is closed by default; origin is carried in words; the Frame adds no `h1` and keeps position before `<main>`.
- **IMPOSSIBLE:** a breadcrumb; a linked future; an outcome rendered for another relation; "nothing changed" on network loss; AI-derived without lineage; human-source and AI-derived sharing markup.

## RED → GREEN
- RED: modules absent. GREEN: 21 passed.
- **Disclosed deviation:** `ReconstructionNote` and its test (plus the FieldFrame tests) were added in the same step, so no RED was demonstrated for those four tests.
- `next/link` renders in static markup without the router; `LogoutButton` needs the App Router, hence the `exit` slot.

## Scope boundary
The origin grammar is applied only to SYSTEM STATE. Human Source content is F03; AI-derived is F04; evidence is F05/F06. The Challenge framing is not marked HUMAN, because authorship is not projected (OR-D); marking it would display certainty that cannot be reconstructed.

## Git state
Uncommitted.

## Result
PASS.
