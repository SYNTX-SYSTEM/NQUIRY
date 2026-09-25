# FIELD REVIEW — SF-05 NQUIRY SYMBIOTIC FRONTEND HUMAN REVIEW REPAIR (doc 26)
STATUS: READY_FOR_HUMAN_FRONTEND_REVIEW — not FIELD_GREEN, not APPROVED, not PUBLISHED, not RELEASE_READY (human authority closes those)
Tree: worktree `frontend-symbiotic` at HEAD `644e1c8` + the uncommitted SF-02/SF-03/SF-04/SF-05 materialization (nothing reset, committed, tagged, pushed, merged or published). Architecture: doc 26 (sha256 `14ed130a7b8c5568…`, byte-identical copy in the worktree). Visual reference image: used for the right side's design language only (contours, translucency, nuclei, luminous relations); no layout, label, chart, gauge or watermark reproduced; the left field untouched in grammar.

## 1. FBR closure map (doc 26 §6)
| FBR | Root repair | Proof |
|---|---|---|
| HR-01 duplicate-looking Workspaces | `normalizeWorkspaces()` (id-normalization before geometry; homonyms disambiguated by founding time · id8) | L0 workspaces.test; L3 sf05; H 57–60 |
| HR-02 waterfall | ring segmentation (inner 5 + founding, outer rest); constellation 224 px capsules | L3 sf05 geometry; H 57–60 |
| HR-03 sidebar grammar | organ v2: one surface, faint membranes, contours, glyph/title/marker/tone per class | L3 sf05 chambers; H 61–68 |
| HR-04 proof text | `ProvenanceSpine` | L0/L3/H |
| HR-05 undifferentiated classes | `data-semantic` chamber classes + tone tokens; authority chain, roster marks, tokens, boundary classes | L0/L3/H |
| HR-06 `Committed.` boxes | commit resonance event after the re-read; quiet proof line | L0/L3/H 12 |
| HR-07 passive login | attention/focus reciprocity, dense stars, membrane, quiet loading | L3/H 54–56 |
| HR-08 breadcrumb wrap | field-path compression law | L3/H 66 |
| HR-09 Decision Surface raw | field frame + chambers around the unchanged components | L3/H 68 |
| HR-10 identifiers | `Token`/`Identifiers` (separator breaks, keep-all, copy) | L0/L3 |
| HR-11 confirmation | confirmation chamber (irreversible class, facts, cancel/commit) | L3/H 22 |
| HR-12/13/14 hover, ambient, breathing | intensification (auras, pulses, breathing phase, dense stars) | L3/P |
| HR-15 forms in a sidebar | `chamber-action` grammar, chamber-integrated controls | L3/H |

## 2. Proof ladder on the final tree
| Lane | Result |
|---|---|
| L0 vitest | 287 / 287 (25 files; SF-05 adds workspaces 7 · sf05-primitives 9 · fieldEvent 4; sf03/sf04 primitives updated) |
| L5 tsc / eslint | tsc 0 errors · eslint clean (React Compiler rules) |
| L3 isolated mocked browser (desktop 1280 + Pixel 7) | 168 / 168 — desktop 1280 + Pixel 7, 2.7 min (sf05 36 cases incl. reduced motion; sf04 30; sf01/sf03/decision/etc. regression) |
| L7 isolated real stack (alone) | F03 protected human question spec alone 2 / 2 (2.6 min, load ≈ 5) · full lane: 12 / 14 in 9.5 min (full parallel lane, load ≈ 6): the F03 protected human question spec (desktop + mobile) hit its 90 s budget while taking a screenshot, exactly as in chain 5; it passes alone 2 / 2 on this tree (11 min earlier) and in every isolated run since chain 6 — recorded as observation 7, not a regression |
| H review harness, 68 states on :13400 | 68 / 68 (run-10; SF-04 states 1–53 + SF-05 54–68; runtime rebuilt from this tree, 30 same-named Workspaces in the scenario) |
| P perf-ab ×4 CPU throttle | access 16.7 ms · Challenge 16.9 ms · Workspaces overview 22.8 ms (30-capsule constellation) rAF median at ×4; hover 138 ms; trial click 315 ms — `performance/perf-ab-final.md` |

## 3. Performance (doc 26 §51)
perf-ab (`browser-evidence/harness/perf-ab.mjs`, ×4 CPU throttle, Chromium, rAF median / p95 over the settled page):

| Variant | access | Workspaces overview (30 capsules) | Challenge |
|---|---|---|---|
| A full | 16.7 / 17.3 | 22.8 / 47.1 | 16.9 / 22.9 |
| B no background | 16.7 / 17.1 | 16.8 / 25.0 | 16.7 / 17.1 |
| C no core layers | 16.7 / 17.1 | 17.2 / 27.9 | 16.5 / 17.8 |
| H static everything | 16.6 / 17.0 | 16.6 / 17.7 | 16.7 / 17.1 |
| K no dense stars | 16.6 / 17.2 | 19.5 / 38.7 | 16.5 / 18.4 |

Reading: the login field and every Field page except the many-Workspace overview sit at the frame budget (16.7 ms ≈ 60 fps at ×4).
The overview with 30 accessible Workspaces (a 3 500 px document with the constellation in stack mode) costs ~6 ms/frame above budget
at ×4, and variant B shows the cost is the fixed atmospheric background composited over the tall document, not the chambers,
currents or node breathing (already still in the constellation). At 1× this is ≈ 1.5 ms. Silencing the core anatomy there was
measured (run-9: 20.9 ms) and rejected: no gain, and it broke the core law (harness state 51). Density-aware packing / a
third ring for 12+ Workspaces (observation 2) would remove the tall document and is the follow-up. Hover response and the
trial click stay well under 350 ms at ×4; no large animated gradient exists in the tree (only opacity / transform / offset-path
animations, stroke-dash currents, per-particle fill-opacity).

## 4. Evidence
`browser-evidence/run-10` (final tree; 68 screenshots, results.json, MANIFEST.md; runs 1–9 = RED trail); review/FRONTEND_BROWSER_REVIEW.md; review/SWEEPS.md; PROOF_MATRIX.md; CHATGPT_REVIEW.md; tests/SF05-tests.md; architecture-binding/ (WU-26.0, WU-26.1–26.9).

## 5. Confirmations
- Backend semantics unchanged: no file under `apps/api`, `packages`, `migrations` differs; `lib/api/*` unchanged; no new call, no new field read; every capability, reason code, state word and outcome still comes from the server.
- BLUE untouched; RED (F04 worktree) not touched by this run.
- Nothing committed, pushed, tagged, merged or published.

## 6. Acceptance gate (doc 26 §58) — each line bound to a proof
one id → one node (L0/L3/H) · no duplicated list (H 57–60) · field space used (L3 columns/rings) · left field grammar retained (sf04 spec 30/30, sf01/sf03 regression) · right side not a sidebar (L3 organ/chambers, H) · differentiated chambers (tones ≥ 4 distinct) · proof has provenance (spine) · authority ≠ role/membership (chain vs marks) · participation ≠ authority (marks) · HUMAN_ONLY explicit (marker + seal) · frozen set immutable (artifact chamber, no inputs) · Decision Surface symbiotic (L3/H 68) · login living (L3/H 54–56) · hover stronger / particles more visible / ambient alive / nodes breathe (intensification + P) · reduced motion coherent (L3 ×3, H 67) · performance (P) · existing semantic tests (full L3 + L7) · new tests (L0 20 + L3 36) · BLUE/RED untouched · no publication · no FIELD_GREEN claim.

## 7. Known remaining observations (for the human)
1. Founding a Workspace, framing a Challenge and opening a Session navigate to the new context on commit; the origin surface performs no re-read, so no resonance event fires for them (the destination field is the visible effect). If wanted, a hand-over event on arrival is a small follow-up.
2. Beyond two rings (roughly 12+ Workspaces with long names at 1280 px) the overview compresses into the capsule constellation (three per row on the desktop column, four on tablets); a third ring or density-aware packing is a follow-up.
3. Stylesheet consolidation (five dead legacy selectors, five unconsumed doc 25 tokens) stays deferred so the reviewed tree is the proven tree.
4. The Decision Surface remains the PKG-29 prototype view (NON_PROOF) until F07 re-homes it; only its projection language changed.
5. The Workspace overview with 30 accessible Workspaces (the review scenario founds two per harness run) renders at 22.8 ms/frame under ×4 CPU throttle (≈ 1.5 ms at 1×); every other surface sits at the 16.7 ms budget. The cost is the atmospheric background over the 3 500 px constellation document (perf variant B), not a chamber, current or node animation; it goes away with the density-aware packing of observation 2.
6. The wide viewport (1600 px) uses the same three-capsule constellation column as 1280 px; the field space right of the organ stays free there (run-10 screenshot 57).
7. The real-stack F03 protected-question spec (`tests/real-stack/f03-protected-question-field.real.spec.ts`, 90 s budget, ~14 screenshots per case) times out in the full parallel real-stack lane on this host (chain 5 and the final run: 12/14, both timeouts in that spec) and passes alone every time (final tree 2/2). It is a lane budget under load, not a projection defect; raising the spec budget is a test-only follow-up outside this Field's scope (F03 published test).
8. The sf03 mocked "identity centred" / stress Workspace containment cases flaked once each in earlier full-lane runs under host load ≥ 20 (never in the final chains 8–10, never in isolation).

## Post-review note (2026-09-25, late)
The human review rejected the Workspace overview geometry of this Field (ring segmentation + capsule constellation) and a follow-up bounded-visibility experiment. By human instruction the Workspace field was restored to the SF-04 single containment ring (founding relation + every accessible Workspace; id normalization and homonym distinguisher kept), the stack capsule tuning was reverted to SF-04 (`width: auto`, 320 px membrane), and the review runtime database (:13400) was recreated with the three identities and one review scenario. The HR-01/HR-02 geometry rows, harness states 57–60 and the run-1…run-10 Workspace screenshots above describe the superseded geometry. Run screenshots are kept on disk, not in git (MANIFEST.md / results.json are committed).
