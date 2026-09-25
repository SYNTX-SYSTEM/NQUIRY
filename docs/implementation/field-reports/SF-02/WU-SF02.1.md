# WORK UNIT REPORT
FIELD: SF-02 — NQIRY SYMBIOTIC INTERACTION FIELD (materialization of doc 22)
WORK_UNIT: WU-SF02.1 — Dark Field identity, effect-lifecycle extensions, architecture gates

## Mission
Give the whole frontend the Field identity of 22 §17–§20 (dark immersive Field; cyan = living, blue = stable,
red = boundary, neutral = everything else; no green identity) and extend the SF-01 effect lifecycle so that
every relation can carry a relation-specific consequence without a second lifecycle per surface. Encode the
architecture's MUST-REMAIN-IMPOSSIBLE list as static gates over every Field source file.

## MUST BECOME TRUE
1. One stylesheet (`app/globals.css`) defines the Field identity through tokens; every colour of the Field is one
   of the four classes of 22 §18; the F02 light theme (green "settled" identity `--settled #2f5d62 / #9fd0d4`) is gone.
2. Legacy class names used by the untouched F02/F03 components (`.button`, `.panel`, `.outcome`, `.field`,
   `.tag`, `.frozen-artifact`, `.stack`, `.actions-row`, `.muted`, `.mono`) keep working on the dark identity.
3. A settled effect may carry a `detail` (relation-specific consequence) that renders after the consequence
   line; the reducer, the hook and `EffectOutcome` carry it without a second state machine.
4. An `EffectIntent` / `EffectOutcome` can own a *family* of relations (`relationPrefix`), so a payload-keyed
   relation (`session:capture:<fingerprint>`) still shows its intent and outcome.
5. A read failure never speaks of a requested change (SF-01 review D-2): the INDETERMINATE title on the read
   path is "The current projection could not be confirmed."
6. `textFingerprint(text)` (djb2 + length) keys a capture relation by its exact text, so an UNKNOWN outcome is
   retried with the same Idempotency-Key and changed text is a new intent (22 §26.4, §27).

## MUST REMAIN IMPOSSIBLE (gates, `tests/field/gates.test.ts`)
Over `components/field/**`, `components/f03/**`, `lib/field/**`, `lib/burst.ts`, the login page, the
Workspaces pages and the Session page (the file set is asserted non-empty and complete):
- no client timer anywhere except `components/f03/BurstTimer.tsx` (HD-11: time passing changes nothing);
- no role / viewer-flag inference except `lib/field/humanPosition.ts` (a label, never a gate);
- no F04 vocabulary (`BEGIN_ANALYSIS`, `begin-analysis`, `TRN_SESS_006`, `AIOP`, `MockProvider`, `ai_gateway`,
  `AnalysisContact`, `analysis-contact`): the analysis contact zone is absent, not mocked (22 §36);
- no AI invocation, no client persistence (`localStorage`, `sessionStorage`, `indexedDB`, `document.cookie`);
- no import of the F02 `Outcome` component (one effect grammar, 22 §25);
- every allowlisted presentation file never calls a command or auth function;
- the stylesheet contains no `green`, `--settled`, `#2f5d62`, `#9fd0d4` (22 §18.5).
Each gate predicate is proven non-vacuous against a planted violating sample (first describe block).

## FALSIFIER / RED / REPAIR / GREEN
| Test (L0) | RED before | Root change | GREEN |
|---|---|---|---|
| `effectLifecycle.test`: settle carries `detail`; absent detail is `null` | `detail` not on the settled state | `effectLifecycle.ts`: settled state gains `detail: string \| null`; settle event accepts `detail?` | ✓ |
| `outcomeSemantics.test`: read-path INDETERMINATE title has no mutation language; §39 verdict table unchanged for `network_failure` | title read "requested change" (D-2) | `READ_TITLE = { indeterminate: … }` applied only for path `read` (a first attempt also retitled `network_failure` and broke the §39 verdict test → limited to `indeterminate`) | ✓ |
| `primitives.test`: `EffectOutcome` renders `effect-detail` after the consequence; `relationPrefix` matches a payload-keyed relation | props absent | `EffectSurface.tsx`: `owns(relationOf, relation?, relationPrefix?)`; `<p class="effect-detail" data-testid="effect-detail">` | ✓ |
| `gates.test`: "green is not a Field identity" | RED on the F02 stylesheet by construction (it defined `--settled: #2f5d62`) | `globals.css` rewritten (tokens below) | ✓ |
| `gates.test`: the other MUST-REMAIN-IMPOSSIBLE predicates | each proven against a planted sample; the SF-01 gate set (which forbade F03 vocabulary) was obsolete after the F03 sync and is replaced | — | ✓ |

## Identity tokens (`:root`)
`--bg-deep #03060c`, `--bg #070b14`, `--surface #0e1524`, `--ink #e8eef8`, `--muted #93a2ba`,
`--cyan #58dcff` (living: current, possible, human), `--blue #86abff` (stable: established, committed, frozen,
authority), `--red #ff7b86` (boundary: denied, rejected, unknown, not found, load failure), `--human #f1e6d2`
(human authorship marker); legacy aliases `--accent/--authority/--attention/--fault`; geometry tokens
`--field-size 720px`, `--core-size 196px`, `--orbit-r-1 232px`, `--orbit-r-2 322px`, `--node-w 132px`; motion
tokens `--motion-settle 480ms`, `--motion-breathe 9s`, `--motion-drift 160s`, `--motion-relation`.
Reduced motion: `*, *::before, *::after { transition: none; animation: none }` (extended to pseudo-elements after
browser defect D1 in WU-SF02.8; the first rule only covered elements).

Text-bearing animations never change opacity (WU-SF02.8 defect D4): `relation-settle` moves the outcome by
3px and settles its border; `node-shimmer` (loading nodes) pulses the border colour. WCAG contrast therefore
holds at every instant of an animation, not only at rest.

## Proof
- L0 vitest: 219/219 on the final tree (`tests/field/effectLifecycle.test.ts` 16, `outcomeSemantics.test.ts`
  15, `primitives.test.tsx` 25, `gates.test.ts` 5 groups, plus the unchanged baseline).
- tsc 0 errors, eslint clean (React Compiler rules included).

## Not changed
`lib/api/inquiryClient.ts`, `components/f02/**` (still used by the Field: `Unavailable`, `AppShell`,
`LogoutButton`), `components/f03/{BurstTimer,FrozenQuestionSet,OwnQuestions}.tsx`, `packages/**`,
`apps/api/**`, `migrations/**`, dependencies, the legacy `/decision` prototype.

## Result
PASS (L0/L5). Adopted by every surface in WU-SF02.3–SF02.6.
