# WORK UNIT REPORT
FIELD: CYAN_FRONTEND_SYMBIOSIS (Architecture 27 v4, `b0a5101` on `pfc-integration`)
WORK_UNIT: CYAN-PCPG-06 — attachment rendering (level 0.5), contextual governance panel (level 1), deep field inspection (level 2), boundary card (§09.3)
DATE: 2026-10-04 · BASE: `baseline-CYAN-2026-10-04` → `308ab88` (over `checkpoint-CYAN-IDENTITY-PRESENTATION-01`); predecessor `checkpoint-CY-PCPG-05` `2d6163b` (HUMAN_ACCEPTED)
AUTHORITY: the human mandate of 2026-10-04 ("reconstruct the complete real NQUIRY frontend Field from the authoritative system and make the frontend substantially more semantically expressive and coherent with the system it projects; derive the work from the reconstructed Field"); RED pin for the local lanes `checkpoint-PFC-PCPG-18` `41b4324` (HD-27 + the PCPG-05 pin authorization); recorded next relation in `WU-CYAN-PCPG-05.md` §Status.

## Field reconstruction (before the delta)
| Architecture 27 v4 relation | State at the base |
|---|---|
| Level −1 semantic field attachment (PCPG-R12/1 consumption) | materialized (PCPG-01, -05) |
| Level 0 ambient governance perception (object membrane) | materialized (PCPG-04), HUMAN_ACCEPTED |
| **Level 0.5 action-adjacent friction** — crossed steps placed at the existing object areas (§06.3–06.5, §07.2–07.3, §08.3, §09.2, §10.3, §11.3) | **absent**: the placement map existed (PCPG-03) and was consumed by nothing; `cy04` law "nothing at any attachment target" |
| **Level 1 contextual governance panel** (§03, §15 `<details>Field / Governance`) | **absent** |
| **Level 2 deep field inspection** (§03: basis → semantic observation → deltas → chain → capability → ceiling → not materialized) | **absent** |
| **§09.3 boundary card** (what stopped · requested in · why · after · HAR · placement) | **absent** |
| §17 spoken facts | partial (capability words in the membrane) |
First broken relation: `attachPresentation(presentationOf(observation))` → rendering at the mapped targets (exactly the relation PCPG-05 recorded as next). Second: the same object inspected more deeply (panel, card). Repaired through one pure derivation feeding both.

## Delta (CYAN only; RED pin unchanged; no PURPLE; no production)
| File | Change |
|---|---|
| `apps/web/lib/field/pcpgRendering.ts` (new) | pure `governanceRendering(presence, presentation)` → `areas` / `byArea` (per existing area: placed steps as "<operation> · <execution class> — <result · reasonCode>", FBR and HAR flags from the chain, provider-not-executable, superseded, summary), `boundary` (§09.3 card), `panel` (label, three capability axes, basis, semantic observation, delta rows with placement words, card, next valid transition, provider / "Send not materialized", Session-level proof ceiling, not materialized, §17 spoken sentences); words: INDETERMINATE → indeterminate, `target` null → unresolved, `operation` null → Unknown operation |
| `apps/web/components/field/GovernanceAttachment.tsx` (new) | the marker: `<aside data-governance-attachment=area data-prominence=quiet/explicit/prominent>` with field word, summary, one line per placed step (+ marks "first broken relation", "Human Authority required", "retained"), provider line; nothing for an unplaced area; no control |
| `apps/web/components/field/GovernancePanel.tsx` (new) | `<details class="proof-depth governance-panel">` "Field / Governance · <label>": the deep view in the architecture's order incl. the boundary card; without a current observation it states the absence only; no control |
| `apps/web/components/field/IntentObservationChamber.tsx` | optional `panel` prop; the panel is the chamber's last element (the same object, inspected more deeply) |
| `apps/web/app/workspaces/[workspaceId]/sessions/[sessionId]/page.tsx` | `rendering = governanceRendering(observationPresence, governance)`; markers mounted at the active-phase chamber (session-state, burst-panel, question-set areas — after the F03 contact zone, which stays untouched), the Session control chamber (boundary area), the proof chamber (FIELD_PANEL fallback), the derived chamber (provider-related), the decision entry chamber; `panel={rendering.panel}` |
| `apps/web/app/globals.css` | `.governance-attachment*` (strip in the chamber's own vocabulary; prominence by attention/ai edges), `.governance-panel*`, `.boundary-card` |
| `apps/web/tests/field/pcpgRendering.test.tsx` (new, 13), `tests/e2e/cy09-attachments.spec.ts` (new, 6 × 2 devices), `playwright.sf01.config.ts` (mobile regex `cy09`), `scripts/pcpg06-mutation-proof.mjs` (new, 12) | falsifiers below |
| `tests/field/pcpgAttachment.test.ts` 20, `tests/field/governanceMembrane.test.tsx` 19 | successor truths: the relation reaches the UI only through the rendering derivation; the membrane still never attaches |
Not placed by design: `lifecycle-ring` and `path-station` (SESSION_STATE_AREA is rendered at the active-phase chamber, the one session-state surface the organism owns as a chamber); `boundary-marks` (BOUNDARY_AREA is rendered at the Session control chamber; the marks belong to the F02/F03 affordances); `decision-chamber` (decision surface, another route). `DEEP_FIELD_INSPECTOR` remains structurally absent; its content is the panel's deep view.

## Laws (v4 §21, §18) and where they hold
| Law | Materialization |
|---|---|
| NO OBSERVATION != CURRENT | no marker anywhere, panel states the absence (unit + browser) |
| PRESENTATION LOCATION != GOVERNANCE TRUTH; CROSSED FACT != UI COMPONENT | placement only via categories → attachment map → existing areas; the derivation never reads clause text (law + M6); no backend component names (law) |
| INDETERMINATE never denied; `target` null never out of scope; `operation` null = Unknown operation | words table + M1, M2, M9 |
| Send not materialized; canSend never a gate | panel + marker words; M4; superseded → canSend absent (M7) |
| HAR never an approval control; no send-like control | markers and panel contain no button/a/input/form (unit + browser); M5, M8 |
| FBR only from `chain.firstBrokenRelation` | M10, M12; card "first in chain" when no predecessor |
| the organism stays primary | SF-05/SF-04/SF-03/CY-01 lanes unchanged; no sideways scroll on Pixel 7 |

## Proof
| Lane | Result |
|---|---|
| Rendering falsifiers `tests/field/pcpgRendering.test.tsx` | **13 / 13** |
| Full unit suite (37 files, gates laws over the Session page) | **661 / 661** |
| Browser `cy09-attachments` (desktop + Pixel 7) + preservation `cy04-membrane`, `cy05-observation` | **26 / 26** |
| Preservation `cy01-field`, `sf05-field`, `sf04-field`, `sf03-field` (desktop + Pixel 7) | **103 passed, 27 pre-existing skips, 0 failed** |
| `tsc --noEmit`, `eslint .` | clean |
| Mutation proof `scripts/pcpg06-mutation-proof.mjs` | **12 / 12 killed**, byte-identical restore (three survived the first run through falsifier gaps — chain without FBR, loose page wiring law, authority-chamber FBR flag — closed before closure) |
| Real producer, review runtime `127.0.0.1:13500` (RED `checkpoint-PFC-PCPG-18`, this tree) | observation "Analyse the questions, pick the primary question, and give Constantine control" → membrane "Human Authority required"; markers at question-set, authority chamber (prominent), decision entry (prominent), derived chamber (prominent), proof chamber (quiet: the unmapped clause SEMANTIC_UNKNOWN); card: REQUEST_QUESTION_ANALYSIS · provider computation, first in chain, HAR D1 → AUTHORITY_BOUNDARY · NO_QUESTION_SELECTION_RIGHT, chain partial; both devices, no sideways scroll (`browser-evidence/pcpg-06/SUMMARY.md`) |
| Lane hygiene finding | a parallel `next build` and `next dev` had corrupted `.next`; the preservation lanes answered 404 until the cache was cleared — not a product defect (recorded) |

## Status
CYAN-PCPG-06: TECHNICALLY CLOSED → **READY_FOR_HUMAN_FRONTEND_REVIEW** (`HUMAN_REVIEW_GUIDE_PCPG-06.md`). Not
FIELD_GREEN until accepted; not REVIEWED_FIELD, not PUBLISHED_FIELD, not live. Disclosed ceilings unchanged: RED
producer checkpointed not reviewed/published; FIXTURE_NON_PROOF / MOCK semantics; SEND not materialized; R-13 not
started; provider call none; `flags` always empty and every provider delta INDETERMINATE at PCPG-18 (runtime
disclosure of the architecture).

Remaining Architecture 27 relations after this unit: §18 microinteractions beyond the native disclosure (marker →
area focus, delta → span highlight) — presentation refinements for a later unit; the decision surface's own
attachment (`decision-chamber`, another route).

## Checkpoint
| | Value |
|---|---|
| Field commit | `c2a54267ac69bd55749c1947234191558c5f7f76` (tree `13bd497094bf4fa36fd43d85de8241e6dbe78113`) |
| Tag | `checkpoint-CY-PCPG-06` → tag object `4a54b3feffdc7a188bf83bc710272082be50e17d` → `c2a5426`; pushed |
| RED pin (local lanes) | `checkpoint-PFC-PCPG-18` → `41b4324a75077ec33b00ed3a878db7a318fc00d8` (unchanged) |
