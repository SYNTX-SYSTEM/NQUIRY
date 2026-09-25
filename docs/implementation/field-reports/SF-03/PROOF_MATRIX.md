# SF-03 PROOF MATRIX

Every doc 23 falsifier (§20, 1–58) → the lane(s) that would turn it RED → the evidence on the final tree. This is
the INVERSE deep sweep of the delta; the doc 22 falsifiers 1–77 remain proven by `SF-02/PROOF_MATRIX.md` and are
re-exercised here by the unchanged lanes and by harness states 1–30 (SF-02 regression states, re-run on the SF-03 tree).

Lanes: **L0** vitest (`tests/field/geometry.test.ts` 11, `sf03-primitives.test.tsx` 8, SF-02 suites; 232 on the final
tree) · **L3** isolated mocked browser incl. `tests/e2e/sf03-field.spec.ts` (stress content; desktop + Pixel 7; 102) ·
**L7** isolated real stack (14 specs) · **E** SF-03 browser evidence harness on the isolated production runtime
(`review/browser-evidence-2026-09-25/`, states 1–30 regression + 10 doc 23 acceptance states (19, 32–40); final = run-5) ·
**P** `harness/perf-ab.mjs` (×4 CPU throttle) · **H** human review of the screenshots · **C** code-level fact.

| # | Falsifier (doc 23 §20) | Lane(s) | Evidence |
|---|---|---|---|
| 1 | background visually distracting | P, H, C | two blobs ≤ 0.24 alpha, 150–190 s cycles, ±2–3 vmax; E checks min cycle ≥ 90 s; screenshots |
| 2 | generic particle wallpaper | C, H | 7 particles, opacity-only over 96 s; no DOM particle field; screenshots |
| 3 | ambient motion implies state | C, L3 | `aria-hidden`, `pointer-events: none`, no attribute bound to backend state; no test reads it as meaning; gate: no timers |
| 4 | reduced motion loses depth | L3, E | spec "reduced motion keeps every ambient layer"; E `session-field-reduced-motion-depth` (0 animated, ≥ 2 layers shown) |
| 5 | background harms responsiveness without reduction | P | first draft 30 ms → reduced 16.3 / 19.2 ms rAF at ×4 (WU-SF03.3) |
| 6 | node label crosses its border | L3, E | containment probe on every `.node-body` (stress + review content); E `containment` checks on 6+ states |
| 7 | panel label crosses its border | L3, E | same probe on `.plane` and `.trace li` |
| 8 | text made unreadably small | L3, E, C | probe: no material text < 11.5 px; tokens `--type-*`; estimator never shrinks type (`fits:false` instead) |
| 9 | long content causes overlap | L3, E | stress spec + E stress states: 0 overlaps (`nodeOverlaps`) |
| 10 | long content silently clipped | L3, E | core title asserted complete and unclipped (`-webkit-line-clamp` removed); closed proof depth is explicit disclosure |
| 11 | node frames fixed when content needs expansion | L0, L3 | no inline width (SSR test); `width: max-content` (C); frames measured ≥ estimate |
| 12 | nodes overlap | L0, L3, E | geometry test (real content); collision loop; probes |
| 13 | nodes collide with the Core | L0 | geometry test (core box in the collision set) |
| 14 | relation paths obstruct labels | C, H | paths are spokes from the centre to node centres; a spoke never crosses another node's frame unless nodes overlap (12) — human review for aesthetics |
| 15 | responsive geometry removes a capability | L3, L7, E | phone stack keeps grant / unavailable reason / identity (spec); F02/F03 mobile real specs; E phone states |
| 16 | random / unstable geometry | L0, L3 | pure function; spec "identical node positions on reload"; hover "not stable" defect repaired (mode/measure loop) |
| 17 | false authority through proximity | C, H | gravity carriers unchanged (size, intensity, weight); ring membership by relation kind, never by authority rank |
| 18 | Field compressed despite space | E, H | `BREATHE` fractions, column ≥ 700 / ~800 px, ellipse into the longer axis; E "topology uses ≥ 780 px" on wide |
| 19 | breadcrumb detached from the Field | H, E | rail shares depth/border/glow language; separators are relation traces; screenshots |
| 20 | breadcrumb breathing harms readability | L3, E | text ≥ 13.5 px; only the pseudo-element animates |
| 21 | breadcrumb characters move | L3, E | current label's bounding box identical 600–700 ms apart; `transform: none`, no text animation |
| 22 | current orientation ambiguous | L3, E | `aria-current`, cyan glow, weight; unchanged status words |
| 23 | identity left-aligned on desktop | L3, E | identity centre within 12 px of the viewport centre (desktop + wide) |
| 24 | identity displaces navigation | L3, E | trace and exit visible in the same rail; three-column grid |
| 25 | vertical card waterfall on wide desktop | L3, E | two instrument columns at 1600; governance/proof beside the active instrument |
| 26 | scroll caused by unused horizontal space | E, H | wide states: constellation beside the Field; human judgement on remaining scroll |
| 27 | horizontal composition destroys grouping | C, H | each plane keeps its headings/content; only placement changes |
| 28 | instrument composition hides proof | L3, E | proof reachable in every mode (spec: `challenge-authority-proof` visible; E proof checks) |
| 29 | hides governance | L3, E | grant control visible at 1600 and on the phone |
| 30 | available action unreachable | L3, L7 | Open Session / grant / capture / completion reachable (mocked + real specs) |
| 31 | instruments dominate the Field | C, H | topology column ≥ 52 %; instruments in depth |
| 32–34 | dashboard / forms / cards as primary grammar | H, E | E "not a card grid" checks (SF-02 states); screenshots |
| 35 | proof disconnected from its relation | E | reciprocity: governance focus → proof/governance instruments respond; proof plane beside governance on wide |
| 36 | governance disconnected from its authority relation | E, L3 | governance orbit ↔ governance instrument reciprocity |
| 37 | hover reciprocity implies state change | L3 | hover on Open Session: 0 POSTs, no outcome, node state unchanged |
| 38 | hover reciprocity implies authority | L3, E | unavailable relation stays unavailable with its reason during reciprocity |
| 39 | focus behaviour inaccessible by keyboard | L3, E | keyboard focus sets the same attribute (spec + E `reciprocity-keyboard-focus-governance`) |
| 40 | mobile loses capability | L3, L7, E | phone stack checks; mobile real specs |
| 41 | mobile keeps desktop geometry at the cost of readability | L3, E | phone rows full width > 250 px; no text < 11.5 px |
| 42 | lifecycle labels unreadable | E | all 13 labels visible, ≥ 12.5 px (`human-question-field-wide-constellation`, `session-field-wide-frozen`) |
| 43 | human input subordinate to proof detail | E, H | human plane holds the first column; proof beside/below governance |
| 44 | controller and participant conflated | E, L7 | node states `human` vs `governance` + markers; F03 real specs |
| 45 | Owner implied superuser | E, L7 | SF-02 states 8/10 (Challenge creation unavailable for the Owner with reason), 14 (no control) |
| 46 | controller appears to see content during ACTIVE HUMAN_ONLY | L7, E | F03 real spec; E state 18 (count only, no peer text) |
| 47 | committed effect claimed before re-read | L3, E | SF-02 effect tests unchanged; E states 15, 21–22 |
| 48–50 | visual delta changes backend / command / projection semantics | C, L7 | `apps/api`, `packages`, `migrations`, `lib/api/*` untouched; real stack green except the budget note |
| 51–57 | existing tests regress | L0, L3, L7 | 232 / 102 / 12 (+2 budget timeouts, no assertion failed) |
| 58 | Field not reconstructable from evidence | E | every state records projection, checks, HTTP, axe, keyboard walk and screenshot; `setup-scenario.mjs` recreates the relations through the product |

## Ceilings (disclosed)
- Falsifiers 1–2, 14, 17, 19, 26–27, 31–34, 43 are visible-identity judgements: structure is asserted, the human decides.
- The isolated real-stack F03 protected spec exceeds its 90 s budget on this host under load (both projects, no
  assertion failed): environment ceiling recorded in WU-SF03.7 with the re-run result.
- Doc 23 §9.4 breadcrumb → Field reciprocity was not implemented (optional; recorded in WU-SF03.4).
