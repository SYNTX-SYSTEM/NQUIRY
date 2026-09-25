# WORK UNIT REPORT
FIELD: SF-02 — NQIRY SYMBIOTIC INTERACTION FIELD (materialization of doc 22)
WORK_UNIT: WU-SF02.5 — Session Field: reconstructing lifecycle Field, Human Question Field, Frozen Field (22 §12.5–§12.7, §26, §30)

## Mission
Rewrite `app/workspaces/[workspaceId]/sessions/[sessionId]/page.tsx` as the Session Field on the topology
primitives and re-home the published F03 working surface (`components/f03/BurstCapturePanel.tsx`) on the ONE
effect lifecycle of the page, preserving every F02/F03 behaviour, the Human Question Law and authority. The
only projection is `GET /workspaces/{w}/sessions/{s}/position` (13-state lifecycle `phases[]`, `actions.*` with
`relevant`, `sessionControllers`, `participants`, `admitCandidates`, `burst`, `questionSet`, `establishedBy`,
`serverNow`); mutations are the F02 transitions, `/participants`, `/authority-bindings`, F03
`/burst/questions` and `/transitions/complete-burst`.

## MUST BECOME TRUE
- Core regime (`coreRegime(p)`): `human` in QUESTION_GENERATION with an ACTIVE HUMAN_ONLY Burst (Human Question
  Field), `frozen` when the Burst is COMPLETED and the set is frozen (Frozen Field), else `current`. The core's
  state text contains `session-state`. The background regime follows (`human-question`, `frozen`, `session`).
- Ring 1 `session-phases`: all 13 canonical states as nodes in canonical order, `aria-current="step"` on the
  current one, states established / current / future with markers passed / current / later, label density by
  `lifecycleLabelDensity` (capacity 13 on this ring).
- Ring 2 `session-relations`: human nodes for participants, governance nodes for session controllers,
  an `unavailable` "Participation" node when neither exists.
- Planes: active phase (`active-phase`: intents/outcomes of the `session:` family, transition buttons for every
  *relevant* action with the server reason when unavailable (`action-reason-*`), the Burst `dl`
  (`burst-state`, `burst-mode`, `burst-absent`), the `BurstCapturePanel`), governance
  (`session-authority-provenance`, `participants-list/empty`, admit select "Admit participant" / "Admit to
  Session", grant form "Grant session control to" / "Grant session control for this Session" on the
  `governance:` family), proof (`session-last-transition` = `establishedBy` provenance, `session-identifiers`
  ProofDepth, the legacy "Decision surface" link labelled NON_PROOF).
- Effect relations: `session:step:<ACTION>`, `session:admit-participant`, `governance:grant-session-control`,
  `session:capture:<textFingerprint>`, `session:complete-burst`; reconstruction = re-read of `/position`.
- `BurstCapturePanel` takes the page's `effect` and `reload`; details: committed capture "Your question was
  captured exactly as you typed it.", rejected `explainCaptureRejection` ("… Nothing was stored."), blocked "The
  Burst no longer accepts questions. Your text was not stored.", network_failure / indeterminate "Submitting
  the same text again retries the same submission; it cannot create a duplicate." (same key, 22 §27).

## MUST REMAIN IMPOSSIBLE (Human Question Law, 22 §43; F03 as published)
- Capture outside QUESTION_GENERATION / ACTIVE HUMAN_ONLY; capture without `actions.CAPTURE_QUESTION.available`.
- Peer question texts during an active Burst (the server's HD-13 filter is rendered as projected: own list,
  count for the controller, full set only when frozen).
- Completion without the explicit confirmation ("Complete Burst…" → "Freeze the set and complete the Burst").
- Any client timer other than the guidance `BurstTimer` (non-authoritative, "nothing closes it automatically").
- An analysis relation (BEGIN_ANALYSIS) anywhere: absent, not mocked (gate).
- Two lifecycles on the page (the panel no longer owns its own outcome state).

## Preserved F02/F03 contracts (unchanged specs, all asserted on the real stack)
`session-state`, "Begin setup", "Begin challenge capture", "Prepare protected Burst", "Open question
generation", "Admit participant" / "Admit to Session", `participants-list`, `burst-state`, `burst-mode`,
`burst-timer` ("Elapsed", "nothing closes it automatically"), `capture-form`, "Your question" (exact),
"Submit question", Ctrl+Enter submit, `own-question`, `own-question-text`, `own-questions-empty`,
`captured-count`, `action-reason-CAPTURE_QUESTION` (contains "participant"), `complete-button` "Complete
Burst…", `complete-confirm` ("cannot be undone"), `complete-confirm-button` "Freeze the set and complete the
Burst", `frozen-set`, `frozen-verified`, `command-outcome[role=alert]` on rejection containing "Nothing was
stored", `session-last-transition`, "Grant session control to" / "Grant session control for this Session".

## Deliberate semantics
- Transition buttons are shown for `relevant` actions only; each carries the server reason when unavailable.
- The Session controller and participant relations in the core sentence come from `humanPosition` (label);
  every control comes from `actions.*` (gate).
- The legacy `/decision` prototype stays reachable as a NON_PROOF link; it is not part of the Field.

## FALSIFIER / RED / GREEN
Unit: `primitives.test` (prefix-matched outcomes), `effectLifecycle.test` (detail), `burst` tests unchanged.
Real stack: F03 protected-question spec (five identities, denial/forgery/stale checks), F03 accessibility
spec (axe, keyboard-only capture and completion, Pixel 7), F02 inquiry-context spec — WU-SF02.7.
Browser evidence states 14–24 (draft without control, grant committed, Burst prepared, rejected input, own
question, participant own-only, phone Human Question Field, completion confirm, Frozen Field ×3): WU-SF02.8.

## Result
PASS pending the final lane results recorded in WU-SF02.7 (the Session Field is the only surface where a real
run failed in run 1; both causes were repaired at the primitive level, see WU-SF02.7 / WU-SF02.8).
