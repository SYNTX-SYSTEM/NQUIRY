# WORK UNIT REPORT
FIELD: SF-02 — NQIRY SYMBIOTIC INTERACTION FIELD (materialization of doc 22)
WORK_UNIT: WU-SF02.3 — Challenge Field (primary demonstration surface, 22 §6, §12.4)

## Mission
Rewrite `app/workspaces/[workspaceId]/challenges/[challengeId]/page.tsx` as the Challenge Field: the Challenge
is the Core; Sessions and the New-Session relation are ring 1; governance (who holds session control here) is
ring 2; the action, governance and proof planes carry the same relations in depth. Everything is projected from
`GET /workspaces/{w}/challenges/{c}` (`challenge`, `sessions[]`, `sessionControllers[]`, `capabilities`) and
mutated only through `POST …/challenges/{c}/sessions` and `POST …/authority-bindings`.

## MUST BECOME TRUE
- Core = the Challenge title with its framing; `data-core-state` current while confirmed, `loading` with
  `exit={null}` while the read is pending (`challenge-loading`), `boundary` on a load failure (`load-failure`).
- Ring 1 `sessions-list`: the `new-session-node` is `possible` (a button "Open Session") only when
  `capabilities.openSession.available`; otherwise `unavailable` with the server reason as its description
  (`session-create-unavailable`) and no control. Each existing Session is a link named by server projection
  ("Session opened <date>" + `StateName`), never a client ordinal.
- Ring 2: one governance node per SESSION_CONTROL_RIGHT holder (`holder`, `grantedBy`, scope).
- Planes: action (Open a Session; `sessions-empty`; effect relation `open-session`), governance
  (`challenge-authority-proof` ProofDepth with `challenge-authority-list/empty`; grant form "Grant session control
  to" / "Grant session control for this Challenge", relation `grant-challenge-session-control`), proof
  (identifiers, `non-proof-fixture` marker when the Workspace is a NON_PROOF demo founding).
- One effect lifecycle per surface (`useEffectField`), one `command-outcome` at a time; `open-session` commits
  → navigation to the new Session after the canonical re-read.

## MUST REMAIN IMPOSSIBLE
- A Session coordinate before `CreateSession` commits; a disabled "authority" button instead of the reason.
- An Open-Session control not backed by `capabilities.openSession`.
- Any client-side inference of who may open a Session.

## Preserved contracts (asserted by unchanged specs)
F02 real-stack: `getByRole("button", {name: "Open Session"})`, `session-state` on the target page, "Grant
session control to" / "Grant session control for this Challenge", `command-outcome[data-outcome]`. SF-01
mocked and real-stack: `sessions-list` links named "Session opened …", `session-create-unavailable` reason,
`challenge-authority-proof` closed-by-default disclosure, trace/NOT_FOUND reconstruction.

## FALSIFIER / RED / GREEN
The Challenge Field was rewritten against the SF-01 mocked specs (`tests/e2e/sf01-field.spec.ts`, Challenge
tests: trace from projection, unconfirmed trace, NOT_FOUND, unavailable relation, REQUESTED ≠ COMMITTED,
C3-01, INDETERMINATE, commit marker, C3-06, grant boundaries, proof depth, responsive order, reduced motion).
Structural selectors that named SF-01 zones were moved to `field-core` / `data-plane`; the responsive test
gained desktop orbit assertions (`.orbit` present, nodes absolutely positioned) and the phone stack assertion.
Mocked lane on the final tree: WU-SF02.7. Real stack (F02 flow + SF-01 real spec on the Challenge Field):
WU-SF02.7. Browser evidence (states 11–13: desktop, Pixel 7, reduced motion): WU-SF02.8.

## Result
PASS. The Challenge Field is the primary demonstration surface of the evidence set (`challenge-field-PRIMARY-facilitator`).
