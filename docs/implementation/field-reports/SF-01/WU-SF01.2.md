# WORK UNIT REPORT
FIELD: SF-01 — SYMBIOTIC FRONTEND FOUNDATION
WORK_UNIT: WU-SF01.2 — Position: Relation Trace (pure)

## Mission
Repair the First Broken Relation at its root. Position is derived from the confirmed canonical
projection as a Relation Trace, not assembled as page navigation (21 §12, CF-01, CF-02, §14 NOT_FOUND,
falsifier 32).

## Relation materialized
`established parent → established child → current relation → lawful possible relation`, built only
from confirmed coordinates.

## Files changed
- NEW `apps/web/lib/field/position.ts`: `accessTrace`, `workspaceNameTrace`, `workspaceTrace(overview)`, `challengeTrace(detail)`, and `sessionTrace(position)`.
  - `sessionTrace` is a primitive only. It is NOT adopted, because the Session page is in the F03 contact zone.
  - Inputs are the published F02 types (`WorkspaceOverview`, `ChallengeDetail`, `SessionPosition`, `Capability`), imported read-only.
- NEW `apps/web/tests/field/position.test.ts` (12). Fixtures mirror `inquiry_queries` field for field.

## Test-first intent
- **TRUE:**
  - access context alone before confirmation;
  - Workspace → possible or unavailable Challenge relation, from `createChallenge`;
  - Challenge → possible or unavailable Session relation, from `openSession`, with the server reason code;
  - the Session primitive carries its establishing Command, or `null` when none is recorded.
- **IMPOSSIBLE:**
  - a Session coordinate in any pre-Session trace;
  - a future relation carrying an `href`;
  - more than one current coordinate;
  - a linked current coordinate;
  - an invented Challenge title.

## RED → GREEN
- RED: module absent.
- GREEN: 12 passed. Fixture typing was corrected once (inference of a default parameter was too narrow); the test logic was unchanged.

## Ceilings
- The previous state is not projected by F02 (`establishedBy` has no state-before), so the trace cannot show it. Open relation OR-C.
- `phases` (enum-index linear) is intentionally not used as trace history (OR-E).

## DeepSweep
- Chain: CF-01 → PF-01 → CF-02 (pre-Session truth) → authority unchanged (capabilities only select possible vs unavailable; nothing is computed) → API unchanged → pages (WU-SF01.4).
- Inverse: a trace segment ← `workspace` / `challenge` / `capabilities` of a confirmed F02 read ← canonical rows.

## Git state
Uncommitted.

## Result
PASS.
