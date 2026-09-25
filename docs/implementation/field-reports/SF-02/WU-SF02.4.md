# WORK UNIT REPORT
FIELD: SF-02 — NQIRY SYMBIOTIC INTERACTION FIELD (materialization of doc 22)
WORK_UNIT: WU-SF02.4 — Workspace Overview Field and Workspace Field (22 §12.2, §12.3)

## Mission
Rewrite `app/workspaces/page.tsx` (overview) and `app/workspaces/[workspaceId]/page.tsx` (Workspace) on the
topology primitives, projecting only `GET /auth/me`, `GET /workspaces`, `GET /workspaces/{w}` (orientation:
role, heldAuthorityClasses, authorized, governanceCapable) and `GET /workspaces/{w}/overview` (members,
challenges, capabilities), mutating only through `POST /workspaces` (keyless F01 founding),
`POST /workspaces/{w}/challenges` and the membership route.

## MUST BECOME TRUE
Overview Field:
- Core "Workspaces" (`ws-title`) = the identity/access core; orbit `workspaces-list` with the
  `found-workspace-node` (a `possible` button that focuses the founding form's `#workspace-name`) and one link
  node per accessible Workspace (the server list, nothing more).
- Action plane: the founding form (F01 test ids kept), `workspaces-checking` while the read is pending,
  `workspaces-denied` when `/auth/me` is denied, `workspaces-empty` when the list is empty.
- The exit relation (Log out) exists only after the authoritative identity read resolved
  (`exit={identity ? <LogoutButton/> : null}`) — root repair of the mocked-lane logout race (below).

Workspace Field:
- Core = the Workspace (`orientation-workspace-name`) with the human position sentence.
- Ring 1 `challenges-list`: `new-challenge-node` (`possible` only with `capabilities.createChallenge`, else
  `unavailable` + reason `challenge-create-unavailable`) and one link per Challenge.
- Ring 2 `members-orbit`: governance nodes for `heldAuthorityClasses`, human nodes for members.
- Planes: action (create-challenge form / reason, `challenges-empty`, `non-proof-fixture`), governance
  (`orientation-role/authorized/governance-capable`, `members-list`, add-member form test ids), proof
  (`workspace-authority-proof` ProofDepth, `orientation-authority-classes`).
- Boundaries `orientation-error / rejected / denied` on the read path; while unconfirmed the exit slot is
  `null` unless a boundary is shown.

## MUST REMAIN IMPOSSIBLE
- A "Create Challenge" or "Add member" control not backed by the server capability.
- Any role inference in the page (the gate caught the `isGovernanceRoot` token in the first draft; the page now
  passes the F01 projection name `governanceCapable` to `humanPosition`).
- Refs read during render (React Compiler rule): the founding node focuses the input through
  `document.getElementById(...)?.focus()` inside the event handler.

## Defect found by the mocked lane and repaired at the root
- Symptom: mocked run 1 (78/81) — `auth.spec` logout test failed with "element detached".
- Reconstruction (repro script `logout-repro.mjs`): the page's mount-time `GET /auth/me` was still in flight when the
  test switched the mock to 401; the Logout control rendered from the *previous* identity and was detached when the
  read resolved.
- First Broken Relation: EXIT RELATION → AUTHORITATIVE IDENTITY READ. A relation existed before its projection.
- Root repair: the exit slot is rendered only after the read resolves (overview: `identity ? … : null`; Workspace:
  `null` while unconfirmed). Mocked run 2: 81/81.

## Preserved contracts
F01/F02 mocked specs (`workspaces.spec.ts` 10, `auth.spec.ts` 6 — unchanged): founding form test ids,
`workspaces-checking/denied/empty`, `orientation-*`, `members-list`, add-member labels ("Member user id",
"Role", "Add member"), `command-outcome[data-outcome]`. Real stack: "Workspace name" / "Create Workspace",
"Challenge title" / "Create Challenge", `members-list` contains the member name.

## Proof
Mocked lane (all F01/F02/SF-01 specs) and real stack on the final tree: WU-SF02.7. Browser evidence states
7–10 (owner, desktop + Pixel 7) and 25–26 (outsider: empty overview, denied Workspace): WU-SF02.8.

## Result
PASS.
