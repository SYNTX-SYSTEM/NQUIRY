# WORK UNIT REPORT

FIELD: AUTH / AUTHZ — the authorization lifecycle of the product Field (05 governance successors)
WORK_UNIT: WU-AUTHZ-01 — 05 GOV-003 REVOKE_MEMBERSHIP and GOV-004 ASSIGN_ROLE (change of the current role)

| Item | Value |
|---|---|
| ARCHITECTURE_SOURCE | 05 §12 GOV-003, §13 GOV-004, §14 (owner role restriction), §17 (REVOKED terminal), §18 (effectiveness), §28 GOV-015, §37 GOV-020 (membership removal cleanup), §45; 09 §23/§24 (membership / role aggregates), §64 command registry, §102.1 membership revocation bundle; 04 §4 / §17; 06 BND-003 / BND-004 / §31 |
| PREDECESSOR | `b56e46e` (WU-AUTH-19) |
| AUTHORITY | the human mandate of 2026-10-05 ("complete operational product field … workspace membership, roles, grants/capabilities, authorization, revocation"); the architecture already specified both operations (GAP-04-014 closed by 05); RED's `membership_operations_handler` left them as `SUCCESSOR_NOT_BUILT` — `pfc-integration` has not built them either (same file unchanged) |
| PROOF_RADIUS | 8 command falsifiers + 3 HTTP falsifiers → governance radius: membership operations, event basis (contracts), isolation sweep (routes registered), WU-16, F02 HTTP, binding revocation, F01 adversarial governance, typed provenance, `tests/regression`: **279 passed** |
| HUMAN_AUTHORITY_STATE | none crossed; GAP-05-001 (owner succession) stays undefined and is enforced as a refusal |

## FIRST_BROKEN_RELATION_BEFORE
MEMBERSHIP → REVOCATION and MEMBERSHIP → ROLE CHANGE did not exist: a member
could be added but never removed, a role never changed (off-boarding and
re-scoping impossible; the accepted product has human members).

## DELTA
| File | Change |
|---|---|
| `packages/persistence/membership_repository.py` | `revoke_membership` (version-guarded ACTIVE→REVOKED, `revoked_at`, version+1; `MembershipConflict`), `revoke_role`, `touch_membership`, `SqlAlchemyMembershipVersionReader`, `membership_target_ref` |
| `packages/application/membership_operations_handler.py` | `_governance_precommit` (the add-member gate factored: Workspace precheck, envelope, `record_attempt`, BND-001..005 = Owner role AND `WORKSPACE_GOVERNANCE_RIGHT`); `revoke_membership` (one CommitUnit: current role ended, every ACTIVE Workspace binding of the member revoked by the actor, membership REVOKED; `relation_refs` name them all); `change_member_role` (prior assignment ended, new one inserted, aggregate version advanced; before/after audited); refusals `MembershipNotFound` (after ALLOW: no disclosure), `GovernanceRootNotRemovable` (owner_id, ACTIVE governance right, or Owner role — three independent facts), `OwnerRoleNotAssignable` (reused), `RoleUnchanged` |
| `packages/events/contracts.py` | `CMD_REVOKE_MEMBERSHIP_COMMITTED`, `CMD_CHANGE_MEMBER_ROLE_COMMITTED` (aggregate `workspace_membership`, exact payload keys) |
| `packages/application/http_dispatch.py`, `apps/api/.../http/workspaces.py` | `POST /workspaces/{ws}/members/{user}/revoke`, `POST /workspaces/{ws}/members/{user}/role {role}`; envelopes `ok` / `denied {result, reasonCode}` / `rejected` / `failed_precommit` / `indeterminate`; `CommitDenied` mapped to `denied` |
| `packages/application/inquiry_queries.py` | overview capabilities `revokeMembership`, `changeMemberRole` (governance root) |
| tests | `tests/e2e/test_membership_revocation.py` (8), `test_http_workspaces.py` (+3; fixture now patches `http_f02.connect` too), `test_pfc_f09_2_isolation_sweep.py` (routes registered with a real member placeholder) |

## FALSIFIERS
root revokes → membership REVOKED v2, role ended, binding REVOKED by the actor, resolver denies, member gone from the roster and the accessible list, one audit event + one committed event, CommitUnit refs name membership / role / binding, the owner's root untouched · re-add after revoke → new membership, fresh role, old binding not restored, history keeps both rows · the governance root is not removable and not re-labelled (owner, right or role) · non-root member, non-member, non-human → the same denial (no disclosure), non-existent Workspace → precheck denial · unknown or already-revoked target → one not-found class (after the gate) · role change → prior ended, new current with the actor as grantor, aggregate v2, audit before/after, change back works · Owner / non-assignable / unchanged role refused before any effect · a stale membership version → `CommitDenied`, nothing changes · HTTP: envelopes, capabilities true for the root and false for a member, 401 without a session.

## DISCLOSED
Observer / Viewer stay outside the assignable set (RED's add-member choice, no recorded rationale; not widened here). `session_participations.left_at` is not written (no writer exists; a removed member's participations are already ineffective through the participation right's ACTIVE-membership condition — 05 "where governance impact matters"). GAP-05-001 owner succession remains a human/architectural decision. Frontend contact: CYAN member roster (AUTH/CYAN-ACCOUNT-02).
